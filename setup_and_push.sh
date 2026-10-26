#!/usr/bin/env bash
# Assemble the ASURRE repo and push it to GitHub.
#
# Run this from the folder it was extracted into. It expects the benchmark
# tarball at ../survey_ai_benchmark.tar.gz (where it already lives in
# ~/Documents/emnlp2026) and will unpack it into data/.
#
#   bash setup_and_push.sh
#
# Nothing is pushed until the very last step, and it prints what it is about
# to do first.

set -euo pipefail

# SSH, so it uses the ws_gh key from your ~/.ssh/config rather than asking for
# a token. Override with: REPO_URL=https://... bash setup_and_push.sh
REPO_URL="${REPO_URL:-git@github.com:mike-qz-wang/ASURRE.git}"
TARBALL="${1:-../survey_ai_benchmark.tar.gz}"
BRANCH="main"

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$here"

echo "==> Working in $here"

if [ ! -d data ]; then
  if [ ! -f "$TARBALL" ]; then
    echo "Could not find the benchmark tarball at: $TARBALL" >&2
    echo "Pass its path as the first argument, e.g.:" >&2
    echo "  bash setup_and_push.sh ~/Documents/emnlp2026/survey_ai_benchmark.tar.gz" >&2
    exit 1
  fi
  echo "==> Unpacking $TARBALL into data/"
  mkdir -p data
  tar -xzf "$TARBALL" -C data --strip-components=1
else
  echo "==> data/ already present, leaving it alone"
fi

# The pack ships its own README; the repo root README is the one that counts.
if [ -f data/README.md ]; then
  mv -f data/README.md data/PACK-README.md
fi

find . -name '.DS_Store' -delete 2>/dev/null || true

echo "==> Checking tree"
du -sh data docs scripts 2>/dev/null || true
large=$(find . -type f -size +95M -not -path './.git/*' | head -5)
if [ -n "$large" ]; then
  echo "WARNING: files over GitHub's 100 MB limit:" >&2
  echo "$large" >&2
  exit 1
fi

if [ ! -d .git ]; then
  echo "==> git init"
  git init -q -b "$BRANCH"
  git remote add origin "$REPO_URL"
else
  git remote set-url origin "$REPO_URL" 2>/dev/null || git remote add origin "$REPO_URL"
fi

# The commit must be authored by you, not by any tooling that helped build
# this. Refuse rather than publish a commit under the wrong name.
author_email="$(git config user.email || true)"
author_name="$(git config user.name || true)"
case "$author_email$author_name" in
  *anthropic*|*noreply*|*Claude*|*claude*|"")
    echo "Refusing to commit: git identity is '$author_name <$author_email>'." >&2
    echo "Set your own before running this:" >&2
    echo "  git config --global user.name  'Qizhou Wang'" >&2
    echo "  git config --global user.email 'your@email'" >&2
    exit 1
    ;;
esac

git add -A
if git diff --cached --quiet; then
  echo "==> Nothing new to commit"
else
  git commit -q -m "ASURRE benchmark: data, docs and response browser

Companion data for 'Towards Detecting AI-Assisted Responses in Online
Surveys' (EMNLP 2026).

- data/: three source surveys and the augmented benchmark splits
- docs/: respondent-level browser, published via GitHub Pages
- scripts/: rebuild the browser's sample from data/"
  echo "==> Committed as: $(git log -1 --pretty='%an <%ae>')"
fi

if [ -n "${ASURRE_DRY_RUN:-}" ]; then
  echo
  echo "==> Dry run: repo assembled and committed, nothing pushed."
  echo "    Re-run without ASURRE_DRY_RUN to push."
  exit 0
fi

echo
echo "About to push to $REPO_URL ($BRANCH)."
echo "This publishes the dataset publicly. Press Enter to continue, Ctrl-C to stop."
read -r _

git push -u origin "$BRANCH"

cat <<'DONE'

==> Pushed.

To turn on the browser, enable GitHub Pages:
  Settings -> Pages -> Source: "Deploy from a branch"
                       Branch: main, folder: /docs

It will then be live at:
  https://mike-qz-wang.github.io/ASURRE/
DONE
