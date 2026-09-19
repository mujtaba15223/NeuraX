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
        transforms.Grayscale(
            num_output_channels=3
        ),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ]
)


# ============================================================
# RESNET18 FEATURE EXTRACTOR
# ============================================================

def create_model():

    print("Loading ResNet18...")

    weights = models.ResNet18_Weights.DEFAULT

    backbone = models.resnet18(
        weights=weights
    )

    backbone.eval()
    backbone.to(DEVICE)

    return backbone


MODEL = create_model()


# ============================================================
# INTERMEDIATE FEATURE EXTRACTION
# ============================================================

def extract_feature_map(image):

    tensor = transform(
        image
    ).unsqueeze(0)

    tensor = tensor.to(DEVICE)

    with torch.no_grad():

        x = MODEL.conv1(tensor)
        x = MODEL.bn1(x)
        x = MODEL.relu(x)
        x = MODEL.maxpool(x)

        x = MODEL.layer1(x)

        # Layer 2 keeps spatial information.
        # This is important for localized defects.
        x = MODEL.layer2(x)

    return x


# ============================================================
# FEATURE NORMALIZATION
# ============================================================

def normalize_feature_map(feature_map):

    return F.normalize(
        feature_map,
        dim=1,
    )


# ============================================================
# LOAD NORMAL FEATURE DATABASE
# ============================================================

def load_normal_features():

    image_files = sorted(
        TRAIN_GOOD_PATH.glob("*.png")
    )

    print(
        f"Found {len(image_files)} normal "
        "training images."
    )

    if not image_files:
        raise RuntimeError(
            f"No training images found in: "
            f"{TRAIN_GOOD_PATH}"
        )

    features = []

    with torch.no_grad():

        for index, image_path in enumerate(
            image_files,
            start=1,
        ):

            image = Image.open(
                image_path
            ).convert("RGB")

            feature_map = extract_feature_map(
                image
            )

            feature_map = normalize_feature_map(
                feature_map
            )

            features.append(
                feature_map.cpu()
            )

            if index % 50 == 0:

                print(
                    f"Processed {index}/"
                    f"{len(image_files)}"
                )

    return torch.cat(
        features,
        dim=0,
    )


print(
    "Building localized normal "
    "feature database..."
)

NORMAL_FEATURES = load_normal_features()

print(
    "Normal feature database shape: "
    f"{tuple(NORMAL_FEATURES.shape)}"
)


# ============================================================
# NORMAL BASELINE
# ============================================================

def calculate_normal_baseline():

    normal_scores = []

    number_of_samples = (
        NORMAL_FEATURES.shape[0]
    )

    for index in range(
        number_of_samples
    ):

        current = NORMAL_FEATURES[
            index:index + 1
        ]

        others = torch.cat(
            [
                NORMAL_FEATURES[:index],
                NORMAL_FEATURES[index + 1:],
            ],
            dim=0,
        )

        if len(others) == 0:
            continue

        similarity = torch.einsum(
            "nchw,mchw->nmhw",
            current,
            others,
        )

        best_similarity = similarity.max(
            dim=1
        ).values

        distance = (
            1.0 - best_similarity
        )

        score = torch.quantile(
            distance.flatten(),
            0.99,
        ).item()

        normal_scores.append(score)

    if not normal_scores:
        return 0.1

    baseline = torch.tensor(
        normal_scores
    )

    threshold = torch.quantile(
        baseline,
        0.995,
    ).item()

    return float(threshold)


print(
    "Calibrating anomaly threshold..."
)

CALIBRATED_THRESHOLD = (
    calculate_normal_baseline()
)

print(
    "Calibrated threshold: "
    f"{CALIBRATED_THRESHOLD:.4f}"
)


# ============================================================
# LOCALIZED ANOMALY SCORE
# ============================================================

def calculate_anomaly_score(image):

    feature_map = extract_feature_map(
        image
    )

    feature_map = normalize_feature_map(
        feature_map
    )

    normal_features = (
        NORMAL_FEATURES.to(DEVICE)
    )

    # Compare every spatial location of the
    # inspected image against normal references.
    similarities = torch.einsum(
        "nchw,mchw->nmhw",
        feature_map,
        normal_features,
    )

    best_similarity = similarities.max(
        dim=1
    ).values

    anomaly_map = (
        1.0 - best_similarity
    )

    # Ignore the extreme single-pixel response
    # and focus on the strongest localized regions.
    flattened = anomaly_map.flatten()

    top_k = max(
        1,
        int(flattened.numel() * 0.02),
    )

    top_values = torch.topk(
        flattened,
        top_k,
    ).values

    anomaly_score = (
        top_values.mean().item()
    )

    return float(anomaly_score)


# ============================================================
# IMAGE PREDICTION
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

    threshold = (
        CALIBRATED_THRESHOLD
    )

    is_defective = (
        anomaly_score >= threshold
    )

    if is_defective:
        status = "DEFECTIVE"
    else:
        status = "GOOD"

    return {
        "status": status,

        "anomaly_score": round(
            anomaly_score,
            4,
        ),

        "threshold": round(
            threshold,
            4,
        ),

        "is_defective": (
            is_defective
        ),

        "model": (
            "ResNet18 localized "
            "feature anomaly detector"
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
    print(
        "================================"
    )
    print(
        "VISION INSPECTION TEST"
    )
    print(
        "================================"
    )

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
    print(
        "================================"
    )

    print(
        "VISION TEST COMPLETE"
    )

    print(
        "================================"
    )