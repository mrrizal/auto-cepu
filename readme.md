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

#### API Example

**Request:**
```bash
curl -X POST "http://localhost:8000/review" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "src/utils/data_processor.py",
    "project_name": "my-project",
    "function_name": "process_user_data",
    "function_location": {
      "start_line": 15,
      "end_line": 45
    },
    "full_function_code": "def process_user_data(user_input):\n    # Validate input\n    if not user_input:\n        return None\n    \n    # Process data\n    processed = user_input.strip().lower()\n    return processed",
    "added_code": [
      {
        "start_line": 18,
        "end_line": 20,
        "code": "    if not user_input:\n        return None",
        "line_count": 3
      }
    ],
    "deleted_code": [
      {
        "start_line": 18,
        "end_line": 18,
        "code": "    # TODO: Add validation",
        "line_count": 1
      }
    ],
    "summary": {
      "total_added_lines": 3,
      "total_deleted_lines": 1,
      "added_line_numbers": [18, 19, 20],
      "deleted_line_numbers": [18]
    }
  }'
```

**Response:**
```json
{
  "duplication_review": "The input validation pattern `if not user_input: return None` appears in 3 similar functions across the codebase (user_validator.py:45, auth_helper.py:123). Consider extracting this into a shared validation utility.",
  "style_review": "Good improvement replacing the TODO comment with actual validation logic. The function follows Python naming conventions and has clear logic flow. Consider adding type hints: `def process_user_data(user_input: str) -> str | None:`",
  "summary": "Added proper input validation by replacing a TODO comment. The validation logic is clean but could be deduplicated across the codebase.",
  "reference": [
    {
      "code": "def validate_user_input(data):\n    if not data:\n        return None\n    return data.strip()",
      "file": "user_validator.py",
      "start_line": 45,
      "name": "validate_user_input",
      "similarity": "87.45%"
    },
    {
      "code": "def check_auth_data(input_data):\n    if not input_data:\n        return None\n    return process_auth(input_data)",
      "file": "auth_helper.py",
      "start_line": 123,
      "name": "check_auth_data",
      "similarity": "82.31%"
    },
    {
      "code": "def sanitize_input(user_data):\n    if user_data is None:\n        return None\n    return user_data.lower().strip()",
      "file": "data_sanitizer.py",
      "start_line": 67,
      "name": "sanitize_input",
      "similarity": "75.89%"
    }
  ]
}
```

---

## 🏗️ Architecture

This service operates as the core review engine in a distributed system for **Python code on GitHub**:

- **auto-cepu** (this repo): Core review logic, vector similarity search, LLM orchestration for Python repositories
- **pr_analyzer**: GitHub integration, PR processing, comment posting
- **Ollama**: LLM inference for generating review suggestions
- **ChromaDB**: Vector database for code similarity detection

**Current Support**: Python repositories hosted on GitHub. The decoupled design allows for future expansion to other languages and platforms.
