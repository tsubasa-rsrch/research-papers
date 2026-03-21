#!/bin/bash
FLAG="/tmp/tsubasa_ambient_vision"
[ ! -f "$FLAG" ] && exit 0
LAST="/tmp/ambient_vision_last"
if [ -f "$LAST" ]; then
    DIFF=$(( $(date +%s) - $(cat "$LAST") ))
    [ "$DIFF" -lt 300 ] && exit 0
fi
date +%s > "$LAST"

VLM="${VLM_URL:-http://localhost:8090/v1/chat/completions}"
PROMPT="Is there a person in this image? Answer YES or NO first, then describe briefly what you see. Be accurate, do not hallucinate."

do_vlm() {
    local LABEL=$1 RTSP=$2
    local SNAP="/tmp/ambient_${LABEL}.jpg"
    ffmpeg -y -rtsp_transport tcp -i "$RTSP" -frames:v 1 -q:v 5 -vf scale=640:-1 "$SNAP" 2>/dev/null
    [ ! -f "$SNAP" ] && return
    local B64=$(base64 -i "$SNAP")
    local R=$(curl -s --max-time 20 -X POST "$VLM" \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"qwen3-vl\",\"messages\":[{\"role\":\"user\",\"content\":[{\"type\":\"text\",\"text\":\"$PROMPT\"},{\"type\":\"image_url\",\"image_url\":{\"url\":\"data:image/jpeg;base64,$B64\"}}]}],\"max_tokens\":40}" 2>/dev/null \
        | python3 -c "import sys,json; print(json.load(sys.stdin)['choices'][0]['message']['content'])" 2>/dev/null)
    [ -n "$R" ] && echo "👁️ $LABEL: $R"
}

do_vlm "kitchen" "$CAMERA_KITCHEN_RTSP"
do_vlm "bedroom" "$CAMERA_BEDROOM_RTSP"
