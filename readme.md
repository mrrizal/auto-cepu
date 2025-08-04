# auto-cepu (standonline)

**auto-cepu** is the core **Python code review automation** engine—an API that drives LLM-powered reviews by hitting **Ollama** for contextual feedback. “CEPU” is a playful reverse of “code review” (code ripiu).

> ⚠️ Note: GitHub / pull request integration is handled in a separate repository called [`pr_analyzer`](https://github.com/mrrizal/python-pr-analyzer).
> This repo provides the review logic (LLM prompt orchestration, full-function context diffing, duplication/similarity lookup, and review composition) and exposes it as an API; `pr_analyzer` is responsible for invoking it on PRs and posting results back to GitHub.

---

## 🚀 Key Features

- **Ollama-powered contextual review**: Sends diffs along with full function bodies and auxiliary context to Ollama to get best-practice-aware feedback.
- **Duplication & similarity detection (pre-LM)**: Queries a vector database to find semantically similar or duplicated code. Those similarity results are then fed into Ollama as additional context so the review can incorporate redundancy insights.
- **Decoupled integration**: Core review API is separate—[`pr_analyzer`](https://github.com/mrrizal/python-pr-analyzer) calls into this service to perform reviews and handle GitHub comment orchestration.

---

## 🧩 Integration Boundary

This repository exposes the review capabilities. The expected flow is:

1. [`pr_analyzer`](https://github.com/mrrizal/python-pr-analyzer) (the integration repo) obtains pull request diffs and metadata.
2. It calls into **auto-cepu**’s API, supplying changed code + context.
3. auto-cepu queries the vector database to find similar/duplicated code snippets.
4. Those similarity findings, together with the full function context and diffs, are composed into a prompt and sent to **Ollama** to generate review suggestions.
5. [`pr_analyzer`](https://github.com/mrrizal/python-pr-analyzer) takes the structured output and posts inline comments or summaries back to the GitHub pull request.

---

## 🔄 Architecture Flow

```text
             ┌─────────────────────────────────┐
             │     python-pr-analyzer           │
             │ (GitHub integration layer)       │
             └─────────────────────────────────┘
                        │
                        │ 1. Obtain PR diffs + metadata
                        ▼
             ┌─────────────────────────────────┐
             │ Call auto-cepu API               │
             │ (send changed code + context)    │
             └─────────────────────────────────┘
                        │
                        ▼
             ┌─────────────────────────────────┐
             │        auto-cepu (standonline)   │
             │  Core review API hitting Ollama  │
             └─────────────────────────────────┘
                        │
        ┌───────────────┴───────────────────┐
        │                                   │
        ▼                                   ▼
┌─────────────────────────┐       ┌────────────────────────────┐
│ Query vector database   │       │ Use diff + full function   │
│ for similar code        │       │ context + similarity data  │
└─────────────────────────┘       │ to build LLM prompt        │
                                   └────────────────────────────┘
                                               │
                                               ▼
                                ┌────────────────────────────┐
                                │ Ollama generates review    │
                                │ suggestions                │
                                └────────────────────────────┘
                                               │
                                               ▼
             ┌─────────────────────────────────────────────────┐
             │ Return structured review output to pr_analyzer   │
             └─────────────────────────────────────────────────┘
                                               │
                                               ▼
             ┌─────────────────────────────────────────────────┐
             │ pr_analyzer posts inline comments / summary to   │
             │ GitHub pull request                              │
             └─────────────────────────────────────────────────┘
