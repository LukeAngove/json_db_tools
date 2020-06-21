#!/usr/bin/env bash

# Make the directory.
mkdir -p examples/git

# Go there, saving where we are.
pushd examples/git

# Initialise a bare git repository.
git init --bare

# Go back to where we were.
popd

