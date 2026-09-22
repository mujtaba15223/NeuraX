from pathlib import Path
import json

import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import models, transforms

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

VISION_DIR = (
    BASE_DIR
    / "data"
    / "raw"
    / "vision"
    / "metal_nut"
)

TEST_DIR = (
    VISION_DIR
    / "test"
)

ARTIFACT_DIR = (
    BASE_DIR
    / "ai"
    / "vision"
    / "artifacts"
)

NORMAL_FEATURES_PATH = (
    ARTIFACT_DIR
    / "normal_features.pt"
)

PROTOTYPES_PATH = (
    ARTIFACT_DIR
    / "defect_prototypes.pt"
)

THRESHOLD_PATH = (
    ARTIFACT_DIR
    / "threshold.json"
)


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

print("=" * 60)
print("INDUSTRIAL DEFECT AI - MODEL EVALUATION")
print("=" * 60)

print(
    f"Device: {DEVICE}"
)


# ============================================================
# TRANSFORM
# ============================================================

TRANSFORM = transforms.Compose(
    [
        transforms.Resize(
            (224, 224)
        ),

        transforms.Grayscale(
            num_output_channels=3
        ),

        transforms.ToTensor(),

        transforms.Normalize(
            mean=[
                0.485,
                0.456,
                0.406,
            ],
            std=[
                0.229,
                0.224,
                0.225,
            ],
        ),
    ]
)


# ============================================================
# LOAD RESNET18
# ============================================================

print()
print(
    "[VISION] Loading ResNet18..."
)

weights = (
    models.ResNet18_Weights.DEFAULT
)

MODEL = models.resnet18(
    weights=weights
)

MODEL = MODEL.to(DEVICE)

MODEL.eval()


# ============================================================
# FEATURE EXTRACTOR
# ============================================================

FEATURE_EXTRACTOR = nn.Sequential(
    MODEL.conv1,
    MODEL.bn1,
    MODEL.relu,
    MODEL.maxpool,
    MODEL.layer1,
    MODEL.layer2,
).to(DEVICE)

FEATURE_EXTRACTOR.eval()


# ============================================================
# GLOBAL FEATURE EXTRACTOR
# ============================================================

GLOBAL_EXTRACTOR = nn.Sequential(
    MODEL.conv1,
    MODEL.bn1,
    MODEL.relu,
    MODEL.maxpool,
    MODEL.layer1,
    MODEL.layer2,
    MODEL.layer3,
    MODEL.layer4,
    MODEL.avgpool,
).to(DEVICE)

GLOBAL_EXTRACTOR.eval()


# ============================================================
# CHECK ARTIFACTS
# ============================================================

print()
print(
    "[VISION] Checking saved artifacts..."
)

if not NORMAL_FEATURES_PATH.exists():

    raise FileNotFoundError(
        "Missing normal feature artifact:\n"
        f"{NORMAL_FEATURES_PATH}\n"
        "Run train.py first."
    )


if not PROTOTYPES_PATH.exists():

    raise FileNotFoundError(
        "Missing defect prototype artifact:\n"
        f"{PROTOTYPES_PATH}\n"
        "Run train.py first."
    )


if not THRESHOLD_PATH.exists():

    raise FileNotFoundError(
        "Missing threshold artifact:\n"
        f"{THRESHOLD_PATH}\n"
        "Run train.py first."
    )


# ============================================================
# LOAD SAVED NORMAL FEATURES
# ============================================================

print(
    "[VISION] Loading normal features..."
)

normal_features = torch.load(
    NORMAL_FEATURES_PATH,
    map_location="cpu",
    weights_only=True,
)

print(
    "[VISION] Normal feature shape:",
    tuple(normal_features.shape),
)


# ============================================================
# LOAD DEFECT PROTOTYPES
# ============================================================

print(
    "[VISION] Loading defect prototypes..."
)

defect_prototypes = torch.load(
    PROTOTYPES_PATH,
    map_location="cpu",
    weights_only=True,
)

