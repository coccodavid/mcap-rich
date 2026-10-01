#!/usr/bin/env python3
import os
import sys
import time
import shutil
import subprocess
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, TransferSpeedColumn

def check_mcap_cli():
    """Check if the mcap CLI tool is installed and available in PATH."""
    if shutil.which("mcap") is None:
        sys.exit("Error: 'mcap' CLI executable not found in PATH. Please ensure it is installed and accessible.")

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

    # Fallback to standard execution if no input/output is intercepted
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
            # Estrae l'errore generato da mcap e lo mostra nella UI
            _, err = process.communicate()
            err_msg = err.decode('utf-8').strip() if err else "Unknown error"
            progress_ui.update(task_id, description=f"[red]✘ Error: {err_msg}")

if __name__ == "__main__":
    main()
