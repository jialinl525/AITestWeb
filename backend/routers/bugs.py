import csv
import io
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import Integer, cast, func
from sqlalchemy.orm import Session

import models
import schemas
from auth import require_manager
from database import get_db

router = APIRouter()

CSV_HEADER_CR_NUMBER = "CR Number"
CSV_HEADER_TITLE = "Title"
CSV_HEADER_SEVERITY = "Severity"
CSV_HEADER_TYPE = "CR Type"
CSV_HEADER_STATUS = "CR Status"
CSV_HEADER_CREATED_BY = "Created By"
CSV_HEADER_ASSIGNEE = "CR Assignee"
CSV_HEADER_CREATED_ON = "Created On"
CSV_HEADER_PARENT = "Parent CR"
CSV_HEADER_BUILD = "Software Image Integration Build"

BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
WORKSPACE_DIR = os.path.dirname(BACKEND_DIR)
DEFAULT_BUG_CSV_PATH = os.path.join(BACKEND_DIR, "APT_MM_Audio_SZ_Last90.csv")
INVALID_IMAGE_TOKENS = {"", "na", "n/a", "-", "null", "none"}
LOCKED_IMPORT_STATUS_TOKENS = {"verified", "discarded"}
PENDING_CONFIRMATION_BUILD = "pending confirmation"


def _normalize_severity(raw: Optional[str]) -> str:
    text = (raw or "").strip().lower()
    if "critical" in text:
        return "critical"
    if "high" in text:
        return "high"
    if "low" in text:
        return "low"
    return "medium"


def _normalize_status(raw: Optional[str]) -> str:
    text = (raw or "").strip().lower().replace(" ", "").replace("_", "").replace("-", "")
    if text in {"inprogress", "build", "closed", "duplicate", "fixed", "resolved", "verified", "cannotduplicate"}:
        return "fixed"
    if text in {"open", "analysis"}:
        return "analysis"
    if text == "other":
        return "other"
    return "other"


def _sanitize_status(raw: Optional[str]) -> str:
    value = (raw or "").strip()
    return value or "other"


