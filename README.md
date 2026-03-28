# CS50P — QA Automation Learning Bootcamp

**Structured learning journey: Python fundamentals → pytest → Playwright automation testing**

---

## 📋 Overview

Self-directed bootcamp program combining Harvard's CS50P with hands-on QA automation tooling. Three-phase progression building portfolio-ready test automation skills.

**Duration:** 60 days intensive | **Time commitment:** 3h/day | **Output:** 4 Python projects + test framework

---

## 🎯 Three-Phase Structure

### Phase 1: Python Core (Days 1-30)
**Goal:** Fluent Python with clean code practices

| Week | Topics | Project |
|------|--------|---------|
| 1 | Functions, variables, strings, I/O, conditionals | Password strength validator |
| 2 | Data structures: lists, dicts, sets, tuples | Contact manager CLI |
| 3 | Modules, file I/O, error handling, HTTP APIs | Expense tracker with JSON persistence |
| 4 | OOP, classes, inheritance, clean code | Quiz app (integration project) |

**Resources (PT-BR):**
- [Curso em Vídeo — Python Fundamentals](https://www.cursoemvideo.com/curso/python-3-mundo-1/)
- [Python Docs — Portuguese](https://docs.python.org/pt-br/3/)

**Aligned with:** CS50P Problem Sets 0-8

---

### Phase 2: Testing with pytest (Days 31-45)
**Goal:** Professional test suite design and execution

| Days | Topic | Resource |
|------|-------|----------|
| 31-33 | pytest basics, assertions, test discovery | [Microsoft Learn PT-BR](https://learn.microsoft.com/pt-br/training/modules/test-python-with-pytest/) |
| 34-36 | Fixtures, conftest.py, scope management | [Domine Pytest — Udemy PT-BR](https://www.udemy.com/course/domine-pytest/) |
| 37-39 | Parametrization, markers, exception testing | pytest docs |
| 40-42 | Mocking, coverage analysis (pytest-cov) | Udemy |
| 43-45 | **Project:** Test suite ≥80% coverage for Phase 1 projects | — |

**Output:** Test coverage reports, CI-ready test suite

---

### Phase 3: UI + API Automation (Days 46-60)
**Goal:** End-to-end test automation framework

| Days | Topic | Resource |
|------|-------|----------|
| 46-48 | Playwright setup, selectors, navigation | [Playwright com Python — Udemy](https://www.udemy.com/course/playwright-python/) |
| 49-51 | Page Object Model (POM) architecture | Udemy |
| 52-54 | API testing: requests library, status validation, JSON parsing | [NashTech Guide](https://blog.nashtechglobal.com/api-testing-with-pytest-and-python-requests-a-beginners-guide/) |
| 55-57 | Authentication flows, schema validation, fixtures | requests docs + jsonschema |
| 58-60 | **Project:** Mini automation framework (UI + API) → GitHub | — |

**Output:** Production-ready framework with Page Object Model

---

## 📂 Repository Structure

```
cs50-python/
├── week0/                 # CS50P Problem Set 0
│   ├── hello.py
│   ├── einstein.py
│   ├── faces.py
│   └── ...
├── phase1_python/
│   ├── password_validator/
│   │   ├── validator.py
│   │   └── main.py
│   ├── contact_manager/
│   ├── expense_tracker/
│   └── quiz_app/
├── phase2_testing/
│   ├── tests/
│   │   ├── test_validator.py
│   │   ├── test_contacts.py
│   │   └── conftest.py
│   └── coverage_report/
├── phase3_automation/
│   ├── tests/
│   │   ├── ui/
│   │   │   └── test_*.py
│   │   └── api/
│   │       └── test_*.py
│   ├── pages/         # Page Object Model
│   │   ├── base_page.py
│   │   └── login_page.py
│   ├── api/
│   │   └── client.py
│   └── conftest.py
└── README.md
```

---

## 🔧 Code Standards

All code follows these standards:

```python
"""Module docstring."""
from typing import Optional

def normalize_string(raw: str) -> str:
    """Process and clean input string.

    Args:
        raw: Input string to normalize.

    Returns:
        Normalized string ready for use.
    """
    return raw.strip().lower()
```

**Requirements:**
- Type hints on all function signatures
- Google-style docstrings
- PEP 8 compliance (88 char max via Black)
- Single responsibility principle
- No comments for obvious code

---

## 📊 Progress Tracking

| Phase | Status | Days | Checkpoint |
|-------|--------|------|------------|
| Week 0 | ✅ Complete | — | PS0 submitted |
| Phase 1 | 🔄 In Progress | 1-30 | 4 projects, daily commits |
| Phase 2 | ☐ Pending | 31-45 | ≥80% test coverage |
| Phase 3 | ☐ Pending | 46-60 | Framework on GitHub |

---

## 🎓 Learning Methodology

- **Hands-on first:** Code before watching videos
- **Feynman principle:** Explain concepts without references
- **Daily commitment:** Minimum 3h structured learning
- **CI discipline:** Daily commits to GitHub
- **QA mindset:** Test everything before advancing

---

## 🚀 Usage

**To run projects:**

```bash
# Phase 1 projects
cd phase1_python/password_validator
python main.py

# Phase 2 tests
cd phase2_testing
pytest -v --cov=phase1_python tests/

# Phase 3 automation
cd phase3_automation
pytest tests/ui/ tests/api/ -v
```

---

## 📚 Key Resources

| Topic | Resource | Format |
|-------|----------|--------|
| Python Core | Curso em Vídeo (Guanabara) | Video + Exercises |
| pytest | Microsoft Learn PT-BR | Free module + Docs |
| Playwright | Udemy PT-BR (latest) | Video + Labs |
| API Testing | NashTech Blog + Docs | Articles + Reference |

---

## ✅ Success Criteria

Each phase completes when:

1. **All daily objectives met** — concept understood, code written, tested
2. **Feynman check passed** — can explain without references
3. **Code follows standards** — linting clean, tests passing, coverage adequate
4. **Project committed** — GitHub push with clear message

---

## 📞 Support
twitter.com/deehlusa
deehlusa@gmail.com

This is self-directed learning using:
- Official documentation (Python, pytest, Playwright)
- Open-source tutorials (NashTech, Microsoft Learn)
- Claude AI for code review and concept clarification

------------------------------------------------------------

**Last Updated:** 2026-03-28 | Plan Created by Deehlusa with Claude Code/App. 
