# Development Guide

## Environment

Project root:

futures_trading_system

Python executable:

.\.venv\Scripts\python.exe

## Run Unit Tests

.\.venv\Scripts\python.exe -m pytest tests\unit -q

## Run Full Tests

.\.venv\Scripts\python.exe -m pytest -q

## Git Validation

git diff --check
git status --short

## Before Commit

git add <files>
git diff --cached --check
git diff --cached --stat

## After Commit

git push
git status --short --branch
git branch -vv
git log -3 --oneline --decorate

## Development Rules

1. Do not rewrite Git history unless explicitly required.
2. Do not use force push.
3. Do not use reset --hard as a normal development workflow.
4. Do not delete and recreate the Git repository.
5. Production behavior must be changed only when explicitly designed and tested.
6. Every important behavior change requires regression tests.
7. Tests must pass before commit.
8. Prefer small commits with one clear purpose.
9. Use PowerShell commands for Windows development.
10. Do not add future architecture prematurely.

## Test Strategy

Tests should cover:

- Unit behavior
- Integration behavior
- Regression behavior
- Determinism
- Edge cases

For backtest changes, verify both:

- Trade results
- Portfolio results

## Current Git Baseline

Branch:

master

Current commit:

8297008

The repository should remain synchronized with origin/master before starting the next phase.
