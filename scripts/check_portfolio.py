#!/usr/bin/env python3
"""Fail closed on recruiter-facing navigation, examples, and authority claims."""

from __future__ import annotations

import ipaddress
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
RECRUITER_DOCS = (
    README,
    ROOT / "docs/ARCHITECTURE.md",
    ROOT / "docs/DEMO.md",
    ROOT / "docs/EVIDENCE.md",
)
EXAMPLE = ROOT / "docs/examples/portfolio-demo.txt"
DEMO = ROOT / "scripts/portfolio_demo.py"

REQUIRED_README_LINKS = (
    "docs/ARCHITECTURE.md",
    "docs/DEMO.md",
    "docs/EVIDENCE.md",
    "docs/PROVENANCE.md",
    "terraform/modules/",
    "terraform/environments/",
    "platform/",
    "kustomize/",
    "helm-chart/",
    "observability/",
    "tests/",
    ".github/workflows/required.yml",
    ".github/workflows/platform-offline.yml",
)

PRIVATE_PATTERNS = {
    "service-account email": re.compile(
        r"\b[^\s@]+@[^\s@]+\.iam\.gserviceaccount\.com\b", re.I
    ),
    "private registry coordinate": re.compile(r"\.pkg\.dev/", re.I),
    "concrete WIF coordinate": re.compile(
        r"projects/[0-9]+/locations/global/workloadIdentityPools/", re.I
    ),
    "segmented project coordinate": re.compile(
        r"\bproject-[0-9a-f]{8}(?:-[0-9a-f]{3,12}){2,5}\b", re.I
    ),
    "private key material": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
    "Google OAuth access token": re.compile(r"\bya29\.[A-Za-z0-9._-]+"),
    "GitHub classic token": re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"),
}
IPV4 = re.compile(
    r"(?<![0-9])(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})"
    r"(?:\.(?:25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})){3}(?![0-9])"
)
LIVE_DEMO_PATTERNS = {
    "Terraform live action": re.compile(
        r"\bterraform\s+(?:plan|apply|import|destroy|state|force-unlock)\b", re.I
    ),
    "gcloud execution": re.compile(r"(?m)^\s*gcloud\s+", re.I),
    "kubectl mutation": re.compile(
        r"\bkubectl\s+(?:apply|create|delete|patch|replace|rollout|scale|set|exec|run)\b",
        re.I,
    ),
    "Helm mutation": re.compile(
        r"\bhelm\s+(?:install|upgrade|uninstall|rollback)\b", re.I
    ),
    "Skaffold mutation": re.compile(r"\bskaffold\s+(?:run|deploy|dev|delete)\b", re.I),
    "WIF/OIDC permission": re.compile(r"id-token\s*:\s*write", re.I),
    "Google auth action": re.compile(r"google-github-actions/auth", re.I),
}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def checked_docs() -> list[Path]:
    docs = [
        path
        for path in (ROOT / "docs").rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".md", ".txt", ".json", ".yaml", ".yml", ".svg", ".html"}
    ]
    return [README, *sorted(docs)]


def check_links(path: Path, failures: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for raw_target in MARKDOWN_LINK.findall(text):
        target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
        if (
            not target
            or target.startswith(("#", "http://", "https://", "mailto:"))
        ):
            continue
        local = target.split("#", 1)[0].split("?", 1)[0]
        if not local:
            continue
        resolved = (path.parent / local).resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            failures.append(f"{path.relative_to(ROOT)}: link escapes repository: {target}")
            continue
        if not resolved.exists():
            failures.append(f"{path.relative_to(ROOT)}: broken relative link: {target}")


def main() -> int:
    failures: list[str] = []

    for path in (*RECRUITER_DOCS, EXAMPLE, DEMO):
        if not path.is_file():
            failures.append(f"missing portfolio surface: {path.relative_to(ROOT)}")

    if failures:
        for failure in failures:
            print(f"portfolio readiness violation: {failure}", file=sys.stderr)
        return 1

    readme = README.read_text(encoding="utf-8")
    if "python scripts/portfolio_demo.py" not in readme:
        failures.append("README missing exact primary demo command")
    for link in REQUIRED_README_LINKS:
        if link not in readme:
            failures.append(f"README navigation missing: {link}")
    for stale in ("During the current extraction phase", "current extraction phase"):
        if stale in readme:
            failures.append(f"README retains stale extraction-front-door wording: {stale}")

    for path in RECRUITER_DOCS:
        check_links(path, failures)

    for path in checked_docs():
        text = path.read_text(encoding="utf-8", errors="strict")
        rel = path.relative_to(ROOT)
        for label, pattern in PRIVATE_PATTERNS.items():
            if pattern.search(text):
                failures.append(f"{rel}: {label}")
        for match in IPV4.finditer(text):
            if ipaddress.ip_address(match.group(0)).is_global:
                failures.append(f"{rel}: globally routable IPv4 literal")

    demo_text = DEMO.read_text(encoding="utf-8")
    for label, pattern in LIVE_DEMO_PATTERNS.items():
        if pattern.search(demo_text):
            failures.append(f"primary demo contains forbidden authority: {label}")

    completed = subprocess.run(
        [sys.executable, str(DEMO)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    expected = EXAMPLE.read_text(encoding="utf-8")
    if completed.returncode != 0:
        failures.append(
            "primary demo failed: "
            + ((completed.stderr or completed.stdout).strip().splitlines() or ["unknown"])[0]
        )
    elif completed.stdout != expected:
        failures.append("primary demo output drifted from docs/examples/portfolio-demo.txt")

    if failures:
        print("portfolio readiness FAILED", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(
        "portfolio readiness passed: navigation, deterministic demo, sanitation, "
        "and no-live-authority claims are consistent"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
