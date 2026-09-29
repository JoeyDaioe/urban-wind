import argparse
import ast
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
ROOT = Path(__file__).resolve().parent
SCRIPTS = sorted((ROOT / 'scripts').glob('fig*.py'))

def child(script, dpi):
    sys.path.insert(0, str(ROOT / 'src'))
    extra = os.environ.get('WIND_FIGURE_DEPENDENCIES')
    if extra:
        sys.path.insert(0, extra)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.figure import Figure
    import numpy as np
    destination = ROOT / 'outputs' / script.stem
    destination.mkdir(parents=True, exist_ok=True)
    os.environ['WIND_FIGURE_OUTPUT'] = str(destination)
    original_save = Figure.savefig
    saved = []

    def savefig(fig, fname, *args, **kwargs):
        from matplotlib.collections import QuadMesh
        for artist in fig.findobj(match=QuadMesh):
            artist.set_rasterized(True)
        path = Path(fname)
        if not path.is_absolute():
            path = destination / path.name
        path.parent.mkdir(parents=True, exist_ok=True)
        kwargs['dpi'] = dpi
        saved.append(str(path))
        return original_save(fig, path, *args, **kwargs)
    Figure.savefig = savefig
    plt.show = lambda *a, **k: None
    plt.rcdefaults()
    np.random.seed(20260928)
    os.chdir(destination)
    sys.argv = [str(script)]
    runpy.run_path(str(script), run_name='__main__')
    for index, number in enumerate(plt.get_fignums(), 1):
        fig = plt.figure(number)
        for ext in ['png', 'pdf', 'svg']:
            fig.savefig(destination / f'{script.stem}_{index}.{ext}', bbox_inches='tight', facecolor='white')
    if not saved:
        raise RuntimeError('Script produced no saved figure; do not report this as a successful run')
    (destination / 'run_manifest.json').write_text(json.dumps({'script': script.name, 'dpi': dpi, 'files': sorted(set(saved))}, indent=2), encoding='utf-8')
    plt.close('all')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--figure', choices=['1', '2', '3', '4', 'all'], default='all')
    parser.add_argument('--panel', help='Exact script stem, e.g. fig3_ef_pm25_map')
    parser.add_argument('--config', type=Path)
    parser.add_argument('--dpi', type=int, default=300)
    parser.add_argument('--check', action='store_true', help='Compile scripts and inspect configured file locations without plotting')
    parser.add_argument('--_child', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.config:
        os.environ['WIND_FIGURE_CONFIG'] = str(args.config.resolve())
    if args._child:
        return child(args._child.resolve(), args.dpi)
    selected = [p for p in SCRIPTS if (args.figure == 'all' or p.name.startswith('fig' + args.figure + '_')) and (args.panel is None or p.stem == args.panel)]
    if not selected:
        parser.error('No matching figure scripts')
    if args.list:
        for p in selected:
            print(p.stem)
        return
    if args.check:
        for p in [*SCRIPTS, *(ROOT / 'src').glob('*.py')]:
            ast.parse(p.read_text(encoding='utf-8'), filename=str(p))
        sys.path.insert(0, str(ROOT / 'src'))
        from project import input_file
        keys = json.loads((ROOT / 'config.example.json').read_text(encoding='utf-8'))['inputs']
        missing = [key for key in keys if not input_file(key).exists()]
        print(json.dumps({'scripts_compile': True, 'configured_inputs': len(keys), 'missing_files': missing}, indent=2))
        return
    results = []
    for p in selected:
        print('Rendering ' + p.stem, flush=True)
        folder = ROOT / 'outputs' / p.stem
        folder.mkdir(parents=True, exist_ok=True)
        with (folder / 'run.log').open('w', encoding='utf-8') as log:
            code = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--_child', str(p), '--dpi', str(args.dpi)], stdout=log, stderr=subprocess.STDOUT).returncode
        results.append({'script': p.name, 'exit_code': code})
        print('  ' + ('OK' if code == 0 else 'FAILED: see outputs/' + p.stem + '/run.log'), flush=True)
    (ROOT / 'outputs/last_run.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
    if any((r['exit_code'] != 0 for r in results)):
        sys.exit(1)
if __name__ == '__main__':
    main()
