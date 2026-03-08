import subprocess
import sys

def run_git_command(cmd, cwd=r'C:\Users\HP\CascadeProjects\mnemosyne'):
    """Run a git command and return output"""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        shell=True
    )
    return result

# Check git status
print("=== Git Status ===")
result = run_git_command('git status')
print(result.stdout)
print(result.stderr)

# Check current branch
print("\n=== Current Branch ===")
result = run_git_command('git branch -v')
print(result.stdout)

# Push to origin
print("\n=== Pushing to GitHub ===")
result = run_git_command('git push origin main --force')
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
