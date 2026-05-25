# Beacon CLI: Development Roadmap

This document outlines the evolutionary phases of **Beacon**, detailing the strategy to transition it from a static documentation compiler into an intelligent, AI-driven codebase scaffolding assistant.

---

## Current Status: Phase 1 (Completed)
*   **Deliverables**:
    *   Command-line Interface (Typer + Rich) with error fallback.
    *   Specification Parser (YAML Frontmatter + Markdown Headings).
    *   Pydantic Validation schemas (`BeaconSpec` & `ADRSpec`).
    *   Jinja2 Template compiling with user-directory override.
    *   PyPI Packaging & Pytest unit test coverage.

---

## Phase 2: Deterministic Code & Test Scaffolding (Next Step)
*   **Goal**: Generate source folder structures, Python source files, and test files using static templates.
*   **Technical Details**:
    *   Support parsing a list of target `modules` from the `.beacon` file.
    *   When `beacon generate` is run, create corresponding folders (`src/<module_name>/`) and bootstrap files:
        *   `src/<module_name>/__init__.py`
        *   `src/<module_name>/service.py` (empty class/stubs)
    *   Bootstrap matching unit test suites:
        *   `tests/test_<module_name>.py` (stubs containing basic imports and standard pytest templates)
    *   Implement user overrides so developers can place custom module skeletons in `templates/module.py.jinja2`.

---

## Phase 3: AI-Driven Generation (The Core Highlight)
*   **Goal**: Integrate large language models (LLMs) to write functional code and tests based on the specification context.
*   **Technical Details**:
    *   Add `--ai` flag or read environment variables (`OPENAI_API_KEY`, `GEMINI_API_KEY`, or local `OLLAMA_HOST`).
    *   Send the ADR context (e.g. "We will use OAuth2 with JWT tokens") and the module specification to the LLM.
    *   Instruct the LLM to write the actual Python class logic and return it as valid code.
    *   Prompt the LLM to generate corresponding functional `pytest` files with mock databases, fixtures, and assertions to test the generated logic.
    *   Save generated files directly into the project workspace.

---

## Phase 4: CLI Interactive Wizard ("Interview Mode")
*   **Goal**: Create an interactive setup wizard to generate new `.beacon` files from scratch.
*   **Technical Details**:
    *   Introduce `beacon init` command.
    *   Use interactive command line prompts (e.g. using `questionary` or `click.prompt`) styled with Rich.
    *   Ask the developer:
        1.  Project Name
        2.  Modules to create
        3.  Architectural decisions to record (e.g. database choice, auth scheme)
    *   Write the answers directly to a structured `.beacon` file in `/specs/`.

---

## Phase 5: CI/CD & Architecture Linter
*   **Goal**: Enforce architectural consistency in a team environment via automated checks.
*   **Technical Details**:
    *   Add `beacon verify <dir>` command.
    *   Read past ADRs in the repository.
    *   Use LLM embeddings/context to scan new code changes or new ADR specifications.
    *   Raise a lint error if a new specification contradicts an accepted ADR (e.g. proposing a NoSQL DB when a SQL DB standard ADR was accepted).
    *   Support running Beacon as a Git `pre-commit` hook or a GitHub Action to block merging PRs that violate defined specs.
