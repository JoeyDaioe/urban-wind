from project import input_file, output_dir
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
SOURCE = input_file('environment_alpha.csv')
OUTPUT = output_dir()
COLORS = ['#E08E79', '#7ABAF2']
FIGSIZE = (12, 2.5)

def main(style='slim', composite=False):
    if style not in {'slim', 'balanced', 'raincloud', 'density'}:
        raise ValueError(f'Unknown style: {style}')
    columns = ['alpha_urban', 'alpha_rural']
    data = pd.read_csv(SOURCE).dropna(subset=columns)
    data = data.loc[(data[columns] > 0.001).all(axis=1)].copy()
    if len(data) < 2 or not np.isfinite(data[columns].to_numpy()).all():
        raise ValueError('Insufficient or nonfinite alpha data')
    plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman', 'DejaVu Serif'], 'font.size': 13 if composite else 10, 'axes.labelsize': 14 if composite else 11, 'mathtext.fontset': 'stix', 'mathtext.default': 'it', 'axes.linewidth': 0.7, 'xtick.major.width': 0.7, 'ytick.major.width': 0.7, 'xtick.major.size': 3, 'axes.spines.top': False, 'axes.spines.right': False, 'pdf.fonttype': 42, 'svg.fonttype': 'none'})
    fig, (ax, cv_ax) = plt.subplots(1, 2, figsize=(12, 3.7) if composite else FIGSIZE if style == 'slim' else (12, 3.3), sharey=True, gridspec_kw={'width_ratios': [5.8, 1] if composite else [3.8, 1]})
    fig.subplots_adjust(left=0.062, right=0.985, bottom=0.25 if style == 'slim' else 0.19, top=0.94, wspace=0.2 if composite else 0.12)
    if composite:
        cv_position = cv_ax.get_position()
        cv_ax.set_position([cv_position.x0 - 0.018, cv_position.y0, cv_position.width, cv_position.height])
    rng = np.random.default_rng(42)
    records = []
    bounds = []
    for position, (column, label, color) in enumerate(zip(columns, ['Urban', 'Rural'], COLORS)):
        values = data[column].to_numpy()
        kde = gaussian_kde(values)
        bandwidth = float(np.sqrt(kde.covariance[0, 0]))
        grid = np.linspace(values.min() - 2 * bandwidth, values.max() + 2 * bandwidth, 512)
        density = kde(grid)
        width = 0.3 * density / density.max()
        bounds.extend([grid[0], grid[-1]])
        if style in {'raincloud', 'density'}:
            baseline = position - 0.08 if style == 'raincloud' else position + 0.18
            ridge = baseline - density / density.max() * 0.45
            ax.fill_between(grid, ridge, baseline, color=color, alpha=0.28, linewidth=0, zorder=1)
            ax.plot(grid, ridge, color=color, linewidth=1.2, zorder=2)
        else:
            ax.fill_between(grid, position - width, position + width, color=color, alpha=0.3, linewidth=0, zorder=1)
        if style != 'density':
            jitter = rng.uniform(0.13, 0.29, len(values)) if style == 'raincloud' else rng.uniform(-0.14, 0.14, len(values))
            ax.scatter(values, position + jitter, s=3.5, color=color, alpha=0.23, edgecolors='none', zorder=2, rasterized=True)
        if style == 'density':
            q25, median, q75 = np.quantile(values, [0.25, 0.5, 0.75])
            ax.hlines(position + 0.23, q25, q75, color=color, linewidth=3)
            ax.scatter(median, position + 0.23, s=24, color=color, edgecolor='white', linewidth=0.7, zorder=3)
        else:
            ax.boxplot(values, positions=[position], vert=False, widths=0.12 if style == 'raincloud' else 0.18, manage_ticks=False, showfliers=False, patch_artist=True, boxprops={'facecolor': 'none', 'edgecolor': '#303030', 'linewidth': 0.85}, medianprops={'color': '#202020', 'linewidth': 1.1}, whiskerprops={'color': '#303030', 'linewidth': 0.8}, capprops={'color': '#303030', 'linewidth': 0.8}, zorder=3)
        cv = 100 * values.std(ddof=1) / values.mean()
        cv_ax.hlines(position, 0, cv, color=color, linewidth=1.6, alpha=0.85)
        cv_ax.scatter(cv, position, s=44 if composite else 36, color=color, edgecolor='#303030', linewidth=0.7, zorder=3)
        cv_ax.annotate(f'{cv:.1f}%', (cv, position), xytext=(7, 0), textcoords='offset points', va='center', fontsize=13 if composite else 10)
        records.append({'group': label, 'n': len(values), 'mean': values.mean(), 'median': np.median(values), 'std': values.std(ddof=1), 'cv_percent': cv})
    ax.set_yticks([0, 1], ['Urban', 'Rural'])
    ax.set_ylim(1.43, -0.6 if style == 'raincloud' else -0.43)
    ax.tick_params(axis='y', length=0, pad=7)
    ax.set_xlim(min(0.135, min(bounds)), max(0.4, max(bounds)))
    ax.set_xticks(np.arange(0.15, 0.401, 0.05))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.set_xlabel('Wind Shear Coefficient ($\\alpha$)', labelpad=5)
    cv_ax.set_xlim(0, max(16, max((row['cv_percent'] for row in records)) + 4))
    cv_ax.set_xticks([0, 5, 10, 15])
    if composite:
        cv_ax.set_xlim(0, 21)
        cv_ax.set_xticks([0, 10, 20])
    cv_ax.tick_params(axis='y', left=False, labelleft=False)
    cv_ax.set_xlabel('CV (%)', labelpad=5)
    suffix = f'{style}_composite' if composite else style
    for extension in ['png', 'pdf', 'svg']:
        fig.savefig(OUTPUT / f'alpha_distribution_cv_{suffix}.{extension}', dpi=600, facecolor='white')
    plt.close(fig)
    summary = pd.DataFrame(records)
    summary.to_csv(OUTPUT / f'alpha_distribution_cv_{suffix}_summary.csv', index=False)
    print(summary.to_string(index=False))
    print(f'Saved to {OUTPUT}')
if __name__ == '__main__':
    main('density', composite=True)
