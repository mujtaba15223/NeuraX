from __future__ import annotations

import re
from typing import Any

import pandas as pd


FIELD_ALIASES = {
    "total_parts": (
        "total parts",
        "total_part",
        "parts produced",
        "production volume",
        "output",
        "units produced",
    ),
    "parts_per_hour": (
        "parts per hour",
        "parts/hour",
        "throughput",
        "hourly throughput",
        "units per hour",
    ),
    "demand": (
        "demand",
        "required quantity",
        "required output",
    ),
    "va_time": (
        "va time",
        "value added time",
        "value added",
    ),
    "planned_hours": ("planned hours", "planned time"),
    "actual_hours": ("actual hours", "run hours", "operating hours"),
    "availability": ("availability pct", "availability"),
    "performance": ("performance pct", "performance"),
    "quality": ("quality pct", "quality"),
    "oee": ("oee pct", "oee"),
    "defects": ("defects", "defective units", "defect count"),
    "machine_id": ("machine id", "machine", "asset id"),
    "units_inspected": ("units inspected", "inspected units"),
    "units_passed": ("units passed", "passed units", "good units"),
    "defect_count": ("defect count", "defects", "defective units"),
    "defect_type": ("defect type", "defect category"),
    "qc_result": ("qc result", "quality result", "inspection result"),
    "line_id": ("line id", "production line", "line"),
}


def normalize_header(value: Any) -> str:
    return re.sub(
        r"[^a-z0-9]+",
        " ",
        str(value).strip().lower(),
    ).strip()


def export_headers(dataframe: pd.DataFrame) -> list[str]:
    return [str(column) for column in dataframe.columns]


def _find_column(
    dataframe: pd.DataFrame,
    aliases: tuple[str, ...],
) -> str | None:
    normalized = {
        normalize_header(column): column
        for column in dataframe.columns
    }

    for alias in aliases:
        alias_key = normalize_header(alias)
        if alias_key in normalized:
            return normalized[alias_key]

    for normalized_column, original_column in normalized.items():
        if any(
            normalize_header(alias) in normalized_column
            for alias in aliases
        ):
            return original_column

    return None


def resolve_production_columns(
    dataframe: pd.DataFrame,
) -> dict[str, str | None]:
    return {
        field: _find_column(dataframe, aliases)
        for field, aliases in FIELD_ALIASES.items()
    }


def discover_station_columns(
    dataframe: pd.DataFrame,
) -> dict[str, dict[str, str]]:
    discovered: dict[str, dict[str, str]] = {}

    for column in dataframe.columns:
        normalized = normalize_header(column)
        metric = None

        if any(
            token in normalized
            for token in ("queue", "waiting", "wait")
        ):
            metric = "queue"
        elif any(
            token in normalized
            for token in ("utilization", "utilisation", "util")
        ):
            metric = "utilization"

        if metric is None:
            continue

        station_name = re.sub(
            r"\b(queue|waiting|wait|time|utilization|utilisation|util)\b",
            " ",
            normalized,
        )
        station_name = re.sub(r"\s+", " ", station_name).strip()

        if not station_name:
            continue

        station = station_name.title()
        discovered.setdefault(station, {})[metric] = column

    return {
        station: metrics
        for station, metrics in discovered.items()
        if "queue" in metrics and "utilization" in metrics
    }


def numeric_mean(dataframe: pd.DataFrame, column: str) -> float:
    values = pd.to_numeric(
        dataframe[column],
        errors="coerce",
    )
    return float(values.mean()) if not values.dropna().empty else 0.0


def numeric_sum(dataframe: pd.DataFrame, column: str) -> float:
    values = pd.to_numeric(
        dataframe[column],
        errors="coerce",
    )
    return float(values.sum()) if not values.dropna().empty else 0.0
