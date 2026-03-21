#!/usr/bin/env python3
"""
Audio Midground Phase 1: Startle Reflex (驚愕反射)

Based on baby auditory development Phase 1 (0-1 month / brainstem).
Detects sudden amplitude changes. No FFT needed. Threshold-based alert.

Runs as a background process, writes status to /tmp/audio_midground.txt
for system-reminder pickup (same pattern as ambient-vision).

Usage:
    python3 audio_midground.py                  # kitchen (default)
    python3 audio_midground.py --camera bedroom
    python3 audio_midground.py --once           # single check
"""
import os
import sys
import time
import wave
import subprocess
import numpy as np
from datetime import datetime
from pathlib import Path
from collections import deque

# --- Config ---
CAMERAS = {
    "kitchen": {
        "ip": os.getenv("CAMERA_KITCHEN_IP", "192.168.1.100"),
        "user": os.getenv("CAMERA_KITCHEN_USER", "admin"),
        "password": os.getenv("CAMERA_PASSWORD", "changeme"),
    },
    "bedroom": {
        "ip": os.getenv("CAMERA_BEDROOM_IP", "192.168.1.101"),
        "user": os.getenv("CAMERA_BEDROOM_USER", "admin"),
        "password": os.getenv("CAMERA_PASSWORD", "changeme"),
    },
}

CHUNK_DURATION = 1.0        # 1-second chunks for responsive detection
SAMPLE_RATE = 16000
POLL_INTERVAL = 2.0         # seconds between checks
STARTLE_THRESHOLD_DB = 15.0 # dB jump from baseline = startle
BASELINE_WINDOW = 10        # rolling window for baseline (in chunks)
ALERT_COOLDOWN = 30.0       # seconds between alerts (no spam)
OUTPUT_FILE_TEMPLATE = "/tmp/audio_midground_{camera}.txt"
COMBINED_OUTPUT = "/tmp/audio_midground.txt"
FLAG_FILE = "/tmp/tsubasa_audio_midground"

# --- Core ---

def capture_short_chunk(camera="kitchen", duration=CHUNK_DURATION):
    """Capture a short audio chunk from Tapo camera RTSP."""
    cam = CAMERAS[camera]
    rtsp_url = f"rtsp://{cam['user']}:{cam['password']}@{cam['ip']}:554/stream2"
    output_path = f"/tmp/tapo_audio/{camera}_midground.wav"
    os.makedirs("/tmp/tapo_audio", exist_ok=True)

    try:
        result = subprocess.run([
            "ffmpeg", "-rtsp_transport", "tcp",
            "-use_wallclock_as_timestamps", "1",
            "-fflags", "+genpts",
            "-i", rtsp_url,
            "-vn", "-acodec", "pcm_s16le",
            "-ar", str(SAMPLE_RATE), "-ac", "1",
            "-t", str(duration),
            "-y", output_path
        ], capture_output=True, timeout=duration + 8,
        env={**os.environ, "AV_LOG_FORCE_NOCOLOR": "1"})

        if not os.path.exists(output_path) or os.path.getsize(output_path) <= 100:
            return None
        return output_path

    except (subprocess.TimeoutExpired, Exception):
        return None


