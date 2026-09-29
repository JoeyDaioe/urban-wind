from project import input_file, output_dir
import geopandas
import rioxarray
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from matplotlib.gridspec import GridSpec
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
wind = pd.read_csv(input_file('wind_city.csv'))
df = wind
print(df.columns)
print(df['urban_gwa3_250_wind-speed_10m_b1'].isna().sum())
print(df['urbanArea'].isna().sum())
df['urbanArea'] = df['urbanArea'].fillna(0)
size_factor = 3
df['point_size'] = np.log1p(df['urbanArea']) * size_factor
plt.rcParams['font.family'] = 'Times New Roman'

def read_cz_map():
    filename = input_file('Beck_KG_V1_present_0p083.tif')
    data = rioxarray.open_rasterio(filename)
    return data
cz_map = read_cz_map()
nb_class = 5
print(np.min(df['urban_gwa3_250_wind-speed_10m_b1']), np.max(df['urban_gwa3_250_wind-speed_10m_b1']))
breaks = [np.min(df['urban_gwa3_250_wind-speed_10m_b1']), 1, 2, 3, 4, np.max(df['urban_gwa3_250_wind-speed_10m_b1'])]
df['wind_level'] = pd.cut(df['urban_gwa3_250_wind-speed_10m_b1'], bins=breaks, labels=np.arange(1, nb_class + 1, 1), include_lowest=True)
cmap = plt.cm.viridis
norm = plt.Normalize(vmin=df['urban_gwa3_250_wind-speed_10m_b1'].min(), vmax=df['urban_gwa3_250_wind-speed_10m_b1'].max())
dpi = 200
font_size = 9
plt.rc('font', family='Times New Roman', size=font_size)
linewidth = 0.5
plt.rcParams['axes.linewidth'] = linewidth
plt.rcParams['xtick.major.size'] = 4
plt.rcParams['xtick.major.width'] = linewidth
plt.rcParams['ytick.major.size'] = 4
plt.rcParams['ytick.major.width'] = linewidth
fig = plt.figure(figsize=(12, 7), dpi=dpi, linewidth=0.1)
gs = GridSpec(1, 2, width_ratios=[5, 1])
map_proj = ccrs.PlateCarree()
ax = fig.add_subplot(gs[0], projection=map_proj)
world_south = geopandas.read_file(input_file('World_Countries_Generalized_South_Final.shp'))
world_north = geopandas.read_file(input_file('World_Countries_Generalized_North_Final.shp'))
world_south.plot(ax=ax, facecolor='none', edgecolor='#8C8C8C', linewidth=0.5, label='Global South')
world_north.plot(ax=ax, facecolor='none', edgecolor='#E0E0E0', linewidth=0.5, label='Global North')
ax.coastlines(linewidth=0.4, edgecolor='black', alpha=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.3, linestyle='--', edgecolor='black', alpha=0.5)
gridlines = ax.gridlines(draw_labels=True, linewidth=0, color='#D3D3D3', linestyle='-')
gridlines.top_labels = False
gridlines.right_labels = False
gridlines.xlabel_style = {'size': 12}
gridlines.ylabel_style = {'size': 12}
levels = [0, 1, 4, 8, 17, 29, 31]
cz_colors = ['white', '#d78ab6', '#e9b68a', '#fdf798', '#83c5f7', 'white']
cz_map.plot(ax=ax, levels=levels, colors=cz_colors, add_colorbar=False, alpha=1)
scatter = ax.scatter(df['lon'], df['lat'], c=df['urban_gwa3_250_wind-speed_10m_b1'], cmap=cmap, norm=norm, s=df['point_size'], marker='o', edgecolor='black', linewidth=0.3, alpha=0.8, transform=map_proj, label='Wind Speed')
cbar = plt.colorbar(scatter, ax=ax, shrink=0.4, orientation='vertical', pad=0.02, aspect=20)
cbar.set_label('Urban Wind Speed (m/s)', fontsize=15, color='black')
cbar.ax.tick_params(labelsize=15, colors='black')
ax.set_extent([-180, 180, -60, 64], crs=ccrs.PlateCarree())
ax.set_title(' ')
legend_patches_ns = [plt.Line2D([0], [0], color='#8C8C8C', lw=0.5, label='Global South'), plt.Line2D([0], [0], color='#E0E0E0', lw=0.5, label='Global North'), plt.Line2D([0], [0], marker='o', color='black', markerfacecolor='lightgray', markeredgecolor='black', markersize=6, linestyle='None', label='Wind Speed')]
pos = ax.get_position()
left = pos.x1 + 0.1
bottom = pos.y0 + 0.01
height = pos.height + 0.01
width = 0.1
ax2 = fig.add_axes([left, bottom, width, height])
lat_bins = np.arange(-40, 61, 5)
df['lat_bin'] = pd.cut(df['lat'], bins=lat_bins, labels=lat_bins[:-1])
for area, color in [('urban', '#EC8C8E'), ('rural', '#6B9ED9')]:
    grouped = df.groupby('lat_bin', observed=False)[f'{area}_gwa3_250_wind-speed_10m_b1']
    means = grouped.mean()
    std = grouped.std()
    ax2.plot(means, means.index, color=color, label=area.capitalize())
    ax2.fill_betweenx(means.index, means - std, means + std, color=color, alpha=0.2)
ax2.set_xlim(1, 5)
ax2.yaxis.tick_right()
ax2.yaxis.set_label_position('right')
ax2.set_xlabel('Wind Speed (m/s)', fontsize=15, color='black')
ax2.set_ylabel('Latitude', fontsize=15)
ax2.tick_params(axis='x', labelcolor='black', labelsize=12)
yticks = lat_bins[::4]
yticklabels = [f'{lat}°N' if lat > 0 else f'{abs(lat)}°S' if lat < 0 else '0°' for lat in yticks]
ax2.set_yticks(yticks)
ax2.set_yticklabels(yticklabels, fontsize=12)
fig.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95)
ax.legend(handles=[plt.matplotlib.patches.Patch(facecolor=color, label=label) for label, color in zip(['Tropical', 'Arid', 'Temperate', 'Cold'], ['#d78ab6', '#e9b68a', '#fdf798', '#83c5f7'])], loc='lower left', frameon=False, fontsize=8.5)
plt.show()
