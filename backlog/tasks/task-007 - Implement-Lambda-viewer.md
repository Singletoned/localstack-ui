---
id: task-007
title: Implement Lambda viewer
status: In Progress
assignee: []
created_date: '2025-08-07 20:06'
updated_date: '2025-08-07 20:43'
labels: []
dependencies: []
---

## Description

Create read-only interface to view Lambda functions and their configurations

## Acceptance Criteria

- [ ] List page shows all Lambda functions
- [ ] Function details display runtime memory and timeout
- [ ] Environment variables are shown
- [ ] Sort and filter capabilities work
- [ ] Navigation is intuitive

## Implementation Plan

1. Create Lambda service module for read-only operations\n2. Add Lambda function listing with configurations\n3. Create Lambda functions page with search/filter capabilities\n4. Implement function detail view showing runtime, memory, timeout, environment variables\n5. Add navigation links to Lambda viewer\n6. Test Lambda viewer displays LocalStack demo functions correctly
