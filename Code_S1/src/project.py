import json
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def input_file(key):
    config = Path(os.environ.get('WIND_FIGURE_CONFIG', ROOT / 'config.local.json'))
    if not config.is_absolute():
        config = ROOT / config
    if not config.exists():
        config = ROOT / 'config.example.json'
    values = json.loads(config.read_text(encoding='utf-8'))['inputs']
    if key not in values:
        raise KeyError(f'Input {key!r} is not configured in {config}')
    path = Path(values[key])
    return path if path.is_absolute() else ROOT / path

def output_dir():
    path = Path(os.environ.get('WIND_FIGURE_OUTPUT', ROOT / 'outputs'))
    path.mkdir(parents=True, exist_ok=True)
    return path
