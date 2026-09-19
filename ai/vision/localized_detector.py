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

VISION_DATASET = BASE_DIR / "data" / "raw" / "vision" / "metal_nut"
TRAIN_GOOD_PATH = VISION_DATASET / "train" / "good"


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ============================================================
# IMAGE TRANSFORM
# ============================================================

TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


# ============================================================
# RESNET18 INTERMEDIATE FEATURE EXTRACTOR
# ============================================================

class ResNetFeatureExtractor(nn.Module):
    def __init__(self):
        super().__init__()

        weights = models.ResNet18_Weights.DEFAULT
        backbone = models.resnet18(weights=weights)

        # Keep layers up to layer3.
        # Output shape for 224x224 input:
        # [batch, 256, 14, 14]
        self.features = nn.Sequential(
            backbone.conv1,
            backbone.bn1,
            backbone.relu,
            backbone.maxpool,
            backbone.layer1,
            backbone.layer2,
            backbone.layer3,
        )

    def forward(self, x):
        return self.features(x)


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading localized ResNet18 detector...")

MODEL = ResNetFeatureExtractor().to(DEVICE)
MODEL.eval()

print(f"Device: {DEVICE}")


# ============================================================
# BUILD NORMAL PATCH FEATURE DATABASE
# ============================================================

@torch.no_grad()
def build_normal_database():
    features = []

    image_paths = sorted(TRAIN_GOOD_PATH.glob("*.png"))

    print(f"Normal training images found: {len(image_paths)}")

    for index, image_path in enumerate(image_paths, start=1):

        image = Image.open(image_path).convert("RGB")
        tensor = TRANSFORM(image).unsqueeze(0).to(DEVICE)

        feature_map = MODEL(tensor)

        # [1, 256, 14, 14]
        feature_map = feature_map.squeeze(0)

        # Convert:
        # [256, 14, 14]
        # ->
        # [196, 256]
        patches = feature_map.permute(1, 2, 0).reshape(-1, feature_map.shape[0])

        patches = F.normalize(patches, dim=1)

        features.append(patches.cpu())

        if index % 50 == 0:
            print(f"Processed normal images: {index}/{len(image_paths)}")

    database = torch.cat(features, dim=0)

    print(f"Normal patch database shape: {tuple(database.shape)}")

    return database


NORMAL_PATCH_DATABASE = build_normal_database()


# ============================================================
# LOCALIZED ANOMALY MAP
# ============================================================

@torch.no_grad()
def calculate_anomaly_map(image_path):
    image = Image.open(image_path).convert("RGB")
    original_size = image.size

    tensor = TRANSFORM(image).unsqueeze(0).to(DEVICE)

    feature_map = MODEL(tensor)

    # [1, 256, 14, 14]
    _, channels, height, width = feature_map.shape

    # [196, 256]
    patches = feature_map.squeeze(0).permute(1, 2, 0).reshape(
        -1, channels
    )

    patches = F.normalize(patches, dim=1)

    # Compare every image patch against all normal patches.
    #
    # Similarity:
    # [196, normal_patches]
    similarity = torch.mm(
        patches,
        NORMAL_PATCH_DATABASE.to(DEVICE).T
    )

    # For each patch, find the most similar normal patch.
    max_similarity, _ = similarity.max(dim=1)

    # Higher value = more anomalous.
    anomaly_scores = 1.0 - max_similarity

    # Restore spatial layout.
    anomaly_map = anomaly_scores.reshape(height, width)

    # Upscale anomaly map to original image resolution.
    anomaly_map = anomaly_map.unsqueeze(0).unsqueeze(0)

    anomaly_map = F.interpolate(
        anomaly_map,
        size=(original_size[1], original_size[0]),
        mode="bilinear",
        align_corners=False,
    )

    anomaly_map = anomaly_map.squeeze().cpu()

    return anomaly_map


# ============================================================
# LOCALIZED PREDICTION
# ============================================================

def predict_localized(image_path, threshold=0.035):
    image_path = Path(image_path)

    anomaly_map = calculate_anomaly_map(image_path)

    max_score = float(anomaly_map.max())
    mean_score = float(anomaly_map.mean())

    # Pixels above threshold are considered anomalous.
    defect_mask = anomaly_map >= threshold

    defect_pixels = int(defect_mask.sum())

    total_pixels = defect_mask.numel()

    defect_percentage = (
        defect_pixels / total_pixels
    ) * 100

    is_defective = defect_pixels > 0

    if is_defective:
        ys, xs = torch.where(defect_mask)

        x_min = int(xs.min())
        x_max = int(xs.max())
        y_min = int(ys.min())
        y_max = int(ys.max())

        bounding_box = {
            "x_min": x_min,
            "y_min": y_min,
            "x_max": x_max,
            "y_max": y_max,
        }
    else:
        bounding_box = None

    return {
        "status": "DEFECTIVE" if is_defective else "GOOD",
        "is_defective": is_defective,
        "max_anomaly_score": round(max_score, 6),
        "mean_anomaly_score": round(mean_score, 6),
        "threshold": threshold,
        "defect_pixels": defect_pixels,
        "defect_percentage": round(defect_percentage, 4),
        "bounding_box": bounding_box,
        "anomaly_map": anomaly_map,
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_image = (
        VISION_DATASET
        / "test"
        / "scratch"
        / "000.png"
    )

    print()
    print("=" * 50)
    print("LOCALIZED DEFECT TEST")
    print("=" * 50)

    result = predict_localized(test_image)

    print(f"Image: {test_image.name}")
    print(f"Status: {result['status']}")
    print(f"Max anomaly score: {result['max_anomaly_score']}")
    print(f"Mean anomaly score: {result['mean_anomaly_score']}")
    print(f"Threshold: {result['threshold']}")
    print(f"Defect pixels: {result['defect_pixels']}")
    print(f"Defect percentage: {result['defect_percentage']}%")
    print(f"Bounding box: {result['bounding_box']}")

    print("=" * 50)