def _parse_cr_created_on(raw: Optional[str]) -> Optional[datetime]:
    text = (raw or "").strip()
    if not text:
        return None

    formats = [
        "%m/%d/%Y %I:%M:%S %p",
        "%m/%d/%Y %I:%M %p",
        "%m/%d/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y %I:%M:%S",
        "%m/%d/%Y %I:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _normalize_token(raw: Optional[str]) -> str:
    return (raw or "").strip().lower().replace(" ", "").replace("_", "").replace("-", "")


def _is_valid_image_value(raw: Optional[str]) -> bool:
    return _normalize_token(raw) not in INVALID_IMAGE_TOKENS and _normalize_token(raw) != _normalize_token(PENDING_CONFIRMATION_BUILD)


def _split_available_images(raw: Optional[str]) -> List[str]:
    result: List[str] = []
    seen = set()
    for item in (raw or "").split(","):
        value = item.strip()
        token = _normalize_token(value)
        if not token or token in seen or not _is_valid_image_value(value):
            continue
        seen.add(token)
        result.append(value)
    return result


def _merge_available_images(existing_available_images: Optional[str], existing_build: Optional[str], incoming_build: Optional[str]) -> List[str]:
    merged: List[str] = []
    seen = set()

    def add_image(raw_value: Optional[str]):
        value = (raw_value or "").strip()
        token = _normalize_token(value)
        if not token or token in seen or not _is_valid_image_value(value):
            return
        seen.add(token)
        merged.append(value)

    for image in _split_available_images(existing_available_images):
        add_image(image)
    add_image(existing_build)
    for image in _split_available_images(incoming_build):
        add_image(image)

    return merged


def _format_available_images(images: List[str]) -> str:
    return ",".join(images)


def _is_import_locked_status(raw_status: Optional[str]) -> bool:
    return _normalize_token(raw_status) in LOCKED_IMPORT_STATUS_TOKENS


def _get_import_image_value(row: Dict) -> str:
    build_value = (row.get(CSV_HEADER_BUILD) or "").strip()
    if _is_valid_image_value(build_value):
        return build_value

    return "NA"


def _select_primary_bug_row(rows: List[models.Bug]) -> models.Bug:
    if not rows:
        raise ValueError("rows cannot be empty")

    return sorted(
        rows,
        key=lambda row: (
            0 if _is_import_locked_status(row.status) else 1,
            0 if row.test_progress_id is not None else 1,
            0 if row.work_task_id is not None else 1,
            0 if row.cr_created_on is not None else 1,
            row.id,
        ),
    )[0]


def _merge_images_from_bug_rows(rows: List[models.Bug]) -> List[str]:
    merged: List[str] = []
    seen = set()

    def add_image(raw_value: Optional[str]):
        value = (raw_value or "").strip()
        token = _normalize_token(value)
        if not token or token in seen or not _is_valid_image_value(value):
            return
        seen.add(token)
        merged.append(value)

    for row in rows:
        for image in _split_available_images(row.available_images):
            add_image(image)
        add_image(row.software_image_integration_build)

    return merged


def _consolidate_existing_bug_rows(db: Session, rows: List[models.Bug]) -> Optional[models.Bug]:
    if not rows:
        return None

    primary = _select_primary_bug_row(rows)
    duplicates = [row for row in rows if row.id != primary.id]
    if not duplicates:
        return primary

    if not _is_import_locked_status(primary.status):
        all_dates = [row.cr_created_on for row in rows if row.cr_created_on is not None]
        if all_dates:
            primary.cr_created_on = min(all_dates)

        merged_images = _merge_images_from_bug_rows(rows)
        primary.available_images = _format_available_images(merged_images)
        if len(merged_images) > 1:
            primary.software_image_integration_build = PENDING_CONFIRMATION_BUILD
        elif len(merged_images) == 1:
            primary.software_image_integration_build = merged_images[0]

    for row in duplicates:
        db.delete(row)

    db.flush()
    return primary


def _resolve_csv_path(file_path: Optional[str]) -> str:
    if not file_path:
        if os.path.isfile(DEFAULT_BUG_CSV_PATH):
            return DEFAULT_BUG_CSV_PATH
        raise HTTPException(status_code=404, detail="Default CSV file not found")

    normalized = file_path.strip().strip('"').strip("'")
    candidates = []
    if os.path.isabs(normalized):
        candidates.append(normalized)
    else:
        candidates.extend(
            [
                normalized,
                os.path.join(WORKSPACE_DIR, normalized),
                os.path.join(BACKEND_DIR, normalized),
                os.path.join(BACKEND_DIR, os.path.basename(normalized)),
            ]
        )

    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate

    raise HTTPException(status_code=404, detail="CSV file not found")


def _find_test_by_title_fr(db: Session, title: Optional[str]) -> Optional[models.TestProgress]:
    title_text = (title or "").strip()
    if not title_text:
        return None

    candidates = (
        db.query(models.TestProgress)
        .filter(models.TestProgress.fr_number.isnot(None), models.TestProgress.fr_number != "")
        .all()
    )

    title_lower = title_text.lower()
    ordered = sorted(candidates, key=lambda row: len((row.fr_number or "").strip()), reverse=True)
    for row in ordered:
        fr = (row.fr_number or "").strip()
        if fr and fr.lower() in title_lower:
            return row
    return None


def _validate_test_link(db: Session, test_progress_id: Optional[int]) -> None:
    if test_progress_id is None:
        return
    found = db.query(models.TestProgress.id).filter(models.TestProgress.id == test_progress_id).first()
    if not found:
        raise HTTPException(status_code=400, detail="Linked test task not found")


def _validate_work_task_link(db: Session, work_task_id: Optional[int]) -> None:
    if work_task_id is None:
        return
    found = db.query(models.WorkTask.id).filter(models.WorkTask.id == work_task_id).first()
    if not found:
        raise HTTPException(status_code=400, detail="Linked work task not found")


def _apply_auto_test_link(db: Session, payload: Dict, existing: Optional[models.Bug] = None) -> None:
    if payload.get("test_progress_id") is not None:
        return
    if existing and existing.test_progress_id is not None:
        return

    matched = _find_test_by_title_fr(db, payload.get("title"))
    if matched:
        payload["test_progress_id"] = matched.id


def _serialize_bug(row: models.Bug) -> Dict:
    test_task = row.test_progress
    work_task = row.work_task
    return {
        "id": row.id,
        "title": row.title,
        "severity": row.severity,
        "status": row.status,
        "created_by": row.created_by,
        "cr_assignee": row.assigned_to,
        "cr_created_on": row.cr_created_on,
        "software_image_integration_build": row.software_image_integration_build,
        "available_images": row.available_images,
        "test_progress_id": row.test_progress_id,
        "work_task_id": row.work_task_id,
        "external_cr_number": row.external_cr_number,
        "test_task_name": test_task.test_name if test_task else None,
        "test_fr_number": test_task.fr_number if test_task else None,
        "work_task_key": work_task.task_key if work_task else None,
        "work_task_name": work_task.task_name if work_task else None,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
    }


def _apply_bug_order(query):
    # Sort by CR number descending first, then by id descending for stable ordering.
    return query.order_by(cast(func.coalesce(models.Bug.external_cr_number, "0"), Integer).desc(), models.Bug.id.desc())


def _apply_bug_filters(query, status: Optional[str] = None, severity: Optional[str] = None, created_by: Optional[str] = None):
    if status:
        normalized_status = status.strip()
        if normalized_status:
            query = query.filter(func.lower(func.trim(models.Bug.status)) == normalized_status.lower())
    if severity:
        query = query.filter(models.Bug.severity == severity)
    if created_by:
        normalized_created_by = created_by.strip()
        if normalized_created_by:
            query = query.filter(func.lower(func.trim(models.Bug.created_by)) == normalized_created_by.lower())
    return query


def _apply_recent_bug_date_filter(query, recent_days: int = 365):
    if recent_days <= 0:
        return query  # No date filter – return all records
    threshold = datetime.now() - timedelta(days=recent_days)
    return query.filter(models.Bug.cr_created_on.isnot(None), models.Bug.cr_created_on >= threshold)


def _apply_verification_zone_filter(query, verification_zone: Optional[str] = None):
    zone = (verification_zone or "all").strip().lower()
    if zone in {"", "all"}:
        return query

    status_normalized = func.lower(func.trim(func.coalesce(models.Bug.status, "")))
    build_normalized = func.lower(func.trim(func.coalesce(models.Bug.software_image_integration_build, "")))

    is_verified = status_normalized == "verified"
    is_discarded = status_normalized == "discarded"
    has_valid_build = (~build_normalized.in_(["", "na", "n/a", "-", "null", "none"]))

    if zone == "verified":
        return query.filter(is_verified)
    if zone in {"discarded", "abandoned"}:
        return query.filter(is_discarded)
    if zone in {"pending", "pending_verification"}:
        return query.filter(~is_verified, ~is_discarded, has_valid_build)
    if zone in {"waiting", "waiting_build"}:
        return query.filter(~is_verified, ~is_discarded, ~has_valid_build)

    raise HTTPException(status_code=400, detail="Invalid verification zone")


@router.get("/import/csv/fields")
def get_bug_csv_fields(file_path: Optional[str] = None):
    """Extract available CSV fields for bug import."""
    csv_path = _resolve_csv_path(file_path)

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as fp:
        reader = csv.DictReader(fp)
        fields = reader.fieldnames or []
        sample = next(reader, None) or {}

    return {
        "file_path": csv_path,
        "fields": fields,
        "sample": sample,
    }


@router.get("/filters/options")
def get_bug_filter_options(db: Session = Depends(get_db)):
    """Return distinct filter options for bug list page."""
    rows = db.query(models.Bug.created_by, models.Bug.status).all()
    created_by_values = sorted(
        {
            (value or "").strip()
            for (value, _) in rows
            if (value or "").strip()
        },
        key=lambda item: item.lower(),
    )
    status_values = sorted(
        {
            (status_value or "").strip()
            for (_, status_value) in rows
            if (status_value or "").strip()
        },
        key=lambda item: item.lower(),
    )
    return {
        "created_by": created_by_values,
        "status": status_values,
    }


def _upsert_bug_from_csv_row(db: Session, row: Dict) -> str:
    cr_type = (row.get(CSV_HEADER_TYPE) or "").strip().lower()
    if cr_type and cr_type != "bug":
        return "skipped"

    title = (row.get(CSV_HEADER_TITLE) or "").strip()
    cr_number = (row.get(CSV_HEADER_CR_NUMBER) or "").strip()
    build_value = _get_import_image_value(row)
    incoming_created_on = _parse_cr_created_on(row.get(CSV_HEADER_CREATED_ON))
    incoming_images = _split_available_images(build_value)

    existing_rows: List[models.Bug] = []
    if cr_number:
        existing_rows = db.query(models.Bug).filter(models.Bug.external_cr_number == cr_number).order_by(models.Bug.id.asc()).all()

    existing = _consolidate_existing_bug_rows(db, existing_rows)

    if not title and existing is None:
        return "skipped"

    bug_data = {
        "title": title,
        "severity": _normalize_severity(row.get(CSV_HEADER_SEVERITY)),
        "status": _sanitize_status(row.get(CSV_HEADER_STATUS)),
        "created_by": (row.get(CSV_HEADER_CREATED_BY) or "").strip() or "",
        "assigned_to": (row.get(CSV_HEADER_ASSIGNEE) or "").strip() or None,
        "cr_created_on": incoming_created_on,
        "software_image_integration_build": PENDING_CONFIRMATION_BUILD if len(incoming_images) > 1 else (incoming_images[0] if incoming_images else "NA"),
        "available_images": _format_available_images(incoming_images),
        "test_progress_id": None,
        "work_task_id": None,
        "external_cr_number": cr_number or None,
    }

    if existing:
        if _is_import_locked_status(existing.status):
            return "skipped"

        if incoming_created_on is not None and (existing.cr_created_on is None or incoming_created_on < existing.cr_created_on):
            existing.cr_created_on = incoming_created_on

        preserve_existing_build = _is_valid_image_value(existing.software_image_integration_build)
        merged_images = _merge_available_images(
            existing.available_images,
            existing.software_image_integration_build,
            build_value,
        )
        existing.available_images = _format_available_images(merged_images)

        if not preserve_existing_build:
            if len(merged_images) > 1:
                existing.software_image_integration_build = PENDING_CONFIRMATION_BUILD
            elif len(merged_images) == 1:
                existing.software_image_integration_build = merged_images[0]

        return "updated"

    _apply_auto_test_link(db, bug_data)
    db_bug = models.Bug(**bug_data)
    db.add(db_bug)
    db.flush()
    return "imported"


def _import_bugs_from_reader(reader: csv.DictReader, db: Session, limit: int = 0) -> Dict[str, int]:
    imported = 0
    updated = 0
    skipped = 0

    for row in reader:
        if limit > 0 and (imported + updated) >= limit:
            break

        result = _upsert_bug_from_csv_row(db, row)
        if result == "imported":
            imported += 1
        elif result == "updated":
            updated += 1
        else:
            skipped += 1

    return {
        "imported": imported,
        "updated": updated,
        "skipped": skipped,
    }


@router.post("/import/csv")
def import_bugs_from_csv(
    payload: schemas.BugCsvImportRequest,
    db: Session = Depends(get_db),
    _: Dict = Depends(require_manager),
):
    """Import bugs from CSV and auto-link to test task by FR keyword in title when possible."""
    csv_path = _resolve_csv_path(payload.file_path)

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as fp:
        reader = csv.DictReader(fp)
        stats = _import_bugs_from_reader(reader, db, payload.limit)

    db.commit()

    return {
        "file_path": csv_path,
        "imported": stats["imported"],
        "updated": stats["updated"],
        "skipped": stats["skipped"],
    }


@router.post("/import/csv/upload")
async def import_bugs_from_csv_upload(
    file: UploadFile = File(...),
    limit: int = 0,
    db: Session = Depends(get_db),
    _: Dict = Depends(require_manager),
):
    """Import bugs from uploaded CSV file."""
    filename = (file.filename or "").strip()
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV file is supported")

    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="Uploaded CSV file is empty")

    try:
        text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV encoding must be UTF-8") from exc

    reader = csv.DictReader(io.StringIO(text))
    stats = _import_bugs_from_reader(reader, db, limit)
    db.commit()

    return {
        "file_name": filename,
        "imported": stats["imported"],
        "updated": stats["updated"],
        "skipped": stats["skipped"],
    }


