from project import input_file, output_dir
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
import matplotlib.colors as mcolors
file_paths = [input_file('Northern_Countries_50m_wind_speed__m_s__data.csv'), input_file('Southern_Countries_50m_wind_speed__m_s__data.csv')]
labels = ['Global North', 'Global South']
line_colors = ['#377eb8', '#e41a1c']
scatter_colors = ['#8bbce0', '#f1a0a0']
linestyles_fitted = ['--', '--']
markers_original = ['o', 'o']
try:
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 14
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    cmap = mcolors.LinearSegmentedColormap.from_list('NatureGreys', ['#ffffff', '#a0a0a0'])
    num_sectors = 360
    angular_width = 2 * np.pi / num_sectors
    angle_offset = 0
    max_radius_for_bg = 5.7
    for i in range(num_sectors):
        start_angle = angle_offset + i * angular_width
        color = cmap(i / (num_sectors - 1) if num_sectors > 1 else 0)
        rect = patches.Rectangle((start_angle, 1.5), angular_width, max_radius_for_bg - 1.5, facecolor=color, alpha=0.5, zorder=0, transform=ax.transData)
        ax.add_patch(rect)
    for idx, file_path in enumerate(file_paths):
        df = pd.read_csv(file_path)
        required_columns = ['ISA intensity', 'Original Y', 'Fitted Y', 'R-squared']
        for col in required_columns:
            if col not in df.columns:
                print(f"Error: CSV file '{file_path}' must contain column '{col}'. Columns found: {df.columns}")
                exit()
        r_squared_value = df['R-squared'].iloc[0]
        df['angle_degrees'] = df['ISA intensity'] * 360
        df['angle_radians'] = np.deg2rad(df['angle_degrees'])
        ax.plot(df['angle_radians'], df['Original Y'], label=f'{labels[idx]} Original Y', color=line_colors[idx], linestyle='None', marker=markers_original[idx], markersize=6, alpha=0.7, markerfacecolor=scatter_colors[idx], markeredgecolor=scatter_colors[idx], zorder=1)
        ax.plot(df['angle_radians'], df['Fitted Y'], label=f'{labels[idx]} Fitted Y', color=line_colors[idx], linestyle=linestyles_fitted[idx], linewidth=2, zorder=1)
    ax.set_theta_zero_location('E')
    ax.set_theta_direction(1)
    isa_intensity_ticks_num = 8
    isa_intensity_ticks = np.linspace(0, 1, isa_intensity_ticks_num + 1, endpoint=True)[0:-1]
    xticks_positions = isa_intensity_ticks * 2 * np.pi
    ax.set_xticks(xticks_positions)
    xticklabels = [f'{tick:.2f}' for tick in isa_intensity_ticks]
    ax.set_xticklabels(xticklabels, fontsize=12)
    for label, angle_rad in zip(ax.get_xticklabels(), xticks_positions):
        label.set_rotation(0)
        label.set_ha('center')
    ax.set_ylim(bottom=1.5)
    ax.grid(False)
    plt.tight_layout(rect=[0, 0, 1, 1], pad=2)
    plt.show()
except FileNotFoundError as e:
    print(f'Error: File not found at path: {file_path}')
except Exception as e:
    print(f'An error occurred: {e}')
