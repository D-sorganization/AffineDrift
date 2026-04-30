$ErrorActionPreference = "Continue"
$env:GIT_TERMINAL_PROMPT="0"
gh auth setup-git

$prs = @(1628, 1629, 1630, 1631, 1632)
foreach ($pr in $prs) {
    Write-Host "==========================="
    Write-Host "Processing PR $pr"
    Write-Host "==========================="
    
    # Clean workspace explicitly without git clean
    git merge --abort -q 2>$null
    git reset --hard HEAD

    # Checkout exact PR head
    git fetch origin pull/$pr/head:pr-$pr
    git checkout pr-$pr -f

    # Force auto-fixes
    ruff check --fix --unsafe-fixes .
    ruff format .
    black .

    # Commit fixes if there are any
    git add -u
    git commit -m "chore: auto-fix formatting and violations"
    
    # Push back
    git push origin HEAD --force

    # Attempt immediate merge
    $merge_out = gh pr merge $pr --merge 2>&1
    if ($merge_out -match "is not mergeable" -or $merge_out -match "unstable status" -or $merge_out -match "required status checks") {
        Write-Host "Strict checks required, falling back to --auto..."
        gh pr merge $pr --auto --merge
    } else {
        Write-Host "Merged immediately."
    }
}
Write-Host "All done with AffineDrift!"
