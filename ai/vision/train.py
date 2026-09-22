from pathlib import Path
import json

import torch
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

TEST_PATH = (
    VISION_DATASET
    / "test"
)

ARTIFACT_DIR = (
    BASE_DIR
    / "ai"
    / "vision"
    / "artifacts"
)

ARTIFACT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

print(
    f"Using device: {DEVICE}"
)


# ============================================================
# TRANSFORM
# ============================================================

transform = transforms.Compose(
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

print(
    "Loading pretrained ResNet18..."
)

weights = (
    models.ResNet18_Weights.DEFAULT
)

model = models.resnet18(
    weights=weights
)

model.eval()
model.to(DEVICE)


# ============================================================
# FEATURE MAP
# ============================================================

def extract_feature_map(
    image
):

    tensor = transform(
        image
    ).unsqueeze(0)

    tensor = tensor.to(
        DEVICE
    )

    with torch.no_grad():

        x = model.conv1(
            tensor
        )

        x = model.bn1(
            x
        )

        x = model.relu(
            x
        )

        x = model.maxpool(
            x
        )

        x = model.layer1(
            x
        )

        x = model.layer2(
            x
        )

    x = F.normalize(
        x,
        dim=1,
    )

    return x.squeeze(0).cpu()


# ============================================================
# GLOBAL FEATURE
# ============================================================

def extract_global_feature(
    image
):

    tensor = transform(
        image
    ).unsqueeze(0)

    tensor = tensor.to(
        DEVICE
    )

    with torch.no_grad():

        x = model.conv1(
            tensor
        )

        x = model.bn1(
            x
        )

        x = model.relu(
            x
        )

        x = model.maxpool(
            x
        )

        x = model.layer1(
            x
        )

        x = model.layer2(
            x
        )

        x = model.layer3(
            x
        )

        x = model.layer4(
            x
        )

        x = model.avgpool(
            x
        )

        x = torch.flatten(
            x,
            1,
        )

        x = F.normalize(
            x,
            dim=1,
        )

    return x.squeeze(0).cpu()


# ============================================================
# LOAD NORMAL FEATURES
# ============================================================

def build_normal_features():

    image_files = sorted(
        TRAIN_GOOD_PATH.glob(
            "*.png"
        )
    )

    if not image_files:

        raise RuntimeError(
            "No normal images found in: "
            f"{TRAIN_GOOD_PATH}"
        )

    print()
    print(
        "Building normal feature database..."
    )

    features = []

    for index, image_path in enumerate(
        image_files,
        start=1,
    ):

        image = Image.open(
            image_path
        ).convert("RGB")

        feature = (
            extract_feature_map(
                image
            )
        )

        features.append(
            feature
        )

        print(
            f"\rNormal images: "
            f"{index}/{len(image_files)}",
            end="",
        )

    print()

    features = torch.stack(
        features
    )

    output_path = (
        ARTIFACT_DIR
        / "normal_features.pt"
    )

    torch.save(
        features,
        output_path,
    )

    print(
        "Saved:",
        output_path
    )

    return features


# ============================================================
# BUILD DEFECT PROTOTYPES
# ============================================================

DEFECT_CLASSES = [
    "bent",
    "color",
    "flip",
    "scratch",
]


def build_defect_prototypes():

    print()
    print(
        "Building defect prototypes..."
    )

    prototypes = {}

    counts = {}

    for defect_class in DEFECT_CLASSES:

        class_path = (
            TEST_PATH
            / defect_class
        )

        image_files = sorted(
            class_path.glob(
                "*.png"
            )
        )

        if not image_files:

            print(
                f"WARNING: "
                f"No images for "
                f"{defect_class}"
            )

            continue

        features = []

        for index, image_path in enumerate(
            image_files,
            start=1,
        ):

            image = Image.open(
                image_path
            ).convert("RGB")

            feature = (
                extract_global_feature(
                    image
                )
            )

            features.append(
                feature
            )

            print(
                f"\r{defect_class}: "
                f"{index}/{len(image_files)}",
                end="",
            )

        print()

        feature_matrix = torch.stack(
            features
        )

        prototype = (
            feature_matrix.mean(
                dim=0
            )
        )

        prototype = F.normalize(
            prototype.unsqueeze(0),
            dim=1,
        ).squeeze(0)

        prototypes[
            defect_class
        ] = prototype

        counts[
            defect_class
        ] = len(
            image_files
        )

    if not prototypes:

        raise RuntimeError(
            "No defect prototypes "
            "could be created."
        )

    output_path = (
        ARTIFACT_DIR
        / "defect_prototypes.pt"
    )

    torch.save(
        prototypes,
        output_path,
    )

    print(
        "Saved:",
        output_path
    )

    return prototypes, counts


# ============================================================
# CALCULATE NORMAL THRESHOLD
# ============================================================

def calculate_threshold(
    normal_features
):

    print()
    print(
        "Calculating anomaly threshold..."
    )

    normal_scores = []

    normal_score_records = []

    number_of_samples = (
        normal_features.shape[0]
    )

    for index in range(
        number_of_samples
    ):

        current = (
            normal_features[
                index:index + 1
            ]
        )

        others = torch.cat(
            [
                normal_features[
                    :index
                ],

                normal_features[
                    index + 1:
                ],
            ],
            dim=0,
        )

        if others.shape[0] == 0:

            continue

        similarity = torch.einsum(
            "nchw,mchw->nmhw",
            current,
            others,
        )

        best_similarity = (
            similarity.max(
                dim=1
            ).values
        )

        distance = (
            1.0
            - best_similarity
        )

        score = torch.quantile(
            distance.flatten(),
            0.99,
        ).item()

        normal_scores.append(
            score
        )

        normal_score_records.append(
            (
                score,
                index,
            )
        )

        print(
            f"\rThreshold samples: "
            f"{index + 1}/"
            f"{number_of_samples}",
            end="",
        )

    print()

    if not normal_scores:

        raise RuntimeError(
            "Unable to calculate "
            "normal threshold."
        )

    scores = torch.tensor(
        normal_scores
    )

    threshold = torch.quantile(
        scores,
        0.995,
    ).item()

    threshold = float(
        threshold
    )

    # ========================================================
    # PRINT TOP NORMAL OUTLIERS
    # ========================================================

    normal_score_records.sort(
        reverse=True
    )

    image_files = sorted(
        TRAIN_GOOD_PATH.glob(
            "*.png"
        )
    )

    print()
    print(
        "Top 10 normal-image anomaly scores:"
    )

    for score, index in normal_score_records[:10]:

        print(
            f"  {image_files[index].name}: "
            f"{score:.6f}"
        )

    # ========================================================
    # SAVE THRESHOLD
    # ========================================================

    output_path = (
        ARTIFACT_DIR
        / "threshold.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            {
                "threshold": threshold
            },
            file,
            indent=4,
        )

    print(
        f"Threshold: {threshold:.6f}"
    )

    print(
        "Saved:",
        output_path
    )

    return threshold


