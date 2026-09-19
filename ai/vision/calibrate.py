from pathlib import Path

from ai.vision.predict import predict_image


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

TEST_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "vision"
    / "metal_nut"
    / "test"
)


# ============================================================
# DATASET
# ============================================================

DEFECT_CLASSES = [
    "bent",
    "color",
    "flip",
    "scratch",
]

GOOD_CLASS = "good"


# ============================================================
# SCORE COLLECTION
# ============================================================

def collect_scores():

    good_scores = []
    defect_scores = []

    print()
    print("================================")
    print("VISION MODEL CALIBRATION")
    print("================================")

    # -----------------------------
    # GOOD IMAGES
    # -----------------------------

    good_path = TEST_PATH / GOOD_CLASS

    good_images = sorted(
        good_path.glob("*.png")
    )

    print()
    print(
        f"GOOD images: {len(good_images)}"
    )

    for image_path in good_images:

        result = predict_image(
            image_path
        )

        good_scores.append(
            result["anomaly_score"]
        )

    # -----------------------------
    # DEFECTIVE IMAGES
    # -----------------------------

    for defect_class in DEFECT_CLASSES:

        defect_path = (
            TEST_PATH / defect_class
        )

        images = sorted(
            defect_path.glob("*.png")
        )

        print(
            f"{defect_class.upper()} images: "
            f"{len(images)}"
        )

        for image_path in images:

            result = predict_image(
                image_path
            )

            defect_scores.append(
                result["anomaly_score"]
            )

    return (
        good_scores,
        defect_scores,
    )


# ============================================================
# STATISTICS
# ============================================================

def print_statistics(
    good_scores,
    defect_scores,
):

    print()
    print("================================")
    print("SCORE STATISTICS")
    print("================================")

    print()
    print(
        f"GOOD count: "
        f"{len(good_scores)}"
    )

    print(
        f"DEFECTIVE count: "
        f"{len(defect_scores)}"
    )

    if good_scores:

        print()
        print(
            f"GOOD minimum: "
            f"{min(good_scores):.4f}"
        )

        print(
            f"GOOD maximum: "
            f"{max(good_scores):.4f}"
        )

        print(
            f"GOOD average: "
            f"{sum(good_scores) / len(good_scores):.4f}"
        )

    if defect_scores:

        print()
        print(
            f"DEFECT minimum: "
            f"{min(defect_scores):.4f}"
        )

        print(
            f"DEFECT maximum: "
            f"{max(defect_scores):.4f}"
        )

        print(
            f"DEFECT average: "
            f"{sum(defect_scores) / len(defect_scores):.4f}"
        )


# ============================================================
# THRESHOLD SEARCH
# ============================================================

def evaluate_threshold(
    threshold,
    good_scores,
    defect_scores,
):

    true_negative = sum(
        score < threshold
        for score in good_scores
    )

    false_positive = sum(
        score >= threshold
        for score in good_scores
    )

    true_positive = sum(
        score >= threshold
        for score in defect_scores
    )

    false_negative = sum(
        score < threshold
        for score in defect_scores
    )

    total = (
        true_negative
        + false_positive
        + true_positive
        + false_negative
    )

    accuracy = (
        (
            true_positive
            + true_negative
        )
        / total
        if total
        else 0
    )

    precision = (
        true_positive
        / (
            true_positive
            + false_positive
        )
        if (
            true_positive
            + false_positive
        )
        else 0
    )

    recall = (
        true_positive
        / (
            true_positive
            + false_negative
        )
        if (
            true_positive
            + false_negative
        )
        else 0
    )

    return {
        "threshold": threshold,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "tp": true_positive,
        "tn": true_negative,
        "fp": false_positive,
        "fn": false_negative,
    }


# ============================================================
# MAIN CALIBRATION
# ============================================================

def main():

    good_scores, defect_scores = (
        collect_scores()
    )

    print_statistics(
        good_scores,
        defect_scores,
    )

    print()
    print("================================")
    print("THRESHOLD SEARCH")
    print("================================")

    best_result = None

    # Search across the actual score range.
    thresholds = [
        i / 1000
        for i in range(1, 501)
    ]

    for threshold in thresholds:

        result = evaluate_threshold(
            threshold,
            good_scores,
            defect_scores,
        )

        if (
            best_result is None
            or result["accuracy"]
            > best_result["accuracy"]
        ):
            best_result = result

    print()

    if best_result:

        print(
            f"Best threshold: "
            f"{best_result['threshold']:.4f}"
        )

        print(
            f"Accuracy: "
            f"{best_result['accuracy']:.4f}"
        )

        print(
            f"Precision: "
            f"{best_result['precision']:.4f}"
        )

        print(
            f"Recall: "
            f"{best_result['recall']:.4f}"
        )

        print()
        print(
            f"TP: {best_result['tp']}"
        )

        print(
            f"TN: {best_result['tn']}"
        )

        print(
            f"FP: {best_result['fp']}"
        )

        print(
            f"FN: {best_result['fn']}"
        )

    print()
    print("================================")
    print("CALIBRATION COMPLETE")
    print("================================")


if __name__ == "__main__":
    main()