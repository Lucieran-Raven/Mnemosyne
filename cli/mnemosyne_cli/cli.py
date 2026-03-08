"""
Mnemosyne CLI - Automation tool for managing Mnemosyne infrastructure
"""

import click
import subprocess
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import yaml

console = Console()

PROJECT_ROOT = Path(__file__).parent.parent.parent

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Mnemosyne CLI - Manage your AI Memory Layer infrastructure"""
    pass

@cli.group()
def deploy():
    """Deploy services to cloud infrastructure"""
    pass

@deploy.command()
@click.option("--env", default="staging", help="Environment (staging/production)")
@click.option("--region", default="us-central1", help="GCP region")
def api(env, region):
    """Deploy API service to Cloud Run"""
    console.print(Panel(f"Deploying API to {env}...", style="blue"))
    
    try:
        # Build and deploy to Cloud Run
        subprocess.run([
            "gcloud", "run", "deploy", f"mnemosyne-api-{env}",
            "--source", str(PROJECT_ROOT / "api"),
            "--region", region,
            "--platform", "managed",
            "--allow-unauthenticated"
        ], check=True)
        console.print("[green]API deployed successfully![/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Deployment failed: {e}[/red]")
        sys.exit(1)

@deploy.command()
@click.option("--env", default="staging", help="Environment")
def dashboard(env):
    """Deploy dashboard to Vercel"""
    console.print(Panel(f"Deploying Dashboard to {env}...", style="blue"))
    
    try:
        subprocess.run([
            "vercel", "--prod" if env == "production" else ""
        ], cwd=PROJECT_ROOT / "dashboard", check=True)
        console.print("[green]Dashboard deployed successfully![/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Deployment failed: {e}[/red]")
        sys.exit(1)

@deploy.command()
@click.option("--env", default="staging", help="Environment")
def infra(env):
    """Deploy infrastructure with Terraform"""
    console.print(Panel(f"Deploying infrastructure to {env}...", style="blue"))
    
    infra_dir = PROJECT_ROOT / "infra"
    try:
        subprocess.run(["terraform", "init"], cwd=infra_dir, check=True)
        subprocess.run(["terraform", "apply", f"-var=env={env}", "-auto-approve"], 
                      cwd=infra_dir, check=True)
        console.print("[green]Infrastructure deployed successfully![/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Infrastructure deployment failed: {e}[/red]")
        sys.exit(1)

@cli.group()
def status():
    """Check system health and status"""
    pass

@status.command()
def all():
    """Check all services status"""
    table = Table(title="Mnemosyne System Status", box=box.ROUNDED)
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("URL", style="blue")
    table.add_column("Version", style="yellow")
    
    services = [
        ("API", "gcloud run services describe mnemosyne-api-staging --region us-central1 --format 'value(status.conditions[0].status)'", "https://api.mnemosyne.dev"),
        ("Dashboard", "vercel list --confirm", "https://dashboard.mnemosyne.dev"),
        ("Database", "pg_isready -h $DB_HOST", "internal"),
        ("Redis", "redis-cli -u $REDIS_URL ping", "internal"),
        ("Pinecone", "curl -s $PINECONE_HOST", "internal"),
    ]
    
    for name, check_cmd, url in services:
        try:
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, timeout=10)
            is_healthy = result.returncode == 0 and ("yes" in result.stdout.lower() or "true" in result.stdout.lower() or "pong" in result.stdout.lower())
            status_text = "[green]Healthy[/green]" if is_healthy else "[red]Down[/red]"
        except:
            status_text = "[yellow]Unknown[/yellow]"
        
        table.add_row(name, status_text, url, "v0.1.0")
    
    console.print(table)

@status.command()
def queue():
    """Check background job queue status"""
    console.print(Panel("Queue Status", style="blue"))
    try:
        result = subprocess.run([
            "gcloud", "tasks", "queues", "describe", "mnemosyne-distillation",
            "--location", "us-central1", "--format", "table(stats.tasks_count, stats.execution_count)"
        ], capture_output=True, text=True, check=True)
        console.print(result.stdout)
    except subprocess.CalledProcessError:
        console.print("[yellow]Queue information unavailable[/yellow]")

@cli.group()
def logs():
    """View service logs"""
    pass

@logs.command()
@click.option("--service", default="api", help="Service name")
@click.option("--follow", "-f", is_flag=True, help="Follow logs")
def service(service, follow):
    """View service logs from Cloud Run"""
    cmd = ["gcloud", "logging", "read", f"resource.labels.service_name=mnemosyne-{service}-staging"]
    if follow:
        cmd.append("--follow")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped following logs[/yellow]")

@logs.command()
def errors():
    """View recent errors across all services"""
    console.print(Panel("Recent Errors (last 1 hour)", style="red"))
    try:
        subprocess.run([
            "gcloud", "logging", "read", 
            'severity>=ERROR AND resource.labels.service_name:"mnemosyne"',
            "--limit", "50"
        ])
    except subprocess.CalledProcessError:
        console.print("[yellow]Could not retrieve errors[/yellow]")

@cli.group()
def db():
    """Database management commands"""
    pass

@db.command()
def migrate():
    """Run database migrations"""
    console.print(Panel("Running database migrations...", style="blue"))
    try:
        subprocess.run([
            "alembic", "upgrade", "head"
        ], cwd=PROJECT_ROOT / "api", check=True)
        console.print("[green]Migrations completed![/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Migration failed: {e}[/red]")

@db.command()
def backup():
    """Trigger database backup"""
    console.print(Panel("Creating database backup...", style="blue"))
    try:
        result = subprocess.run([
            "gcloud", "sql", "backups", "create",
            "--instance", "mnemosyne-postgres",
            "--description", f"Manual backup {datetime.now().isoformat()}"
        ], check=True, capture_output=True, text=True)
        console.print("[green]Backup initiated![/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Backup failed: {e}[/red]")

@db.command()
def reset():
    """Reset local database (DANGER)"""
    if not click.confirm("This will DELETE all local data. Are you sure?"):
        return
    
    console.print(Panel("Resetting local database...", style="red"))
    try:
        subprocess.run([
            "docker-compose", "down", "-v"
        ], cwd=PROJECT_ROOT, check=True)
        subprocess.run([
            "docker-compose", "up", "-d", "postgres", "redis"
        ], cwd=PROJECT_ROOT, check=True)
        console.print("[green]Database reset complete![/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Reset failed: {e}[/red]")

@cli.group()
def config():
    """Manage configuration and secrets"""
    pass

@config.command()
def validate():
    """Validate all configuration files"""
    console.print(Panel("Validating configuration...", style="blue"))
    
    errors = []
    
    # Check API config
    api_config = PROJECT_ROOT / "api" / "app" / "core" / "config.py"
    if not api_config.exists():
        errors.append("API config not found")
    
    # Check Docker Compose
    compose_file = PROJECT_ROOT / "docker-compose.yml"
    if compose_file.exists():
        try:
            subprocess.run(["docker-compose", "config"], cwd=PROJECT_ROOT, 
                          check=True, capture_output=True)
        except subprocess.CalledProcessError:
            errors.append("Docker Compose config is invalid")
    
    if errors:
        for error in errors:
            console.print(f"[red]✗ {error}[/red]")
        sys.exit(1)
    else:
        console.print("[green]All configurations valid![/green]")

@config.command()
def env():
    """Show required environment variables"""
    required_vars = [
        ("GEMINI_API_KEY", "Google AI Studio API key"),
        ("PINECONE_API_KEY", "Pinecone vector DB API key"),
        ("PINECONE_HOST", "Pinecone index host"),
        ("DATABASE_URL", "PostgreSQL connection string"),
        ("REDIS_URL", "Redis connection string"),
        ("CLERK_SECRET_KEY", "Clerk authentication secret"),
        ("CLERK_PUBLISHABLE_KEY", "Clerk public key"),
        ("GOOGLE_CLOUD_PROJECT", "GCP project ID"),
    ]
    
    table = Table(title="Required Environment Variables", box=box.ROUNDED)
    table.add_column("Variable", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Status", style="green")
    
    import os
    for var, desc in required_vars:
        status = "[green]Set[/green]" if os.getenv(var) else "[red]Missing[/red]"
        table.add_row(var, desc, status)
    
    console.print(table)

@cli.group()
def dev():
    """Development utilities"""
    pass

@dev.command()
def setup():
    """Setup local development environment"""
    console.print(Panel("Setting up development environment...", style="blue"))
    
    steps = [
        ("Creating Python virtual environment", "python -m venv .venv"),
        ("Installing API dependencies", "pip install -r api/requirements.txt"),
        ("Installing SDK dependencies", "pip install -e sdk/"),
        ("Installing CLI dependencies", "pip install -e cli/"),
        ("Starting local services", "docker-compose up -d postgres redis"),
    ]
    
    for desc, cmd in steps:
        console.print(f"[blue]{desc}...[/blue]")
        try:
            subprocess.run(cmd, cwd=PROJECT_ROOT, shell=True, check=True)
            console.print(f"[green]✓[/green]")
        except subprocess.CalledProcessError as e:
            console.print(f"[red]✗ Failed: {e}[/red]")
            sys.exit(1)
    
    console.print("\n[green]Development environment ready![/green]")
    console.print("Run [cyan]mnemosyne dev start[/cyan] to start all services")

@dev.command()
def start():
    """Start all local services"""
    console.print(Panel("Starting local services...", style="blue"))
    
    services = [
        ("Database", "docker-compose up -d postgres redis"),
        ("API", "cd api && uvicorn app.main:app --reload --port 8000"),
        ("Dashboard", "cd dashboard && npm run dev"),
    ]
    
    for name, cmd in services:
        console.print(f"[blue]Starting {name}...[/blue]")
        # In real implementation, would use multiprocessing or tmux
        console.print(f"[yellow]Run manually:[/yellow] {cmd}")

@dev.command()
def test():
    """Run all tests"""
    console.print(Panel("Running test suite...", style="blue"))
    
    test_dirs = [
        ("API Tests", "api"),
        ("SDK Tests", "sdk"),
        ("CLI Tests", "cli"),
    ]
    
    for name, dir in test_dirs:
        console.print(f"\n[blue]{name}:[/blue]")
        try:
            subprocess.run(
                ["pytest", "-v", "--tb=short"],
                cwd=PROJECT_ROOT / dir,
                check=True
            )
        except subprocess.CalledProcessError:
            console.print(f"[red]{name} failed[/red]")

@dev.command()
def lint():
    """Run linters on all code"""
    console.print(Panel("Running linters...", style="blue"))
    
    linters = [
        ("API (Ruff)", "api", "ruff check ."),
        ("API (MyPy)", "api", "mypy app/"),
        ("SDK (Ruff)", "sdk", "ruff check ."),
        ("Dashboard (ESLint)", "dashboard", "npm run lint"),
    ]
    
    for name, dir, cmd in linters:
        console.print(f"[blue]{name}...[/blue]")
        try:
            subprocess.run(cmd, cwd=PROJECT_ROOT / dir, shell=True, check=True)
            console.print(f"[green]✓[/green]")
        except subprocess.CalledProcessError:
            console.print(f"[red]✗ {name} has issues[/red]")

@cli.command()
def version():
    """Show version information"""
    console.print(Panel("Mnemosyne CLI v0.1.0", style="blue"))
    console.print("API: v0.1.0")
    console.print("SDK: v0.1.0")
    console.print("Dashboard: v0.1.0")

def main():
    cli()

if __name__ == "__main__":
    main()