# ============================================================
# SAVE METADATA
# ============================================================

def save_metadata(
    normal_features,
    defect_counts,
    threshold,
):

    metadata = {

        "model": "ResNet18",

        "feature_layer": "layer2",

        "image_size": [
            224,
            224,
        ],

        "normal_training_images": int(
            normal_features.shape[0]
        ),

        "defect_reference_images": (
            defect_counts
        ),

        "defect_classes": (
            DEFECT_CLASSES
        ),

        "threshold": threshold,

        "dataset": "MVTec AD metal_nut",

        "classification_method": (
            "prototype-based"
        ),

    }

    output_path = (
        ARTIFACT_DIR
        / "metadata.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
        )

    print(
        "Saved:",
        output_path
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print(
        "=" * 70
    )

    print(
        "INDUSTRIAL DEFECT AI "
        "OFFLINE MODEL BUILD"
    )

    print(
        "=" * 70
    )

    # --------------------------------------------------------
    # STEP 1
    # --------------------------------------------------------

    normal_features = (
        build_normal_features()
    )

    # --------------------------------------------------------
    # STEP 2
    # --------------------------------------------------------

    defect_prototypes, defect_counts = (
        build_defect_prototypes()
    )

    # --------------------------------------------------------
    # STEP 3
    # --------------------------------------------------------

    threshold = (
        calculate_threshold(
            normal_features
        )
    )

    # --------------------------------------------------------
    # STEP 4
    # --------------------------------------------------------

    save_metadata(
        normal_features,
        defect_counts,
        threshold,
    )

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    print()
    print(
        "=" * 70
    )

    print(
        "MODEL BUILD COMPLETE"
    )

    print(
        "=" * 70
    )

    print()

    print(
        "Artifacts created:"
    )

    print(
        "  ai/vision/artifacts/"
    )

    print(
        "    normal_features.pt"
    )

    print(
        "    defect_prototypes.pt"
    )

    print(
        "    threshold.json"
    )

    print(
        "    metadata.json"
    )
+

    print()

    print(
        "The backend will later load "
        "these artifacts instead of "
        "processing the entire dataset "
        "at startup."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()