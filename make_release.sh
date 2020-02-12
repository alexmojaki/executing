#!/usr/bin/env bash
set -eux;

if [${1+x}]; then
    if [[ ${1} =~ ^v?([0-9]+)(\.[0-9]+)?(\.[0-9]+)?$ ]]; then
        :;
    else
        echo "Not a valid release tag.";
        exit 1;
    fi;
else
    echo "${0} <major>.<minor>.<patch>";
    exit 1;
fi;

export TAG="v${1}";
echo "$TAG"
git tag "${TAG}";
git push origin master "${TAG}";
rm -rf ./build ./dist;
python3 -m pep517.build -b .;
twine upload ./dist/*.whl;
