from pathlib import Path
from PIL import Image


# ============================================================
# MVTec AD — METAL NUT DATASET EXPLORATION
# ============================================================

DATASET_PATH = Path("data/raw/vision/metal_nut")

TRAIN_PATH = DATASET_PATH / "train"
TEST_PATH = DATASET_PATH / "test"
GROUND_TRUTH_PATH = DATASET_PATH / "ground_truth"


print("=" * 70)
print("MVTec AD — METAL NUT DATASET EXPLORATION")
print("=" * 70)


# ============================================================
# 1. DATASET STRUCTURE
# ============================================================

print("\nDataset Path:")
print(DATASET_PATH)


# ============================================================
# 2. TRAINING DATA
# ============================================================

print("\n" + "=" * 70)
print("TRAINING DATA")
print("=" * 70)

train_classes = [
    folder for folder in TRAIN_PATH.iterdir()
    if folder.is_dir()
]

total_train_images = 0

for folder in sorted(train_classes):

    images = [
        file for file in folder.iterdir()
        if file.is_file()
    ]

    count = len(images)
    total_train_images += count

    print(f"{folder.name}: {count} images")

print("\nTotal training images:", total_train_images)


# ============================================================
# 3. TEST DATA
# ============================================================

print("\n" + "=" * 70)
print("TEST DATA")
print("=" * 70)

test_classes = [
    folder for folder in TEST_PATH.iterdir()
    if folder.is_dir()
]

total_test_images = 0

for folder in sorted(test_classes):

    images = [
        file for file in folder.iterdir()
        if file.is_file()
    ]

    count = len(images)
    total_test_images += count

    print(f"{folder.name}: {count} images")

print("\nTotal test images:", total_test_images)


# ============================================================
# 4. DEFECT CLASSES
# ============================================================

print("\n" + "=" * 70)
print("DEFECT CLASSES")
print("=" * 70)

defect_classes = [
    folder.name
    for folder in sorted(test_classes)
    if folder.name != "good"
]

print("Defect classes:")

for defect in defect_classes:
    print("-", defect)

print("\nNumber of defect classes:", len(defect_classes))


# ============================================================
# 5. GOOD VS DEFECTIVE TEST IMAGES
# ============================================================

good_test_path = TEST_PATH / "good"

good_count = len([
    file for file in good_test_path.iterdir()
    if file.is_file()
])

defect_count = total_test_images - good_count

print("\n" + "=" * 70)
print("GOOD VS DEFECTIVE")
print("=" * 70)

print("Good test images:", good_count)
print("Defective test images:", defect_count)
print("Total test images:", total_test_images)


# ============================================================
# 6. IMAGE DIMENSIONS
# ============================================================

print("\n" + "=" * 70)
print("IMAGE INFORMATION")
print("=" * 70)

example_image = next(
    file
    for folder in test_classes
    for file in folder.iterdir()
    if file.is_file()
)

with Image.open(example_image) as image:

    print("Example image:", example_image)
    print("Image size:", image.size)
    print("Image mode:", image.mode)
    print("Image format:", image.format)


# ============================================================
# 7. GROUND TRUTH MASKS
# ============================================================

print("\n" + "=" * 70)
print("GROUND TRUTH MASKS")
print("=" * 70)

ground_truth_classes = [
    folder
    for folder in GROUND_TRUTH_PATH.iterdir()
    if folder.is_dir()
]

for folder in sorted(ground_truth_classes):

    masks = [
        file
        for file in folder.iterdir()
        if file.is_file()
    ]

    print(f"{folder.name}: {len(masks)} masks")


# ============================================================
# 8. SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("DATASET SUMMARY")
print("=" * 70)

print("Dataset: MVTec AD - metal_nut")
print("Training images:", total_train_images)
print("Test images:", total_test_images)
print("Good test images:", good_count)
print("Defective test images:", defect_count)
print("Defect classes:", len(defect_classes))
print("Image size:", "700 x 700")
print("Image mode:", "RGB")


# ============================================================
# END
# ============================================================

print("\n" + "=" * 70)
print("VISION DATASET EXPLORATION COMPLETE")
print("=" * 70)