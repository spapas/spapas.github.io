#!/bin/bash

set -e

echo "REPO: $GITHUB_REPOSITORY"
echo "ACTOR: $GITHUB_ACTOR"

remote_repo="https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
remote_branch=${GH_PAGES_BRANCH:=gh-pages}

echo 'Installing Python Requirements 🐍 '
pip install -r requirements.txt

echo 'Add more deps '
git clone https://github.com/spapas/pelican-octopress-theme
git clone https://github.com/getpelican/pelican-plugins

echo 'Building site 👷 '
pelican content -o output -s ghconf.py
pelican content -o output2 -s ghconf2.py

echo 'Publishing to GitHub Pages master 📤 '
pushd output
git init
git remote add deploy "$remote_repo"
git checkout master || git checkout --orphan master
git config user.name "${GITHUB_ACTOR}"
git config user.email "${GITHUB_ACTOR}@users.noreply.github.com"
git add .

echo -n 'Files to Commit:' && ls -l | wc -l
git commit -m "Automated deployment to GitHub Pages on $(date +%s%3N)"
git push deploy master --force
rm -fr .git
popd

echo 'Publishing to GitHub Pages master2 📤 '
pushd output2
git init
git remote add deploy "$remote_repo"
git checkout master2 || git checkout --orphan master2
git config user.name "${GITHUB_ACTOR}"
git config user.email "${GITHUB_ACTOR}@users.noreply.github.com"

git add .

echo -n 'Files to Commit:' && ls -l | wc -l
git commit -m "Automated deployment to GitHub Pages on $(date +%s%3N)"
git push deploy master2 --force
rm -fr .git
popd

echo 'Done 🎉🎉 🕺💃 '
