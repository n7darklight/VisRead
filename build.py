import os
import shutil
import platform
import subprocess
import sys

def main():
    """
    Builds the Flet desktop application into a standalone executable
    by calling the Flet command-line interface.
    """
    # --- Configuration ---
    app_name = "VisRead"
    entry_point = "src/main.py"
    assets_dir = "src/assets"
    
    # --- Platform Detection ---
    system = platform.system().lower()
    if system not in ["windows", "linux", "darwin"]:
        print(f"Unsupported platform: {system}. Exiting build.")
        return

    print(f"Detected Platform: {system.capitalize()}")
    print(f"Starting build for {app_name}...")

    # --- Construct the build command for the Flet CLI ---
    # Determine the correct path separator for --add-data
    separator = ";" if system == "windows" else ":"

    # CORRECTED: Use 'flet pack' with '--add-data' instead of '--assets'
    command = [
        "flet",
        "pack",
        entry_point,
        "--distpath", "dist",
        "--name", app_name,
        "--add-data", f"{assets_dir}{separator}assets",
        "--icon", "src/assets/icon.png",
    ]

    print("\nRunning command:")
    print(" ".join(command))
    print()

    # --- Execute the build command ---
    try:
        # On Windows, shell=True can help find commands in the venv path.
        is_windows = system == "windows"
        subprocess.run(command, check=True, shell=is_windows)
        print("\n-----------------------------------------")
        print(f"Build successful!")
        print(f"Executable for {app_name} is located in the 'dist' folder.")
        print("-----------------------------------------\n")
    except subprocess.CalledProcessError as e:
        print("\n-----------------------------------------")
        print(f"Build failed with error: {e}")
        print("-----------------------------------------\n")
    except FileNotFoundError:
        print("\n-----------------------------------------")
        print("Error: 'flet' command not found.")
        print("Please ensure Flet is installed and your virtual environment is activated.")
        print("-----------------------------------------\n")


if __name__ == "__main__":
    # Clean up previous build directory if it exists
    if os.path.exists("dist"):
        print("Removing previous build directory...")
        shutil.rmtree("dist")

    # --- Auto-configure splash screen for the new Flet build process ---
    # Flet's build process now automatically looks for 'assets/images/splash.png'.
    splash_dir = os.path.join("src", "assets", "images")
    splash_file_path = os.path.join(splash_dir, "splash.png")
    icon_file_path = os.path.join("src", "assets", "icon.png")

    if not os.path.exists(splash_file_path) and os.path.exists(icon_file_path):
        print(f"Creating splash screen image at '{splash_file_path}'...")
        os.makedirs(splash_dir, exist_ok=True)
        shutil.copy(icon_file_path, splash_file_path)
    
    main()
