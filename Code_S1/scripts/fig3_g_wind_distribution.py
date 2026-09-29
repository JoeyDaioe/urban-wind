from project import input_file, output_dir
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import mannwhitneyu
from matplotlib.ticker import MaxNLocator
DATA_PATH = input_file('wind_final.csv')
OUTPUT_PATH = 'wind_speed_10m_comparison_large_font_v2.png'
WIND_SPEED_COLUMN = 'urban_gwa3_250_wind-speed_10m_b1'
VIOLIN_EDGE_COLORS = ['#CAB2D6', '#9ECAE1', '#FCBBA1']
DOT_COLORS = ['#6A3D9A', '#1F78B4', '#E31A1C']
DOT_TRANSPARENCY = 0.3
LINE_EXTEND = 0.22
plt.rcParams.update({'font.family': 'Times New Roman', 'font.size': 16, 'axes.linewidth': 2.0, 'xtick.major.width': 2.0, 'ytick.major.width': 2.0, 'xtick.major.size': 6, 'ytick.major.size': 6, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.titlecolor': 'black', 'axes.labelcolor': 'black', 'xtick.color': 'black', 'ytick.color': 'black', 'mathtext.default': 'regular'})

def prepare_data():
    try:
        data = pd.read_csv(DATA_PATH)
    except FileNotFoundError:
        print(f'Error: Data file not found at {DATA_PATH}')
        return None
    except Exception as e:
        print(f'Error reading data file: {e}')
        return None
    if WIND_SPEED_COLUMN not in data.columns or 'NSclass' not in data.columns:
        print(f"Error: Required columns ('{WIND_SPEED_COLUMN}', 'NSclass') not found.")
        print(f'Available columns sample: {list(data.columns)[:10]}')
        return None
    data['wind_speed_10m'] = pd.to_numeric(data[WIND_SPEED_COLUMN], errors='coerce')
    data.dropna(subset=['wind_speed_10m', 'NSclass'], inplace=True)
    q1 = data['wind_speed_10m'].quantile(0.25)
    q3 = data['wind_speed_10m'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = max(0, q1 - 1.5 * iqr)
    upper_bound = q3 + 1.5 * iqr
    data_filtered = data.copy()
    print(f'Original valid records: {len(data)}, Retained records: {len(data_filtered)}')
    print(f"10m Wind Speed Range: {data_filtered['wind_speed_10m'].min():.2f} ~ {data_filtered['wind_speed_10m'].max():.2f} m/s")
    if len(data_filtered) == 0:
        return None
    data_filtered['region'] = data_filtered['NSclass'].map({1: 'Global North', 0: 'Global South'})
    return data_filtered[['region', 'wind_speed_10m']]

def draw_plot(data):
    if data is None or data.empty:
        print('Cannot draw plot: No data provided.')
        return
    fig, ax = plt.subplots(figsize=(7, 6), dpi=600)
    plot_data = pd.concat([data[['region', 'wind_speed_10m']], data[['wind_speed_10m']].assign(region='All cities')], ignore_index=True)
    plot_data['region'] = pd.Categorical(plot_data['region'], categories=['All cities', 'Global North', 'Global South'], ordered=True)
    sns.violinplot(x='region', y='wind_speed_10m', data=plot_data, palette=VIOLIN_EDGE_COLORS, hue='region', legend=False, inner=None, linewidth=1.0, saturation=0.7, ax=ax)
    sns.boxplot(x='region', y='wind_speed_10m', data=plot_data, width=0.15, showcaps=False, fliersize=0, boxprops={'facecolor': 'none', 'edgecolor': 'black', 'linewidth': 1.5}, medianprops={'color': 'black', 'linewidth': 1.5}, whiskerprops={'color': 'black', 'linewidth': 1.5}, ax=ax)
    sns.stripplot(x='region', y='wind_speed_10m', data=plot_data, palette=DOT_COLORS, hue='region', legend=False, size=3, alpha=DOT_TRANSPARENCY, jitter=0.1, edgecolor='white', linewidth=0.2, ax=ax)

    def get_stars(p_value):
        if p_value < 0.001:
            return '***'
        if p_value < 0.01:
            return '**'
        if p_value < 0.05:
            return '*'
        return ''
    comparisons = [(1, 2)]
    comparisons.sort(key=lambda x: abs(x[1] - x[0]), reverse=True)
    y_max_data = plot_data['wind_speed_10m'].max()
    y_min_data = plot_data['wind_speed_10m'].min()
    y_range = y_max_data - y_min_data
    y_max_plot_base = y_max_data + y_range * 0.05
    lines_plotted = 0
    for group_idx1, group_idx2 in comparisons:
        cat1 = plot_data.region.cat.categories[group_idx1]
        cat2 = plot_data.region.cat.categories[group_idx2]
        data1 = plot_data[plot_data.region == cat1]['wind_speed_10m']
        data2 = plot_data[plot_data.region == cat2]['wind_speed_10m']
        if not data1.empty and (not data2.empty):
            try:
                stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
                stars = get_stars(p_value)
                print(f"MWU ({cat1} vs {cat2}): p = {p_value:.4e}, Stars = '{stars}'")
                if stars:
                    y_line = y_max_plot_base + lines_plotted * y_range * 0.12
                    y_star = y_line + y_range * 0.015
                    x1, x2 = (group_idx1, group_idx2)
                    ax.plot([x1, x2], [y_line, y_line], color='black', lw=1.5)
                    ax.plot([x1, x1], [y_line, y_line - y_range * 0.02], color='black', lw=1.5)
                    ax.plot([x2, x2], [y_line, y_line - y_range * 0.02], color='black', lw=1.5)
                    ax.text(np.mean([x1, x2]), y_star, stars, ha='center', va='bottom', fontsize=18, color='black', fontweight='bold')
                    lines_plotted += 1
            except ValueError as ve:
                print(f'Warning: {ve}')
    if lines_plotted > 0:
        final_y_max = y_max_plot_base + lines_plotted * y_range * 0.12 + y_range * 0.08
        ax.set_ylim(bottom=0, top=final_y_max)
    else:
        ax.set_ylim(bottom=0, top=y_max_data + y_range * 0.08)
    ax.set_xticks(ticks=[0, 1, 2])
    ax.set_xticklabels(labels=['All cities', 'Global North', 'Global South'], fontsize=16, color='black')
    ax.set_ylabel('10m Wind Speed (m s$^{-1}$)', fontsize=22, labelpad=10, color='black')
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6, prune=None))
    ax.tick_params(axis='x', which='major', labelsize=16, labelcolor='black', color='black')
    ax.tick_params(axis='y', which='major', labelsize=16, labelcolor='black', color='black')
    ax.grid(False)
    ax.set_xlabel('')
    plt.tight_layout()
    try:
        plt.savefig(OUTPUT_PATH, bbox_inches='tight', dpi=600)
        print(f'Image successfully saved to: {OUTPUT_PATH}')
    except Exception as e:
        print(f'Error saving plot: {e}')
    plt.show()
if __name__ == '__main__':
    prepared_wind_data = prepare_data()
    if prepared_wind_data is not None:
        draw_plot(prepared_wind_data)
    else:
        print('Exiting program due to data preparation errors.')
