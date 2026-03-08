@echo off
cd /d C:\Users\HP\CascadeProjects\mnemosyne
git status
git log --oneline -3
git branch -v
git push origin main --force
pause
