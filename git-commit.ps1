# Git operations script
Write-Host "Adding all changes to git..."
git add .

Write-Host "Committing changes..."
git commit -m "Fix codebase issues for professional excellence: Remove duplicate dependencies, create missing migrations directory, ensure demo GIF is properly tracked"

Write-Host "Pushing to develop branch..."
git push origin develop

Write-Host "Git operations completed successfully!"
