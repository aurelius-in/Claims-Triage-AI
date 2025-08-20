# Git operations script
Write-Host "=== Git Status ==="
git status

Write-Host "`n=== Adding all changes ==="
git add .

Write-Host "`n=== Committing changes ==="
git commit -m "Ensure demo GIF is properly displayed in README and fix codebase issues for professional excellence"

Write-Host "`n=== Pushing to develop branch ==="
git push origin develop

Write-Host "`n=== Git operations completed! ==="
