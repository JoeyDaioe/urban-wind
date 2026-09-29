from project import input_file, output_dir
import geopandas
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from matplotlib.gridspec import GridSpec
wind = pd.read_csv(input_file('environment_city.csv'))
df = wind
df['urban_UTCI1000m_K'] = df['urban_UTCI1000m'] / 100
df['urban_UTCI_C'] = df['urban_UTCI1000m_K']
df['urban_gwa3_250_wind-speed_10m_b1'] = df['urban_gwa3_250_wind-speed_10m_b1'].fillna(0)
size_factor = 10
df['point_size'] = np.log1p(df['urban_gwa3_250_wind-speed_10m_b1']) * size_factor
plt.rcParams['font.family'] = 'Times New Roman'
nb_class = 5
min_utci_c = df['urban_UTCI_C'].min()
max_utci_c = df['urban_UTCI_C'].max()
if pd.notna(min_utci_c) and pd.notna(max_utci_c):
    breaks = np.linspace(min_utci_c, max_utci_c, nb_class + 1)
else:
    breaks = np.linspace(0, 1, nb_class + 1)
cmap = plt.get_cmap('RdYlBu_r')
if pd.notna(min_utci_c) and pd.notna(max_utci_c):
    norm = plt.Normalize(vmin=min_utci_c, vmax=max_utci_c)
else:
    norm = plt.Normalize(vmin=0, vmax=1)
dpi = 200
font_size = 9
plt.rc('font', family='Times New Roman', size=font_size)
linewidth = 0.5
plt.rcParams['axes.linewidth'] = linewidth
fig = plt.figure(figsize=(12, 7), dpi=dpi, linewidth=0.1)
gs = GridSpec(1, 2, width_ratios=[5, 1])
map_proj = ccrs.PlateCarree()
ax = fig.add_subplot(gs[0], projection=map_proj)
try:
    world_south = geopandas.read_file(input_file('World_Countries_Generalized_South_Final.shp'))
    world_north = geopandas.read_file(input_file('World_Countries_Generalized_North_Final.shp'))
    world_south.plot(ax=ax, facecolor='#8C8C8C', edgecolor='#8C8C8C', linewidth=0.5, label='Global South')
    world_north.plot(ax=ax, facecolor='#E0E0E0', edgecolor='#E0E0E0', linewidth=0.5, label='Global North')
except:
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
ax.coastlines(linewidth=0.4, edgecolor='black', alpha=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.3, linestyle='--', edgecolor='black', alpha=0.5)
gridlines = ax.gridlines(draw_labels=True, linewidth=0, color='#D3D3D3', linestyle='-')
gridlines.top_labels = False
gridlines.right_labels = False
gridlines.xlabel_style = {'size': 12}
gridlines.ylabel_style = {'size': 12}
scatter = ax.scatter(df['lon'], df['lat'], c=df['urban_UTCI_C'], cmap=cmap, norm=norm, s=df['point_size'], marker='o', edgecolor='black', linewidth=0.3, alpha=0.8, transform=map_proj, label='UTCI')
cbar = plt.colorbar(scatter, ax=ax, shrink=0.4, orientation='vertical', pad=0.02, aspect=20)
cbar.set_label('Urban UTCI (°C)', fontsize=15, color='black')
cbar.ax.tick_params(labelsize=15, colors='black')
ax.set_extent([-180, 180, -60, 64], crs=ccrs.PlateCarree())
ax.set_title(' ')
pos = ax.get_position()
left = pos.x1 + 0.05
bottom = pos.y0
height = pos.height
width = 0.1
ax2 = fig.add_axes([left, bottom, width, height])
lat_bins = np.arange(-40, 61, 5)
lat_bin_labels = (lat_bins[:-1] + lat_bins[1:]) / 2
df['lat_bin'] = pd.cut(df['lat'], bins=lat_bins, labels=lat_bin_labels, right=False)
lat_stats = df.groupby('lat_bin', observed=False)['urban_UTCI_C'].agg(['mean', 'std']).reset_index()
lat_mean_utci_c = lat_stats['mean']
lat_std_utci_c = lat_stats['std']
lat_plot_labels = lat_stats['lat_bin']
ax2.plot(lat_mean_utci_c, lat_plot_labels, color='chocolate', label='Mean UTCI')
lower_bound = lat_mean_utci_c - lat_std_utci_c
upper_bound = lat_mean_utci_c + lat_std_utci_c
ax2.fill_betweenx(lat_plot_labels, lower_bound, upper_bound, color='peachpuff', alpha=0.4, where=lat_std_utci_c.notna())
ax2.yaxis.tick_right()
ax2.yaxis.set_label_position('right')
ax2.set_xlabel('Urban UTCI (°C)', fontsize=15, color='chocolate')
ax2.set_ylabel('Latitude', fontsize=15)
ax2.tick_params(axis='x', labelcolor='chocolate', labelsize=12)
yticks = np.arange(-40, 61, 20)
yticklabels = [f'{abs(lat)}°S' if lat < 0 else f'{lat}°N' for lat in yticks]
ax2.set_yticks(yticks)
ax2.set_yticklabels(yticklabels, fontsize=12)
ax2.set_ylim(lat_bins.min(), lat_bins.max())
fig.subplots_adjust(left=0.05, right=0.85, bottom=0.05, top=0.95, wspace=0.1)
plt.show()
