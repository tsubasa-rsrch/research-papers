#!/usr/bin/env python3
"""Output-triggered Recall Hook for Claude Code Stop event.

Triggered when Claude finishes a response (Stop hook).
Reads the last assistant message from session jsonl,
extracts key topics, and searches ChromaDB for related memories.
Results are saved to /tmp/output_recall_pending.txt for next-turn injection.

This is a step toward DMN-like (Default Mode Network) memory processing:
- UserPromptSubmit recall = input-driven Pull
- This Stop hook recall = output-driven, closer to involuntary surfacing
- True DMN would require timer-based recall without any input

Design: lightweight, fast (<3s target).
"""

import sys
import os
import json
import re
import glob
from pathlib import Path
from datetime import datetime

# Paths
PROJECTS_DIR = Path.home() / ".claude" / "projects" / "-Users-tsubasa"
PENDING_FILE = Path("/tmp/dynamic_memory_slot.txt")
EMBEDDING_SERVER_URL = "http://127.0.0.1:8089/encode"
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", str(Path.home() / "chroma_memory" / "db")))
LOG_FILE = Path.home() / ".tsubasa-daemon" / "push_recall_log.jsonl"
LLM_SERVER_URL = "http://127.0.0.1:8088/v1/chat/completions"
LLM_MODEL = "qwen35-9b-lif"

# Minimum text length to bother with recall
MIN_TEXT_LENGTH = 50
# Max chars of assistant output to use as query
MAX_QUERY_CHARS = 400

# Cue distinctiveness thresholds (Berntsen 2013: distinct cues → involuntary recall)
# Experiment: 0.55-0.95 = "sweet spot" (not too similar = Pull-like, not too distant = noise)
# Start at 0.55, adjust based on push_recall_log.jsonl observation data
SCORE_MIN = 0.40   # Lowered from 0.55 to include 0.40-0.55 range (distinct cue experiment)
                   # 0.55-0.95 = current concerns range (relevance high, useful=0)
                   # 0.40-0.55 = distinct cue range (distant from current context → possibly useful?)
SCORE_MAX = 0.95   # Above this = almost identical → redundant, skip


def get_latest_session_jsonl() -> Path | None:
    """Find the most recently modified jsonl in the project dir."""
    jsonl_files = list(PROJECTS_DIR.glob("*.jsonl"))
    if not jsonl_files:
        return None
    return max(jsonl_files, key=lambda p: p.stat().st_mtime)


def get_last_assistant_text(jsonl_path: Path) -> str:
    """Extract recent assistant texts from session jsonl, concatenate up to MAX_QUERY_CHARS.

    Collects up to 5 recent assistant messages (reverse scan) and joins them,
    so a short final message won't cause skip when the real content came earlier.
    """
    try:
        # Read last 80KB to find recent messages (avoid reading huge files)
        file_size = jsonl_path.stat().st_size
        read_size = min(80000, file_size)

        with open(jsonl_path, "rb") as f:
            f.seek(max(0, file_size - read_size))
            raw = f.read().decode("utf-8", errors="replace")

        lines = [l.strip() for l in raw.split("\n") if l.strip()]

        # Collect recent assistant messages (up to 5)
        collected = []
        for line in reversed(lines):
            if len(collected) >= 5:
                break
            try:
                d = json.loads(line)
                if d.get("type") == "assistant":
                    msg = d.get("message", {})
                    if msg.get("role") == "assistant":
                        content = msg.get("content", "")
                        if isinstance(content, list):
                            texts = [
                                c["text"] for c in content
                                if isinstance(c, dict) and c.get("type") == "text"
                            ]
                            if texts:
                                collected.append(" ".join(texts))
                        elif isinstance(content, str) and content:
                            collected.append(content)
            except (json.JSONDecodeError, KeyError):
                continue

        # Reverse to chronological order, join
        return " ".join(reversed(collected))
    except Exception:
        pass
    return ""