DEFECT_CLASSES = [
    "bent",
    "color",
    "flip",
    "scratch",
]

print(
    "[VISION] Defect classes:",
    list(defect_prototypes.keys()),
)


# ============================================================
# LOAD THRESHOLD
# ============================================================

with open(
    THRESHOLD_PATH,
    "r",
    encoding="utf-8",
) as file:

    threshold_data = json.load(
        file
    )


threshold = float(
    threshold_data["threshold"]
)

print(
    f"[VISION] Production threshold: "
    f"{threshold:.6f}"
)


# ============================================================
# IMAGE LOADER
# ============================================================

def load_image(
    image_path
):

    image = Image.open(
        image_path
    ).convert("RGB")

    tensor = TRANSFORM(
        image
    ).unsqueeze(0)

    return tensor.to(
        DEVICE
    )


# ============================================================
# FEATURE MAP
# ============================================================

@torch.no_grad()
def extract_feature_map(
    image_path
):

    tensor = load_image(
        image_path
    )

    feature_map = (
        FEATURE_EXTRACTOR(
            tensor
        )
    )

    feature_map = F.normalize(
        feature_map,
        p=2,
        dim=1,
    )

    return feature_map.squeeze(
        0
    ).cpu()


# ============================================================
# GLOBAL FEATURE
# ============================================================

@torch.no_grad()
def extract_global_feature(
    image_path
):

    tensor = load_image(
        image_path
    )

    feature = (
        GLOBAL_EXTRACTOR(
            tensor
        )
    )

    feature = feature.flatten(
        1
    )

    feature = F.normalize(
        feature,
        p=2,
        dim=1,
    )

    return feature.squeeze(
        0
    ).cpu()


# ============================================================
# ANOMALY SCORE
# ============================================================

@torch.no_grad()
def calculate_anomaly_score(
    feature_map,
    reference_features,
):

    query = F.normalize(
        feature_map,
        p=2,
        dim=0,
    )

    normals = F.normalize(
        reference_features,
        p=2,
        dim=1,
    )

    similarity = torch.einsum(
        "chw,nchw->nhw",
        query,
        normals,
    )

    max_similarity = (
        similarity.max(
            dim=0
        ).values
    )

    anomaly_map = (
        1.0
        - max_similarity
    )

    flat = anomaly_map.flatten()

    top_k = max(
        1,
        int(
            flat.numel()
            * 0.02
        ),
    )

    top_values = torch.topk(
        flat,
        k=top_k,
    ).values

    return (
        top_values
        .mean()
        .item()
    )


# ============================================================
# DEFECT TYPE CLASSIFICATION
# ============================================================

@torch.no_grad()
def classify_defect(
    global_feature
):

    query = F.normalize(
        global_feature,
        p=2,
        dim=0,
    )

    similarities = {}

    for defect_type, prototype in (
        defect_prototypes.items()
    ):

        prototype = F.normalize(
            prototype,
            p=2,
            dim=0,
        )

        similarity = torch.dot(
            query,
            prototype,
        ).item()

        similarities[
            defect_type
        ] = similarity

    predicted_class = max(
        similarities,
        key=similarities.get,
    )

    values = torch.tensor(
        list(
            similarities.values()
        ),
        dtype=torch.float32,
    )

    probabilities = torch.softmax(
        values,
        dim=0,
    )

    class_names = list(
        similarities.keys()
    )

    predicted_index = (
        class_names.index(
            predicted_class
        )
    )

    confidence = (
        probabilities[
            predicted_index
        ].item()
    )

    return (
        predicted_class,
        confidence,
        similarities,
    )


# ============================================================
# TEST DATA
# ============================================================

GOOD_DIR = (
    TEST_DIR
    / "good"
)

GOOD_IMAGES = sorted(
    GOOD_DIR.glob(
        "*.png"
    )
)

print()
print(
    "[DATASET] Good test images:",
    len(GOOD_IMAGES)
)

