from pathlib import Path

import numpy as np
from PIL import Image


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

TEST_PATH = VISION_DATASET / "test"

GROUND_TRUTH_PATH = (
    VISION_DATASET / "ground_truth"
)


# ============================================================
# IMAGE / MASK HELPERS
# ============================================================

def load_image(path):
    return Image.open(path).convert("RGB")


def load_mask(path):
    mask = Image.open(path).convert("L")
    return np.array(mask) > 0


# ============================================================
# LOCALIZATION METRICS
# ============================================================

def calculate_metrics(
    predicted_mask,
    ground_truth_mask,
):

    predicted_mask = predicted_mask.astype(bool)
    ground_truth_mask = ground_truth_mask.astype(bool)

    intersection = np.logical_and(
        predicted_mask,
        ground_truth_mask,
    ).sum()

    union = np.logical_or(
        predicted_mask,
        ground_truth_mask,
    ).sum()

    predicted_area = predicted_mask.sum()
    ground_truth_area = ground_truth_mask.sum()

    iou = (
        intersection / union
        if union > 0
        else 0.0
    )

    precision = (
        intersection / predicted_area
        if predicted_area > 0
        else 0.0
    )

    recall = (
        intersection / ground_truth_area
        if ground_truth_area > 0
        else 0.0
    )

    return {
        "iou": iou,
        "precision": precision,
        "recall": recall,
        "ground_truth_area": int(
            ground_truth_area
        ),
        "predicted_area": int(
            predicted_area
        ),
    }


# ============================================================
# SCRATCH DATASET CHECK
# ============================================================

def inspect_scratch_samples():

    image_dir = (
        TEST_PATH / "scratch"
    )

    mask_dir = (
        GROUND_TRUTH_PATH / "scratch"
    )

    images = sorted(
        image_dir.glob("*.png")
    )

    masks = sorted(
        mask_dir.glob("*_mask.png")
    )

    print()
    print("================================")
    print("SCRATCH LOCALIZATION DATA")
    print("================================")

    print(
        f"Scratch images: {len(images)}"
    )

    print(
        f"Scratch masks:  {len(masks)}"
    )

    if not images:
        raise RuntimeError(
            "No scratch test images found."
        )

    if not masks:
        raise RuntimeError(
            "No scratch ground-truth masks found."
        )

    image_path = images[0]

    mask_path = (
        mask_dir
        / f"{image_path.stem}_mask.png"
    )

    if not mask_path.exists():
        raise RuntimeError(
            f"Mask not found for "
            f"{image_path.name}"
        )

    image = load_image(
        image_path
    )

    mask = load_mask(
        mask_path
    )

    print()
    print(
        f"Example image: "
        f"{image_path.name}"
    )

    print(
        f"Image size: "
        f"{image.size}"
    )

    print(
        f"Mask size: "
        f"{mask.shape[1]}x{mask.shape[0]}"
    )

    print(
        f"Defect pixels: "
        f"{int(mask.sum())}"
    )

    defect_percentage = (
        mask.sum()
        / mask.size
        * 100
    )

    print(
        f"Defect coverage: "
        f"{defect_percentage:.2f}%"
    )

    print()
    print("Ground-truth mask successfully loaded.")


# ============================================================
# MAIN
# ============================================================

def main():

    inspect_scratch_samples()

    print()
    print("================================")
    print("LOCALIZATION CHECK COMPLETE")
    print("================================")


if __name__ == "__main__":
    main()