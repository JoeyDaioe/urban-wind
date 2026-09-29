from project import input_file, output_dir
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
from scipy.stats import t
COLORS = ['#6B8E23', '#FF69B4', '#E6A100', '#4169E1', '#FF7F00']
GROUPS = ['Global', 'Tropical', 'Temperate', 'Cold', 'Arid']
INPUT = input_file('city_h01_primary_indicator.csv')
OUTPUT = output_dir()
ALPHA_INPUT = input_file('wind_speed_with_alpha_indices.csv')

def interval(values, statistic):
    values = np.asarray(values, dtype=float)
    if len(values) < 2 or not np.isfinite(values).all():
        raise ValueError('At least two finite observations are required')
    if statistic == 'median_iqr':
        lower, center, upper = np.quantile(values, [0.25, 0.5, 0.75])
    elif statistic == 'mean_ci95':
        center = values.mean()
        width = t.ppf(0.975, len(values) - 1) * values.std(ddof=1) / np.sqrt(len(values))
        lower, upper = (center - width, center + width)
    else:
        raise ValueError(f'Unknown statistic: {statistic}')
    return (center, lower, upper)

def load_data():
    alpha = pd.read_csv(ALPHA_INPUT)
    height = pd.read_csv(INPUT)
    alpha = alpha.loc[(alpha.r_squared_urban > 0.95) & (alpha.r_squared_rural > 0.95)]
    height = height.loc[(height.profile_r2_urban > 0.95) & (height.profile_r2_rural > 0.95)]
    if alpha.city_id.duplicated().any() or height.city_id.duplicated().any():
        raise ValueError('Duplicate city IDs')
    if set(alpha.city_id) != set(height.city_id):
        raise ValueError('Panels have different quality-filtered city populations')
    return (alpha, height)

def summarize(statistic='median_iqr'):
    alpha, height = load_data()
    records = []
    for group in GROUPS:
        a = alpha if group == 'Global' else alpha.loc[alpha.cz_name.str.strip().eq(group)]
        h = height if group == 'Global' else height.loc[height.climate_zone.str.strip().eq(group)]
        if set(a.city_id) != set(h.city_id):
            raise ValueError(f'Climate membership differs: {group}')
        valid = h.loc[h['H0.1_status'].ne('no_initial_stilling') & np.isfinite(h['H0.1_m'])]
        for panel, series, values in [('A', 'Urban', a.alpha_urban), ('A', 'Rural', a.alpha_rural), ('D', 'H0.1', valid['H0.1_m'])]:
            center, lower, upper = interval(values, statistic)
            records.append(dict(panel=panel, group=group, series=series, statistic=statistic, n=len(values), n_quality_filtered=len(a), center=center, lower=lower, upper=upper, n_extrapolated_above_200m=int((values > 200).sum()) if panel == 'D' else 0))
    return pd.DataFrame(records)

def draw(ax, summary, panel, panel_label=True):
    for i, group in enumerate(GROUPS):
        for row in summary.loc[(summary.panel == panel) & (summary.group == group)].itertuples():
            offset = (-0.16 if row.series == 'Urban' else 0.16) if panel == 'A' else 0
            ax.errorbar(i + offset, row.center, yerr=[[row.center - row.lower], [row.upper - row.center]], fmt='o', color=COLORS[i], markersize=7, markerfacecolor='white' if row.series == 'Rural' else COLORS[i], markeredgecolor=COLORS[i] if row.series == 'Rural' else 'black', markeredgewidth=1.2 if row.series == 'Rural' else 0.7, linewidth=1.5, capsize=3.5)
    ax.set_xticks(range(len(GROUPS)), GROUPS)
    ax.set_xlim(-0.55, len(GROUPS) - 0.45)
    ax.tick_params(axis='x', labelsize=9)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', linestyle='--', alpha=0.25)
    ax.set_ylabel('Wind Shear Coefficient ($\\alpha$)' if panel == 'A' else 'Practical Wind-Stilling Height (m)')
    if panel == 'A':
        ax.legend(handles=[Line2D([], [], marker='o', linestyle='none', color='#444444', markerfacecolor=face, markersize=11, markeredgewidth=0.8 if label == 'Urban' else 2.2, label=label) for label, face in [('Urban', '#444444'), ('Rural', 'white')]], frameon=False, loc='upper right', fontsize=17, handletextpad=0.4, borderpad=0.2)
        ax.margins(y=0.2)
    else:
        ax.axhline(200, color='#777777', linestyle=':', linewidth=0.8)
        ax.set_ylim(95, 395)
    if panel_label:
        ax.text(-0.16, 1.03, panel, transform=ax.transAxes, fontweight='bold', fontsize=15)

def main():
    OUTPUT.mkdir(exist_ok=True)
    plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman'], 'font.size': 11, 'mathtext.fontset': 'stix', 'pdf.fonttype': 42})
    for statistic in ['median_iqr']:
        summary = summarize(statistic)
        summary.to_csv(OUTPUT / f'statistics_{statistic}.csv', index=False)
        fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), layout='constrained')
        for ax, panel in zip(axes, ['A', 'D']):
            draw(ax, summary, panel)
        for ext in ['png', 'pdf']:
            fig.savefig(OUTPUT / f'panels_AD_{statistic}.{ext}', dpi=300)
        plt.close(fig)
        if statistic == 'median_iqr':
            for panel in ['A', 'D']:
                fig, ax = plt.subplots(figsize=(5.6, 7.2), layout='constrained')
                draw(ax, summary, panel, panel_label=False)
                ax.yaxis.label.set_size(20)
                ax.tick_params(axis='y', labelsize=16)
                ax.tick_params(axis='x', labelsize=12)
                for ext in ['png', 'pdf']:
                    fig.savefig(OUTPUT / f'panel_{panel}_{statistic}.{ext}', dpi=300)
                plt.close(fig)
    print(f'Saved figures and statistics to {OUTPUT}')
if __name__ == '__main__':
    main()
