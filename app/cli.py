"""CLI module for Gaia Commons Council."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
import yaml

from app.scenario import run_scenario


@click.group()
def cli():
    """Gaia Commons Council CLI."""
    pass


@cli.command(name='run-scenario')
@click.option('--name', required=True, help='Name of the scenario to run')
@click.option('--config', type=click.Path(exists=True), help='Path to JSON or YAML config file')
@click.option('--output', type=click.Path(), help='Path to write output JSON')
@click.option('--async', 'async_mode', is_flag=True, help='Run in background (inline for CLI)')
def run_scenario_cmd(name: str, config: Optional[str], output: Optional[str], async_mode: bool):
    """
    Run a scenario with the given name and optional configuration.
    
    For CLI usage, --async flag runs inline (background execution only available via HTTP API).
    """
    try:
        # Load config if provided
        config_dict = None
        if config:
            config_path = Path(config)
            with open(config_path, 'r') as f:
                if config_path.suffix in ['.yaml', '.yml']:
                    config_dict = yaml.safe_load(f)
                elif config_path.suffix == '.json':
                    config_dict = json.load(f)
                else:
                    raise ValueError(f"Unsupported config file format: {config_path.suffix}")
        
        # Run the scenario (always inline for CLI, even with --async flag)
        result = run_scenario(name=name, config=config_dict)
        
        # Convert to JSON
        output_json = json.dumps(result, indent=2)
        
        # Write to output file if specified
        if output:
            output_path = Path(output)
            output_path.write_text(output_json)
        
        # Print to stdout
        print(output_json)
        
        sys.exit(0)
        
    except Exception as e:
        error_msg = {"error": str(e), "type": type(e).__name__}
        print(json.dumps(error_msg, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    cli()
