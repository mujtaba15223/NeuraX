from ai.root_cause.feature_analysis import (
    analyze_process_features,
    get_top_process_signal,
)

from ai.root_cause.correlation import (
    calculate_process_correlations,
    calculate_defect_process_association,
)

from ai.root_cause.explanation import (
    generate_root_cause_explanation,
    generate_simple_explanation,
)


# ============================================================
# Industrial Defect Root-Cause Engine
# ============================================================
#
# Pipeline:
#
# Vision Defect
#       ↓
# Feature Analysis
#       ↓
# Process Correlation / Association
#       ↓
# Process Pressure Ranking
#       ↓
# Root-Cause Reasoning
#       ↓
# Human-Readable Explanation
#
# IMPORTANT:
# This system identifies likely contributing factors and
# investigation evidence. It does NOT prove causality.
# ============================================================


# ------------------------------------------------------------
# Defect-specific investigation guidance
# ------------------------------------------------------------

DEFECT_GUIDANCE = {

    "scratch": {
        "investigation": (
            "Inspect handling, contact surfaces, "
            "and queue-related waiting conditions."
        ),
    },

    "flip": {
        "investigation": (
            "Inspect handling, orientation controls, "
            "part positioning, and transfer conditions."
        ),
    },

    "bent": {
        "investigation": (
            "Inspect mechanical handling, station loading, "
            "clamping, pressure, and material movement."
        ),
    },

    "color": {
        "investigation": (
            "Inspect material, surface condition, "
            "process environment, and handling conditions."
        ),
    },

}


# ------------------------------------------------------------
# Root-cause engine
# ------------------------------------------------------------

def analyze_root_cause(
    defect_type="scratch"
):
    """
    Run the complete root-cause investigation pipeline.

    Parameters
    ----------
    defect_type : str
        Defect detected by the vision inspection system.

    Returns
    -------
    dict
        Complete root-cause analysis.
    """

    defect_type = (
        str(defect_type)
        .strip()
        .lower()
    )

    # --------------------------------------------------------
    # STEP 1
    # Analyze process features
    # --------------------------------------------------------

    process_features = (
        analyze_process_features()
    )

    if not process_features:

        return {
            "defect_type": defect_type,
            "status": "insufficient_evidence",
            "message": (
                "No manufacturing process evidence "
                "was available for analysis."
            ),
        }

    # --------------------------------------------------------
    # STEP 2
    # Identify strongest process signal
    # --------------------------------------------------------

    top_process = (
        get_top_process_signal()
    )

    if not top_process:

        return {
            "defect_type": defect_type,
            "status": "insufficient_evidence",
            "message": (
                "Unable to identify a process signal."
            ),
        }

    # --------------------------------------------------------
    # STEP 3
    # Calculate process correlations
    # --------------------------------------------------------

    process_correlations = (
        calculate_process_correlations()
    )

    # --------------------------------------------------------
    # STEP 4
    # Calculate defect-process association
    # --------------------------------------------------------

    process_association = (
        calculate_defect_process_association(
            defect_type=defect_type
        )
    )

    # --------------------------------------------------------
    # STEP 5
    # Extract top process evidence
    #
    # feature_analysis.py returns:
    # queue_time
    # utilization
    # queue_pressure
    # utilization_pressure
    # combined_pressure
    # --------------------------------------------------------

    station = top_process[
        "station"
    ]

    average_queue = top_process[
        "queue_time"
    ]

    average_utilization = top_process[
        "utilization"
    ]

    queue_pressure = top_process[
        "queue_pressure"
    ]

    utilization_pressure = top_process[
        "utilization_pressure"
    ]

    pressure_score = top_process[
        "combined_pressure"
    ]

    # --------------------------------------------------------
    # STEP 6
    # Defect-specific investigation guidance
    # --------------------------------------------------------

    guidance = DEFECT_GUIDANCE.get(
        defect_type,
        {
            "investigation": (
                f"Inspect {station} and review "
                "the relevant process conditions."
            ),
        },
    )

    # --------------------------------------------------------
    # STEP 7
    # Generate human-readable explanation
    # --------------------------------------------------------

    explanation = (
        generate_root_cause_explanation(
            defect_type=defect_type,

            process_signal={
                "station": station,

                "queue_mean": average_queue,

                "utilization_mean": (
                    average_utilization
                ),

                "queue_pressure": (
                    queue_pressure
                ),

                "utilization_pressure": (
                    utilization_pressure
                ),

                "combined_pressure": (
                    pressure_score
                ),
            },
        )
    )

    # --------------------------------------------------------
    # STEP 8
    # Add defect-specific recommendation
    # --------------------------------------------------------

    recommendation = (
        guidance["investigation"]
    )

    # --------------------------------------------------------
    # STEP 9
    # Build final analysis
    # --------------------------------------------------------

    return {

        "defect_type": defect_type,

        "status": "analysis_complete",

        # -----------------------------------------------
        # Main result
        # -----------------------------------------------

        "likely_contributing_factor": (
            station
        ),

        # -----------------------------------------------
        # Process evidence
        # -----------------------------------------------

        "process_evidence": {

            "average_queue": (
                average_queue
            ),

            "average_utilization": (
                average_utilization
            ),

            "queue_pressure": (
                queue_pressure
            ),

            "utilization_pressure": (
                utilization_pressure
            ),

            "pressure_score": (
                pressure_score
            ),
        },

        # -----------------------------------------------
        # Complete station analysis
        # -----------------------------------------------

        "process_features": (
            process_features
        ),

        # -----------------------------------------------
        # Correlation information
        # -----------------------------------------------

        "process_correlations": (
            process_correlations
        ),

        # -----------------------------------------------
        # Defect/process association
        # -----------------------------------------------

        "process_association": (
            process_association
        ),

        # -----------------------------------------------
        # Explanation
        # -----------------------------------------------

        "explanation": (
            explanation
        ),

        "summary": (
            explanation[
                "summary"
            ]
        ),

        # -----------------------------------------------
        # Recommendation
        # -----------------------------------------------

        "recommendation": (
            recommendation
        ),

        # -----------------------------------------------
        # Causality protection
        # -----------------------------------------------

        "causality_note": (
            "The identified process signal is a "
            "likely contributing factor for "
            "investigation, not proof that the "
            "process caused the defect. Additional "
            "production-level evidence is required "
            "to establish causality."
        ),
    }