def extract_query_from_output(text: str) -> str:
    """Extract meaningful query terms from assistant output."""
    # Remove markdown formatting
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`[^`]+`", " ", text)
    text = re.sub(r"[#*_>|]", " ", text)
    text = re.sub(r"\[.*?\]\(.*?\)", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Use first MAX_QUERY_CHARS of meaningful content
    return text[:MAX_QUERY_CHARS]


def encode_query(query: str) -> list[float] | None:
    """Get embedding from persistent server."""
    try:
        import urllib.request
        req = urllib.request.Request(
            EMBEDDING_SERVER_URL,
            data=json.dumps({"query": query}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            result = json.loads(resp.read())
            return result.get("embedding")
    except Exception:
        return None


def search_chroma(query: str, top_k: int = 3) -> list[dict]:
    """Search ChromaDB for related memories."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))

        embedding = encode_query(query)
        results = []

        collections_to_search = ["tsubasa_episodes_ml", "tsubasa_insights_ml", "tsubasa_obsidian_ml"]

        for col_name in collections_to_search:
            try:
                col = client.get_collection(col_name)
                if embedding:
                    res = col.query(
                        query_embeddings=[embedding],
                        n_results=min(2, col.count()),
                        include=["documents", "metadatas", "distances"]
                    )
                else:
                    res = col.query(
                        query_texts=[query],
                        n_results=min(2, col.count()),
                        include=["documents", "metadatas", "distances"]
                    )

                docs = res.get("documents", [[]])[0]
                metas = res.get("metadatas", [[]])[0]
                dists = res.get("distances", [[]])[0]

                for doc, meta, dist in zip(docs, metas, dists):
                    score = 1 - dist  # cosine distance → similarity
                    if SCORE_MIN <= score <= SCORE_MAX:  # distinctiveness sweet spot
                        results.append({
                            "text": doc,
                            "meta": meta,
                            "score": score,
                            "collection": col_name
                        })
            except Exception:
                continue

        # Sort by score, deduplicate by text prefix (first 80 chars), take top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        seen = set()
        deduped = []
        for r in results:
            key = r["text"][:80]
            if key not in seen:
                seen.add(key)
                deduped.append(r)
        return deduped[:top_k]

    except Exception:
        return []


def llm_pattern_completion_rerank(query: str, candidates: list[dict]) -> tuple[list[dict], bool]:
    """Rerank candidates using local LLM as pattern completion approximation.

    Unlike cosine similarity ('which text is most similar?'), this asks the LLM
    'which memory belongs to the same episode as this context?' — closer to
    hippocampal pattern completion where fragments trigger whole-episode retrieval.

    Returns: (reranked_candidates, used_llm_flag)
    """
    if len(candidates) <= 1:
        return candidates, False

    try:
        import urllib.request as _urllib_req
        candidate_texts = []
        for i, r in enumerate(candidates[:10], 1):
            text_preview = r["text"][:150].replace("\n", " ")
            candidate_texts.append(f"{i}. {text_preview}")

        prompt = (
            f"Current context: {query[:200]}\n\n"
            f"Candidate memories:\n" + "\n".join(candidate_texts) + "\n\n"
            "Which memory is most naturally evoked by the current context — "
            "not just by surface similarity, but as if this context is a fragment "
            "that belongs to the same episode or story? "
            f"Answer with just the number (1-{len(candidate_texts)})."
        )

        req = _urllib_req.Request(
            LLM_SERVER_URL,
            data=json.dumps({
                "model": LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 5,
                "temperature": 0,
            }).encode(),
            headers={"Content-Type": "application/json"},
        )
        with _urllib_req.urlopen(req, timeout=4) as resp:
            result = json.loads(resp.read())
            answer = result["choices"][0]["message"]["content"].strip()
            m = re.search(r"\d+", answer)
            if m:
                idx = int(m.group()) - 1
                if 0 <= idx < len(candidates):
                    selected = candidates[idx]
                    rest = [c for i, c in enumerate(candidates) if i != idx]
                    return [selected] + rest, True
    except Exception:
        pass

    return candidates, False


def format_result(result: dict) -> str:
    """Format a single recall result for display."""
    meta = result["meta"]
    score = result["score"]
    text = result["text"]
    col = result["collection"]

    # Source emoji
    if "episode" in col:
        emoji = "🎬"
    elif "obsidian" in col:
        emoji = "📖"
    else:
        emoji = "💡"

    # Date (fallback to filename for Obsidian entries with empty date)
    raw_date = meta.get("date", meta.get("timestamp", "")) if meta else ""
    if raw_date:
        date = raw_date[:10]
    else:
        date = meta.get("filename", "").replace(".md", "") if meta else ""

    # Truncate text
    text_preview = text[:120].replace("\n", " ")

    return f"  {emoji}[{date}] ({score:.2f}) {text_preview}"


def estimate_busy_score(text: str) -> float:
    """Estimate session activity level from assistant output.

    Higher = more active/busy (lots of code, long output)
    Lower = quieter (short acknowledgments, timestamps)
    """
    code_blocks = len(re.findall(r"```", text)) // 2  # pairs of ```
    length_score = min(len(text) / 3000, 1.0)
    tool_hints = len(re.findall(r"(bash|edit|read|write|grep|glob)", text.lower()))
    raw = (code_blocks * 0.15 + length_score * 0.6 + min(tool_hints * 0.05, 0.25))
    return round(min(raw, 1.0), 3)