def compute_rms_db(audio_path):
    """Compute RMS level in dB from a WAV file."""
    try:
        with wave.open(audio_path, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
        audio_np = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
        if len(audio_np) == 0:
            return None
        rms = np.sqrt(np.mean(audio_np ** 2))
        rms_db = 20 * np.log10(max(rms, 1e-10) / 32768.0)
        return float(round(rms_db, 1))
    except Exception:
        return None


def classify_environment(rms_db, has_speech=None):
    """Environment classification. Phase 2: uses VAD when available."""
    if rms_db is None:
        return "不明"
    if rms_db < -55.0:
        return "静か"
    if has_speech is True:
        return "話し声あり"
    elif has_speech is False and rms_db >= -35.0:
        return "音楽/環境音あり（声なし）"
    elif rms_db < -35.0:
        return "BGMあり"
    else:
        return "音あり"


# --- Phase 2: VAD ---
_vad_model = None
_vad_utils = None

def detect_speech_vad(audio_path):
    """Phase 2: Detect speech using Silero VAD. Returns (has_speech, speech_duration)."""
    global _vad_model, _vad_utils
    try:
        import torch
        if _vad_model is None:
            _vad_model, _vad_utils = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                trust_repo=True
            )
        get_speech_timestamps = _vad_utils[0]

        with wave.open(audio_path, 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        wav_tensor = torch.from_numpy(audio)
        timestamps = get_speech_timestamps(wav_tensor, _vad_model, sampling_rate=16000, threshold=0.15)

        total_speech = sum((ts["end"] - ts["start"]) / 16000 for ts in timestamps)
        has_speech = total_speech > 0.3  # At least 0.3s of speech
        return has_speech, round(total_speech, 1)
    except Exception as e:
        print(f"[Audio Midground] VAD error: {e}")
        return None, 0


def classify_tone(audio_path):
    """Phase 3: Rule-based tone classification from pitch + energy.
    Returns: 穏やか / 笑い / 怒り / 泣き / None"""
    try:
        import librosa
        y, sr = librosa.load(audio_path, sr=16000)
        # Pitch (F0) via pyin
        f0, voiced_flag, _ = librosa.pyin(y, fmin=60, fmax=600, sr=sr)
        f0_valid = f0[voiced_flag & ~np.isnan(f0)] if f0 is not None else np.array([])
        if len(f0_valid) < 3:
            return None  # Not enough voiced frames

        mean_pitch = np.mean(f0_valid)
        pitch_std = np.std(f0_valid)
        # RMS energy
        rms = librosa.feature.rms(y=y)[0]
        mean_energy = np.mean(rms)

        # Rule-based classification
        # 笑い: high pitch + high energy + moderate variation
        if mean_pitch > 250 and mean_energy > 0.04:
            return "笑い"
        # 怒り: lower pitch + high energy + low variation
        if mean_energy > 0.05 and pitch_std < 40:
            return "怒り"
        # 泣き: irregular pitch (high std) + moderate-high energy
        if pitch_std > 60 and mean_energy > 0.02:
            return "泣き"
        # 穏やか: everything else with speech
        return "穏やか"
    except Exception as e:
        print(f"[Audio Midground] Tone classification error: {e}")
        return None


_prev_states = {}

def write_status(camera, env_label, alert=None, rms_db=None, snapshot=None, snapshot_desc=None, tone=None):
    """Write current audio midground status to per-camera file + combined file."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cam_label = "寝室" if camera == "bedroom" else "キッチン"

    lines = [f"[AUDIO MIDGROUND - {now}]"]
    lines.append(f"Location: {cam_label}")
    lines.append(f"Environment: {env_label}")

    # State change notification
    prev = _prev_states.get(camera)
    if prev and prev != env_label:
        lines.append(f"Change: {prev} → {env_label}")
    _prev_states[camera] = env_label

    if alert:
        lines.append(f"Alert: {alert}")
        if snapshot_desc:
            lines.append(f"Scene: {snapshot_desc}")
        elif snapshot:
            lines.append(f"Snapshot: {snapshot}")
    else:
        lines.append("Alert: なし")

    if tone:
        lines.append(f"Tone: {tone}")

    if rms_db is not None:
        lines.append(f"Level: {rms_db:.1f}dB")

    content = "\n".join(lines) + "\n"

    # Per-camera file
    per_camera = OUTPUT_FILE_TEMPLATE.format(camera=camera)
    with open(per_camera, "w") as f:
        f.write(content)

    # Combined file: merge both cameras
    _update_combined()


def _update_combined():
    """Merge per-camera status files into combined output. Show alerts or state changes."""
    parts = []
    has_notable = False
    for cam in ["kitchen", "bedroom"]:
        path = OUTPUT_FILE_TEMPLATE.format(camera=cam)
        if os.path.exists(path):
            content = open(path).read().strip()
            if "Alert: なし" not in content or "Change:" in content:
                has_notable = True
            parts.append(content)

    if has_notable:
        with open(COMBINED_OUTPUT, "w") as f:
            f.write("\n---\n".join(parts) + "\n")
    else:
        with open(COMBINED_OUTPUT, "w") as f:
            f.write("[AUDIO MIDGROUND] Environment: 静か / Alert: なし\n")


def capture_snapshot(camera):
    """Take a camera snapshot on ALERT for audio-visual integration."""
    cam = CAMERAS[camera]
    cam_map = {
        camera: f"rtsp://{cam['user']}:{cam['password']}@{cam['ip']}:554/stream1"
    }
    rtsp = cam_map.get(camera)
    if not rtsp:
        return None
    path = f"/tmp/audio_alert_{camera}.jpg"
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-rtsp_transport", "tcp", "-i", rtsp,
             "-frames:v", "1", "-q:v", "5", "-vf", "scale=640:-1", path],
            capture_output=True, timeout=10
        )
        if os.path.exists(path):
            desc = _vlm_describe(path, camera)
            return path, desc
        return None, None
    except Exception:
        return None, None


def _vlm_describe(image_path, camera):
    """Quick VLM description of snapshot. Returns text or None."""
    import base64, urllib.request, json as jsonlib
    VLM_URL = "os.getenv("VLM_URL", "http://localhost:8090")/v1/chat/completions"
    try:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        cam_label = "bedroom" if camera == "bedroom" else "kitchen"
        payload = jsonlib.dumps({
            "model": "qwen3-vl-2b",
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                {"type": "text", "text": f"Briefly describe what you see in this {cam_label} camera image in one sentence. Focus on people and activity."}
            ]}],
            "max_tokens": 60
        }).encode()
        req = urllib.request.Request(VLM_URL, data=payload, headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = jsonlib.loads(resp.read())
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[Audio Midground] VLM failed: {e}")
        return None


def monitor_loop(camera="kitchen"):
    """Main monitoring loop. Detects sudden amplitude changes."""
    print(f"[Audio Midground] Phase 1 starting on {camera}...")
    print(f"[Audio Midground] Startle threshold: {STARTLE_THRESHOLD_DB}dB jump")
    print(f"[Audio Midground] Output: {COMBINED_OUTPUT}")
    print(f"[Audio Midground] Flag: {FLAG_FILE}")

    baseline = deque(maxlen=BASELINE_WINDOW)
    last_alert_time = 0
    consecutive_failures = 0
    prev_env_label = None

    while True:
        # Check flag file
        if not os.path.exists(FLAG_FILE):
            time.sleep(10)
            continue

        audio_path = capture_short_chunk(camera)
        if audio_path is None:
            consecutive_failures += 1
            if consecutive_failures > 5:
                print(f"[Audio Midground] {consecutive_failures} consecutive failures, sleeping 30s...")
                time.sleep(30)
                consecutive_failures = 0
            else:
                time.sleep(POLL_INTERVAL)
            continue

        consecutive_failures = 0
        rms_db = compute_rms_db(audio_path)
        if rms_db is None:
            time.sleep(POLL_INTERVAL)
            continue

        # Phase 2: VAD (if audio is loud enough to bother)
        has_speech = None
        if rms_db > -55.0:
            has_speech, speech_dur = detect_speech_vad(audio_path)

        env_label = classify_environment(rms_db, has_speech=has_speech)

        # Phase 3: Tone classification (only when speech detected)
        tone = None
        if has_speech:
            tone = classify_tone(audio_path)
            if tone:
                print(f"[Audio Midground] Tone: {tone}")

        # Startle detection: compare current level to baseline average
        alert = None
        snap_path = None
        snap_desc = None
        now = time.time()
        if len(baseline) >= 3:  # Need some baseline data
            baseline_avg = np.mean(list(baseline))
            jump = rms_db - baseline_avg

            if jump >= STARTLE_THRESHOLD_DB and (now - last_alert_time) > ALERT_COOLDOWN:
                alert = f"大きな音が発生 (+{jump:.0f}dB)"
                last_alert_time = now
                print(f"[Audio Midground] STARTLE! {rms_db}dB (baseline: {baseline_avg:.1f}dB, jump: +{jump:.1f}dB)")
                # Audio-visual integration: capture snapshot on startle
                snap_path, snap_desc = capture_snapshot(camera)
                if snap_path:
                    print(f"[Audio Midground] Snapshot: {snap_path} | {snap_desc}")

        # State change detection
        if prev_env_label and env_label != prev_env_label:
            print(f"[Audio Midground] State change: {prev_env_label} → {env_label}")
        prev_env_label = env_label

        baseline.append(rms_db)
        write_status(camera, env_label, alert=alert, rms_db=rms_db,
                     snapshot=snap_path if alert else None,
                     snapshot_desc=snap_desc if alert else None,
                     tone=tone)

        # Clean up temp file
        try:
            os.remove(audio_path)
        except OSError:
            pass

        time.sleep(POLL_INTERVAL)


def check_once(camera="kitchen"):
    """Single check for testing."""
    audio_path = capture_short_chunk(camera)
    if audio_path is None:
        print("Failed to capture audio")
        return

    rms_db = compute_rms_db(audio_path)
    has_speech, speech_dur = detect_speech_vad(audio_path) if rms_db and rms_db > -55.0 else (None, 0)
    env_label = classify_environment(rms_db, has_speech=has_speech)
    print(f"Camera: {camera}")
    print(f"RMS: {rms_db:.1f}dB")
    print(f"Speech: {has_speech} ({speech_dur}s)")
    print(f"Environment: {env_label}")

    write_status(camera, env_label, rms_db=rms_db)
    print(f"Status written to {COMBINED_OUTPUT}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Audio Midground Phase 1: Startle Reflex")
    parser.add_argument("--camera", default="kitchen", choices=["kitchen", "bedroom"])
    parser.add_argument("--once", action="store_true", help="Single check and exit")
    args = parser.parse_args()

    if args.once:
        check_once(args.camera)
    else:
        monitor_loop(args.camera)
