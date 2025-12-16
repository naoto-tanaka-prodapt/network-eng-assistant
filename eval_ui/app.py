import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "agents_output.csv"
ANNOTATIONS_PATH = BASE_DIR / "data" / "annotations.json"

app = FastAPI(title="Agent Evaluation UI")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _clean_header(name: str) -> str:
    """Drop BOM and whitespace from a CSV header."""
    return name.lstrip("\ufeff").strip()


def _load_samples() -> List[Dict]:
    if not DATA_PATH.exists():
        raise RuntimeError(f"CSV not found: {DATA_PATH}")

    with DATA_PATH.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise RuntimeError("CSV has no header row.")

        fieldnames = [_clean_header(h) for h in reader.fieldnames]
        samples: List[Dict] = []
        for idx, row in enumerate(reader):
            cleaned: Dict[str, Dict] = {}
            for i, value in enumerate(row.values()):
                raw_value = value or ""
                parsed = None
                try:
                    parsed = json.loads(raw_value)
                except Exception:
                    parsed = None
                cleaned[fieldnames[i]] = {"raw": raw_value, "parsed": parsed}

            cleaned["sections"] = [
                {"key": "input", "title": "User Input", "content": cleaned.get("input", {})},
                {"key": "identify", "title": "Identify Step", "content": cleaned.get("identify", {})},
                {"key": "locating", "title": "Location Step", "content": cleaned.get("locating", {})},
                {"key": "analyze input", "title": "Analyze Input Notes", "content": cleaned.get("analyze input", {})},
                {"key": "analyze", "title": "Analyze Step", "content": cleaned.get("analyze", {})},
                {"key": "Action", "title": "Action Step", "content": cleaned.get("Action", {})},
                {"key": "validate", "title": "Validate Step", "content": cleaned.get("validate", {})},
            ]

            samples.append({"id": idx, "data": cleaned})
        return samples


def _load_annotations() -> Dict[str, Dict]:
    if not ANNOTATIONS_PATH.exists():
        return {}
    with ANNOTATIONS_PATH.open(encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save_annotations(annotations: Dict[str, Dict]) -> None:
    ANNOTATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ANNOTATIONS_PATH.open("w", encoding="utf-8") as f:
        json.dump(annotations, f, ensure_ascii=False, indent=2)


SAMPLES = _load_samples()


def _next_unannotated(annotations: Dict[str, Dict]) -> Optional[int]:
    for sample in SAMPLES:
        if str(sample["id"]) not in annotations:
            return sample["id"]
    return None


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, idx: Optional[int] = None):
    annotations = _load_annotations()
    if not SAMPLES:
        raise HTTPException(status_code=500, detail="No samples found in CSV.")

    sample_idx = idx
    if sample_idx is None or sample_idx < 0 or sample_idx >= len(SAMPLES):
        sample_idx = _next_unannotated(annotations) or 0

    sample = SAMPLES[sample_idx]
    progress = {
        "total": len(SAMPLES),
        "annotated": len(annotations),
        "remaining": len(SAMPLES) - len(annotations),
    }
    status_map = {int(k): v for k, v in annotations.items()}

    return templates.TemplateResponse(
        "sample.html",
        {
            "request": request,
            "sample": sample,
            "SAMPLES": SAMPLES,
            "progress": progress,
            "annotations": status_map,
        },
    )


@app.post("/annotate")
async def annotate(
    sample_id: int = Form(...),
    verdict: str = Form(...),
    reason: str = Form(""),
):
    if verdict not in {"pass", "fail"}:
        raise HTTPException(status_code=400, detail="Invalid verdict.")
    if verdict == "fail" and not reason.strip():
        raise HTTPException(status_code=400, detail="Reason is required when marking fail.")

    annotations = _load_annotations()
    annotations[str(sample_id)] = {
        "verdict": verdict,
        "reason": reason.strip(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_annotations(annotations)

    next_idx = _next_unannotated(annotations)
    target_idx = next_idx if next_idx is not None else sample_id

    return RedirectResponse(url=f"/?idx={target_idx}", status_code=303)
