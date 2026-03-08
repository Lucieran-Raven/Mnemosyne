#!/usr/bin/env pwsh
# Mnemosyne GitHub Secrets Setup Script
# Run this to set all required secrets for deployment

param(
    [Parameter(Mandatory=$false)]
    [string]$NetlifyAuthToken = "",
    
    [Parameter(Mandatory=$false)]
    [string]$NetlifySiteId = ""
)

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Mnemosyne GitHub Secrets Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if gh CLI is installed
try {
    $ghVersion = gh --version 2>$null
    Write-Host "✓ GitHub CLI (gh) found" -ForegroundColor Green
} catch {
    Write-Host "✗ GitHub CLI (gh) not found. Install from: https://cli.github.com/" -ForegroundColor Red
    exit 1
}

# Check if logged in
try {
    $authStatus = gh auth status 2>&1
    if ($authStatus -match "Logged in") {
        Write-Host "✓ Authenticated with GitHub" -ForegroundColor Green
    } else {
        throw "Not logged in"
    }
} catch {
    Write-Host "✗ Not logged into GitHub CLI. Run: gh auth login" -ForegroundColor Red
    exit 1
}

# Secrets to set
$secrets = @{
    "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY" = "pk_test_cHJlbWl1bS1raWQtODAuY2xlcmsuYWNjb3VudHMuZGV2JA"
    "CLERK_SECRET_KEY" = "sk_test_rHMXD8hVbc3LFJopYLsFMi4lvAcp4lQ1kId1nBVFUD"
}

# Add Netlify secrets if provided
if ($NetlifyAuthToken) {
    $secrets["NETLIFY_AUTH_TOKEN"] = $NetlifyAuthToken
}
if ($NetlifySiteId) {
    $secrets["NETLIFY_SITE_ID"] = $NetlifySiteId
}

Write-Host ""
Write-Host "Setting secrets for repository: Lucieran-Raven/Mnemosyne" -ForegroundColor Yellow
Write-Host ""

foreach ($secret in $secrets.GetEnumerator()) {
    $name = $secret.Key
    $value = $secret.Value
    
    Write-Host "Setting $name..." -NoNewline
    
    try {
        $value | gh secret set $name --repo="Lucieran-Raven/Mnemosyne" 2>$null
        Write-Host " ✓" -ForegroundColor Green
    } catch {
        Write-Host " ✗ Failed: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Netlify secrets were set
if (-not $NetlifyAuthToken -or -not $NetlifySiteId) {
    Write-Host "⚠ Missing Netlify secrets. To complete setup:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Get Netlify Auth Token:" -ForegroundColor White
    Write-Host "   - Go to https://app.netlify.com/user/applications/personal" -ForegroundColor Gray
    Write-Host "   - Generate new token" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Get Netlify Site ID:" -ForegroundColor White
    Write-Host "   - Create site at https://app.netlify.com/" -ForegroundColor Gray
    Write-Host "   - Site Settings → General → Site Details" -ForegroundColor Gray
    Write-Host "   - Copy 'Site ID'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Run this script again with:" -ForegroundColor White
    Write-Host "   .\setup-github-secrets.ps1 -NetlifyAuthToken 'your-token' -NetlifySiteId 'your-site-id'" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "- Push to main branch to trigger deployment" -ForegroundColor Gray
Write-Host "- Monitor at: https://github.com/Lucieran-Raven/Mnemosyne/actions" -ForegroundColor Gray
