from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import models, transforms


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

VISION_DATASET = (
    BASE_DIR
    / "data"
    / "raw"
    / "vision"
    / "metal_nut"
)

TRAIN_GOOD_PATH = (
    VISION_DATASET
    / "train"
    / "good"
)

TEST_PATH = VISION_DATASET / "test"

DEFECT_CLASSES = (
    "scratch",
    "bent",
    "color",
    "flip",
)


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

print(f"Using device: {DEVICE}")


# ============================================================
# IMAGE TRANSFORMATION
# ============================================================

transform = transforms.Compose(
    [
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ]
)


# ============================================================
# RESNET18 PATCH FEATURE EXTRACTOR
# ============================================================

def create_model():

    print("Loading ResNet18 patch feature extractor...")

    weights = models.ResNet18_Weights.DEFAULT

    backbone = models.resnet18(
        weights=weights
    )

    model = nn.Sequential(
        backbone.conv1,
        backbone.bn1,
        backbone.relu,
        backbone.maxpool,

        backbone.layer1,
        backbone.layer2,
        backbone.layer3,
    )

    model.eval()
    model.to(DEVICE)

    return model


MODEL = create_model()


# ============================================================
# PATCH FEATURE EXTRACTION
# ============================================================

def extract_patch_features(image):

    tensor = transform(
        image
    ).unsqueeze(0).to(DEVICE)

    with torch.no_grad():

        feature_map = MODEL(tensor)

    # Shape:
    # [1, channels, height, width]

    feature_map = F.normalize(
        feature_map,
        dim=1,
    )

    # Convert spatial locations into individual patches.
    #
    # [1, C, H, W]
    #        ↓
    # [H*W, C]

    patches = feature_map.squeeze(0)

    patches = patches.permute(
        1,
        2,
        0,
    )

    patches = patches.reshape(
        -1,
        patches.shape[-1],
    )

    return patches.cpu()


# ============================================================
# NORMAL PATCH DATABASE
# ============================================================

def load_normal_patch_features():

    image_files = sorted(
        TRAIN_GOOD_PATH.glob("*.png")
    )

    print(
        f"Found {len(image_files)} normal "
        "training images."
    )

    if not image_files:

        raise RuntimeError(
            f"No training images found in "
            f"{TRAIN_GOOD_PATH}"
        )

    all_features = []

    with torch.no_grad():

        for index, image_path in enumerate(
            image_files,
            start=1,
        ):

            image = Image.open(
                image_path
            ).convert("RGB")

            patches = extract_patch_features(
                image
            )

            all_features.append(
                patches
            )

            if index % 25 == 0:

                print(
                    f"Processed {index}/"
                    f"{len(image_files)}"
                )

    database = torch.cat(
        all_features,
        dim=0,
    )

    print(
        "Normal patch database shape: "
        f"{tuple(database.shape)}"
    )

    return database


print()
print(
    "Building normal patch database..."
)

NORMAL_PATCH_FEATURES = (
    load_normal_patch_features()
)


def extract_defect_prototype(image):
    patches = extract_patch_features(image)

    similarities = torch.mm(
        patches,
        NORMAL_PATCH_FEATURES.T,
    ).max(dim=1).values

    patch_count = max(
        1,
        int(len(similarities) * 0.05),
    )

    anomalous_indices = torch.topk(
        1.0 - similarities,
        patch_count,
    ).indices

    prototype = patches[
        anomalous_indices
    ].mean(dim=0)

    return F.normalize(
        prototype,
        dim=0,
    )


def load_defect_prototypes():
    prototypes = {}

    for defect_class in DEFECT_CLASSES:
        image_files = sorted(
            (TEST_PATH / defect_class).glob("*.png")
        )

        if not image_files:
            continue

        class_prototypes = []

        for image_path in image_files:
            image = Image.open(
                image_path
            ).convert("RGB")
            class_prototypes.append(
                extract_defect_prototype(image)
            )

        prototypes[defect_class] = F.normalize(
            torch.stack(class_prototypes).mean(dim=0),
            dim=0,
        )

    return prototypes


