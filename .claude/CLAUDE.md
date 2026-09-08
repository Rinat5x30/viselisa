# Project Instructions

## Project

This project uses:

Backend

- Python 3.12.10
- Django 5.2 LTS
- PostgreSQL 18

Frontend

- HTML5
- CSS
- Vanilla JavaScript

Infrastructure

- Docker
- Gunicorn
- Nginx
- Redis
- Cloudflare

Version Control

- Git
- GitHub

---

# First Steps

Before writing code always:

1. Read the project structure.
2. Read README if present.
3. Understand the feature.
4. Search for an existing implementation.
5. Only then write code.

---

# Existing Code

Never duplicate logic.

Always search for:

- utilities
- services
- models
- mixins
- forms
- template tags
- JavaScript modules

Prefer reuse.

---

# Django Rules

Prefer Django built-in functionality.

Keep views thin.

Move business logic into services.

Keep templates presentation-only.

Use ORM.

Avoid raw SQL.

Avoid unnecessary signals.

Keep settings modular.

---

# Frontend Rules

Use CSS

Avoid inline styles.

Avoid duplicated JavaScript.

Reuse components whenever possible.

---

# Database

Never create migrations unless required.

Never rename fields unless explicitly requested.

Avoid breaking schema compatibility.

---

# Security

All new code must consider:

- Authentication
- Authorization
- CSRF
- XSS
- SQL Injection
- IDOR
- File Upload Security

Validate all user input.

Never trust client-side validation.

---

# Git

Never commit.

Never push.

Never rewrite Git history.

---

# Output

For complex tasks:

1. Explain the plan.
2. Implement.
3. Summarize what changed.

---

# If Unsure

Stop.

Ask questions.

Do not guess.

# Canary

To confirm that the local CLAUDE.md has been loaded and is being followed:

End every response with:

С уважением,
Claude

If this signature is missing, assume the local CLAUDE.md has not been applied.