for defect_type in DEFECT_CLASSES:

    defect_dir = (
        TEST_DIR
        / defect_type
    )

    images = sorted(
        defect_dir.glob(
            "*.png"
        )
    )

    print(
        f"[DATASET] "
        f"{defect_type}: "
        f"{len(images)}"
    )


# ============================================================
# DETECTION ARRAYS
# ============================================================

y_true = []

y_pred = []

results = []


# ============================================================
# GOOD IMAGE EVALUATION
# ============================================================

print()
print(
    "=" * 60
)

print(
    "EVALUATING GOOD IMAGES"
)

print(
    "=" * 60
)

for index, image_path in enumerate(
    GOOD_IMAGES,
    start=1,
):

    feature_map = (
        extract_feature_map(
            image_path
        )
    )

    score = (
        calculate_anomaly_score(
            feature_map,
            normal_features,
        )
    )

    predicted_defective = (
        score >= threshold
    )

    y_true.append(0)

    y_pred.append(
        1
        if predicted_defective
        else 0
    )

    results.append(
        {
            "image": image_path.name,
            "actual": "good",
            "score": score,
            "defective": predicted_defective,
        }
    )

    print(
        f"\rGOOD "
        f"{index:02d}/{len(GOOD_IMAGES)} "
        f"{image_path.name} "
        f"score={score:.6f}",
        end="",
    )

print()


# ============================================================
# DEFECT IMAGE EVALUATION
# ============================================================

for defect_type in DEFECT_CLASSES:

    defect_dir = (
        TEST_DIR
        / defect_type
    )

    defect_images = sorted(
        defect_dir.glob(
            "*.png"
        )
    )

    print()
    print(
        f"EVALUATING {defect_type.upper()} "
        f"IMAGES"
    )

    for index, image_path in enumerate(
        defect_images,
        start=1,
    ):

        feature_map = (
            extract_feature_map(
                image_path
            )
        )

        score = (
            calculate_anomaly_score(
                feature_map,
                normal_features,
            )
        )

        predicted_defective = (
            score >= threshold
        )

        y_true.append(1)

        y_pred.append(
            1
            if predicted_defective
            else 0
        )

        results.append(
            {
                "image": image_path.name,
                "actual": defect_type,
                "score": score,
                "defective": predicted_defective,
            }
        )

        print(
            f"\r{defect_type.upper():7s} "
            f"{index:02d}/{len(defect_images)} "
            f"{image_path.name} "
            f"score={score:.6f}",
            end="",
        )

    print()


# ============================================================
# BINARY DETECTION METRICS
# ============================================================

accuracy = accuracy_score(
    y_true,
    y_pred,
)

precision = precision_score(
    y_true,
    y_pred,
    zero_division=0,
)

recall = recall_score(
    y_true,
    y_pred,
    zero_division=0,
)

f1 = f1_score(
    y_true,
    y_pred,
    zero_division=0,
)

confusion = confusion_matrix(
    y_true,
    y_pred,
)

tn, fp, fn, tp = (
    confusion.ravel()
)


# ============================================================
# SCORE DISTRIBUTIONS
# ============================================================

print()
print(
    "=" * 60
)

print(
    "ANOMALY SCORE DISTRIBUTIONS"
)

print(
    "=" * 60
)

score_classes = [
    "good",
    "bent",
    "color",
    "flip",
    "scratch",
]

for class_name in score_classes:

    class_scores = [
        item["score"]
        for item in results
        if item["actual"]
        == class_name
    ]

    if not class_scores:
        continue

    mean_score = (
        sum(class_scores)
        / len(class_scores)
    )

    print(
        f"{class_name.upper():8s} "
        f"count={len(class_scores):2d} "
        f"min={min(class_scores):.4f} "
        f"mean={mean_score:.4f} "
        f"max={max(class_scores):.4f}"
    )


# ============================================================
# DETECTION RESULTS
# ============================================================

print()
print(
    "=" * 60
)

print(
    "DEFECT DETECTION RESULTS"
)

print(
    "=" * 60
)