@router.get("/query")
def query_bugs(
    status: str = None,
    severity: str = None,
    created_by: str = None,
    verification_zone: str = "all",
    test_id: Optional[int] = None,
    recent_days: int = 365,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Query bugs with filters, CR-number-desc ordering, and pagination metadata."""
    base_query = db.query(models.Bug)
    base_query = _apply_recent_bug_date_filter(base_query, recent_days=recent_days)
    base_query = _apply_bug_filters(base_query, status=status, severity=severity, created_by=created_by)
    base_query = _apply_verification_zone_filter(base_query, verification_zone=verification_zone)
    if test_id is not None:
        base_query = base_query.filter(models.Bug.test_progress_id == test_id)

    total = base_query.count()
    rows = _apply_bug_order(base_query).offset(skip).limit(limit).all()

    return {
        "items": [_serialize_bug(row) for row in rows],
        "total": total,
        "skip": skip,
        "limit": limit,
    }

@router.get("/", response_model=List[schemas.Bug])
def get_bugs_list(
    status: str = None,
    severity: str = None,
    created_by: str = None,
    verification_zone: str = "all",
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get the bug list, with optional status and severity filters."""
    query = db.query(models.Bug)
    query = _apply_bug_filters(query, status=status, severity=severity, created_by=created_by)
    query = _apply_verification_zone_filter(query, verification_zone=verification_zone)
    bugs = _apply_bug_order(query).offset(skip).limit(limit).all()
    return [_serialize_bug(row) for row in bugs]

@router.get("/{bug_id}", response_model=schemas.Bug)
def get_bug(bug_id: int, db: Session = Depends(get_db)):
    """Get a single bug record."""
    bug = db.query(models.Bug).filter(models.Bug.id == bug_id).first()
    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    return _serialize_bug(bug)

@router.post("/", response_model=schemas.Bug)
def create_bug(bug: schemas.BugCreate, db: Session = Depends(get_db), _=Depends(require_manager)):
    """Create a new bug. Manager permission is required."""
    payload = bug.model_dump()
    payload["status"] = _sanitize_status(payload.get("status"))
    payload["assigned_to"] = (payload.pop("cr_assignee", None) or "").strip() or None
    payload["cr_created_on"] = _parse_cr_created_on(payload.pop("cr_created_on", None))
    payload["created_by"] = (payload.get("created_by") or "").strip()
    payload["software_image_integration_build"] = (payload.get("software_image_integration_build") or "").strip()
    _validate_test_link(db, payload.get("test_progress_id"))
    _validate_work_task_link(db, payload.get("work_task_id"))
    _apply_auto_test_link(db, payload)

    db_bug = models.Bug(**payload)
    db.add(db_bug)
    db.commit()
    db.refresh(db_bug)
    return _serialize_bug(db_bug)

@router.put("/{bug_id}", response_model=schemas.Bug)
def update_bug(bug_id: int, bug: schemas.BugBase, db: Session = Depends(get_db), _=Depends(require_manager)):
    """Update an existing bug. Manager permission is required."""
    db_bug = db.query(models.Bug).filter(models.Bug.id == bug_id).first()
    if not db_bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    
    payload = bug.model_dump()
    payload["status"] = _sanitize_status(payload.get("status"))
    payload["assigned_to"] = (payload.pop("cr_assignee", None) or "").strip() or None
    payload["cr_created_on"] = _parse_cr_created_on(payload.pop("cr_created_on", None))
    payload["created_by"] = (payload.get("created_by") or "").strip()
    payload["software_image_integration_build"] = (payload.get("software_image_integration_build") or "").strip()
    _validate_test_link(db, payload.get("test_progress_id"))
    _validate_work_task_link(db, payload.get("work_task_id"))
    _apply_auto_test_link(db, payload, db_bug)

    for key, value in payload.items():
        setattr(db_bug, key, value)
    
    db.commit()
    db.refresh(db_bug)
    return _serialize_bug(db_bug)

@router.delete("/{bug_id}")
def delete_bug(bug_id: int, db: Session = Depends(get_db), _=Depends(require_manager)):
    """Delete a bug. Manager permission is required."""
    db_bug = db.query(models.Bug).filter(models.Bug.id == bug_id).first()
    if not db_bug:
        raise HTTPException(status_code=404, detail="Bug not found")
    
    db.delete(db_bug)
    db.commit()
    return {"message": "Bug deleted"}

@router.get("/test/{test_id}", response_model=List[schemas.Bug])
def get_bugs_by_test(test_id: int, db: Session = Depends(get_db)):
    """Get bugs linked to a specific test."""
    bugs = _apply_bug_order(
        db.query(models.Bug).filter(models.Bug.test_progress_id == test_id)
    ).all()
    return [_serialize_bug(row) for row in bugs]

@router.get("/stats/summary")
def get_bug_stats(recent_days: int = 365, db: Session = Depends(get_db)):
    """Get bug summary statistics.

    Summary metrics (total, by_status, by_severity) respect the ``recent_days``
    parameter (0 = all time).  The monthly trend chart always covers the last
    12 complete calendar months so it remains useful regardless of the filter.
    """
    today = datetime.now()

    # ── Summary stats: respect the requested time range ──────────────────────
    stats_query = db.query(models.Bug)
    if recent_days > 0:
        stats_threshold = today - timedelta(days=recent_days)
        stats_query = stats_query.filter(
            models.Bug.cr_created_on.isnot(None),
            models.Bug.cr_created_on >= stats_threshold,
        )

    total_bugs = stats_query.count()
    status_rows = (
        stats_query.with_entities(models.Bug.status, func.count(models.Bug.id))
        .group_by(models.Bug.status)
        .all()
    )
    status_summary = {"fixed": 0, "analysis": 0, "other": 0}
    for raw_status, count in status_rows:
        bucket = _normalize_status(raw_status)
        status_summary[bucket] += count

    critical_bugs = stats_query.filter(models.Bug.severity == "critical").count()
    high_bugs = stats_query.filter(models.Bug.severity == "high").count()
    medium_bugs = stats_query.filter(models.Bug.severity == "medium").count()
    low_bugs = stats_query.filter(models.Bug.severity == "low").count()

    # ── Monthly trend: always the last 12 complete calendar months ────────────
    trend_start_month = today.month - 11
    trend_start_year = today.year
    if trend_start_month <= 0:
        trend_start_month += 12
        trend_start_year -= 1
    trend_threshold = datetime(trend_start_year, trend_start_month, 1)

    trend_query = db.query(models.Bug).filter(
        models.Bug.cr_created_on.isnot(None),
        models.Bug.cr_created_on >= trend_threshold,
    )
    trend_rows = trend_query.with_entities(models.Bug.cr_created_on, models.Bug.status).all()

    monthly_map = {}
    for created_on, raw_status in trend_rows:
        if created_on is None:
            continue
        month_key = created_on.strftime("%Y-%m")
        if month_key not in monthly_map:
            monthly_map[month_key] = {"month": month_key, "total": 0, "fixed": 0}
        monthly_map[month_key]["total"] += 1
        if _normalize_status(raw_status) == "fixed":
            monthly_map[month_key]["fixed"] += 1

    month_keys = []
    for i in range(12):
        m = trend_start_month + i
        y = trend_start_year
        if m > 12:
            m -= 12
            y += 1
        month_keys.append(f"{y:04d}-{m:02d}")

    monthly_trend = [
        monthly_map.get(key, {"month": key, "total": 0, "fixed": 0})
        for key in month_keys
    ]

    return {
        "total": total_bugs,
        "by_status": {
            "fixed": status_summary["fixed"],
            "analysis": status_summary["analysis"],
            "other": status_summary["other"],
        },
        "by_severity": {
            "critical": critical_bugs,
            "high": high_bugs,
            "medium": medium_bugs,
            "low": low_bugs,
        },
        "monthly_trend": monthly_trend,
    }
