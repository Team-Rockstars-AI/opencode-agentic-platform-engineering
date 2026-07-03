#!/usr/bin/env bash
# End-to-end scaffold verification: generate a workspace for the given
# combination and prove the product actually works — placeholders resolved,
# configs parse, skills resolve, and the rendered IaC compiles.
#
# Usage: verify-scaffold-output.sh <terraform|bicep|both> <github|azure-devops> <basic|enterprise>
set -euo pipefail

IAC="${1:?usage: verify-scaffold-output.sh <iac> <devops> <tier>}"
DEVOPS="${2:?usage: verify-scaffold-output.sh <iac> <devops> <tier>}"
TIER="${3:?usage: verify-scaffold-output.sh <iac> <devops> <tier>}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="$(mktemp -d)/out"

# `az bicep build` in CI; plain `bicep build` as a local fallback.
bicep_build() {
  if command -v az >/dev/null 2>&1; then
    az bicep build --file "$1" --stdout >/dev/null
  else
    bicep build "$1" --stdout >/dev/null
  fi
}

echo "=== Scaffolding: iac=$IAC devops=$DEVOPS tier=$TIER -> $TARGET"
python3 "$REPO_ROOT/scripts/scaffold.py" --non-interactive \
  -i "$IAC" -d "$DEVOPS" -g "$TIER" \
  -p e2e-check -l westeurope -t "$TARGET"

echo "=== 1. No unresolved scaffold placeholders"
# {{token}} placeholders must all be resolved. Exemptions:
#   - .git internals
#   - docs/reports/: report *templates* whose tokens are filled by agents at
#     report-writing time, not at scaffold time.
# The pattern deliberately does not match GitHub Actions expressions like
# ${{ github.ref }} (spaces/dots don't fit [a-z_]+).
if grep -rnIE '\{\{[a-z_]+\}\}' "$TARGET" \
    --exclude-dir=.git \
    | grep -v "/docs/reports/"; then
  echo "FAIL: unresolved placeholders found"
  exit 1
fi

echo "=== 2. Generated opencode.json parses and its skill references resolve"
python3 -m json.tool "$TARGET/opencode.json" >/dev/null
(cd "$TARGET" && python3 scripts/validate-skills.py)

echo "=== 3. Generated YAML parses"
python3 - "$TARGET" <<'PY'
import pathlib
import sys

import yaml

root = pathlib.Path(sys.argv[1])
count = 0
for path in list(root.rglob("*.yml")) + list(root.rglob("*.yaml")):
    if ".git" in path.relative_to(root).parts:
        continue
    list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
    count += 1
print(f"{count} YAML files parsed OK")
PY

echo "=== 4. Rendered IaC compiles"
if [ -d "$TARGET/terraform" ]; then
  (
    cd "$TARGET/terraform"
    terraform init -backend=false -input=false >/dev/null
    terraform validate
  )
fi
if [ -d "$TARGET/bicep" ]; then
  bicep_build "$TARGET/bicep/main.bicep"
  echo "bicep/main.bicep built OK"
fi

echo "=== PASS: E2E scaffold verification ($IAC/$DEVOPS/$TIER)"
