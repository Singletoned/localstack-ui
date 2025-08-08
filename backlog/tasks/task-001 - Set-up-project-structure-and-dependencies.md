---
id: task-001
title: Set up project structure and dependencies
status: Done
assignee: []
created_date: "2025-08-07 20:05"
updated_date: "2025-08-07 20:16"
labels: []
dependencies: []
---

## Description

Initialize the LocalStack UI project with Python dependencies, project structure, and formatting configuration

## Acceptance Criteria

- [ ] pyproject.toml created with all required dependencies
- [ ] Project structure created (src/
- [ ] templates/
- [ ] static/)
- [ ] Ruff formatting configured
- [ ] Settings module with configurable file size limit

## Implementation Plan

1. Create pyproject.toml with Starlette, boto3, uvicorn, python-multipart dependencies\n2. Set up project directory structure (src/, templates/, static/)\n3. Configure ruff formatting with project-specific settings\n4. Create settings.py module with configurable file size limit\n5. Test that dependencies install correctly

## Implementation Notes

Created complete project foundation:\n- pyproject.toml with all required dependencies (starlette, uvicorn, boto3, python-multipart, jinja2)\n- Project structure: src/localstack_ui/, templates/, static/\n- Ruff configuration with line-length 100 and isort settings\n- Settings module with configurable MAX_FILE_SIZE_MB (default 1MB)\n- Updated .gitignore to exclude Claude-specific files\n- All dependencies tested and importable
