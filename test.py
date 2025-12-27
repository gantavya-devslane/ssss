#!/usr/bin/env python3

import os
import random
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------- CONFIG ---------------- #

DAYS_BACK = 90
MAIN_COMMITS_PER_DAY = (2, 5)
PR_BRANCHES = 5
PR_COMMITS = 3
ISSUES = 10

TZ = timezone(timedelta(hours=5, minutes=30))  # IST
LOG_DIR = Path("activity")
LOG_DIR.mkdir(exist_ok=True)

COMMIT_MSGS = [
    "fix: edge case handling",
    "feat: improve performance",
    "refactor: clean logic",
    "docs: update readme",
    "chore: maintenance update",
]

ISSUE_TITLES = [
    "Bug in authentication flow",
    "Improve API performance",
    "Docs need clarification",
    "Refactor legacy code",
]

REVIEW_COMMENTS = [
    "LGTM 👍",
    "Minor suggestion, otherwise good",
    "Approved",
]

# ---------------- HELPERS ---------------- #

def run(cmd, env=None):
    subprocess.run(cmd, check=True, env=env)

def commit_at(date, msg):
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date
    env["GIT_COMMITTER_DATE"] = date

    file = LOG_DIR / "main.log"
    with open(file, "a") as f:
        f.write(f"{msg} @ {date}\n")

    run(["git", "add", str(file)])
    run(["git", "commit", "-m", msg], env=env)

# ---------------- HEATMAP COMMITS ---------------- #

def heatmap_commits():
    print("🔥 Creating main-branch commits (heatmap)")
    now = datetime.now(TZ)

    for d in range(DAYS_BACK):
        day = now - timedelta(days=d)
        commits = random.randint(*MAIN_COMMITS_PER_DAY)

        for _ in range(commits):
            t = day.replace(
                hour=random.randint(10, 22),
                minute=random.randint(0, 59),
                second=random.randint(0, 59),
                microsecond=0,
            )
            commit_at(t.isoformat(), random.choice(COMMIT_MSGS))

    run(["git", "push", "origin", "main"])

# ---------------- ISSUES ---------------- #

def create_issues():
    print("📌 Creating issues")
    issues = []

    for _ in range(ISSUES):
        title = random.choice(ISSUE_TITLES)
        out = subprocess.check_output(
            ["gh", "issue", "create", "--title", title, "--body", "Automated issue"],
            text=True
        ).strip()
        issues.append(out.split("/")[-1])

    return issues

# ---------------- PRs + REVIEWS ---------------- #

def prs_and_reviews(issues):
    print("🔁 Creating PRs")

    for i in range(PR_BRANCHES):
        branch = f"pr-{i}"
        run(["git", "checkout", "-b", branch])

        for _ in range(PR_COMMITS):
            commit_at(
                datetime.now(TZ).isoformat(),
                random.choice(COMMIT_MSGS),
            )

        run(["git", "push", "-u", "origin", branch])

        body = "Automated PR"
        if issues:
            body += f"\n\nFixes #{random.choice(issues)}"

        pr_url = subprocess.check_output(
            [
                "gh", "pr", "create",
                "--base", "main",
                "--head", branch,
                "--title", branch,
                "--body", body
            ],
            text=True
        ).strip()

        run(["gh", "pr", "comment", pr_url, "--body", random.choice(REVIEW_COMMENTS)])
        run(["gh", "pr", "merge", pr_url, "--merge", "--admin"])

        run(["git", "checkout", "main"])

# ---------------- MAIN ---------------- #

def main():
    heatmap_commits()
    issues = create_issues()
    prs_and_reviews(issues)
    print("✅ DONE — heatmap WILL update within a few minutes")

if __name__ == "__main__":
    main()
