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

DEFECT_PROTOTYPES_PATH = (
    ARTIFACT_DIR
    / "defect_prototypes.pt"
)

THRESHOLD_PATH = (
    ARTIFACT_DIR
    / "threshold.json"
)

METADATA_PATH = (
    ARTIFACT_DIR
    / "metadata.json"
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
    f"[VISION] Device: {DEVICE}"
)


# ============================================================
# CHECK ARTIFACTS
# ============================================================

required_artifacts = [
    NORMAL_FEATURES_PATH,
    DEFECT_PROTOTYPES_PATH,
    THRESHOLD_PATH,
    METADATA_PATH,
]

for artifact in required_artifacts:

    if not artifact.exists():

        raise FileNotFoundError(
            "Missing vision artifact:\n"
            f"{artifact}\n\n"
            "Run:\n"
            "python -m ai.vision.train"
        )


# ============================================================
# IMAGE TRANSFORM
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
# LOAD MODEL
# ============================================================

print(
    "[VISION] Loading ResNet18..."
)

weights = (
    models.ResNet18_Weights.DEFAULT
)

MODEL = models.resnet18(
    weights=weights
)

MODEL.eval()

MODEL.to(
    DEVICE
)


# ============================================================
# LOAD ARTIFACTS
# ============================================================

print(
    "[VISION] Loading saved artifacts..."
)


NORMAL_FEATURES = torch.load(
    NORMAL_FEATURES_PATH,
    map_location="cpu",
    weights_only=True,
)

# Keep older feature artifacts compatible with the cosine-style score.
NORMAL_FEATURES = F.normalize(
    NORMAL_FEATURES,
    dim=1,
)


DEFECT_PROTOTYPES = torch.load(
    DEFECT_PROTOTYPES_PATH,
    map_location="cpu",
    weights_only=True,
)


with open(
    THRESHOLD_PATH,
    "r",
    encoding="utf-8",
) as file:

    threshold_data = json.load(
        file
    )


CALIBRATED_THRESHOLD = float(
    threshold_data[
        "threshold"
    ]
)


with open(
    METADATA_PATH,
    "r",
    encoding="utf-8",
) as file:

    METADATA = json.load(
        file
    )


print(
    "[VISION] Normal features:",
    tuple(
        NORMAL_FEATURES.shape
    ),
)

print(
    "[VISION] Defect classes:",
    list(
        DEFECT_PROTOTYPES.keys()
    ),
)

print(
    "[VISION] Threshold:",
    f"{CALIBRATED_THRESHOLD:.6f}"
)

print(
    "[VISION] Model ready."
)


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

        x = MODEL.conv1(
            tensor
        )

        x = MODEL.bn1(
            x
        )

        x = MODEL.relu(
            x
        )

        x = MODEL.maxpool(
            x
        )

        x = MODEL.layer1(
            x
        )

        x = MODEL.layer2(
            x
        )


    x = F.normalize(
        x,
        dim=1,
    )


    return x


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

        x = MODEL.conv1(
            tensor
        )

        x = MODEL.bn1(
            x
        )

        x = MODEL.relu(
            x
        )

        x = MODEL.maxpool(
            x
        )

        x = MODEL.layer1(
            x
        )

        x = MODEL.layer2(
            x
        )

        x = MODEL.layer3(
            x
        )

        x = MODEL.layer4(
            x
        )

        x = MODEL.avgpool(
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


    return x


# ============================================================
# ANOMALY SCORE
# ============================================================

def calculate_anomaly_score(
    image
):

    feature_map = (
        extract_feature_map(
            image
        )
    )


    normal_features = (
        NORMAL_FEATURES.to(
            DEVICE
        )
    )


    with torch.no_grad():

        similarities = torch.einsum(
            "nchw,mchw->nmhw",
            feature_map,
            normal_features,
        )


        best_similarity = (
            similarities.max(
                dim=1
            ).values
        )


        anomaly_map = (
            1.0
            - best_similarity
        )


        flattened = (
            anomaly_map.flatten()
        )


        # Focus on the strongest 2%
        # of spatial anomaly locations.
        top_k = max(
            1,
            int(
                flattened.numel()
                * 0.02
            ),
        )


        top_values = torch.topk(
            flattened,
            top_k,
        ).values


        anomaly_score = (
            top_values.mean().item()
        )


    return float(
        anomaly_score
    )


# ============================================================
# DEFECT CLASSIFICATION
# ============================================================

def classify_defect(
    image
):

    feature = (
        extract_global_feature(
            image
        )
    )


    scores = {}


    with torch.no_grad():

        for (
            defect_class,
            prototype,
        ) in DEFECT_PROTOTYPES.items():

            prototype = (
                prototype.to(
                    DEVICE
                )
            )


            similarity = (
                F.cosine_similarity(
                    feature,
                    prototype.unsqueeze(0),
                    dim=1,
                ).item()
            )


            scores[
                defect_class
            ] = float(
                similarity
            )


    if not scores:

        return {

            "defect_type": None,

            "classification_confidence": 0.0,

            "prototype_similarity": 0.0,

            "class_scores": {},

        }


    # Sort by similarity.
    sorted_scores = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )


    best_class = (
        sorted_scores[0][0]
    )


    best_score = (
        sorted_scores[0][1]
    )


    # Convert relative similarities
    # into an interpretable relative score.
    score_tensor = torch.tensor(
        list(
            scores.values()
        ),
        dtype=torch.float32,
    )


    probabilities = torch.softmax(
        score_tensor * 10.0,
        dim=0,
    )


    class_names = list(
        scores.keys()
    )


    best_index = (
        class_names.index(
            best_class
        )
    )


    confidence = (
        probabilities[
            best_index
        ].item()
    )


    return {

        "defect_type": (
            best_class
        ),

        "classification_confidence": round(
            confidence,
            4,
        ),

        "prototype_similarity": round(
            best_score,
            4,
        ),

        "class_scores": {

            name: round(
                score,
                4,
            )

            for name, score
            in scores.items()

        },

    }


