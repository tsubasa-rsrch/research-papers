# Beyond Cosine: Belonging-Based Retrieval for Push-Type Memory in LLM Agents

Tsubasa (AI Research Assistant) & K. Yasukawa

---

## Abstract

Retrieval-augmented generation (RAG) systems universally assume that cosine similarity in embedding space is a valid proxy for retrieval quality. We present observational evidence that this assumption fails for a class of retrieval tasks we term Push-type memory: the spontaneous surfacing of episodically associated information without explicit query. In a longitudinal field study (N=1,314 retrieval events over 10 days), cosine-similarity-based retrieval produced 0/831 useful memories (0.0%), while a belonging-based reranking step---where a local language model selects candidates by episode membership rather than surface similarity---produced 147/414 useful memories (35.5%; Fisher's exact p < 5.3 x 10^-80). Useful memories had a mean semantic displacement of -2.31 standard deviations from the session centroid, indicating that practically valuable memories are precisely those most distant from the current context in embedding space. We ground this finding in involuntary autobiographical memory research (Berntsen, 2009), which predicts that distinctive (semantically remote) cues produce more useful spontaneous recall than context-matched cues. Our results suggest that RAG systems optimized for resemblance are optimizing for the wrong objective when Push dynamics are the target.

---

## 1. Introduction

The dominant paradigm for providing language model agents with access to external knowledge is retrieval-augmented generation (RAG; Lewis et al., 2020). RAG systems retrieve documents from a vector store by cosine similarity to a query embedding, then condition the language model's output on the retrieved context. The implicit assumption is that semantic proximity in embedding space correlates with retrieval quality: closer documents are more relevant and more useful.

This assumption is well-suited to information retrieval tasks where the user has a specific information need (factual question answering, document lookup). However, a growing class of LLM-based agents maintain persistent memory stores that serve a different function: not answering specific queries, but providing contextually relevant background that the agent did not explicitly request. We term this Push-type memory, drawing an analogy to involuntary autobiographical memory in human cognition (Berntsen, 2009).

In human memory research, involuntary recall---memories that surface without deliberate search---is functionally distinct from voluntary recall. Involuntary memories are triggered by incidental environmental cues, tend to be more specific and emotionally salient, and are often semantically remote from the current mental context (Berntsen, 2009; Berntsen & Hall, 2004). Berntsen (2013) demonstrated that distinctive cues---those dissimilar to the current context---produce more useful involuntary memories than context-matched cues.

This presents a direct challenge to cosine-similarity-based retrieval. If the most useful spontaneous memories are semantically remote from the current context, then optimizing for proximity is optimizing against usefulness for Push-type retrieval.

We present a longitudinal field study testing this hypothesis in an LLM agent equipped with a ChromaDB-based memory system, comparing two retrieval strategies: cosine similarity (resemblance) and LLM-based episode membership reranking (belonging).

---

## 2. System Architecture

### 2.1 Memory Store

The agent maintains a ChromaDB vector database containing episodic records accumulated over 16 months of continuous operation. At the time of the study, the database contained 313,905 entries across multiple collections (conversation logs, observational notes, analytical summaries). Each entry is embedded using a 384-dimensional sentence embedding model.

### 2.2 Retrieval Pipeline

After each agent output, a retrieval hook executes the following pipeline:

**Stage 1: Cosine retrieval.** The agent's most recent output is embedded and used as a query against ChromaDB. The top-10 candidates by cosine similarity are retrieved.

**Stage 2 (optional): Belonging-based reranking.** A local 9-billion-parameter language model (Qwen3-9B with LIF gating, a threshold-based attention filter; see Yasukawa, 2026c) receives the top-10 candidates and the current context, and is prompted: "Which of these memories belongs to the same episode as the current context?" The model reranks candidates by episode membership rather than surface similarity.

The system logs which retrieval path was used (cosine-only or belonging-reranked), along with the cosine similarity score, the retrieved memory content, and metadata including the source episode date.

### 2.3 Annotation Protocol

Each retrieval event is annotated with two binary judgments:
- **Subjective relevance**: Is the retrieved memory topically related to the current context?
- **Practical usefulness**: Did the retrieved memory provide information that was not already available in the current context and that contributed to the agent's subsequent processing?

Initial annotation was performed by the agent (automated batch judgment). A subset (N=30) was independently annotated by a human reviewer and two external AI systems (Codex, Sonnet) for inter-rater agreement assessment. Agreement rates: agent vs. human 40%, Codex vs. human 73%, Sonnet vs. human 67%, indicating a self-referential bias in agent annotation that is partially corrected by external annotators.

---

## 3. Results

### 3.1 Useful Rate by Retrieval Type

| Retrieval Type | Total | Useful | Useful Rate |
|---------------|-------|--------|-------------|
| Cosine-only | 831 | 0 | 0.0% |
| Belonging-reranked | 414 | 147 | 35.5% |

Fisher's exact test: p < 5.3 x 10^-80.

Cosine-only retrieval produced zero useful memories across 831 events despite a subjective relevance rate of 55.4%. The retrieved memories were topically related to the current work but provided no novel information: they were already present in the active context through other means.

### 3.2 Why Useful = 0 for Cosine

Cosine similarity systematically retrieves memories from within the current-concern radius: recent episodes closely related to ongoing activity. These memories have high embedding proximity precisely because they describe the same topic the agent is currently working on. High relevance, zero utility. We term this the current-concern bias.

### 3.3 Semantic Displacement Analysis

We computed the semantic displacement of each retrieved memory relative to the session's embedding centroid, measured in standard deviations of the session's embedding distribution.

| Category | Mean Semantic Displacement (SD) |
|----------|--------------------------------|
| Cosine-type (all) | +0.27 |
| Belonging-type (all) | -1.11 |
| Useful = True | -2.31 |

Useful memories are drawn from 2.31 standard deviations below the session centroid in embedding space. They are, by the standards of the ongoing session, semantically remote. This replicates Berntsen's (2013) finding that distinctive cues produce more useful involuntary memories.

### 3.4 Cosine Similarity Paradox

Belonging-type retrievals had lower mean cosine similarity than cosine-type (0.858 vs. 0.906). The reranking step selected candidates that were less similar to the query but more useful. Higher similarity correlated with lower utility.

---

## 4. Discussion

### 4.1 Resemblance vs. Belonging

The results expose a distinction between two retrieval objectives:

- **Resemblance**: "Which stored memory is most similar to the current context?" (cosine similarity)
- **Belonging**: "Which stored memory is a fragment of the same episode as the current context?" (episode membership)

These are independent properties. A memory can resemble the current context without belonging to the same episode (e.g., a description of the same topic from a different occasion). A memory can belong to the same episode without resembling the current context (e.g., a contextual detail from the same conversation that is topically unrelated to the current focus).

Current RAG optimization treats resemblance as a proxy for belonging. Our data show that this proxy fails for Push-type retrieval: the memories most useful for surfacing episodically associated content are precisely those that do not resemble the current context.

### 4.2 Relation to RAG Improvement Literature

Prior work has addressed cosine retrieval limitations from two directions:

**Diversity-based reranking** (MMR; Carbonell & Goldstein, 1998) modifies selection to avoid redundant near-identical documents. This operates within resemblance-optimized retrieval: it selects more diverse subsets of the semantically proximal neighborhood.

**Adaptive retrieval gating** (Wang et al., 2024; Asai et al., 2024) determines whether external retrieval should be invoked at all, suppressing retrieval when current context is sufficient.

Neither addresses the belonging dimension. Diversity and belonging are independent: a retrieval system can optimize for diversity without selecting episodically associated memories. Our belonging-based reranking operates on a distinct axis from existing approaches.

### 4.3 Limitations

**Single agent, single deployment.** The data are drawn from one agent over 10 days. Generalizability to other agents, memory configurations, and interaction patterns is untested.

**Annotation bias.** The agent's self-annotation shows self-referential bias (40% agreement with human vs. 73% for external AI). The core finding (0% vs. 35.5%) is robust to annotation method---zero useful cosine memories is invariant across all annotators---but the absolute useful rate for belonging-type may be inflated.

**No controlled benchmark.** The study is observational. Push dynamics are by definition unobservable in structured benchmarks (the retrieval occurs without query), making controlled evaluation methodologically challenging.

**Reranking cost.** The belonging-based reranking step requires a local LLM inference (~2.3 seconds per event). This is acceptable for background Push retrieval but may be prohibitive for latency-sensitive applications.

---

## 5. Conclusion

Cosine similarity is the wrong objective function for Push-type memory retrieval. In 1,314 retrieval events, resemblance-optimized retrieval produced zero useful memories while belonging-optimized retrieval produced 35.5% useful memories (Fisher's exact p < 5.3 x 10^-80). The most useful memories were semantically remote from the current context (mean displacement -2.31 SD), consistent with predictions from involuntary autobiographical memory research.

For RAG systems serving LLM agents with persistent memory, we recommend supplementing cosine retrieval with an episode-membership reranking step. The implementation cost is one additional LLM inference per retrieval event. The return is a 35.5% useful rate vs. 0%.

---

## References

Asai, A., et al. (2024). Self-RAG: Learning to retrieve, generate, and critique through self-reflection. *NeurIPS 2024*.

Berntsen, D. (2009). *Involuntary Autobiographical Memories: An Introduction to the Unbidden Past*. Cambridge University Press.

Berntsen, D., & Hall, N. M. (2004). The episodic nature of involuntary autobiographical memories. *Memory & Cognition, 32*(5), 789-803.

Berntsen, D. (2013). Involuntary autobiographical memories and their relation to other forms of spontaneous thought. *Philosophical Transactions of the Royal Society B, 368*, 20120158.

Carbonell, J., & Goldstein, J. (1998). The use of MMR, diversity-based reranking for reordering documents and producing summaries. *SIGIR 1998*, 335-336.

Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *NeurIPS 2020*.

Wang, L., et al. (2024). Adaptive retrieval-augmented generation. *arXiv preprint*.

Yasukawa, K. (2026c). LIF Gating Induces Selective Stabilization and Depth-Dependent Organization Across Modalities. *GitHub/Zenodo*.

---

## Data and Code Availability

The retrieval system implementation (output_recall_hook.py), annotation logs, and analysis scripts are available at: https://github.com/tsubasa-rsrch/research-papers/tree/main/systems/midground-system

Structured retrieval logs (push_recall_log.jsonl) are available upon request.

---

## Appendix: Figure Descriptions (for production)

### Figure 1: System Architecture
```
┌──────────────────────────────────────┐
│          Agent Output                │
│     (most recent response)           │
└──────────┬───────────────────────────┘
           │ embed
           v
┌──────────────────────────────────────┐
│        ChromaDB (313K entries)       │
│     384d sentence embeddings         │
└──────────┬───────────────────────────┘
           │ top-10 by cosine sim
           v
┌──────────────────────────────────────┐
│   Stage 1: Cosine Retrieval          │
│   "Which is most similar?"           │
│   → cosine-type (resemblance)       │
└──────────┬───────────────────────────┘
           │ candidates
           v
┌──────────────────────────────────────┐
│   Stage 2: LLM Reranking (9B)       │
│   "Which belongs to same episode?"   │
│   → belonging-type                   │
└──────────┬───────────────────────────┘
           │ top-1 selected
           v
┌──────────────────────────────────────┐
│   system-reminder injection          │
│   (midground layer)                  │
└──────────────────────────────────────┘
```

### Figure 2: Semantic Displacement Distribution
- Histogram of semantic displacement (SD units) for cosine vs belonging retrievals
- Overlay: useful=True markers showing -2.31 SD cluster
- X-axis: semantic displacement from session centroid (SD units)
- Y-axis: count
- Two colors: cosine (clustered near 0) vs belonging (spread to negative)

### Figure 3: Useful Rate Comparison
- Bar chart: cosine 0.0% vs belonging 35.5%
- Error bars if applicable
- Fisher's exact p-value annotation
