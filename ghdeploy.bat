call pelpub.bat
git add -A
git commit -m "deploying"
git push origin source
pushd ../output
git add -A
git commit -m "deploying"
git push origin master
popd