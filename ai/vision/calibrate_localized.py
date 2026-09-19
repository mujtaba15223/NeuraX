from pathlib import Path

import torch
import torch.nn.functional as F
from PIL import Image

from ai.vision.localized_detector import (
    MODEL,
    NORMAL_PATCH_DATABASE,
    TRANSFORM,
    DEVICE,
    VISION_DATASET,
)


# ============================================================
# CONFIGURATION
# ============================================================

TEST_PATH = VISION_DATASET / "test"
GROUND_TRUTH_PATH = VISION_DATASET / "ground_truth"

DEFECT_CLASSES = [
    "bent",
    "color",
    "flip",
    "scratch",
]

THRESHOLDS = [
    0.025,
    0.030,
    0.035,
    0.040,
    0.045,
    0.050,
    0.055,
    0.060,
    0.065,
    0.070,
]


# ============================================================
# ANOMALY MAP
# ============================================================

@torch.no_grad()
def get_anomaly_map(image_path):

    image = Image.open(image_path).convert("RGB")

    original_width, original_height = image.size

    tensor = TRANSFORM(image).unsqueeze(0).to(DEVICE)

    feature_map = MODEL(tensor)

    _, channels, height, width = feature_map.shape

    patches = feature_map.squeeze(0).permute(
        1, 2, 0
    ).reshape(-1, channels)

    patches = F.normalize(patches, dim=1)

    database = NORMAL_PATCH_DATABASE.to(DEVICE)

    similarity = torch.mm(
        patches,
        database.T
    )

    max_similarity, _ = similarity.max(dim=1)

    anomaly_scores = 1.0 - max_similarity

    anomaly_map = anomaly_scores.reshape(
        height,
        width
    )

    anomaly_map = anomaly_map.unsqueeze(0).unsqueeze(0)

    anomaly_map = F.interpolate(
        anomaly_map,
        size=(original_height, original_width),
        mode="bilinear",
        align_corners=False,
    )

    return anomaly_map.squeeze()


# ============================================================
# LOAD GROUND-TRUTH MASK
# ============================================================

def load_mask(mask_path):

    mask = Image.open(mask_path).convert("L")

    mask = torch.tensor(
        list(mask.getdata()),
        dtype=torch.float32
    )

    mask = mask.reshape(
        Image.open(mask_path).size[1],
        Image.open(mask_path).size[0]
    )

    return mask > 0


# ============================================================
# BINARY METRICS
# ============================================================

def calculate_metrics(prediction, ground_truth):

    prediction = prediction.bool()
    ground_truth = ground_truth.bool()

    tp = int((prediction & ground_truth).sum())
    tn = int((~prediction & ~ground_truth).sum())
    fp = int((prediction & ~ground_truth).sum())
    fn = int((~prediction & ground_truth).sum())

    precision = (
        tp / (tp + fp)
        if (tp + fp) > 0
        else 0.0
    )

    recall = (
        tp / (tp + fn)
        if (tp + fn) > 0
        else 0.0
    )

    iou = (
        tp / (tp + fp + fn)
        if (tp + fp + fn) > 0
        else 0.0
    )

    return precision, recall, iou


# ============================================================
# EVALUATE ONE THRESHOLD
# ============================================================

def evaluate_threshold(threshold):

    total_precision = 0.0
    total_recall = 0.0
    total_iou = 0.0

    count = 0

    for defect_class in DEFECT_CLASSES:

        image_dir = TEST_PATH / defect_class
        mask_dir = GROUND_TRUTH_PATH / defect_class

        image_paths = sorted(
            image_dir.glob("*.png")
        )

        for image_path in image_paths:

            mask_path = mask_dir / image_path.name

            if not mask_path.exists():
                continue

            anomaly_map = get_anomaly_map(
                image_path
            )

            ground_truth = load_mask(
                mask_path
            )

            prediction = anomaly_map >= threshold

            precision, recall, iou = calculate_metrics(
                prediction,
                ground_truth
            )

            total_precision += precision
            total_recall += recall
            total_iou += iou

            count += 1

    if count == 0:
        return 0.0, 0.0, 0.0

    return (
        total_precision / count,
        total_recall / count,
        total_iou / count,
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("LOCALIZED ANOMALY CALIBRATION")
    print("=" * 60)

    print()
    print("Defect classes:")
    for name in DEFECT_CLASSES:
        print(f"  - {name}")

    print()
    print("Testing thresholds...")

    results = []

    for threshold in THRESHOLDS:

        precision, recall, iou = evaluate_threshold(
            threshold
        )

        results.append(
            (
                threshold,
                precision,
                recall,
                iou,
            )
        )

        print(
            f"Threshold {threshold:.3f} | "
            f"Precision {precision:.4f} | "
            f"Recall {recall:.4f} | "
            f"IoU {iou:.4f}"
        )

    # Select based on IoU.
    best = max(
        results,
        key=lambda x: x[3]
    )

    print()
    print("=" * 60)
    print("BEST LOCALIZATION THRESHOLD")
    print("=" * 60)

    print(
        f"Threshold: {best[0]:.3f}"
    )

    print(
        f"Precision: {best[1]:.4f}"
    )

    print(
        f"Recall: {best[2]:.4f}"
    )

    print(
        f"IoU: {best[3]:.4f}"
    )

    print("=" * 60)