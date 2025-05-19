import click
from scanner import scan_model
from viewer import view_model
from autoscan import automate_scans

@click.group()
def cli():
    """BackdoorSnitch - Neural Network Model Backdoor Scanner"""
    pass

@cli.command()
@click.argument('model_path')
@click.option('--output', default='scan_results.json', help='File to save the scan output (JSON)')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def scan(model_path, output, verbose):
    """Scan an ONNX model for backdoors"""
    scan_model(model_path, output, verbose)

@cli.command()
@click.argument('model_path')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def view(model_path, verbose):
    """View metadata of the ONNX model"""
    view_model(model_path, verbose)

@cli.command()
@click.argument('directory')
@click.option('--interval', default=3600, help='Interval in seconds between scans')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def autoscan(directory, interval, verbose):
    """Automatically scan all ONNX models in a directory at intervals"""
    automate_scans(directory, interval, verbose)

if __name__ == '__main__':
    cli()
