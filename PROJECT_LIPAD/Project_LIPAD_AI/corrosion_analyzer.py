"""HSV + YCrCb corrosion detection for video inspection (wet/dry environments)."""

from __future__ import annotations

import os
from datetime import datetime, timezone

import cv2
import numpy as np

K_CONSTANT = 0.05
N_EXPONENT = 0.5
MIN_CONTOUR_AREA_PX = 150


def _hsv_bounds(environment: str) -> tuple[np.ndarray, np.ndarray]:
    env = (environment or "Wet").strip().lower()
    if env == "dry":
        return np.array([3, 85, 37]), np.array([13, 255, 200])
    return np.array([0, 100, 40]), np.array([25, 255, 200])


def _severity_from_rar(rar: float) -> str:
    if rar <= 0:
        return "None"
    if rar < 5:
        return "Minor"
    if rar < 15:
        return "Moderate"
    return "Severe"


def _enhance_frame(frame: np.ndarray, environment: str) -> np.ndarray:
    env = (environment or "Wet").strip().lower()
    if env == "dry":
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        return cv2.cvtColor(cv2.merge((cl, a, b)), cv2.COLOR_LAB2BGR)
    yuv = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV)
    yuv[:, :, 0] = cv2.equalizeHist(yuv[:, :, 0])
    return cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)


def _corrosion_mask(frame: np.ndarray, environment: str) -> np.ndarray:
    enhanced = _enhance_frame(frame, environment)
    lower, upper = _hsv_bounds(environment)
    hsv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2HSV)
    mask_hsv = cv2.inRange(hsv, lower, upper)

    env = (environment or "Wet").strip().lower()
    if env == "wet":
        ycrcb = cv2.cvtColor(enhanced, cv2.COLOR_BGR2YCrCb)
        cr_channel = ycrcb[:, :, 1]
        _, mask_cr = cv2.threshold(cr_channel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        mask = cv2.bitwise_and(mask_hsv, mask_cr)
    else:
        mask = mask_hsv

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask


def annotate_corrosion_frame(
    frame: np.ndarray,
    environment: str,
    patch_stats: dict[int, dict],
    next_patch_id: int,
) -> tuple[np.ndarray, int]:
    """Detect rust on a single frame, update tracking stats, return overlay."""
    mask = _corrosion_mask(frame, environment)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    display = frame.copy()

    for cnt in contours:
        area_px = cv2.contourArea(cnt)
        if area_px < MIN_CONTOUR_AREA_PX:
            continue

        m = cv2.moments(cnt)
        if m["m00"] == 0:
            continue
        cx = int(m["m10"] / m["m00"])
        cy = int(m["m01"] / m["m00"])

        matched_id = None
        for pid, stats in patch_stats.items():
            dx = cx - stats["cx"]
            dy = cy - stats["cy"]
            if (dx * dx + dy * dy) ** 0.5 < 80:
                matched_id = pid
                break

        if matched_id is None:
            matched_id = next_patch_id
            next_patch_id += 1
            patch_stats[matched_id] = {
                "areas_px": [],
                "cx": cx,
                "cy": cy,
                "frames": 0,
            }

        patch_stats[matched_id]["areas_px"].append(area_px)
        patch_stats[matched_id]["cx"] = cx
        patch_stats[matched_id]["cy"] = cy
        patch_stats[matched_id]["frames"] += 1

        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(display, (x, y), (x + w, y + h), (0, 0, 255), 2)

    return display, next_patch_id


def patch_stats_to_rows(
    patch_stats: dict[int, dict],
    gsd_mm_per_px: float,
    environment: str,
    native_w: int,
    native_h: int,
    video_label: str,
    annotated: str = "",
) -> list[dict]:
    rows: list[dict] = []
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for pid in sorted(patch_stats.keys()):
        stats = patch_stats[pid]
        if not stats["areas_px"]:
            continue
        max_area_px = float(np.max(stats["areas_px"]))
        area_mm2 = max_area_px * (gsd_mm_per_px**2)
        rar = (area_mm2 / max(native_w * native_h * (gsd_mm_per_px**2), 1e-6)) * 100.0
        forecast_30d = area_mm2 + (K_CONSTANT * (30**N_EXPONENT))
        rows.append(
            {
                "TimestampUTC": ts,
                "Video": video_label,
                "Annotated_Video": annotated,
                "Type": "Corrosion",
                "Environment": environment,
                "Severity": _severity_from_rar(rar),
                "Crack_ID": f"Corrosion#{pid}",
                "Avg_Length_mm": 0.0,
                "Avg_Width_mm": 0.0,
                "Avg_Orientation_Deg": 0.0,
                "Avg_Area_mm2": round(area_mm2, 2),
                "Forecast_30d_mm2": round(forecast_30d, 2),
                "Rust_Area_Ratio_pct": round(rar, 2),
                "Total_Frames_Tracked": stats["frames"],
                "Critical_Shear_Alert": 0,
                "GSD_mm_per_px": float(gsd_mm_per_px),
            }
        )
    return rows


def analyze_corrosion_video(
    video_path: str,
    gsd_mm_per_px: float,
    environment: str = "Wet",
    frame_stride: int = 5,
    max_frames: int = 0,
    output_video: str | None = None,
) -> list[dict]:
    """Sample video frames, detect rust patches, return CSV-ready rows."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {video_path}")

    fps = float(cap.get(cv2.CAP_PROP_FPS) or 30.0)
    native_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    native_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

    writer = None
    if output_video:
        os.makedirs(os.path.dirname(os.path.abspath(output_video)), exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_video, fourcc, fps, (native_w, native_h))

    patch_stats: dict[int, dict] = {}
    next_patch_id = 1
    frame_idx = 0
    processed = 0

    while cap.isOpened():
        ok, frame = cap.read()
        if not ok:
            break
        frame_idx += 1
        if frame_stride > 1 and frame_idx % frame_stride != 0:
            continue
        processed += 1
        if max_frames and processed > max_frames:
            break

        display, next_patch_id = annotate_corrosion_frame(
            frame, environment, patch_stats, next_patch_id
        )
        if writer is not None:
            writer.write(display)

    cap.release()
    if writer is not None:
        writer.release()

    annotated = os.path.abspath(output_video) if output_video else ""
    video_abs = os.path.abspath(video_path)
    return patch_stats_to_rows(
        patch_stats,
        gsd_mm_per_px,
        environment,
        native_w,
        native_h,
        video_abs,
        annotated,
    )
