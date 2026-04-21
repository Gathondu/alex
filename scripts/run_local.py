#!/usr/bin/env python3
"""
Run both frontend and backend locally for development.
This script starts the NextJS frontend and FastAPI backend in parallel.
"""

import os
import sys
import subprocess
import signal
import time
import socket
from pathlib import Path

# Track subprocesses for cleanup
processes = []
npm_cmd = "npm.cmd" if os.name == "nt" else "npm"

def cleanup(signum=None, frame=None):
    """Clean up all subprocess on exit"""
    print("\n🛑 Shutting down services...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except:
            proc.kill()
    sys.exit(0)

# Register cleanup handlers
signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def check_requirements():
    """Check if required tools are installed"""
    checks = []

    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        node_version = result.stdout.strip()
        checks.append(f"✅ Node.js: {node_version}")
    except FileNotFoundError:
        checks.append("❌ Node.js not found - please install Node.js")

    # Check npm
    try:
        result = subprocess.run([npm_cmd, "--version"], capture_output=True, text=True)
        npm_version = result.stdout.strip()
        checks.append(f"✅ npm: {npm_version}")
    except FileNotFoundError:
        checks.append("❌ npm not found - please install npm")

    # Check uv (which manages Python for us)
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        uv_version = result.stdout.strip()
        checks.append(f"✅ uv: {uv_version}")
    except FileNotFoundError:
        checks.append("❌ uv not found - please install uv")

    print("\n📋 Prerequisites Check:")
    for check in checks:
        print(f"  {check}")

    # Exit if any critical tools are missing
    if any("❌" in check for check in checks):
        print("\n⚠️  Please install missing dependencies and try again.")
        sys.exit(1)

def check_env_files():
    """Check if environment files exist"""
    project_root = Path(__file__).parent.parent

    root_env = project_root / ".env"
    frontend_env = project_root / "frontend" / ".env.local"

    missing = []

    if not root_env.exists():
        missing.append(".env (root project file)")
    if not frontend_env.exists():
        missing.append("frontend/.env.local")

    if missing:
        print("\n⚠️  Missing environment files:")
        for file in missing:
            print(f"  - {file}")
        print("\nPlease create these files with the required configuration.")
        print("The root .env should have all backend variables from Parts 1-7.")
        print("The frontend/.env.local should have Clerk keys.")
        sys.exit(1)

    print("✅ Environment files found")

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a TCP port is currently in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0

def get_port_owner_info(port: int) -> str:
    """Best-effort process owner lookup for an in-use port."""
    if os.name != "nt":
        return ""

    try:
        netstat = subprocess.run(
            ["netstat", "-ano", "-p", "tcp"],
            capture_output=True,
            text=True,
            check=True
        )
        for line in netstat.stdout.splitlines():
            line = line.strip()
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                pid = parts[-1]
                return f"(PID {pid})"
    except Exception:
        return ""

    return ""

def check_required_ports():
    """Ensure required local ports are free before launching services."""
    required_ports = {
        8000: "FastAPI backend",
        3000: "NextJS frontend",
    }

    conflicts = []
    for port, service_name in required_ports.items():
        if is_port_in_use(port):
            owner = get_port_owner_info(port)
            owner_suffix = f" {owner}" if owner else ""
            conflicts.append(f"  - Port {port} is already in use{owner_suffix} ({service_name})")

    if conflicts:
        print("\n⚠️  Required ports are unavailable:")
        for conflict in conflicts:
            print(conflict)
        print("\nPlease stop the existing processes or change dev server ports, then run again.")
        sys.exit(1)

def print_startup_failure(proc, service_name: str):
    """Print startup diagnostics when a service exits early."""
    code = proc.poll()
    print(f"  ❌ {service_name} process exited before startup completed (exit code: {code})")

    try:
        stdout, stderr = proc.communicate(timeout=2)
    except Exception:
        stdout, stderr = "", ""

    if stdout and stdout.strip():
        print(f"  --- {service_name} stdout ---")
        print(stdout.strip())
    if stderr and stderr.strip():
        print(f"  --- {service_name} stderr ---")
        print(stderr.strip())

def start_backend():
    """Start the FastAPI backend"""
    backend_dir = Path(__file__).parent.parent / "backend" / "api"

    print("\n🚀 Starting FastAPI backend...")

    # Check if dependencies are installed
    if not (backend_dir / ".venv").exists() and not (backend_dir / "uv.lock").exists():
        print("  Installing backend dependencies...")
        subprocess.run(["uv", "sync"], cwd=backend_dir, check=True)

    # Start the backend
    proc = subprocess.Popen(
        ["uv", "run", "main.py"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    processes.append(proc)

    # Wait for backend to start
    print("  Waiting for backend to start...")
    for _ in range(30):  # 30 second timeout
        if proc.poll() is not None:
            print_startup_failure(proc, "Backend")
            cleanup()
        try:
            import httpx
            response = httpx.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("  ✅ Backend running at http://localhost:8000")
                print("     API docs: http://localhost:8000/docs")
                return proc
        except:
            time.sleep(1)

    print("  ❌ Backend failed to start")
    cleanup()

def start_frontend():
    """Start the NextJS frontend"""
    frontend_dir = Path(__file__).parent.parent / "frontend"

    print("\n🚀 Starting NextJS frontend...")

    # Check if dependencies are installed
    if not (frontend_dir / "node_modules").exists():
        print("  Installing frontend dependencies...")
        subprocess.run([npm_cmd, "install"], cwd=frontend_dir, check=True)

    # Start the frontend
    proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Combine stderr with stdout
        text=True,
        bufsize=1
    )
    processes.append(proc)

    # Wait for frontend to start
    print("  Waiting for frontend to start...")
    import httpx
    for i in range(30):  # 30 second timeout
        # If the process exits early, fail fast
        if proc.poll() is not None:
            print_startup_failure(proc, "Frontend")
            cleanup()

        # Start probing after a short warm-up
        if i > 5:
            try:
                httpx.get("http://localhost:3000", timeout=1)
                print("  ✅ Frontend running at http://localhost:3000")
                return proc
            except httpx.ConnectError:
                pass  # Server not ready yet
            except:
                # Any non-connection response means the server is up
                print("  ✅ Frontend running at http://localhost:3000")
                return proc

        time.sleep(1)

    print("  ❌ Frontend failed to start")
    cleanup()

def monitor_processes():
    """Monitor running processes and show their output"""
    print("\n" + "="*60)
    print("🎯 Alex Financial Advisor - Local Development")
    print("="*60)
    print("\n📍 Services:")
    print("  Frontend: http://localhost:3000")
    print("  Backend:  http://localhost:8000")
    print("  API Docs: http://localhost:8000/docs")
    print("\n📝 Logs will appear below. Press Ctrl+C to stop.\n")
    print("="*60 + "\n")

    # Monitor processes
    while True:
        for proc in processes:
            # Check if process is still running
            if proc.poll() is not None:
                print(f"\n⚠️  A process has stopped unexpectedly!")
                cleanup()

            # Read any available output
            try:
                line = proc.stdout.readline()
                if line:
                    print(f"[LOG] {line.strip()}")
            except:
                pass

        time.sleep(0.1)

def main():
    """Main entry point"""
    print("\n🔧 Alex Financial Advisor - Local Development Setup")
    print("="*50)

    # Check prerequisites
    check_requirements()
    check_env_files()
    check_required_ports()

    # Install httpx if needed
    try:
        import httpx
    except ImportError:
        print("\n📦 Installing httpx for health checks...")
        subprocess.run(["uv", "add", "httpx"], check=True)

    # Start services
    backend_proc = start_backend()
    frontend_proc = start_frontend()

    # Monitor processes
    try:
        monitor_processes()
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()