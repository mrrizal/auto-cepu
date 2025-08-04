# auto-cepu

**auto-cepu** is the core **Python code review automation** engine—an API that leverages LLM-powered reviews through **Ollama** for intelligent, contextual feedback. "CEPU" is a playful reverse of "code review" (code ripiu).

> ⚠️ **Integration Note**: GitHub pull request integration is handled separately in [`pr_analyzer`](https://github.com/mrrizal/python-pr-analyzer). This repository provides the core review logic and exposes it as an API, while `pr_analyzer` handles PR processing and GitHub comment posting.

---

## 🚀 Key Features

- **Ollama-powered contextual review**: Analyzes code diffs with full function context and auxiliary information to provide intelligent, best-practice-aware feedback
- **Duplication & similarity detection**: Uses vector database queries to identify semantically similar or duplicated code, feeding these insights to the LLM for comprehensive reviews
- **Decoupled architecture**: Core review API separates concerns—[`pr_analyzer`](https://github.com/mrrizal/python-pr-analyzer) handles GitHub integration while this service focuses on review generation

---

## 🔄 How It Works

```text
             ┌─────────────────────────────────┐
             │     python-pr-analyzer           │
             │ (GitHub integration layer)       │
             └─────────────────────────────────┘
                        │
                        │ 1. Extract PR diffs + metadata
                        ▼
             ┌─────────────────────────────────┐
             │ Call auto-cepu API               │
             │ (send changed code + context)    │
             └─────────────────────────────────┘
                        │
                        ▼
             ┌─────────────────────────────────┐
             │        auto-cepu                 │
             │  Core review engine + API        │
             └─────────────────────────────────┘
                        │
        ┌───────────────┴───────────────────┐
        │                                   │
        ▼                                   ▼
┌─────────────────────────┐       ┌────────────────────────────┐
│ Query vector database   │       │ Build comprehensive prompt │
│ for similar code        │       │ with diff + context +      │
└─────────────────────────┘       │ similarity insights        │
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
             │ Return structured review to pr_analyzer          │
             └─────────────────────────────────────────────────┘
                                               │
                                               ▼
             ┌─────────────────────────────────────────────────┐
             │ pr_analyzer posts comments to GitHub PR         │
             └─────────────────────────────────────────────────┘
```

---

## 🛠️ Setup & Usage

### Prerequisites
- Python 3.8+
- Ollama installed and running
- ChromaDB for vector storage

### Installation
```bash
git clone <this-repo-url>
cd auto-cepu
pip install -r requirements.txt
```

### Usage

#### 1. Clone and Index a Repository
First, clone a Python repository and index its code for similarity detection:

```bash
# Clone a repository
python main.py --clone --repo-url https://github.com/username/my-project --name my-project

# Index the cloned code for vector similarity search
python main.py --index --name my-project
```

#### 2. Start the Review API Server
Launch the FastAPI server to handle review requests:

```bash
python main.py --run-server
```

The API will be available at `http://localhost:8000` with automatic reload enabled for development.

#### 3. Complete Workflow Example
Here's a complete workflow for setting up a repository:

```bash
# Clone, index, and start server in one command
python main.py --clone --repo-url https://github.com/username/my-project --name my-project --index --run-server
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--repo-url` | URL of the Git repository to clone |
| `--name` | Name for the repository directory (default: 'repo') |
| `--clone` | Clone the specified repository |
| `--index` | Parse and index Python code chunks for similarity search |
| `--run-server` | Start the FastAPI review API server |

### API Integration

Once the server is running, external services like [`pr_analyzer`](https://github.com/mrrizal/python-pr-analyzer) can make HTTP requests to trigger code reviews. The API accepts code diffs and context, performs similarity analysis, and returns structured review feedback powered by Ollama.

---

## 🏗️ Architecture

This service operates as the core review engine in a distributed system for **Python code on GitHub**:

- **auto-cepu** (this repo): Core review logic, vector similarity search, LLM orchestration for Python repositories
- **pr_analyzer**: GitHub integration, PR processing, comment posting
- **Ollama**: LLM inference for generating review suggestions
- **ChromaDB**: Vector database for code similarity detection

**Current Support**: Python repositories hosted on GitHub. The decoupled design allows for future expansion to other languages and platforms.
