# GitHub Actions YAML Guide

A comprehensive reference for understanding GitHub Actions workflow files, based on your class assignment using FastAPI + pytest.

---

## Table of Contents
1. [runs-on vs requires-python](#runs-on-vs-requires-python)
2. [Ubuntu Versions](#ubuntu-versions)
3. [The Dash in YAML Lists](#the-dash-in-yaml-lists)
4. [Checkout Action](#checkout-action)
5. [What is a Runner](#what-is-a-runner)
6. [Setup-Python Action](#setup-python-action)
7. [Python Version Syntax](#python-version-syntax)
8. [actions vs astral-sh](#actions-vs-astral-sh)
9. [Semantic Versioning](#semantic-versioning)
10. [Default Workflow Behavior](#default-workflow-behavior)
11. [uv sync Commands](#uv-sync-commands)
12. [uv run pytest with Flags](#uv-run-pytest-with-flags)

---

## runs-on vs requires-python

These are **two completely different things**:

### `runs-on`
- **What it is:** The operating system the runner uses
- **Examples:** `ubuntu-22.04`, `windows-latest`, `macos-latest`
- **Where:** In the workflow file (YAML)
- **Purpose:** Specifies which environment/OS your workflow runs on

### `requires-python`
- **What it is:** The Python version your project supports
- **Location:** In `pyproject.toml`
- **Example:** `requires-python = ">=3.10"`
- **Purpose:** Specifies minimum Python version for your project

### The Relationship

```yaml
# In your workflow
runs-on: ubuntu-22.04          # OS = Ubuntu 22.04

# In setup-python step
python-version: "3.10"         # Python version = 3.10
                               # Should match requires-python minimum
```

### Best Practice
- `runs-on`: Use `ubuntu-22.04` (specific version prevents future conflicts)
- `python-version`: Use the **minimum version from `pyproject.toml`** (ensures compatibility for all users)

---

## Ubuntu Versions

### Available Options
- `ubuntu-latest` (currently 24.04)
- `ubuntu-22.04` (LTS, stable, recommended)
- `ubuntu-20.04` (older LTS, equally stable)

### Which to Use?

| Version | Use Case |
|---------|----------|
| `ubuntu-22.04` | **Recommended for assignments** - specific, stable, won't break in future |
| `ubuntu-20.04` | Perfectly fine, just slightly older support end date |
| `ubuntu-latest` | Works but can cause issues if OS updates break your setup |

### Why Not "Slim" Versions?
Slim Ubuntu versions **don't exist in GitHub Actions**. All runners come pre-installed with common tools.

---

## The Dash in YAML Lists

The `-` is **required YAML syntax** for list items, not just formatting.

### Why It's Necessary

```yaml
steps:
  - name: Checkout code      # <- This dash means "item 1 in the list"
    uses: actions/checkout@v4

  - name: Set up Python      # <- This dash means "item 2 in the list"
    uses: actions/setup-python@v5
```

### Without the Dash (Invalid)

```yaml
steps:
  name: Checkout code        # ❌ INVALID - no dash means YAML doesn't recognize this as a list
  uses: actions/checkout@v4
```

### What It Does
- Tells YAML that each item is a **separate element in an array**
- Without it, the parser can't understand the structure
- It's part of YAML's fundamental syntax

---

## Checkout Action

### What It Does

The `actions/checkout@v4` action:
1. **Connects to your GitHub repository**
2. **Fetches your code** from the exact commit that triggered the workflow
3. **Places it on the runner** so subsequent steps can use it

### Visual Process

```
Your GitHub Repository (on GitHub servers)
            ↓
    checkout@v4 downloads code
            ↓
GitHub Actions Runner (temp VM)
/home/runner/work/repo-name/
    └── Your project files now here
```

### Under the Hood

The action essentially runs:
```bash
git clone https://github.com/YOUR-USER/YOUR-REPO.git .
git checkout <commit-sha>  # The exact commit that triggered the workflow
```

### Why It's Needed
Without `checkout`, the runner has **no code** to work with. pytest, your app, everything would fail because there's nothing to test.

### Version to Use
**Always use `@v4`** — it's the current, fastest, most secure version.

---

## What is a Runner

A **runner** is a **temporary virtual machine** that GitHub provides to execute your workflow.

### How It Works

```
You push code to GitHub
        ↓
GitHub Actions triggers
        ↓
GitHub creates Runner (temporary VM)
├─ OS: Ubuntu 22.04 (or specified in runs-on)
├─ CPU: Available resources
├─ Memory: Available resources
└─ Storage: Fresh, clean filesystem
        ↓
Your workflow steps run on the runner
        ↓
Workflow completes
        ↓
GitHub deletes the runner (auto cleanup)
```

### Key Facts About Runners

| Aspect | Details |
|--------|---------|
| **Lifetime** | Created when workflow starts, deleted when it ends |
| **Storage** | Fresh, empty filesystem each time (no persistence) |
| **Isolation** | Completely separate from other runners |
| **Cost** | Free for public repos; limited minutes for private |
| **Execution Time** | Push completes immediately; runner works in background |

### Important: Push ≠ Workflow Completion

```
14:32:15 → You run: git push
14:32:16 → Push completes ✓ (code is on GitHub NOW)
14:32:17 → Runner starts (background job)
14:32:45 → Tests finish (you can see results on GitHub)
```

Your code is already on GitHub before the runner even finishes.

---

## Setup-Python Action

### What It Does

Similar to checkout, `actions/setup-python@v5`:
1. **Connects to Python distribution repository**
2. **Downloads the specified Python version**
3. **Installs it on the runner**
4. **Makes it available** in PATH

### Why It's Needed

The runner starts with **no Python installed**. This action installs it.

```
Runner starts (fresh Ubuntu, NO Python)
        ↓
setup-python@v5 downloads Python 3.10
        ↓
Python 3.10 installed on runner
        ↓
pip install, pytest, etc. can now run
```

### Which Version to Specify

**Use the minimum version from your `pyproject.toml`:**

```toml
# In pyproject.toml
requires-python = ">=3.10"
```

```yaml
# In workflow
- uses: actions/setup-python@v5
  with:
    python-version: "3.10"  # ← Match the minimum from pyproject.toml
```

### Why Not Your Local Version?

```
Your machine:     Python 3.12
pyproject.toml:   requires-python = ">=3.10"
GitHub Actions:   Should be 3.10 (minimum supported)

❌ DON'T use 3.12 (just because that's what you have)
✓ DO use 3.10 (minimum from pyproject.toml)
```

You want to verify your code works on the minimum version you support.

---

## Python Version Syntax

In YAML, these formats have differences:

### The Three Formats

| Format | YAML Type | Result |
|--------|-----------|--------|
| `"3.13"` | String | `"3.13"` ✓ |
| `'3.13'` | String | `"3.13"` ✓ |
| `3.13` | Float (number) | `3.13` ⚠️ |

### Why It Matters

`python-version` expects a **string**. Here's what happens:

```yaml
python-version: "3.13"    # ✓ YAML says "this is text" → Works correctly
python-version: '3.13'    # ✓ YAML says "this is text" → Works correctly
python-version: 3.13      # ⚠️ YAML says "this is a number" → GitHub converts to string (works but unnecessary)
```

### The Real Problem: Trailing Zeros

```yaml
python-version: 3.10      # YAML might parse as: 3.1 (LOSES the trailing 0!)
python-version: "3.10"    # YAML preserves as: "3.10" (correct)
```

### Best Practice

**Always use quotes:**
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: "3.10"  # ✓ Correct way
```

Single vs double quotes doesn't matter (`'3.10'` = `"3.10"`), just **always include quotes**.

---

## actions vs astral-sh

Both are **GitHub Actions**, but from **different organizations**.

### The Difference

```
actions/checkout@v4
↑
Published by: GitHub (official)

astral-sh/setup-uv@v1
↑
Published by: Astral (company behind uv tool)
```

### Full Breakdown

```
astral-sh/setup-uv@v1
│         │      │
│         │      └─ Version tag
│         └────────── Repository/action name
└─────────────────── Organization/publisher


actions/checkout@v4
│      │      │
│      │      └─ Version tag
│      └──────── Repository/action name
└─────────────── Organization (GitHub)
```

### They Work Identically

Whether `actions/...` or `astral-sh/...`:
- Same syntax
- Same execution model
- Same security model
- Only difference: who publishes and maintains it

### In Your Workflow

```yaml
- uses: actions/checkout@v4
  # GitHub's official action (safe, well-maintained)

- uses: actions/setup-python@v5
  # GitHub's official action

- uses: astral-sh/setup-uv@v2
  # Astral's official action (they make uv, so they maintain this)
```

### Why Trust Third-Party Actions?

- **Official source:** astral-sh is the official company behind uv
- **Community adoption:** Widely used in real projects
- **Active maintenance:** Recently updated and supported
- **Transparency:** Code is public on GitHub

---

## Semantic Versioning

Version numbers follow a pattern: `MAJOR.MINOR.PATCH`

```
0.10.11
│ │  │
│ │  └─ PATCH (bug fixes, minor improvements)
│ └──── MINOR (new features, backwards compatible)
└────── MAJOR (breaking changes)
```

### What Each Number Means

| Version Number | Meaning | Example |
|---|---|---|
| MAJOR | Breaking changes | 0→1 (incompatible) |
| MINOR | New features, backwards compatible | 0.10→0.11 (safe to update) |
| PATCH | Bug fixes and patches | 0.10.0→0.10.11 (always safe) |

### Practical Example

```
0.10.0 → base version
0.10.1 → patch (bug fix)
0.10.2 → another patch
...
0.10.11 → 11 patches applied (more stable than 0.10.0)
```

**Result:** `0.10.11` is better than `0.10.0` (same features, more bug fixes).

### When to Update Versions

| Scenario | Should Update? |
|----------|---|
| New patch available (0.10.0→0.10.1) | ✓ Yes (safe) |
| New minor version (0.10→0.11) | ✓ Usually (new features) |
| New major version (0→1) | ⚠️ Check for breaking changes |

### In Your Workflow

```yaml
- uses: astral-sh/setup-uv@v2
  with:
    version: "0.10.11"  # ← This is the uv TOOL version
```

Note: `@v2` is the action version (different from uv version).

---

## Default Workflow Behavior

### The Rule: All or Nothing

By default, **the workflow succeeds only if EVERY step succeeds**.

### Execution Flow

```
Step 1: run ✓
Step 2: run ✓
Step 3: run ✗ (FAILURE)
Step 4: NOT EXECUTED (blocked)
Step 5: NOT EXECUTED (blocked)

Final result: WORKFLOW FAILED
```

When a step fails, **subsequent steps don't run** (by default).

### Example

```yaml
steps:
  - name: Checkout
    uses: actions/checkout@v4

  - name: Setup Python
    uses: actions/setup-python@v5

  - name: Run tests
    run: pytest              # If this fails, next steps don't run

  - name: Generate report
    run: python report.py    # Won't run if pytest failed
```

### You Can Override This (Advanced)

```yaml
- name: Run tests
  run: pytest
  continue-on-error: true    # Continue even if this fails

- name: Always run
  if: always()               # Runs regardless of previous steps
  run: echo "Complete"
```

### For Your Assignment

**Use the default behavior:**
```yaml
- run: pytest
# If tests fail, workflow fails (intended)
```

You want all tests to pass before success.

---

## uv sync Commands

### `uv sync` (No Arguments)

```bash
uv sync
```

**Installs:**
- ✓ Regular dependencies (from `[project] dependencies`)
- ✗ Dev dependencies (from `[dependency-groups]`)

**Use when:** You only need dependencies for running your app.

### `uv sync --group dev`

```bash
uv sync --group dev
```

**Installs:**
- ✓ Regular dependencies
- ✓ Dev dependencies

**Use when:** You need both app dependencies and testing dependencies.

### `uv sync --only-group dev`

```bash
uv sync --only-group dev
```

**Installs:**
- ✗ Regular dependencies
- ✓ Dev dependencies only

**Use when:** Very rare (usually for testing only)

### Example pyproject.toml

```toml
[project]
dependencies = ["fastapi", "uvicorn"]

[dependency-groups]
dev = ["pytest", "pytest-asyncio", "black"]
```

### Which Command for Your Workflow?

```yaml
- name: Install dependencies
  run: uv sync --group dev
  # Installs:
  # - fastapi, uvicorn (for your app)
  # - pytest, pytest-asyncio (for testing)
```

Use `--group dev` because you need **both** to run tests.

---

## uv run pytest with Flags

### `uv run pytest`

**What it does:**
1. `uv` activates your virtual environment (with all dependencies)
2. `pytest` discovers and runs all test files
3. Reports results

### Test Discovery

pytest automatically finds:
- **Files:** `test_*.py` or `*_test.py`
- **Functions:** `def test_*`
- **Classes:** `class Test*`

### Example Project

```
project/
├── app/
│   └── main.py
├── tests/
│   ├── test_main.py       # ✓ pytest finds
│   └── test_routes.py     # ✓ pytest finds
└── utils.py               # ✗ ignored
```

### The `-v` Flag (Verbose)

```bash
uv run pytest -v
```

### Without `-v`

```
pytest
```

**Output:**
```
test_main.py .....                           [100%]
5 passed in 0.23s
```

You see: Total passed/failed only.

### With `-v`

```
uv run pytest -v
```

**Output:**
```
test_main.py::test_hello PASSED                      [ 20%]
test_main.py::test_world PASSED                      [ 40%]
test_main.py::test_add PASSED                        [ 60%]
test_main.py::test_subtract PASSED                   [ 80%]
test_main.py::test_divide PASSED                     [100%]

5 passed in 0.23s
```

You see: Each test individually with status.

### Why Use `-v`?

| Scenario | Without `-v` | With `-v` |
|----------|---|---|
| All pass | ✓ Clear | ✓ Clear |
| Some fail | ✗ Hard to debug | ✓ Exactly which failed |
| GitHub logs | Less helpful | Much more helpful |

### Other Useful Flags

| Flag | Purpose |
|---|---|
| `-v` | Verbose (show each test) |
| `-s` | Show print statements (stdout) |
| `-x` | Stop on first failure |
| `--tb=short` | Shorter error messages |
| `-k "pattern"` | Run only matching tests |

### For Your Workflow

```yaml
- name: Run tests
  run: uv run pytest -v
  # Recommended: detailed output helps with debugging
```

---

## Complete Workflow Example

Here's a complete example combining everything:

```yaml
name: Tests
on: [push]

jobs:
  test:
    runs-on: ubuntu-22.04                    # Specific OS version

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        # Downloads your code

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"             # From pyproject.toml minimum

      - name: Setup uv
        uses: astral-sh/setup-uv@v2
        with:
          version: "0.10.11"                 # Specific version

      - name: Install dependencies
        run: uv sync --group dev
        # Installs app + dev dependencies

      - name: Run tests
        run: uv run pytest -v
        # Runs tests with verbose output
```

---

## Quick Reference

| Concept | Key Point |
|---------|-----------|
| `runs-on` | OS environment (github's machine) |
| `requires-python` | Python version support (your project) |
| `-` in YAML | Required list syntax |
| `checkout` | Downloads your code to runner |
| `runner` | Temporary VM that executes workflow |
| `setup-python` | Installs Python on runner |
| Version syntax | Always use quotes: `"3.10"` |
| Actions source | Different publishers (actions/ or astral-sh/) |
| Semantic versioning | MAJOR.MINOR.PATCH pattern |
| Default behavior | Stop on first failure |
| `uv sync --group dev` | Install app + dev dependencies |
| `pytest -v` | Verbose output (show each test) |

---

## Your Assignment Context

For your FastAPI + pytest GitHub Actions setup:
- **OS:** `ubuntu-22.04` (stable, specific)
- **Python:** Match `requires-python` minimum in `pyproject.toml`
- **Dependencies:** `uv sync --group dev` (need pytest)
- **Testing:** `uv run pytest -v` (verbose helps debugging)

This creates a CI/CD pipeline that automatically tests your code on every push—a professional practice in software development.
