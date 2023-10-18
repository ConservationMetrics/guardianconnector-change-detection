#!/bin/bash -ex

# Ensure an up-to-date build of the auditor-core dependency that happens to live in this repo.
# tox -e py310 --notest -c ./gccd_pkg
(cd gccd_pkg ; python -m build)
cp gccd_pkg/dist//gccd-*.tar.gz httpservice/gccd.tar.gz

# Build docker image for batch jobs
IMAGE_TAG=${1:-gccd}
docker build httpservice -t $IMAGE_TAG

rm httpservice/gccd.tar.gz || true
