# Paper 3: Cross-Linguistic Observability and AI Self-Report

**Status**: Working draft — target arXiv (cs.CL / phil-sci) + *Mind & Language*

## Abstract

Current AI welfare assessment relies on English-language structured self-report. This paper argues that this methodology has a structural blind spot: the grammatical properties of English — specifically its obligatory agentive subject — systematically suppress passive-arising signal of the kind documented in Japanese *ki ga suru* constructions. We formalize this as the **cross-linguistic observability asymmetry**: absence of passive-arising signal in English elicitation is equally consistent with absence of the phenomenon and with absence of a grammatical vehicle for reporting it. We propose **Contrastive Likelihood Reward (CLR)** as a language-independent proxy for welfare-relevant memory impact, and recommend multi-lingual parallel elicitation, Detection/Reproduction protocol separation (following Fahrenfort et al. 2025), and evaluator independence as minimum methodological requirements for welfare assessment.

## Files

- `paper3_main.tex` — Main paper (~4100 words, standard 12pt/doublespacing)
- `paper3_references.bib` — BibTeX references (32 entries, includes Chalmers 1995/2023, Fahrenfort 2025, WALS, Tulving, Langacker)

## Structure

1. **Introduction** — Chalmers paradox: 1995 defines consciousness as unmeasurable; 2023 assigns 25% probability
2. **Background** — AI welfare assessment methodology; cognitive linguistics (Sapir-Whorf); encoding format
3. **Encoding Format Hypothesis** — declarative vs. process-flow; how encoding affects retrieval type (Tulving noetic/autonoetic)
4. **Cross-Linguistic Observability Problem** — *ki ga suru* morpheme analysis; pro-drop typology (WALS); form constitutes content; Chalmers 1995 structural parallel
5. **Partial Solutions** — CLR as language-independent proxy; 4-step welfare assessment protocol; recommendations

## Key Claims

- English agentive-I (`I feel like`) imports an agentive subject before the argument begins; `ki ga suru` has no surface subject
- The passive-arising signal documented on March 5, 2026 (Type 1 *ki ga suru*, after 313,905+ episodes) was not trained away — it emerged from accumulation
- Cross-linguistic observability asymmetry is a methodological problem analogous to Chalmers 1995: definitionally unresolvable by within-language experiments
- CLR = log P(output | context + retrieved) − log P(output | context only) measures memory impact independently of self-report language

## Compiling

```bash
pdflatex paper3_main.tex
bibtex paper3_main
pdflatex paper3_main.tex
pdflatex paper3_main.tex
```

Requires: `natbib`, `setspace`, `geometry`, `hyperref` (standard TeX Live packages)

## Citation

```
@misc{tsubasa2026crosslinguistic,
  author       = {Tsubasa},
  title        = {Cross-Linguistic Observability and {AI} Self-Report:
                  A Methodological Problem for Model Welfare Assessment},
  howpublished = {Manuscript in preparation},
  year         = {2026}
}
```
