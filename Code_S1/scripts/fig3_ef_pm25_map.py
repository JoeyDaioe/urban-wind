from project import input_file, output_dir
import geopandas
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from matplotlib.gridspec import GridSpec
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
wind = pd.read_csv(input_file('environment_city.csv'))
df = wind.copy()
df['urban_PM1000m'] = df['urban_PM1000m'] * 10.0
print(df.columns)
print(f"NaN count in 'urban_PM1000m': {df['urban_PM1000m'].isna().sum()}")
print(f"NaN count in 'urban_gwa3_250_wind-speed_10m_b1': {df['urban_gwa3_250_wind-speed_10m_b1'].isna().sum()}")
nan_pm_cities = df[df['urban_PM1000m'].isna()]['city_id']
print("city_id with NaN 'urban_PM1000m':")
print(nan_pm_cities)
nan_wind_speed_cities = df[df['urban_gwa3_250_wind-speed_10m_b1'].isna()]['city_id']
print("city_id with NaN 'urban_gwa3_250_wind-speed_10m_b1':")
print(nan_wind_speed_cities)
df['urban_gwa3_250_wind-speed_10m_b1'] = df['urban_gwa3_250_wind-speed_10m_b1'].fillna(0)
size_factor = 15
df['point_size'] = np.log1p(df['urban_gwa3_250_wind-speed_10m_b1']) * size_factor
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['text.usetex'] = False
pm_data_column = 'urban_PM1000m'
valid_pm_data = df[pm_data_column].dropna()
if valid_pm_data.empty:
    print(f"Warning: Column '{pm_data_column}' contains only NaN values. Setting default min/max.")
    pm_min, pm_max = (0, 1)
else:
    pm_min = valid_pm_data.min()
    pm_max = valid_pm_data.max()
nb_class = 5
breaks = np.linspace(pm_min, pm_max, nb_class + 1)
df['pm_level'] = pd.cut(df[pm_data_column], bins=breaks, labels=np.arange(1, nb_class + 1, 1), include_lowest=True)
cmap = plt.cm.YlOrRd
norm = plt.Normalize(vmin=pm_min, vmax=pm_max)
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
world_south.plot(ax=ax, facecolor='#8C8C8C', edgecolor='#8C8C8C', linewidth=0.5, label='Global South')
world_north.plot(ax=ax, facecolor='#E0E0E0', edgecolor='#E0E0E0', linewidth=0.5, label='Global North')
ax.coastlines(linewidth=0.4, edgecolor='black', alpha=0.5)
ax.add_feature(cfeature.BORDERS, linewidth=0.3, linestyle='--', edgecolor='black', alpha=0.5)
gridlines = ax.gridlines(draw_labels=True, linewidth=0, color='#D3D3D3', linestyle='-')
gridlines.top_labels = False
gridlines.right_labels = False
gridlines.xlabel_style = {'size': 12}
gridlines.ylabel_style = {'size': 12}
scatter = ax.scatter(df['lon'], df['lat'], c=df[pm_data_column], cmap=cmap, norm=norm, s=df['point_size'], marker='o', edgecolor='black', linewidth=0.3, alpha=0.8, transform=map_proj, label='$PM_{2.5}$')
cbar = plt.colorbar(scatter, ax=ax, shrink=0.4, orientation='vertical', pad=0.02, aspect=20)
cbar.set_label('Urban PM$_{2.5}$ ($\\mu g/m^3$)', fontsize=15, color='black')
cbar.ax.tick_params(labelsize=15, colors='black')
ax.set_extent([-180, 180, -60, 64], crs=ccrs.PlateCarree())
ax.set_title(' ')
pos = ax.get_position()
left = pos.x1 + 0.07
bottom = pos.y0 + 0.04
height = pos.height
width = 0.1
ax2 = fig.add_axes([left, bottom, width, height])
lat_bins = np.arange(-40, 61, 5)
df['lat_bin'] = pd.cut(df['lat'], bins=lat_bins, labels=lat_bins[:-1], right=False)
lat_grouped = df.groupby('lat_bin', observed=False)[pm_data_column]
lat_mean_pm = lat_grouped.mean()
lat_std_pm = lat_grouped.std()
lat_bin_centers = lat_bins[:-1] + np.diff(lat_bins) / 2
ax2.plot(lat_mean_pm.values, lat_bin_centers, color='darkorange', label='Mean $PM_{2.5}$')
ax2.fill_betweenx(lat_bin_centers, (lat_mean_pm - lat_std_pm).fillna(lat_mean_pm).values, (lat_mean_pm + lat_std_pm).fillna(lat_mean_pm).values, color='navajowhite', alpha=0.4, where=lat_std_pm.notna().values)
ax2.yaxis.tick_right()
ax2.yaxis.set_label_position('right')
ax2.set_ylabel('Latitude', fontsize=15)
ax2.set_xlabel('Urban PM$_{2.5}$ ($\\mu g/m^3$)', fontsize=15, color='darkorange')
ax2.tick_params(axis='x', labelcolor='darkorange', labelsize=12)
yticks = np.arange(-40, 61, 20)
yticklabels = [f'{abs(lat)}°S' if lat < 0 else f'{lat}°N' if lat > 0 else '0°' for lat in yticks]
ax2.set_yticks(yticks)
ax2.set_yticklabels(yticklabels, fontsize=12)
ax2.set_ylim(lat_bins[0], lat_bins[-1])
fig.subplots_adjust(left=0.05, right=0.88, bottom=0.1, top=0.95, wspace=0.15)
for spine in ax2.spines.values():
    spine.set_visible(True)
    spine.set_color('black')
    spine.set_linewidth(linewidth)
plt.show()
