#!/usr/bin/env bash

set -euo pipefail

repo_root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cd "$repo_root"

base_branch=${BASE_BRANCH:-master}
configured_pythons=$(uv run --locked python -c 'import json; print("\n".join(json.load(open("asv.conf.json"))["pythons"]))')
mapfile -t python_versions <<< "$configured_pythons"
python_bin_dir=$PWD/.asv/python-bin

git rev-parse --verify "$base_branch^{commit}" >/dev/null
merge_base=$(git merge-base "$base_branch" HEAD)
range="$merge_base..HEAD"

if [[ -z $(git rev-list --max-count=1 "$range") ]]; then
    echo "No commits to benchmark in $range" >&2
    exit 1
fi

mkdir -p "$python_bin_dir"
for version in "${python_versions[@]}"; do
    if ! executable=$(uv python find "$version" 2>/dev/null); then
        uv python install "$version"
        executable=$(uv python find "$version")
    fi
    ln -sfn "$executable" "$python_bin_dir/python$version"
done

export PATH="$python_bin_dir:$PATH"

branch=$(git branch --show-current)
echo "Benchmarking ${branch:-HEAD} commits in $range, including base $merge_base"
git show --no-patch --oneline "$merge_base"
git log --oneline --reverse "$range"

# A revision range excludes its lower bound; include the base as a comparison point.
commit_file=$PWD/.asv/branch-commits.txt
printf '%s\n' "$merge_base" > "$commit_file"
git rev-list --reverse "$range" >> "$commit_file"

asv=(uv run --locked --group benchmarks asv)

# Additional arguments are passed to `asv run`, for example:
#   ./benchmarks/run_branch_benchmarks.sh --quick --bench ColdLookup
"${asv[@]}" run "HASHFILE:$commit_file" --interleave-rounds "$@"
"${asv[@]}" publish

echo "Published report to .asv/html"