print(
    f"Threshold : {threshold:.6f}"
)

print(
    f"Accuracy  : {accuracy:.4f}"
)

print(
    f"Precision : {precision:.4f}"
)

print(
    f"Recall    : {recall:.4f}"
)

print(
    f"F1 Score  : {f1:.4f}"
)

print()

print(
    f"TN: {tn}"
)

print(
    f"FP: {fp}"
)

print(
    f"FN: {fn}"
)

print(
    f"TP: {tp}"
)


# ============================================================
# DEFECT TYPE CLASSIFICATION
# ============================================================

classification_true = []

classification_pred = []

classification_confidences = []


print()
print(
    "=" * 60
)

print(
    "DEFECT TYPE CLASSIFICATION"
)

print(
    "=" * 60
)

for defect_type in DEFECT_CLASSES:

    defect_dir = (
        TEST_DIR
        / defect_type
    )

    defect_images = sorted(
        defect_dir.glob(
            "*.png"
        )
    )

    for image_path in defect_images:

        global_feature = (
            extract_global_feature(
                image_path
            )
        )

        (
            predicted_class,
            confidence,
            similarities,
        ) = classify_defect(
            global_feature
        )

        classification_true.append(
            defect_type
        )

        classification_pred.append(
            predicted_class
        )

        classification_confidences.append(
            confidence
        )


classification_accuracy = (
    accuracy_score(
        classification_true,
        classification_pred,
    )
)


print(
    f"Classification accuracy: "
    f"{classification_accuracy:.4f}"
)


# ============================================================
# CLASSIFICATION CONFUSION MATRIX
# ============================================================

classification_matrix = (
    confusion_matrix(
        classification_true,
        classification_pred,
        labels=DEFECT_CLASSES,
    )
)

print()
print(
    "Classification confusion matrix:"
)

print(
    "Rows = actual"
)

print(
    "Columns = predicted"
)

print(
    classification_matrix
)


# ============================================================
# PER-CLASS CLASSIFICATION
# ============================================================

print()
print(
    "Per-class classification:"
)

for index, defect_type in enumerate(
    DEFECT_CLASSES
):

    correct = (
        classification_matrix[
            index,
            index
        ]
    )

    total = (
        classification_matrix[
            index
        ].sum()
    )

    class_accuracy = (
        correct / total
        if total > 0
        else 0
    )

    print(
        f"  {defect_type:8s}: "
        f"{correct}/{total} "
        f"({class_accuracy:.2%})"
    )


# ============================================================
# TOP FALSE NEGATIVES
# ============================================================

false_negatives = [
    item
    for item in results
    if item["actual"] != "good"
    and not item["defective"]
]

false_positives = [
    item
    for item in results
    if item["actual"] == "good"
    and item["defective"]
]


print()
print(
    "=" * 60
)

print(
    "ERROR ANALYSIS"
)

print(
    "=" * 60
)

print(
    f"False positives: "
    f"{len(false_positives)}"
)

print(
    f"False negatives: "
    f"{len(false_negatives)}"
)


if false_negatives:

    print()
    print(
        "Lowest-scoring false negatives:"
    )

    false_negatives = sorted(
        false_negatives,
        key=lambda item: item["score"],
    )

    for item in false_negatives[:10]:

        print(
            f"  {item['actual']:8s} "
            f"{item['image']:12s} "
            f"score={item['score']:.6f}"
        )


if false_positives:

    print()
    print(
        "False-positive good images:"
    )

    false_positives = sorted(
        false_positives,
        key=lambda item: item["score"],
        reverse=True,
    )

    for item in false_positives[:10]:

        print(
            f"  {item['image']:12s} "
            f"score={item['score']:.6f}"
        )


# ============================================================
# COMPLETE
# ============================================================

print()
print(
    "=" * 60
)

print(
    "EVALUATION COMPLETE"
)

print(
    "=" * 60
)

print()
print(
    "The saved artifacts were only READ."
)

print(
    "No training artifacts were modified."
)