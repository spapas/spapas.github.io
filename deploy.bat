call pelpub.bat
git add -A
git commit -m "deploying"
git push origin2 source
pushd output
git add -A
git commit -m "deploying"
git push origin2 master
popd