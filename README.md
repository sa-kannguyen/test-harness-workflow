# test-harness-workflow

MVP harness workflow sample for a slash-like command:

- Input: a design image (`.png/.jpg/.webp`)
- Output: `design-style-summary.md`
- Side effect: create a GitHub issue with label `design-summary`

## Command (Python + gh CLI)

```bash
python3 harness/design_style_writer.py \
  --image ./sample.png \
  --out ./design-style-summary.md \
  --repo sa-kannguyen/test-harness-workflow \
  --label design-summary
```

## Prerequisites

- Python 3.10+
- `gh` CLI authenticated (`gh auth status`)
- (Optional, recommended) `OPENAI_API_KEY` for AI image analysis

If `OPENAI_API_KEY` is not set, the script still runs and generates a **template/fallback** summary so the harness flow can be tested end-to-end.

## What this demonstrates

This is a minimal Harness-workflow implementation:

1. Validate inputs
2. Analyze image (AI or fallback)
3. Write markdown artifact
4. Ensure issue label exists
5. Create GitHub issue linking the artifact

You can treat this as the base pattern to expand later for `/story-writer`, `/prd-writer`, etc.
