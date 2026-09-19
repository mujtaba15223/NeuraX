from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torchvision import models, transforms


# ============================================================
# MVTec AD - Metal Nut
# Per-Defect Anomaly Score Analysis
# ============================================================

DATASET_PATH = Path("data/raw/vision/metal_nut")

TRAIN_GOOD_PATH = DATASET_PATH / "train" / "good"
TEST_PATH = DATASET_PATH / "test"

DEFECT_CLASSES = [
    "bent",
    "color",
    "flip",
    "scratch",
]

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.Grayscale(num_output_channels=3),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


def build_feature_extractor():

    print("\nLoading pretrained ResNet18...")

    weights = models.ResNet18_Weights.DEFAULT

    model = models.resnet18(
        weights=weights
    )

    model.fc = torch.nn.Identity()

    model = model.to(DEVICE)
    model.eval()

    print(
        f"Feature extractor device: {DEVICE}"
    )

    return model


def extract_feature(model, image_path):

    image = Image.open(
        image_path
    ).convert("RGB")

    tensor = transform(image)
    tensor = tensor.unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        feature = model(tensor)

    feature = feature.squeeze(0)
    feature = feature.cpu().numpy()

    norm = np.linalg.norm(feature)

    if norm > 0:
        feature = feature / norm

    return feature


def build_normal_database(model):

    image_paths = sorted(
        TRAIN_GOOD_PATH.glob("*.png")
    )

    print(
        f"\nNormal training images: "
        f"{len(image_paths)}"
    )

    features = []

    for image_path in image_paths:

        feature = extract_feature(
            model,
            image_path
        )

        features.append(feature)

    return np.stack(features)


def calculate_anomaly_score(
    feature,
    normal_features
):

    similarities = np.dot(
        normal_features,
        feature
    )

    best_similarity = np.max(
        similarities
    )

    return float(
        1.0 - best_similarity
    )


def collect_scores(
    model,
    normal_features
):

    results = []

    for defect_class in DEFECT_CLASSES:

        class_path = (
            TEST_PATH / defect_class
        )

        if not class_path.exists():
            continue

        for image_path in sorted(
            class_path.glob("*.png")
        ):

            feature = extract_feature(
                model,
                image_path
            )

            score = calculate_anomaly_score(
                feature,
                normal_features
            )

            results.append(
                {
                    "image": image_path,
                    "defect": defect_class,
                    "score": score,
                }
            )

    return results


def print_class_statistics(
    defect_class,
    scores
):

    print("\n" + "-" * 70)
    print(
        f"{defect_class.upper()} ANOMALY SCORES"
    )
    print("-" * 70)

    print(
        f"Count: {len(scores)}"
    )

    print(
        f"Minimum: "
        f"{np.min(scores):.6f}"
    )

    print(
        f"Maximum: "
        f"{np.max(scores):.6f}"
    )

    print(
        f"Mean: "
        f"{np.mean(scores):.6f}"
    )

    print(
        f"Median: "
        f"{np.median(scores):.6f}"
    )

    print(
        f"25th percentile: "
        f"{np.percentile(scores, 25):.6f}"
    )

    print(
        f"75th percentile: "
        f"{np.percentile(scores, 75):.6f}"
    )

    print(
        f"90th percentile: "
        f"{np.percentile(scores, 90):.6f}"
    )

    print(
        f"95th percentile: "
        f"{np.percentile(scores, 95):.6f}"
    )


def main():

    print("\n" + "=" * 70)
    print(
        "MVTec AD - PER-DEFECT ANOMALY ANALYSIS"
    )
    print("=" * 70)

    model = build_feature_extractor()

    print(
        "\nBuilding normal feature database..."
    )

    normal_features = (
        build_normal_database(model)
    )

    print(
        "\nAnalyzing defect classes..."
    )

    results = collect_scores(
        model,
        normal_features
    )

    for defect_class in DEFECT_CLASSES:

        scores = np.array([
            result["score"]
            for result in results
            if result["defect"] == defect_class
        ])

        if len(scores) > 0:

            print_class_statistics(
                defect_class,
                scores
            )

    print("\n" + "=" * 70)
    print(
        "PER-DEFECT ANALYSIS COMPLETE"
    )
    print("=" * 70)


if __name__ == "__main__":
    main()