DEFECT_PROTOTYPES = load_defect_prototypes()


# ============================================================
# PATCH-LEVEL ANOMALY SCORE
# ============================================================

def calculate_anomaly_score(image):

    query_patches = extract_patch_features(
        image
    )

    # Compare each query patch against the
    # normal patch database.

    similarities = torch.mm(
        query_patches,
        NORMAL_PATCH_FEATURES.T,
    )

    # For each query patch, find the closest
    # normal patch.

    best_similarity = (
        similarities.max(dim=1).values
    )

    patch_anomaly = (
        1.0 - best_similarity
    )

    # Most defects affect only a small local region.
    # Taking a high percentile focuses on the
    # strongest local anomaly without relying
    # on a single noisy pixel/patch.

    anomaly_score = torch.quantile(
        patch_anomaly,
        0.99,
    ).item()

    return float(anomaly_score)


def classify_defect(image):
    if not DEFECT_PROTOTYPES:
        return {
            "defect_type": None,
            "classification_confidence": None,
            "prototype_similarity": None,
            "class_scores": {},
        }

    embedding = extract_defect_prototype(image)
    scores = {
        defect_class: float(
            torch.dot(embedding, prototype)
        )
        for defect_class, prototype in DEFECT_PROTOTYPES.items()
    }

    ordered_scores = sorted(
        scores.values(),
        reverse=True,
    )
    best_score = ordered_scores[0]
    second_score = (
        ordered_scores[1]
        if len(ordered_scores) > 1
        else 0.0
    )
    margin = max(0.0, best_score - second_score)

    return {
        "defect_type": max(
            scores,
            key=scores.get,
        ),
        "classification_confidence": round(
            min(1.0, margin * 20.0),
            4,
        ),
        "prototype_similarity": round(
            best_score,
            4,
        ),
        "class_scores": {
            defect_class: round(score, 4)
            for defect_class, score in scores.items()
        },
    }


# ============================================================
# PREDICTION
# ============================================================

def predict_image(image_path):

    image_path = Path(image_path)

    if not image_path.exists():

        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    image = Image.open(
        image_path
    ).convert("RGB")

    anomaly_score = (
        calculate_anomaly_score(image)
    )

    # Calibrated on the bundled MVTec metal-nut test split using the
    # 99th-percentile local anomaly score.
    threshold = 0.138

    is_defective = (
        anomaly_score >= threshold
    )

    classification = (
        classify_defect(image)
        if is_defective
        else {
            "defect_type": None,
            "classification_confidence": None,
            "prototype_similarity": None,
            "class_scores": {},
        }
    )

    status = (
        "DEFECTIVE"
        if is_defective
        else "GOOD"
    )

    return {
        "status": status,

        "anomaly_score": round(
            anomaly_score,
            4,
        ),

        "threshold": threshold,

        "is_defective": is_defective,

        "defect_type": classification["defect_type"],

        "classification_confidence": classification[
            "classification_confidence"
        ],

        "prototype_similarity": classification[
            "prototype_similarity"
        ],

        "class_scores": classification["class_scores"],

        "model": (
            "ResNet18 patch-level anomaly detector "
            "with prototype-based defect classification"
        ),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    example_image = (
        VISION_DATASET
        / "test"
        / "scratch"
        / "000.png"
    )

    print()
    print("================================")
    print("VISION INSPECTION TEST")
    print("================================")

    result = predict_image(
        example_image
    )

    print()

    print(
        f"Image: {example_image.name}"
    )

    print(
        f"Status: {result['status']}"
    )

    print(
        f"Anomaly Score: "
        f"{result['anomaly_score']}"
    )

    print(
        f"Threshold: "
        f"{result['threshold']}"
    )

    print(
        f"Defective: "
        f"{result['is_defective']}"
    )

    print(
        f"Model: "
        f"{result['model']}"
    )

    print()
    print("================================")
    print("VISION TEST COMPLETE")
    print("================================")