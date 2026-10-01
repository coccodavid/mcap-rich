#!/usr/bin/env python3
import os
import sys
import time
import shutil
import platform
import json
import urllib.request
import subprocess
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm
from rich.progress import (
    Progress, TextColumn, BarColumn, TaskProgressColumn, 
    TimeRemainingColumn, TransferSpeedColumn, DownloadColumn
)

console = Console()

def get_system_architecture():
    """Detect the OS and architecture to map to Foxglove's release names."""
    sys_os = platform.system().lower()
    machine = platform.machine().lower()

    if sys_os == "linux":
        target_os = "linux"
    elif sys_os == "darwin":
        target_os = "macos"
    elif sys_os == "windows":
        target_os = "windows"
    else:
        return None, None

    if machine in ["x86_64", "amd64"]:
        target_arch = "amd64"
    elif machine in ["arm64", "aarch64"]:
        target_arch = "arm64"
    else:
        return target_os, None

    return target_os, target_arch

def download_mcap_cli():
    """Fetch the latest mcap CLI from GitHub API and download it."""
    target_os, target_arch = get_system_architecture()
    if not target_os or not target_arch:
        console.print("[red]✘ Unsupported OS or architecture for automatic download.[/red]")
        sys.exit(1)

    binary_name = f"mcap-{target_os}-{target_arch}"
    if target_os == "windows":
        binary_name += ".exe"

    console.print("[cyan]Searching for the latest mcap CLI release on GitHub...[/cyan]")
    api_url = "https://api.github.com/repos/foxglove/mcap/releases"
    
    try:
        req = urllib.request.Request(api_url, headers={'User-Agent': 'mcap-rich-cli'})
        with urllib.request.urlopen(req) as response:
            releases = json.loads(response.read().decode())
    except Exception as e:
        console.print(f"[red]✘ Failed to reach GitHub API: {e}[/red]")
        sys.exit(1)

    # Find the latest release tagged as a CLI release
    download_url = None
    for release in releases:
        if release.get("tag_name", "").startswith("mcap-cli/"):
            for asset in release.get("assets", []):
                if asset.get("name") == binary_name:
                    download_url = asset.get("browser_download_url")
                    break
        if download_url:
            break

    if not download_url:
        console.print(f"[red]✘ Could not find a binary for {binary_name}.[/red]")
        sys.exit(1)

    # Determine installation directory (e.g. ~/.local/bin)
    install_dir = Path.home() / ".local" / "bin"
    install_dir.mkdir(parents=True, exist_ok=True)
    executable_path = install_dir / ("mcap.exe" if target_os == "windows" else "mcap")

    # Download with a rich progress bar
    progress_ui = Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        DownloadColumn(),
        TransferSpeedColumn()
    )

    try:
        with urllib.request.urlopen(download_url) as response:
            total_length = int(response.info().get("Content-Length", 0))
            
            with progress_ui:
                task_id = progress_ui.add_task("Downloading mcap...", total=total_length)
                
                with open(executable_path, "wb") as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        progress_ui.update(task_id, advance=len(chunk))
        
        # Make it executable on Linux/macOS
        if target_os != "windows":
            executable_path.chmod(executable_path.stat().st_mode | 0o111)
            
        console.print(f"[green]✔ mcap CLI successfully installed in {install_dir}[/green]")
        
        # Add to PATH for the current python runtime if not already there
        os.environ["PATH"] = str(install_dir) + os.pathsep + os.environ.get("PATH", "")
        return True

    except Exception as e:
        console.print(f"[red]✘ Download failed: {e}[/red]")
        if executable_path.exists():
            executable_path.unlink()
        sys.exit(1)


def check_mcap_cli():
    """Check if the mcap CLI tool is installed, prompt download if missing."""
    if shutil.which("mcap") is None:
        console.print("[yellow]The official 'mcap' CLI tool is required but was not found in your PATH.[/yellow]")
        if Confirm.ask("Would you like to automatically download and install it now?"):
            download_mcap_cli()
        else:
            sys.exit("Error: 'mcap' CLI executable is missing. Please install it manually.")

def get_input_and_output(args):
    """Extract input files and output file from CLI arguments."""
    inputs = [arg for arg in args if arg.endswith('.mcap')]
    output = None
    if "-o" in args:
        out_idx = args.index("-o") + 1
        if out_idx < len(args):
            output = args[out_idx]
    return inputs, output

def main():
    args = sys.argv[1:]
    if not args:
        sys.exit("Usage: mcap-rich <mcap command with arguments>")

    check_mcap_cli()

    command_name = args[0]
    inputs, output = get_input_and_output(args)

    if not inputs or not output:
        subprocess.run(["mcap"] + args)
        return

    total_input_size = sum(os.path.getsize(f) for f in inputs if os.path.exists(f))
    total_size_mb = total_input_size / (1024 * 1024)
    total_size_str = f"{total_size_mb / 1024:.2f} GB" if total_size_mb > 1024 else f"{total_size_mb:.1f} MB"
    
    progress_ui = Progress(
        TextColumn("{task.description}"),          
        BarColumn(),                               
        TaskProgressColumn(),                      
        TextColumn("[blue]{task.fields[current_size_str]} / {task.fields[total_size_str]}"), 
        TransferSpeedColumn(),
        TimeRemainingColumn(),                     
    )

    mcap_cmd = ["mcap"] + args
    
    with progress_ui:
        task_id = progress_ui.add_task(
            f"[yellow]Executing mcap {command_name}...", 
            total=total_input_size, 
            current_size_str="0.0 MB",
            total_size_str=total_size_str
        )
        
        process = subprocess.Popen(mcap_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        
        while process.poll() is None:
            if os.path.exists(output):
                current_size = os.path.getsize(output)
                size_mb = current_size / (1024 * 1024)
                size_str = f"{size_mb / 1024:.2f} GB" if size_mb > 1024 else f"{size_mb:.1f} MB"
                
                progress_ui.update(task_id, completed=current_size, current_size_str=size_str)
            time.sleep(0.5)

        if process.returncode == 0:
            progress_ui.update(task_id, completed=total_input_size, description=f"[green]✔ mcap {command_name} completed")
        else:
            _, err = process.communicate()
            err_msg = err.decode('utf-8').strip() if err else "Unknown error"
            
            err_msg_short = err_msg.split('\n')[0]
            progress_ui.update(task_id, description=f"[red]✘ Error: {err_msg_short}")
            
            if output and os.path.exists(output):
                os.remove(output)

if __name__ == "__main__":
    main()