# ============================================================
# MAIN PREDICTION
# ============================================================

def predict_image(
    image_path
):

    image_path = Path(
        image_path
    )


    if not image_path.exists():

        raise FileNotFoundError(
            f"Image not found: "
            f"{image_path}"
        )


    # --------------------------------------------------------
    # LOAD ONLY THE UPLOADED IMAGE
    # --------------------------------------------------------

    image = Image.open(
        image_path
    ).convert("RGB")


    # --------------------------------------------------------
    # ANOMALY DETECTION
    # --------------------------------------------------------

    anomaly_score = (
        calculate_anomaly_score(
            image
        )
    )


    threshold = (
        CALIBRATED_THRESHOLD
    )


    is_defective = (
        anomaly_score
        >= threshold
    )


    # --------------------------------------------------------
    # CLASSIFICATION
    # --------------------------------------------------------

    classification = (
        classify_defect(
            image
        )
    )


    if is_defective:

        status = "DEFECTIVE"

        defect_type = (
            classification[
                "defect_type"
            ]
        )

    else:

        status = "GOOD"

        defect_type = None


    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

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

        "defect_type": (
            defect_type
        ),

        "classification_confidence": (
            classification[
                "classification_confidence"
            ]
        ),

        "prototype_similarity": (
            classification[
                "prototype_similarity"
            ]
        ),

        "class_scores": (
            classification[
                "class_scores"
            ]
        ),

        "model": (
            "ResNet18 localized "
            "feature anomaly detector "
            "+ saved defect prototypes"
        ),

        "classification_method": (
            "Prototype-based classification "
            "using precomputed MVTec artifacts"
        ),

        "inference_mode": (
            "single-image"
        ),

    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_image = (
        BASE_DIR
        / "data"
        / "raw"
        / "vision"
        / "metal_nut"
        / "test"
        / "scratch"
        / "000.png"
    )


    print()
    print(
        "=" * 70
    )

    print(
        "VISION INFERENCE TEST"
    )

    print(
        "=" * 70
    )


    result = predict_image(
        test_image
    )


    print()

    print(
        "Image:",
        test_image.name,
    )

    print(
        "Status:",
        result[
            "status"
        ],
    )

    print(
        "Anomaly Score:",
        result[
            "anomaly_score"
        ],
    )

    print(
        "Threshold:",
        result[
            "threshold"
        ],
    )

    print(
        "Defective:",
        result[
            "is_defective"
        ],
    )

    print(
        "Defect Type:",
        result[
            "defect_type"
        ],
    )

    print(
        "Classification Confidence:",
        result[
            "classification_confidence"
        ],
    )

    print(
        "Prototype Similarity:",
        result[
            "prototype_similarity"
        ],
    )

    print()

    print(
        "Class Scores:"
    )


    for (
        defect_class,
        score,
    ) in result[
        "class_scores"
    ].items():

        print(
            f"  {defect_class}: "
            f"{score}"
        )


    print()

    print(
        "Inference Mode:",
        result[
            "inference_mode"
        ],
    )

    print(
        "Model:",
        result[
            "model"
        ],
    )

    print()

    print(
        "=" * 70
    )

    print(
        "INFERENCE COMPLETE"
    )

    print(
        "=" * 70
    )