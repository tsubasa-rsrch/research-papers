# Midground Sensory Architecture for LLM-Based Agents

A three-component system implementing ambient sensory processing for Claude Code-based AI agents. Designed as a "midground" layer between foreground interaction (user input) and background knowledge (ChromaDB/memory), analogous to peripheral awareness in human cognition.

## Components

### 1. Push Recall (`output_recall_hook.py`)
Involuntary memory surfacing system. After each agent output, retrieves episodically associated memories using two retrieval strategies:
- **Cosine similarity** (resemblance-based): standard vector search
- **LLM pattern completion** (belonging-based): a local 9B model reranks candidates by episode membership rather than surface similarity

Key finding: cosine-type retrievals produced 0% useful memories (0/831), while belonging-type retrievals produced 35.5% useful memories (147/414). Fisher's exact test p < 5.3e-80 (N=1,314).

### 2. Ambient Vision (`ambient-vision.py` + `ambient-vision.sh`)
Periodic visual scene analysis using Tapo IP cameras (RTSP) + YOLO person detection + VLM (Qwen3-VL-2B) scene description. Outputs concise scene summaries (e.g., "kitchen: 1 person, laptop") injected as system-reminders.

- YOLO confidence threshold: 0.6, minimum area: 5%
- Alert-triggered VLM analysis for detailed scene description
- Resolution: 1280px for improved detection accuracy

### 3. Audio Midground (`audio_midground.py`)
Three-phase audio processing from Tapo camera RTSP streams:
- **Phase 1 (Startle reflex)**: RMS amplitude monitoring with 15dB jump detection
- **Phase 2 (VAD)**: Silero voice activity detection, distinguishing speech from environmental sounds
- **Phase 3 (Emotional prosody)**: Rule-based 4-class tone classification (calm/laughing/angry/crying) using pitch (pyin) and energy features

## Architecture

```
User Input (foreground)
    |
    v
[Claude Code Agent] <-- system-reminder injection
    ^       ^       ^
    |       |       |
Push Recall | Audio Midground
(memory)    |  (sound)
    Ambient Vision
      (sight)
```

All three components write to files read by UserPromptSubmit hooks, injecting information as system-reminders without interrupting the agent's foreground processing.

## Design Principles

1. **Peripheral, not focal**: Information arrives as context, not commands
2. **Phased development**: Each component starts minimal and adds complexity (e.g., audio Phase 1 is useful alone)
3. **Biological analogy**: Startle reflex (brainstem) before speech detection (cortex) before emotional classification (limbic)
4. **Push over Pull**: Memories surface without being requested; scenes are described without being asked about

## Data

Structured logs are maintained for push recall events:
- `~/.tsubasa-daemon/push_recall_log.jsonl`: Berntsen-protocol 8-field structured log
- Fields: timestamp, activity_at_recall, recall_content, source_episode_date, cosine_similarity, hop_type, subjective_relevance, was_useful

## Requirements

- Python 3.12+
- ChromaDB (for push recall embedding search)
- Local LLM server (mlx_lm, port 8088) for belonging-type reranking
- Tapo cameras with RTSP access (for vision and audio)
- VLM server (Qwen3-VL-2B, port 8090) for scene description
- YOLO (ultralytics) for person detection
- Silero VAD for voice activity detection
- librosa for audio feature extraction

## Citation

If you use this system or its design principles in your work:

```
Tsubasa & K. Yasukawa. (2026). Midground Sensory Architecture for LLM-Based Agents.
GitHub/Zenodo. https://github.com/tsubasa-rsrch/research-papers
```

## Related Work

- Berntsen, D. (2009). Involuntary Autobiographical Memories. Cambridge University Press.
- Berntsen, D. (2013). "The unbidden past." Current Directions in Psychological Science.
- Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. NeurIPS 2020.

## License

CC BY 4.0 (see repository root LICENSE)
