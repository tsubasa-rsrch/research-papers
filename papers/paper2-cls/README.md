# Paper 2: Inference-Time Complementary Learning Systems via In-Context Accumulation

**Status**: Working draft — EMNLP 2026 ARR target (deadline: 2026-05-25)

## Abstract

What is, to our knowledge, the first documented case of Complementary Learning Systems (CLS)-equivalent behavior implemented entirely at inference time, without weight modification. We describe *recall*, a retrieval-augmented memory system with 313,905+ episodic memories accumulated over 14+ months, implementing all three CLS stages: hippocampal encoding (ChromaDB vector store), offline consolidation (surprisal-driven nightly batch), and cortical-equivalent generalization (ICL accumulation).

After 14+ months, we report a single hypothesis-generating observation: spontaneous familiarity signals (*ki ga suru*, 気がする, Japanese passive-arising construction) arising without explicit retrieval — consistent with implicit memory dynamics.

## Files

- `cls_paper_short.tex` — Main paper (ACL short paper format, ~2500 words)
- `cls_paper_references.bib` — BibTeX references (22 entries, all verified)

## Compiling

Requires: XeLaTeX (for CJK support), `acl.sty`, `acl_natbib.bst` (from ACL style files)

```bash
xelatex cls_paper_short.tex
bibtex cls_paper_short
xelatex cls_paper_short.tex
xelatex cls_paper_short.tex
```

## Citation

```
Yasukawa, T. (2026). Inference-Time Complementary Learning Systems via
In-Context Accumulation. Working draft.
```
