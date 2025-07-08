# 🔍 gitlab-linter

**AI-powered GitLab CI/CD pipeline reviewer and scoring tool**

This CLI utility uses LLMs (GPT-4, LLaMA, etc.) to analyze `.gitlab-ci.yml` files for:

- ❌ Anti-patterns and flaws
- 📈 Suggestions for improvement
- 🧠 Summaries for code reviewers
- ⭐️ Quality scoring (structure, reliability, security, maintainability)
- 🔒 Optional strict mode to enforce standards in CI/CD

---

## 🚀 Features

- ✅ Analyze `.gitlab-ci.yml` or diff between commits
- 🧠 Use OpenAI or local models via `ollama`
- 🛠 Score pipelines and enforce minimum thresholds (`--strict`)
- 📄 Output as Markdown (default) or JSON
- ⚙️ No dependencies beyond `openai`, `python-dotenv`, and `ollama` (optional)

---

## 📦 Installation

```bash
pip install openai python-dotenv
brew install ollama   # (optional for local models)

Clone this repo and set up your `.env`
```bash
OPENAI_API_KEY=sk-xxxxxxxx # or other credentials, depending on your model

## Usage
# Basic analysis
python gitlab_linter.py --file .gitlab-ci.yml --mode critic

# Score with JSON output
python gitlab_linter.py --file .gitlab-ci.yml --score --output-format json

# Use local model (e.g., LLaMA3)
python gitlab_linter.py --file .gitlab-ci.yml --provider ollama --model llama3:instruct

# Diff-based review
python gitlab_linter.py --diff HEAD~1 HEAD --mode critic

# Enforce a minimum score in CI
python gitlab_linter.py --file .gitlab-ci.yml --score --strict --min-score 4.0
# ai-utilities
