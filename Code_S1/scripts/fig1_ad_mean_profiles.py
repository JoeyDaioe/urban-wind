from project import input_file, output_dir
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
wind = pd.read_csv(input_file('wind_city.csv'))
heights = ['10m', '50m', '100m', '150m', '200m']
urban_cols = [f'urban_gwa3_250_wind-speed_{h}_b1' for h in heights]
rural_cols = [f'rural_gwa3_250_wind-speed_{h}_b1' for h in heights]
urban_mean = wind[urban_cols].mean()
urban_std = wind[urban_cols].std()
rural_mean = wind[rural_cols].mean()
rural_std = wind[rural_cols].std()
fig = plt.figure(figsize=(8, 6), dpi=200)
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 22
fig.patch.set_facecolor('none')
fig.patch.set_alpha(0)
ax2 = fig.add_subplot(111, polar=True)
ax2.set_facecolor('none')
N = len(heights)
bar_width = 2 * np.pi / N * 0.35
angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
cmap = mcolors.LinearSegmentedColormap.from_list('GreenGradient', ['#e0f2e1', '#4caf50'])
num_heights = len(heights)
angular_width = 2 * np.pi / num_heights
angle_offset = np.deg2rad(-35)
for i in range(num_heights):
    start_angle = angle_offset + i * angular_width
    color = cmap(i / (num_heights - 1) if num_heights > 1 else 0)
    rect = patches.Rectangle((start_angle, 0), angular_width, max(urban_mean.max(), rural_mean.max()) * 1.2, facecolor=color, alpha=0.5, zorder=0)
    ax2.add_patch(rect)
bars_urban = ax2.bar(angles - bar_width / 2, urban_mean.values, width=bar_width, color='#e41a1c', alpha=0.7, yerr=urban_std.values, capsize=3, error_kw={'elinewidth': 1}, label='Urban')
bars_rural = ax2.bar(angles + bar_width / 2, rural_mean.values, width=bar_width, color='#377eb8', alpha=0.7, yerr=rural_std.values, capsize=3, error_kw={'elinewidth': 1}, label='Rural')
ax2.set_xticks(angles)
ax2.set_xticklabels(heights, fontsize=22)
ax2.tick_params(axis='x', pad=10)
ax2.legend(loc='upper left', bbox_to_anchor=(0.85, 0.2), fontsize=20, frameon=False)
ax2.grid(color='lightgray', linestyle='-', linewidth=0.5)
plt.tight_layout()
plt.savefig('polar_bar_chart_stronger_green_gradient_bg.png', dpi=300)
plt.show()
wind = pd.read_csv(input_file('wind_city.csv'))
heights = ['10m', '50m', '100m', '150m', '200m']
wind_speed_diff_cols = [f'gwa3_250_wind-speed_{h}_b1_diff' for h in heights]
wind_diff_mean = wind[wind_speed_diff_cols].mean()
wind_diff_std = wind[wind_speed_diff_cols].std()
fig, ax = plt.subplots(figsize=(8, 6), dpi=200, subplot_kw={'projection': 'polar'})
plt.rcParams['font.family'] = 'Times New Roman'
fig.patch.set_facecolor('none')
fig.patch.set_alpha(0)
ax.set_facecolor('none')
N = len(heights)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False)
cmap = mcolors.LinearSegmentedColormap.from_list('BlueGradient', ['#e0f7fa', '#0288d1'])
num_heights = len(heights)
angular_width = 2 * np.pi / num_heights
angle_offset = np.deg2rad(-35)
for i in range(num_heights):
    start_angle = angle_offset + i * angular_width
    color = cmap(i / (num_heights - 1) if num_heights > 1 else 0)
    rect = patches.Rectangle((start_angle, -1.3), angular_width, 1.4, facecolor=color, alpha=0.5, zorder=0)
    ax.add_patch(rect)
ax.errorbar(angles, wind_diff_mean.values, yerr=wind_diff_std.values, fmt='o-', capsize=5, color='#ff7f00', label='UWSDI', lw=2)
max_r = max(wind_diff_mean.max() + wind_diff_std.max(), 1)
theta = np.linspace(0, 2 * np.pi, 100)
ax.plot(theta, np.full_like(theta, max_r), color='gray', lw=0.5, ls='--')
ax.set_ylim(-1.3, 0.1)
ax.set_xticks(angles)
ax.set_xticklabels(heights, fontsize=22)
ax.tick_params(axis='x', pad=10)
ax.legend(loc='upper left', bbox_to_anchor=(0.85, 0.2), fontsize=20, frameon=False)
ax.grid(color='lightgray', linestyle='-', linewidth=0.5)
ax.set_yticks(np.linspace(-1.2, 0, 4))
plt.tight_layout()
plt.savefig('circular_plot_wind_speed_diff_with_bg.png', dpi=300)
plt.show()