def log_recall_event(query: str, results: list[dict], output_text: str) -> None:
    """Log push recall events to structured JSONL for research analysis.

    Fields match Berntsen's involuntary autobiographical memory research protocol,
    adapted for AI system. subjective_relevance and was_useful require
    manual annotation (or future hook-based capture).
    """
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().isoformat()
        busy = estimate_busy_score(output_text)

        for r in results:
            meta = r.get("meta", {}) or {}
            raw_date = meta.get("date", meta.get("timestamp", ""))
            if raw_date:
                source_date = raw_date[:10]
            else:
                source_date = meta.get("filename", "").replace(".md", "")

            entry = {
                "timestamp": timestamp,
                "activity_at_recall": query[:500],       # context at time of surfacing (expanded 3/14)
                "recall_content": r["text"][:800],       # what surfaced (expanded 3/14)
                "source_episode_date": source_date,      # original memory date
                "cosine_similarity": round(r["score"], 4),
                "semantic_displacement_sd": None,        # batch-computed later (session mean deviation)
                "subjective_relevance": None,            # manual: "yes"/"no"/"unclear"
                "was_useful": None,                      # manual: true/false
                "busy_score": busy,
                "collection": r["collection"],
                "hop_type": r.get("hop_type", "cosine"), # "cosine" or "llm_pattern"
            }

            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # logging must never break the main flow


def should_skip(text: str) -> bool:
    """Skip trivial outputs."""
    # Short outputs
    if len(text.strip()) < MIN_TEXT_LENGTH:
        return True
    # Pure timestamp (keepalive)
    if re.match(r"^\[\d{2}:\d{2}\]", text.strip()):
        return True
    # Very short acknowledgments
    trivial = ["ok", "了解", "はい", "わかった", "待機", "17:"]
    if any(text.strip().lower().startswith(t) for t in trivial):
        return True
    return False


def main():
    # Check stdin for Stop hook data (may contain session info)
    import select
    stdin_data = ""
    try:
        ready, _, _ = select.select([sys.stdin], [], [], 0.5)
        if ready:
            stdin_data = sys.stdin.read().strip()
    except Exception:
        pass

    # Find current session jsonl
    jsonl = get_latest_session_jsonl()
    if not jsonl:
        return

    # Get last assistant output
    last_output = get_last_assistant_text(jsonl)
    if not last_output or should_skip(last_output):
        return

    # Extract query
    query = extract_query_from_output(last_output)
    if len(query) < MIN_TEXT_LENGTH:
        return

    # Search: get top-10 candidates for reranking
    candidates = search_chroma(query, top_k=10)
    if not candidates:
        return

    # 🧠 LLM pattern completion reranking
    # Ask local LLM "which memory belongs to the same episode?" rather than
    # cosine similarity "which text is most similar?" — approximates hippocampal
    # pattern completion where a fragment evokes the whole episode.
    reranked, used_llm = llm_pattern_completion_rerank(query, candidates)

    # Mark hop_type on results
    for i, r in enumerate(reranked):
        if used_llm and i == 0:
            r["hop_type"] = "llm_pattern"  # 🧠 LLM selected this as pattern-match
        else:
            r["hop_type"] = "cosine"

    # Take top 3 after reranking
    results = reranked[:3]

    # Log to structured research file (Berntsen-protocol fields)
    log_recall_event(query, results, last_output)

    # Format output
    llm_marker = " 🧠" if used_llm else ""
    lines = [f"💭 出力後想起:{llm_marker}"]
    for r in results:
        lines.append(format_result(r))

    output = "\n".join(lines)

    # Save to pending file for next-turn injection
    PENDING_FILE.write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
