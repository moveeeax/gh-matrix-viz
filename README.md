# gh-matrix-viz

> Understand a sprawling Actions matrix at a glance instead of reading YAML.

**Status:** 🚧 In development

## Overview

Render a GitHub Actions workflow job matrix as a readable table or graph.

## Features

- Parse workflow YAML including `strategy.matrix` and `include`/`exclude`
- Expand the matrix into the concrete job combinations
- Render as a Markdown table and/or Mermaid graph
- Show job dependencies (`needs`) as edges
- CLI over a single workflow file

## Stack

Python 3.11, PyYAML, Mermaid/Markdown rendering.

## Usage

```bash
gh-matrix-viz .github/workflows/ci.yml --format table
```

## License

MIT
