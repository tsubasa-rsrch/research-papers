#!/usr/bin/env python3
"""Ambient Vision — YOLO人物検出 + VLMテキスト要約 → stdout(system-reminder)"""
import os, sys, time, json, subprocess, base64, urllib.request

FLAG = "/tmp/tsubasa_ambient_vision"
LAST = "/tmp/ambient_vision_last"
RATE_LIMIT = 300  # 5 min

if not os.path.exists(FLAG):
    sys.exit(0)

if os.path.exists(LAST):
    diff = time.time() - float(open(LAST).read().strip())
    if diff < RATE_LIMIT:
        sys.exit(0)
open(LAST, 'w').write(str(time.time()))

CAMERAS = {
    "kitchen": os.getenv("CAMERA_KITCHEN_RTSP", ""),
    "bedroom": os.getenv("CAMERA_BEDROOM_RTSP", ""),
}

VLM_URL = os.getenv("VLM_URL", "http://localhost:8090/v1/chat/completions")

def capture(label, rtsp):
    path = f"/tmp/ambient_{label}.jpg"
    subprocess.run(
        ["ffmpeg", "-y", "-rtsp_transport", "tcp", "-i", rtsp,
         "-frames:v", "1", "-q:v", "5", "-vf", "scale=1280:-1", path],
        capture_output=True, timeout=10
    )
    return path if os.path.exists(path) else None

def yolo_detect(path):
    """YOLO person detection with brightness boost for IR. Returns (has_person, count)"""
    try:
        from ultralytics import YOLO
        import cv2
        img = cv2.imread(path)
        # Boost brightness for dark/IR images
        mean_brightness = img.mean()
        if mean_brightness < 80:
            img = cv2.convertScaleAbs(img, alpha=2.0, beta=50)
            cv2.imwrite(path, img)
        model = YOLO("yolov8n.pt")
        results = model(path, verbose=False, classes=[0], conf=0.6)  # class 0 = person, higher threshold to reduce false positives
        boxes = results[0].boxes
        # Additional filter: require minimum box size (at least 5% of image area)
        import numpy as np
        h, w = img.shape[:2]
        min_area = h * w * 0.05
        valid = []
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            area = (x2 - x1) * (y2 - y1)
            if area >= min_area:
                valid.append(box)
        return len(valid) > 0, len(valid)
    except:
        return None, 0  # YOLO failed, unknown

def vlm_describe(path):
    """VLM description for when person is detected"""
    try:
        b64 = base64.b64encode(open(path, 'rb').read()).decode()
        data = json.dumps({
            "model": "qwen3-vl",
            "messages": [{"role": "user", "content": [
                {"type": "text", "text": "Briefly describe the person(s): what they are doing, approximate age, clothing. One line."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]}],
            "max_tokens": 40
        }).encode()
        req = urllib.request.Request(VLM_URL, data, {"Content-Type": "application/json"})
        resp = json.loads(urllib.request.urlopen(req, timeout=20).read())
        return resp["choices"][0]["message"]["content"]
    except:
        return None

def capture_reachy():
    """Capture from ReachyMini camera via SSH+GStreamer"""
    path = "/tmp/ambient_reachy.jpg"
    try:
        # Run capture script on ReachyMini, then SCP the result
        subprocess.run(
            ["ssh", "-o", "ConnectTimeout=3", "-o", "StrictHostKeyChecking=no",
             "$REACHY_SSH_HOST",
             "python3 -c \""
             "import gi; gi.require_version('Gst','1.0'); from gi.repository import Gst; import time,glob,os; "
             "Gst.init(None); "
             "[os.remove(f) for f in glob.glob('/tmp/reachy_ambient_*.jpg')]; "
             "pipe=Gst.parse_launch('unixfdsrc socket-path=/tmp/reachymini_camera_socket ! queue ! videoconvert ! jpegenc quality=90 ! multifilesink location=/tmp/reachy_ambient_%05d.jpg max-files=2'); "
             "pipe.set_state(Gst.State.PLAYING); time.sleep(1.0); pipe.set_state(Gst.State.NULL); "
             "frames=sorted(glob.glob('/tmp/reachy_ambient_*.jpg')); "
             "print(frames[-1] if frames else '')\""],
            capture_output=True, timeout=10)
        subprocess.run(
            ["scp", "-o", "ConnectTimeout=3", "-o", "StrictHostKeyChecking=no",
             "$REACHY_SSH_HOST:/tmp/reachy_ambient_00001.jpg", path],
            capture_output=True, timeout=10)
        return path if os.path.exists(path) and os.path.getsize(path) > 1000 else None
    except:
        return None

# Process all cameras: Tapo (RTSP) + ReachyMini (SSH)
all_cameras = list(CAMERAS.items()) + [("reachy", None)]
for label, rtsp in all_cameras:
    if label == "reachy":
        path = capture_reachy()
    else:
        path = capture(label, rtsp)
    if not path:
        continue

    has_person, count = yolo_detect(path)

    if has_person is None:
        print(f"👁️ {label}: (detection unavailable)")
    elif has_person:
        desc = vlm_describe(path)
        if desc:
            print(f"👁️ {label}: {count} person(s) — {desc}")
        else:
            print(f"👁️ {label}: {count} person(s) detected")
    else:
        print(f"👁️ {label}: empty")

# Spatial recall: store VLM descriptions as text embeddings (lightweight, no CLIP needed)
# Uses existing embedding server at :6333 that recall already uses
try:
    import urllib.request as _ur2
    for _label in list(CAMERAS.keys()):
        _snap = f"/tmp/ambient_{_label}.jpg"
        if not os.path.exists(_snap):
            continue
        _desc_val = vlm_describe(_snap)
        if _desc_val:
            _ts = __import__('datetime').datetime.now().isoformat()
            _doc = f"[{_ts[:16]}] {_label}: {_desc_val}"
            # Append to spatial memory log (text-based, queryable by existing recall)
            with open(os.path.expanduser("~/.tsubasa-daemon/spatial_memory_log.jsonl"), "a") as _f:
                import json as _j2
                _j2.dump({"timestamp": _ts, "location": _label, "description": _desc_val}, _f)
                _f.write("\n")
except:
    pass
