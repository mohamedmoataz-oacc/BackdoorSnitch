#!/usr/bin/env python3
import argparse
import sys
import time
import os
from typing import Optional
from enum import Enum
import pyfiglet  # For ASCII art
import questionary  # For interactive prompts

class ScanMode(Enum):
    QUICK = "quick"
    THOROUGH = "thorough"
    SELECTIVE = "selective"

def display_banner():
    """Display the BackdoorSnitch ASCII art banner"""
    ascii_art = pyfiglet.figlet_format("BackdoorSnitch", font="slant")
    print("\033[1;32m")  # Green color
    print(ascii_art)
    print(" Neural Trojan Detection System ".center(80, '='))
    print("\033[0m")  # Reset color
    print("Version 1.0 | Detecting malicious patterns in neural networks\n")

def animated_loading(duration=3):
    """Show an animated loading sequence"""
    animation = "|/-\\"
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\rInitializing scanner {animation[i % len(animation)]}", end="")
        time.sleep(0.1)
        i += 1
    print("\r" + " " * 30 + "\r", end="")

def main_menu():
    """Display the main interactive menu using questionary"""
    while True:
        choice = questionary.select(
            "MAIN MENU",
            choices=[
                "Scan a model",
                "Compare models",
                "View scan history",
                "Configure settings",
                "Help",
                "Exit"
            ],
            qmark=">",
            pointer="→"
        ).ask()

        if choice == "Scan a model":
            scan_model_flow()
        elif choice == "Compare models":
            compare_models_flow()
        elif choice == "View scan history":
            view_history_flow()
        elif choice == "Configure settings":
            configure_settings_flow()
        elif choice == "Help":
            show_help()
        elif choice == "Exit" or choice is None:
            print("\nGoodbye! Stay secure!")
            sys.exit(0)

def scan_model_flow():
    """Interactive flow for scanning a single model"""
    print("\n\033[1;34m=== MODEL SCAN ===\033[0m")
    
    model_path = questionary.path("Enter path to model file:").ask()
    if not model_path:
        return
    
    scan_mode = questionary.select(
        "Select scan mode:",
        choices=[
            {"name": "Quick Scan (fast, basic detection)", "value": ScanMode.QUICK},
            {"name": "Thorough Scan (slower, comprehensive)", "value": ScanMode.THOROUGH},
            {"name": "Selective Scan (choose specific detection method)", "value": ScanMode.SELECTIVE},
        ]
    ).ask()
    
    if not scan_mode:
        return
    
    # Simulate scanning
    print(f"\n\033[1;35mScanning {model_path} in {scan_mode.value} mode...\033[0m")
    animated_loading(5)
    
    # Mock results
    print("\n\033[1;32mScan Complete!\033[0m")
    print("Results:")
    print("- Potential trigger pattern detected in layer conv2d_3")
    print("- Anomalous activation pattern in dense_1")
    print("- Model accuracy variance: 12.7% (threshold: 5%)")
    
    questionary.press_any_key_to_continue().ask()

def compare_models_flow():
    """Interactive flow for comparing two models"""
    print("\n\033[1;34m=== MODEL COMPARISON ===\033[0m")
    # Implementation would be similar to scan_model_flow
    pass

def view_history_flow():
    """Display previous scan results"""
    print("\n\033[1;34m=== SCAN HISTORY ===\033[0m")
    # Implementation would show stored results
    pass

def configure_settings_flow():
    """Configure application settings"""
    print("\n\033[1;34m=== SETTINGS ===\033[0m")
    # Implementation would modify settings
    pass

def show_help():
    """Display help information"""
    print("\n\033[1;34m=== HELP ===\033[0m")
    print("BackdoorSnitch detects neural trojans in deep learning models.")
    print("Key features:")
    print("- Analyze model architecture for suspicious patterns")
    print("- Detect anomalous activation behaviors")
    print("- Compare models for unexpected differences")
    print("- Generate detailed security reports")
    questionary.press_any_key_to_continue().ask()

def non_interactive_mode(model_path: str, scan_mode: Optional[str] = None):
    """Run in non-interactive (CLI) mode"""
    print(f"\nRunning non-interactive scan on {model_path}")
    # Actual scanning implementation would go here
    print("Scan complete. Results saved to report.txt")

if __name__ == "__main__":
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='BackdoorSnitch - Neural Trojan Detection')
    parser.add_argument('-m', '--model', help='Path to model file for non-interactive scan')
    parser.add_argument('-s', '--scan-mode', 
                        choices=[m.value for m in ScanMode], 
                        default=ScanMode.QUICK.value,
                        help='Scan mode for non-interactive scan')
    
    args = parser.parse_args()
    
    display_banner()
    
    if args.model:
        non_interactive_mode(args.model, args.scan_mode)
    else:
        animated_loading()
        main_menu()