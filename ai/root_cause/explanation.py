from datetime import datetime


# ============================================================
# ROOT CAUSE EXPLANATION
# ============================================================

def generate_root_cause_explanation(
    defect_type,
    process_signal,
):
    """
    Convert visual inspection and process evidence into
    a human-readable investigation explanation.

    This function describes evidence and hypotheses.
    It does not claim proven manufacturing causality.
    """

    if not process_signal:
        return {
            "summary": (
                f"A {defect_type} visual anomaly was detected, "
                "but no significant process signal was available "
                "for investigation."
            ),

            "evidence": [],

            "recommended_action": (
                "Review the inspection image and collect "
                "additional process data."
            ),

            "causality_note": (
                "The available evidence is insufficient "
                "to establish a manufacturing cause."
            ),
        }

    station = process_signal.get(
        "station",
        "Unknown",
    )

    queue_mean = process_signal.get(
        "queue_mean",
        0,
    )

    utilization_mean = process_signal.get(
        "utilization_mean",
        0,
    )

    combined_pressure = process_signal.get(
        "combined_pressure",
        0,
    )

    queue_pressure = process_signal.get(
        "queue_pressure",
        0,
    )

    utilization_pressure = process_signal.get(
        "utilization_pressure",
        0,
    )

    summary = (
        f"The visual inspection indicates a "
        f"{defect_type} anomaly. "
        f"Among the available process signals, "
        f"{station} shows the strongest combined "
        f"process pressure."
    )

    evidence = [
        {
            "factor": f"{station} queue time",
            "value": round(
                queue_mean,
                4,
            ),
            "description": (
                "Average queue-time signal associated "
                "with the process station."
            ),
        },
        {
            "factor": f"{station} utilization",
            "value": round(
                utilization_mean,
                4,
            ),
            "description": (
                "Average station utilization signal."
            ),
        },
        {
            "factor": "Queue pressure",
            "value": round(
                queue_pressure,
                4,
            ),
            "description": (
                "Normalized queue pressure relative "
                "to the highest observed station."
            ),
        },
        {
            "factor": "Utilization pressure",
            "value": round(
                utilization_pressure,
                4,
            ),
            "description": (
                "Normalized utilization pressure relative "
                "to the highest observed station."
            ),
        },
        {
            "factor": "Combined process pressure",
            "value": round(
                combined_pressure,
                4,
            ),
            "description": (
                "Weighted process-pressure indicator "
                "used to prioritize investigation."
            ),
        },
    ]

    recommended_action = (
        f"Inspect {station} for handling conditions, "
        "contact-surface interactions, queue-related "
        "waiting, and process variation while reviewing "
        f"the detected {defect_type} anomaly."
    )

    causality_note = (
        "The identified process signal is a likely "
        "contributing factor for investigation, not "
        "proof that the process caused the defect. "
        "Additional production-level evidence is "
        "required to establish causality."
    )

    return {
        "summary": summary,

        "evidence": evidence,

        "recommended_action": (
            recommended_action
        ),

        "causality_note": causality_note,

        "generated_at": (
            datetime.utcnow().isoformat()
            + "Z"
        ),
    }


# ============================================================
# SIMPLE EXPLANATION
# ============================================================

def generate_simple_explanation(
    defect_type,
    station,
):
    """
    Generate a short explanation suitable for a dashboard card.
    """

    return (
        f"{defect_type.capitalize()} anomaly detected. "
        f"{station} currently shows the strongest "
        "process-pressure signal and should be reviewed "
        "as a potential contributing factor."
    )


# ============================================================
# CLI TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("ROOT CAUSE EXPLANATION")
    print("=" * 60)

    example_signal = {
        "station": "Drilling",
        "queue_mean": 2.4623,
        "utilization_mean": 0.5210,
        "queue_pressure": 1.0,
        "utilization_pressure": 0.7620,
        "combined_pressure": 0.9049,
    }

    explanation = (
        generate_root_cause_explanation(
            defect_type="scratch",
            process_signal=example_signal,
        )
    )

    print()
    print("SUMMARY")
    print(
        explanation["summary"]
    )

    print()
    print("EVIDENCE")

    for item in explanation["evidence"]:

        print(
            f"- {item['factor']}: "
            f"{item['value']}"
        )

    print()
    print("RECOMMENDED ACTION")
    print(
        explanation[
            "recommended_action"
        ]
    )

    print()
    print("CAUSALITY NOTE")
    print(
        explanation[
            "causality_note"
        ]
    )