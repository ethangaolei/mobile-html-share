#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  ./scripts/publish_html.sh <html-file> [slug]

Examples:
  ./scripts/publish_html.sh ~/Downloads/report.html kunpeng-org-design
  ./scripts/publish_html.sh /path/to/page.html

What it does:
  1. Copies the HTML file to reports/YYYY-MM-DD-slug/index.html
  2. Copies sibling assets folder if present: <html-basename>_files or assets
  3. Commits and pushes to GitHub
  4. Prints the GitHub Pages URL for WeChat sharing
USAGE
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ] || [ $# -lt 1 ]; then
  usage
  exit 0
fi

INPUT="$1"
SLUG="${2:-}"

if [ ! -f "$INPUT" ]; then
  echo "ERROR: HTML file not found: $INPUT" >&2
  exit 1
fi

case "${INPUT##*.}" in
  html|htm|HTML|HTM) ;;
  *) echo "ERROR: input must be an .html/.htm file" >&2; exit 1 ;;
esac

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

if [ -z "$SLUG" ]; then
  base="$(basename "$INPUT")"
  base="${base%.*}"
  # keep ascii/number/chinese roughly safe; replace spaces and punctuation with '-'
  SLUG="$(printf '%s' "$base" | tr '[:upper:]' '[:lower:]' | sed -E 's/[[:space:]]+/-/g; s/[^[:alnum:]一-龥_-]+/-/g; s/^-+//; s/-+$//; s/-+/-/g')"
fi

if [ -z "$SLUG" ]; then
  SLUG="report"
fi

DATE="$(date +%F)"
TARGET_DIR="reports/${DATE}-${SLUG}"
mkdir -p "$TARGET_DIR"
cp "$INPUT" "$TARGET_DIR/index.html"

INPUT_DIR="$(cd "$(dirname "$INPUT")" && pwd)"
INPUT_BASE="$(basename "$INPUT")"
INPUT_STEM="${INPUT_BASE%.*}"

# Copy common asset folders if they exist beside the HTML.
for asset_dir in "${INPUT_STEM}_files" "assets"; do
  if [ -d "$INPUT_DIR/$asset_dir" ]; then
    rm -rf "$TARGET_DIR/$asset_dir"
    cp -R "$INPUT_DIR/$asset_dir" "$TARGET_DIR/$asset_dir"
  fi
done

# Add a tiny metadata file for traceability.
cat > "$TARGET_DIR/published.txt" <<META
source=$INPUT
published_at=$(date '+%Y-%m-%d %H:%M:%S %Z')
slug=$SLUG
META

git add "$TARGET_DIR"

if git diff --cached --quiet; then
  echo "No changes to publish."
else
  git commit -m "Publish report: ${DATE}-${SLUG}"
  git push
fi

REMOTE_URL="$(git remote get-url origin)"
OWNER_REPO="$(printf '%s' "$REMOTE_URL" | sed -E 's#^https://github.com/##; s#^git@github.com:##; s#\.git$##')"
OWNER="${OWNER_REPO%%/*}"
REPO="${OWNER_REPO#*/}"
URL="https://${OWNER}.github.io/${REPO}/${TARGET_DIR}/"

echo ""
echo "Published: $URL"
echo "WeChat share URL: $URL"