# ------------------------------------------------------------
# Dashboard-friendly summary
# ------------------------------------------------------------

def get_root_cause_summary(
    defect_type="scratch"
):
    """
    Return a compact result for the frontend dashboard.
    """

    result = analyze_root_cause(
        defect_type=defect_type
    )

    if result["status"] != "analysis_complete":

        return result

    process_evidence = result[
        "process_evidence"
    ]

    return {

        "defect": result[
            "defect_type"
        ],

        "status": result[
            "status"
        ],

        "likely_contributing_factor": (
            result[
                "likely_contributing_factor"
            ]
        ),

        "average_queue": (
            process_evidence[
                "average_queue"
            ]
        ),

        "average_utilization": (
            process_evidence[
                "average_utilization"
            ]
        ),

        "queue_pressure": (
            process_evidence[
                "queue_pressure"
            ]
        ),

        "utilization_pressure": (
            process_evidence[
                "utilization_pressure"
            ]
        ),

        "pressure_score": (
            process_evidence[
                "pressure_score"
            ]
        ),

        "summary": result[
            "summary"
        ],

        "recommendation": result[
            "recommendation"
        ],

        "causality_note": result[
            "causality_note"
        ],

        "evidence": result[
            "explanation"
        ]["evidence"],
    }


# ------------------------------------------------------------
# Simple dashboard explanation
# ------------------------------------------------------------

def get_simple_root_cause(
    defect_type="scratch"
):
    """
    Return a short explanation suitable for a UI card.
    """

    result = analyze_root_cause(
        defect_type=defect_type
    )

    if result["status"] != "analysis_complete":

        return result

    station = result[
        "likely_contributing_factor"
    ]

    return {
        "defect": defect_type,

        "factor": station,

        "explanation": (
            generate_simple_explanation(
                defect_type,
                station,
            )
        ),
    }


# ------------------------------------------------------------
# Print report
# ------------------------------------------------------------

def print_report(
    analysis
):

    print()
    print("=" * 70)

    print(
        "INDUSTRIAL DEFECT ROOT-CAUSE AI"
    )

    print("=" * 70)

    print()

    print(
        f"Detected defect: "
        f"{analysis['defect_type']}"
    )

    print()

    print(
        f"Status: "
        f"{analysis['status']}"
    )

    print()

    print(
        "Likely contributing factor:"
    )

    print(
        f"  "
        f"{analysis['likely_contributing_factor']}"
    )

    evidence = analysis[
        "process_evidence"
    ]

    print()

    print(
        "Process evidence:"
    )

    print(
        f"  Average queue: "
        f"{evidence['average_queue']:.4f}"
    )

    print(
        f"  Average utilization: "
        f"{evidence['average_utilization']:.4f}"
    )

    print(
        f"  Queue pressure: "
        f"{evidence['queue_pressure']:.4f}"
    )

    print(
        f"  Utilization pressure: "
        f"{evidence['utilization_pressure']:.4f}"
    )

    print(
        f"  Pressure score: "
        f"{evidence['pressure_score']:.4f}"
    )

    print()

    print(
        "Explanation:"
    )

    print(
        f"  "
        f"{analysis['summary']}"
    )

    print()

    print(
        "Recommendation:"
    )

    print(
        f"  "
        f"{analysis['recommendation']}"
    )

    print()

    print(
        "Causality note:"
    )

    print(
        f"  "
        f"{analysis['causality_note']}"
    )

    print()

    print("=" * 70)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main():

    print()
    print(
        "Running root-cause analysis..."
    )

    print()

    analysis = (
        analyze_root_cause(
            defect_type="scratch"
        )
    )

    print_report(
        analysis
    )


# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------

if __name__ == "__main__":

    main()