call pelpub.bat
git add -A
git commit -m "deploying"
git push origin2 source
cd output
git add -A
git commit -m "deploying"
git push origin2 master