from project import input_file, output_dir
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import mannwhitneyu
DATA_PATH = input_file('environment_city.csv')
OUTPUT_PATH = 'Fig3D_PM25_x10.png'
VIOLIN_EDGE_COLORS = ['#CAB2D6', '#9ECAE1', '#FCBBA1']
DOT_COLORS = ['#6A3D9A', '#1F78B4', '#E31A1C']
DOT_TRANSPARENCY = 0.3
LINE_EXTEND = 0.22
STAR_POSITION = 0.99
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
    if 'urban_PM1000m' not in data.columns or 'NSclass' not in data.columns:
        print("Error: Required columns ('urban_PM1000m', 'NSclass') not found in the CSV.")
        return None
    data['utci_scaled'] = data['urban_PM1000m'] * 10.0
    data.dropna(subset=['utci_scaled', 'NSclass'], inplace=True)
    q1 = data['utci_scaled'].quantile(0.25)
    q3 = data['utci_scaled'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    data_filtered = data[(data['utci_scaled'] >= lower_bound) & (data['utci_scaled'] <= upper_bound)].copy()
    print(f'Original data points: {len(data)}, After outlier removal: {len(data_filtered)}')
    if len(data_filtered) == 0:
        print('Warning: All data points were removed as outliers.')
        return None
    data_filtered['region'] = data_filtered['NSclass'].map({1: 'Global North', 0: 'Global South'})
    return data_filtered[['region', 'utci_scaled']]

def draw_plot(data):
    if data is None or data.empty:
        print('Cannot draw plot: No data provided.')
        return
    fig, ax = plt.subplots(figsize=(7, 6), dpi=600)
    plot_data = pd.concat([data[['region', 'utci_scaled']], data[['utci_scaled']].assign(region='All cities')], ignore_index=True)
    plot_data['region'] = pd.Categorical(plot_data['region'], categories=['All cities', 'Global North', 'Global South'], ordered=True)
    sns.violinplot(x='region', y='utci_scaled', data=plot_data, palette=VIOLIN_EDGE_COLORS, inner=None, linewidth=1.0, saturation=0.7, ax=ax)
    sns.boxplot(x='region', y='utci_scaled', data=plot_data, width=0.15, showcaps=False, fliersize=0, boxprops={'facecolor': 'none', 'edgecolor': 'black', 'linewidth': 1.5}, medianprops={'color': 'black', 'linewidth': 1.5}, whiskerprops={'color': 'black', 'linewidth': 1.5}, ax=ax)
    sns.stripplot(x='region', y='utci_scaled', data=plot_data, palette=DOT_COLORS, size=3, alpha=DOT_TRANSPARENCY, jitter=0.1, edgecolor='white', linewidth=0.2, ax=ax)

    def get_stars(p_value):
        if p_value < 0.001:
            return '***'
        if p_value < 0.01:
            return '**'
        if p_value < 0.05:
            return '*'
        return ''
    comparisons = [(0, 1, (0 - LINE_EXTEND, 1 + LINE_EXTEND)), (1, 2, (1 - LINE_EXTEND, 2 + LINE_EXTEND)), (0, 2, (0 - LINE_EXTEND, 2 + LINE_EXTEND))]
    comparisons.sort(key=lambda x: abs(x[2][1] - x[2][0]), reverse=True)
    y_max_data = plot_data['utci_scaled'].max()
    y_min_data = plot_data['utci_scaled'].min()
    y_range = y_max_data - y_min_data
    y_max_plot_base = y_max_data + y_range * 0.05
    lines_plotted = 0
    for i, (group_idx1, group_idx2, line_pos_indices) in enumerate(comparisons):
        cat1 = plot_data.region.cat.categories[group_idx1]
        cat2 = plot_data.region.cat.categories[group_idx2]
        data1 = plot_data[plot_data.region == cat1]['utci_scaled']
        data2 = plot_data[plot_data.region == cat2]['utci_scaled']
        if not data1.empty and (not data2.empty):
            try:
                stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
                stars = get_stars(p_value)
                print(f"Mann-Whitney U ({cat1} vs {cat2}): p={p_value:.4g}, Sig='{stars}'")
                if stars:
                    y_line = y_max_plot_base + lines_plotted * y_range * 0.12
                    y_star = y_line * STAR_POSITION
                    x1, x2 = (group_idx1, group_idx2)
                    ax.plot([x1, x2], [y_line, y_line], color='black', lw=1.5)
                    ax.plot([x1, x1], [y_line, y_line - y_range * 0.015], color='black', lw=1.5)
                    ax.plot([x2, x2], [y_line, y_line - y_range * 0.015], color='black', lw=1.5)
                    ax.text(np.mean([x1, x2]), y_star, stars, ha='center', va='bottom', fontsize=18, color='black')
                    lines_plotted += 1
            except ValueError as ve:
                print(f'Warning error: {ve}')
    if lines_plotted > 0:
        final_y_max = y_max_plot_base + lines_plotted * y_range * 0.12 + y_range * 0.02
        ax.set_ylim(top=final_y_max)
    else:
        ax.set_ylim(top=y_max_data + y_range * 0.05)
    ax.set_xticks(ticks=[0, 1, 2])
    ax.set_xticklabels(labels=['All cities', 'Global North', 'Global South'], fontsize=16, color='black')
    ax.set_ylabel('Urban PM$_{2.5}$ ($\\mathrm{\\mu g\\ m^{-3}}$)', fontsize=26, labelpad=10, color='black')
    ax.yaxis.set_label_coords(-0.12, 0.5)
    from matplotlib.ticker import MaxNLocator
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5, prune='both'))
    ax.tick_params(axis='x', which='major', labelsize=16, labelcolor='black', color='black')
    ax.tick_params(axis='y', which='major', labelsize=16, labelcolor='black', color='black')
    ax.grid(False)
    ax.set_xlabel('')
    plt.tight_layout()
    try:
        plt.savefig(OUTPUT_PATH, bbox_inches='tight', dpi=600)
        print(f'Image saved to: {OUTPUT_PATH}')
    except Exception as e:
        print(f'Error saving plot: {e}')
    plt.show()
if __name__ == '__main__':
    prepared_north_south_data = prepare_data()
    if prepared_north_south_data is not None:
        north_data = prepared_north_south_data[prepared_north_south_data['region'] == 'Global North']
        south_data = prepared_north_south_data[prepared_north_south_data['region'] == 'Global South']
        if not north_data.empty and (not south_data.empty):
            north_mean = north_data['utci_scaled'].mean()
            south_mean = south_data['utci_scaled'].mean()
            mean_difference = north_mean - south_mean
            print(f'Diff: {mean_difference:.4f}')
        draw_plot(prepared_north_south_data)
    else:
        print('Exiting program due to data preparation errors.')
