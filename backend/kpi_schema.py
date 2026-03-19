from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional


def _normalize_token(value: Optional[str]) -> str:
    text = (value or "").strip().lower()
    return "".join(ch for ch in text if ch.isalnum())


KPI_SCHEMA_VERSION = 2
KPI_SCHEMA_FILE = Path(__file__).with_name("kpi_schema_data.json")

DEFAULT_KPI_SCHEMA: Dict[str, object] = {
    "version": KPI_SCHEMA_VERSION,
    "categories": [
        {
            "key": "ASR",
            "label": "ASR",
            "description": "Speech-to-text model family used for command recognition, dictation, and conversational transcription.",
            "implementation_notes": "Common implementations combine front-end audio preprocessing, acoustic modeling, language modeling, and post-processing tuned for streaming or offline scenarios.",
            "metrics": [
                {"key": "power_consumption", "label": "Power", "unit": "W", "direction": "lower", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Average platform power draw during the ASR test run."},
                {"key": "latency", "label": "Latency", "unit": "ms", "direction": "lower", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Recognition response delay from audio input to final result."},
                {"key": "accuracy_en", "label": "Accuracy-en", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "English recognition accuracy under the current benchmark set."},
                {"key": "accuracy_cn", "label": "Accuracy-cn", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Chinese recognition accuracy under the current benchmark set."},
                {"key": "accuracy_es", "label": "Accuracy-es", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Spanish recognition accuracy under the current benchmark set."},
                {"key": "accuracy_total", "label": "Accuracy-total", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Overall aggregated ASR accuracy across supported evaluation sets."},
            ],
        },
        {
            "key": "TTS",
            "label": "TTS",
            "description": "Text-to-speech model family used for voice playback, assistant prompts, and spoken UI output.",
            "implementation_notes": "Typical stacks combine text normalization, acoustic generation, and neural vocoder components, with tuning between naturalness, throughput, and on-device resource usage.",
            "metrics": [
                {"key": "power_consumption", "label": "Power", "unit": "W", "direction": "lower", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Average platform power draw during TTS inference."},
                {"key": "latency", "label": "Latency", "unit": "ms", "direction": "lower", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Speech synthesis delay from text request to audible output start."},
                {"key": "accuracy_en", "label": "Accuracy-en", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "English synthesis quality score or proxy benchmark score."},
                {"key": "accuracy_cn", "label": "Accuracy-cn", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Chinese synthesis quality score or proxy benchmark score."},
                {"key": "accuracy_es", "label": "Accuracy-es", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Spanish synthesis quality score or proxy benchmark score."},
                {"key": "accuracy_total", "label": "Accuracy-total", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Overall aggregated TTS quality score across supported evaluation sets."},
            ],
        },
        {
            "key": "Translation",
            "label": "Translation",
            "description": "Text translation model family for multilingual translation quality and throughput comparison.",
            "implementation_notes": "Implementations usually rely on multilingual encoders and decoders with domain tuning, terminology constraints, and serving optimizations for batch or real-time translation.",
            "metrics": [
                {"key": "power_consumption", "label": "Power", "unit": "W", "direction": "lower", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Average platform power draw during translation inference."},
                {"key": "latency", "label": "Latency", "unit": "ms", "direction": "lower", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "End-to-end translation response delay for the configured test case."},
                {"key": "accuracy_en_to_cn", "label": "Accuracy-en to cn", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "English to Chinese translation accuracy or quality score."},
                {"key": "accuracy_cn_to_en", "label": "Accuracy-cn to en", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Chinese to English translation accuracy or quality score."},
                {"key": "accuracy_en_to_es", "label": "Accuracy-en to es", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "English to Spanish translation accuracy or quality score."},
                {"key": "accuracy_es_to_en", "label": "Accuracy-es to en", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Spanish to English translation accuracy or quality score."},
                {"key": "accuracy_total", "label": "Accuracy-total", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Overall aggregated translation quality across configured language directions."},
            ],
        },
        {
            "key": "VoiceCallTranslation Solution",
            "label": "VoiceCallTranslation Solution",
            "description": "Full voice-call translation solution integrating ASR, translation, and TTS in one streaming workflow.",
            "implementation_notes": "These solutions typically orchestrate multiple model stages in real time, so pipeline coordination, buffering strategy, and stage latency balancing strongly affect user experience.",
            "metrics": [
                {"key": "power_consumption", "label": "Power", "unit": "W", "direction": "lower", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Average platform power draw across the end-to-end voice call translation workflow."},
                {"key": "e2e_latency", "label": "E2E Latency", "unit": "ms", "direction": "lower", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Total pipeline latency from source speech input to translated speech output."},
                {"key": "accuracy_en_to_cn", "label": "Accuracy-en to cn", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "English to Chinese translation quality within the full voice-call solution."},
                {"key": "accuracy_cn_to_en", "label": "Accuracy-cn to en", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Chinese to English translation quality within the full voice-call solution."},
                {"key": "accuracy_total", "label": "Accuracy-total", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Overall user-facing quality score for the full voice-call translation pipeline."},
            ],
        },
        {
            "key": "LPI Recording",
            "label": "LPI Recording",
            "description": "Low-power idle or always-on audio recording scenario focused on battery-sensitive capture workloads.",
            "implementation_notes": "Implementations usually emphasize DSP offload, low-duty-cycle wakeups, and data path simplification to minimize steady-state energy cost.",
            "metrics": [
                {"key": "power_consumption", "label": "Power", "unit": "W", "direction": "lower", "chart_roles": ["ladder", "table", "form"], "definition": "Average platform power draw while the low-power recording pipeline remains active."},
            ],
        },
        {
            "key": "Multi Model Detection",
            "label": "Multi Model Detection",
            "description": "Multi-trigger or multi-model detection stack for wake word, event detection, or front-end sensing workloads.",
            "implementation_notes": "Common implementations chain lightweight detectors with policy logic to balance responsiveness, false accept rate, and compute cost under continuous listening constraints.",
            "metrics": [
                {"key": "power_consumption", "label": "Power", "unit": "W", "direction": "lower", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Average platform power draw while all detection models are active."},
                {"key": "latency", "label": "Latency", "unit": "ms", "direction": "lower", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Detection response delay from trigger condition to final decision."},
                {"key": "wakeup_rate", "label": "Wakeup Rate", "unit": "%", "direction": "higher", "chart_roles": ["ladder", "scatter", "table", "form"], "definition": "Successful wakeup or detection rate under the configured benchmark."},
            ],
        },
    ],
    "category_aliases": {
        "voicecalltranslationsolution": "VoiceCallTranslation Solution",
        "voicecalltranslation": "VoiceCallTranslation Solution",
    },
    "metric_aliases": {
        "power": "power_consumption",
        "powerconsumption": "power_consumption",
        "latency": "latency",
        "e2elatency": "e2e_latency",
        "wakeuprate": "wakeup_rate",
        "accuracytotal": "accuracy_total",
        "accuracyoverall": "accuracy_total",
        "accuracyen": "accuracy_en",
        "accuracycn": "accuracy_cn",
        "accuracyzh": "accuracy_cn",
        "accuracyes": "accuracy_es",
        "accuracyentocn": "accuracy_en_to_cn",
        "accuracycntoen": "accuracy_cn_to_en",
        "accuracyentoes": "accuracy_en_to_es",
        "accuracyestoen": "accuracy_es_to_en",
    },
    "metric_filter_aliases": {
        "accuracy_total": ["accuracy_overall"],
        "accuracy_cn": ["accuracy_zh"],
        "e2e_latency": ["latency"],
    },
}

_schema_cache: Optional[Dict[str, object]] = None


def _sanitize_metric(metric: Dict[str, Any]) -> Dict[str, object]:
    metric_key = str(metric.get("key") or "").strip()
    if not metric_key:
        raise ValueError("Metric key is required")

    direction = str(metric.get("direction") or "higher").strip().lower()
    if direction not in {"higher", "lower"}:
        raise ValueError(f"Invalid metric direction for {metric_key}: {direction}")

    chart_roles: List[str] = []
    for role in metric.get("chart_roles", []) or []:
        role_name = str(role or "").strip().lower()
        if role_name and role_name not in chart_roles:
            chart_roles.append(role_name)
    if not chart_roles:
        chart_roles = ["table", "form"]

    return {
        "key": metric_key,
        "label": str(metric.get("label") or metric_key).strip(),
        "unit": str(metric.get("unit") or "").strip(),
        "direction": direction,
        "chart_roles": chart_roles,
        "definition": str(metric.get("definition") or "").strip(),
    }


def _sanitize_category(category: Dict[str, Any]) -> Dict[str, object]:
    category_key = str(category.get("key") or "").strip()
    if not category_key:
        raise ValueError("Category key is required")

    metrics: List[Dict[str, object]] = []
    seen_metric_tokens = set()
    for metric in category.get("metrics", []) or []:
        sanitized_metric = _sanitize_metric(metric)
        metric_token = _normalize_token(str(sanitized_metric["key"]))
        if metric_token in seen_metric_tokens:
            raise ValueError(f"Duplicate metric key in {category_key}: {sanitized_metric['key']}")
        seen_metric_tokens.add(metric_token)
        metrics.append(sanitized_metric)

    if not metrics:
        raise ValueError(f"Category {category_key} must contain at least one metric")

    return {
        "key": category_key,
        "label": str(category.get("label") or category_key).strip(),
        "description": str(category.get("description") or "").strip(),
        "implementation_notes": str(category.get("implementation_notes") or "").strip(),
        "metrics": metrics,
    }


def _sanitize_schema(raw_schema: Dict[str, Any]) -> Dict[str, object]:
    categories: List[Dict[str, object]] = []
    seen_category_tokens = set()
    for category in raw_schema.get("categories", []) or []:
        sanitized_category = _sanitize_category(category)
        category_token = _normalize_token(str(sanitized_category["key"]))
        if category_token in seen_category_tokens:
            raise ValueError(f"Duplicate category key: {sanitized_category['key']}")
        seen_category_tokens.add(category_token)
        categories.append(sanitized_category)

    category_aliases = {
        _normalize_token(alias): str(target).strip()
        for alias, target in (raw_schema.get("category_aliases", {}) or {}).items()
        if _normalize_token(alias) and str(target).strip()
    }
    metric_aliases = {
        _normalize_token(alias): str(target).strip()
        for alias, target in (raw_schema.get("metric_aliases", {}) or {}).items()
        if _normalize_token(alias) and str(target).strip()
    }
    metric_filter_aliases = {
        str(key).strip(): [str(item).strip() for item in values if str(item).strip()]
        for key, values in (raw_schema.get("metric_filter_aliases", {}) or {}).items()
        if str(key).strip()
    }

    return {
        "version": KPI_SCHEMA_VERSION,
        "categories": categories,
        "category_aliases": category_aliases,
        "metric_aliases": metric_aliases,
        "metric_filter_aliases": metric_filter_aliases,
    }


def _write_schema_file(schema: Dict[str, object]) -> None:
    KPI_SCHEMA_FILE.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")


def _load_schema_file() -> Dict[str, object]:
    if not KPI_SCHEMA_FILE.exists():
        default_schema = _sanitize_schema(deepcopy(DEFAULT_KPI_SCHEMA))
        _write_schema_file(default_schema)
        return default_schema

    raw_text = KPI_SCHEMA_FILE.read_text(encoding="utf-8")
    loaded = json.loads(raw_text)
    return _sanitize_schema(loaded)


def _get_schema_ref() -> Dict[str, object]:
    global _schema_cache
    if _schema_cache is None:
        _schema_cache = _load_schema_file()
    return _schema_cache


def _save_schema(schema: Dict[str, object]) -> Dict[str, object]:
    global _schema_cache
    sanitized = _sanitize_schema(schema)
    _write_schema_file(sanitized)
    _schema_cache = sanitized
    return sanitized


def get_kpi_schema_payload() -> Dict[str, object]:
    return deepcopy(_get_schema_ref())


def create_schema_category(category: Dict[str, Any]) -> Dict[str, object]:
    schema = get_kpi_schema_payload()
    sanitized_category = _sanitize_category(category)
    category_token = _normalize_token(str(sanitized_category["key"]))
    for existing in schema["categories"]:
        if _normalize_token(str(existing["key"])) == category_token:
            raise ValueError(f"Category already exists: {sanitized_category['key']}")
    schema["categories"].append(sanitized_category)
    _save_schema(schema)
    return deepcopy(sanitized_category)


def update_schema_category(category_key: str, category: Dict[str, Any]) -> Dict[str, object]:
    schema = get_kpi_schema_payload()
    target_token = _normalize_token(category_key)
    for index, existing in enumerate(schema["categories"]):
        if _normalize_token(str(existing["key"])) != target_token:
            continue
        incoming = dict(category)
        incoming["key"] = str(existing["key"])
        sanitized_category = _sanitize_category(incoming)
        schema["categories"][index] = sanitized_category
        _save_schema(schema)
        return deepcopy(sanitized_category)
    raise ValueError(f"Category not found: {category_key}")


def delete_schema_category(category_key: str) -> None:
    schema = get_kpi_schema_payload()
    target_token = _normalize_token(category_key)
    filtered = [
        category
        for category in schema["categories"]
        if _normalize_token(str(category["key"])) != target_token
    ]
    if len(filtered) == len(schema["categories"]):
        raise ValueError(f"Category not found: {category_key}")
    schema["categories"] = filtered
    _save_schema(schema)


def get_category_metric_fields() -> Dict[str, List[str]]:
    result: Dict[str, List[str]] = {}
    for category in _get_schema_ref()["categories"]:
        key = str(category["key"])
        metrics = [str(metric["key"]) for metric in category.get("metrics", [])]
        result[key] = metrics
    return result


def get_metric_meta_by_key() -> Dict[str, Dict[str, object]]:
    meta: Dict[str, Dict[str, object]] = {}
    for category in _get_schema_ref()["categories"]:
        for metric in category.get("metrics", []):
            metric_key = str(metric["key"])
            if metric_key in meta:
                continue
            meta[metric_key] = deepcopy(metric)
    return meta


def get_metric_filter_aliases() -> Dict[str, List[str]]:
    return deepcopy(_get_schema_ref().get("metric_filter_aliases", {}))


def get_category_keys() -> List[str]:
    return [str(category["key"]) for category in _get_schema_ref()["categories"]]


def canonical_category(value: Optional[str]) -> str:
    raw = (value or "").strip()
    token = _normalize_token(raw)
    if not token:
        return raw

    for category in _get_schema_ref()["categories"]:
        category_key = str(category["key"])
        if _normalize_token(category_key) == token:
            return category_key

    aliases = _get_schema_ref().get("category_aliases", {})
    return str(aliases.get(token, raw))


def canonical_metric(value: Optional[str]) -> str:
    raw = (value or "").strip()
    token = _normalize_token(raw)
    if not token:
        return raw

    aliases = _get_schema_ref().get("metric_aliases", {})
    if token in aliases:
        return str(aliases[token])

    for metric_key in get_metric_meta_by_key().keys():
        if _normalize_token(metric_key) == token:
            return metric_key

    return raw


def is_lower_better_metric(metric_key: Optional[str]) -> bool:
    canonical_key = canonical_metric(metric_key)
    meta = get_metric_meta_by_key().get(canonical_key, {})
    return str(meta.get("direction", "higher")).lower() == "lower"


def get_metrics_for_category(category_key: str) -> List[str]:
    fields = get_category_metric_fields()
    return fields.get(canonical_category(category_key), [])


def get_scatter_metric_keys_for_category(category_key: str) -> List[str]:
    category = canonical_category(category_key)
    for item in _get_schema_ref()["categories"]:
        if str(item["key"]) != category:
            continue
        result: List[str] = []
        for metric in item.get("metrics", []):
            roles = {str(role).lower() for role in metric.get("chart_roles", [])}
            if "scatter" in roles:
                result.append(str(metric["key"]))
        return result
    return []
