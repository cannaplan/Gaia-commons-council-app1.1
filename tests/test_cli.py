"""Tests for the CLI module."""

import json
from click.testing import CliRunner

from app.cli import cli


def test_run_scenario_basic():
    """Test run-scenario command with basic arguments."""
    runner = CliRunner()
    result = runner.invoke(cli, ['run-scenario', '--name', 'demo'])
    
    # Should exit with code 0
    assert result.exit_code == 0
    
    # Output should be valid JSON
    output_data = json.loads(result.output)
    
    # Check expected keys
    assert 'id' in output_data
    assert 'name' in output_data
    assert 'status' in output_data
    assert 'result' in output_data
    assert 'started_at' in output_data
    assert 'finished_at' in output_data
    
    # Check values
    assert output_data['name'] == 'demo'
    assert output_data['status'] == 'finished'
    assert 'summary' in output_data['result']
    assert 'input_config' in output_data['result']


def test_run_scenario_with_json_config(tmp_path):
    """Test run-scenario command with JSON config file."""
    # Create a temporary config file
    config_file = tmp_path / "config.json"
    config_data = {"param1": "value1", "param2": 42}
    config_file.write_text(json.dumps(config_data))
    
    runner = CliRunner()
    result = runner.invoke(cli, [
        'run-scenario',
        '--name', 'test-scenario',
        '--config', str(config_file)
    ])
    
    assert result.exit_code == 0
    output_data = json.loads(result.output)
    
    # Config should be in result
    assert output_data['result']['input_config'] == config_data


def test_run_scenario_with_output_file(tmp_path):
    """Test run-scenario command with output file."""
    output_file = tmp_path / "output.json"
    
    runner = CliRunner()
    result = runner.invoke(cli, [
        'run-scenario',
        '--name', 'demo',
        '--output', str(output_file)
    ])
    
    assert result.exit_code == 0
    
    # Check output file was created
    assert output_file.exists()
    
    # Check output file contains valid JSON
    output_data = json.loads(output_file.read_text())
    assert output_data['name'] == 'demo'
