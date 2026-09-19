# src/content/

This directory will contain the **actual learning content** for C-NOTE.

## Structure (Phase 2+)

```
content/
├── sheet-150/
│   ├── arrays/
│   │   ├── contains-duplicate.md
│   │   └── two-sum.md
│   └── strings/
│       └── ...
├── computer-networks/
│   └── ...
└── ...
```

## Content Format

Each question is a Markdown file with YAML frontmatter:

```markdown
---
id: contains-duplicate
title: Contains Duplicate
difficulty: easy
tags: [arrays, hash-set]
---

## Problem Statement

Given an integer array `nums`, return `true` if any value appears at least twice.

## Approach

...
```

## Principles

- Content is **data**, not hardcoded JSX
- The UI consumes content files as structured data
- Components are content-agnostic
- Adding new questions does NOT require touching any React component

## Phase Status

❌ Not populated in Phase 1
✅ Directory structure and format planned
✅ Domain types defined in `src/types/subject.ts`
