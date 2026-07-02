#!/usr/bin/env python3
import argparse
import base64
import datetime as dt
import mimetypes
import json
import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent
from urllib import request


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def check_gh_auth() -> None:
    try:
        run(["gh", "auth", "status"])
    except Exception:
        print("❌ gh auth not ready. Run: gh auth login", file=sys.stderr)
        raise


def ensure_label(repo: str, label: str) -> None:
    # no-op if label exists
    cp = run(["gh", "label", "list", "--repo", repo, "--limit", "200", "--json", "name"], check=False)
    if cp.returncode != 0:
        return
    names = {x["name"] for x in json.loads(cp.stdout or "[]")}
    if label in names:
        return
    run([
        "gh", "label", "create", label,
        "--repo", repo,
        "--color", "1D76DB",
        "--description", "Auto-generated design style summary",
    ], check=False)


def _fallback_summary(image_name: str) -> str:
    return dedent(f"""
    ## Design Style Summary (Fallback Mode)

    Source image: `{image_name}`

    > OPENAI_API_KEY is not configured, so this is a template summary.

    ### 1) Visual tone & mood
    - Modern and clean
    - Balanced contrast, readable hierarchy

    ### 2) Color palette (estimated)
    - Primary: infer from dominant accent color
    - Neutral: background + text grayscale spectrum
    - Semantic: success/warning/error (if shown)

    ### 3) Typography
    - Likely sans-serif family
    - Distinct heading/body scales
    - Medium-to-strong weight for CTA labels

    ### 4) Layout & spacing
    - Grid-based composition
    - Repeated spacing rhythm (8px-like system)
    - Clear section separation with whitespace

    ### 5) Component style
    - Buttons: rounded corners, strong CTA emphasis
    - Cards/containers: soft elevation or border-based grouping
    - Inputs: compact, high readability, clear focus state

    ### 6) Reuse recommendations
    - Define design tokens (colors, radius, spacing, type scale)
    - Create base components before feature implementation
    - Add visual regression tests for key pages/components
    """).strip() + "\n"


def _analyze_with_openai(image_path: Path) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback_summary(image_path.name)

    with image_path.open("rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    mime = mimetypes.guess_type(str(image_path))[0] or "image/png"

    prompt = dedent("""
    Analyze this UI/design image and produce concise markdown in Vietnamese.
    Include sections:
    1) Visual tone & mood
    2) Color palette (estimated hex when possible)
    3) Typography
    4) Layout & spacing patterns
    5) Component style (button/card/input/nav...)
    6) Practical implementation recommendations for product team
    Keep it practical and action-oriented.
    """).strip()

    payload = {
        "model": "gpt-4.1-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    },
                ],
            }
        ],
        "temperature": 0.2,
    }

    req = request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    with request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    content = body["choices"][0]["message"]["content"].strip()
    header = f"# Design Style Summary\n\nGenerated: {dt.datetime.now().isoformat()}\n\n"
    return header + content + "\n"


def create_issue(repo: str, label: str, image: Path, out: Path, summary: str) -> str:
    title = f"Design style summary from {image.name}"
    body = dedent(f"""
    Auto-generated from image: `{image}`

    Artifact file: `{out}`

    ---

    {summary[:5000]}
    """).strip()

    cp = run([
        "gh", "issue", "create",
        "--repo", repo,
        "--title", title,
        "--body", body,
        "--label", label,
    ])
    return cp.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate design-style-summary.md and GitHub issue from an image")
    parser.add_argument("--image", required=True, help="Path to input image")
    parser.add_argument("--out", default="design-style-summary.md", help="Output markdown path")
    parser.add_argument("--repo", required=True, help="GitHub repo in owner/name format")
    parser.add_argument("--label", default="design-summary", help="GitHub issue label")
    args = parser.parse_args()

    image_path = Path(args.image).expanduser().resolve()
    out_path = Path(args.out).expanduser().resolve()

    if not image_path.exists():
        print(f"❌ Image not found: {image_path}", file=sys.stderr)
        return 1

    if image_path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        print("❌ Supported image types: .png .jpg .jpeg .webp", file=sys.stderr)
        return 1

    check_gh_auth()
    ensure_label(args.repo, args.label)

    summary = _analyze_with_openai(image_path)
    out_path.write_text(summary, encoding="utf-8")

    issue_url = create_issue(args.repo, args.label, image_path, out_path, summary)

    print(f"✅ Wrote: {out_path}")
    print(f"✅ Issue: {issue_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
