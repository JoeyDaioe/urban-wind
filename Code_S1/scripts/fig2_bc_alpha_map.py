from project import input_file, output_dir
import warnings
import geopandas
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rioxarray
import cartopy.crs as ccrs
import cartopy.feature as cfeature
warnings.filterwarnings('ignore')
alpha_filepath = input_file('wind_speed_with_alpha_indices.csv')
city_info_filepath = input_file('df_city_info2_with_GAUL.csv')
cz_map_filepath = input_file('Beck_KG_V1_present_0p083.tif')
world_south_shp = input_file('World_Countries_Generalized_South_Final.shp')
world_north_shp = input_file('World_Countries_Generalized_North_Final.shp')
print('Result: ')
try:
    df_alpha = pd.read_csv(alpha_filepath)
    print(f'Result: {len(df_alpha)}Result: ')
except FileNotFoundError as e:
    print(f'Result: {e}')
    df_alpha = pd.DataFrame()
reliable_data = df_alpha[(df_alpha['r_squared_urban'] > 0.95) & (df_alpha['r_squared_rural'] > 0.95)].copy()
if 'urbanArea' in reliable_data.columns:
    reliable_data['urbanArea'] = reliable_data['urbanArea'].fillna(0)
    size_factor = 3
    reliable_data['point_size'] = np.log1p(reliable_data['urbanArea']) * size_factor
else:
    reliable_data['point_size'] = 10
try:
    cz_map = rioxarray.open_rasterio(cz_map_filepath)
    world_south = geopandas.read_file(world_south_shp)
    world_north = geopandas.read_file(world_north_shp)
except Exception as e:
    print(f'Result: {e})')
    cz_map = None
    world_south = None
    world_north = None

def plot_urban_map_with_combined_zonal(df, urban_col='alpha_urban', rural_col='alpha_rural', cmap='YlOrRd', vmin=None, vmax=None, urban_color='#EC8C8E', rural_color='#6B9ED9', save_filename='urban_alpha_with_zonal_contrast.png'):
    dpi = 200
    font_size = 9
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['axes.unicode_minus'] = False
    plt.rc('font', size=font_size)
    linewidth = 0.5
    plt.rcParams['axes.linewidth'] = linewidth
    plt.rcParams['xtick.major.size'] = 4
    plt.rcParams['xtick.major.width'] = linewidth
    plt.rcParams['ytick.major.size'] = 4
    plt.rcParams['ytick.major.width'] = linewidth
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['axes.facecolor'] = 'white'
    fig = plt.figure(figsize=(12, 7), dpi=dpi)
    map_proj = ccrs.PlateCarree()
    ax = fig.add_axes([0.05, 0.05, 0.75, 0.9], projection=map_proj)
    if world_south is not None and world_north is not None:
        world_south.plot(ax=ax, facecolor='none', edgecolor='#8C8C8C', linewidth=0.5, transform=map_proj, zorder=2)
        world_north.plot(ax=ax, facecolor='none', edgecolor='#E0E0E0', linewidth=0.5, transform=map_proj, zorder=2)
    ax.coastlines(linewidth=0.4, edgecolor='black', alpha=0.5, zorder=3)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, linestyle='--', edgecolor='black', alpha=0.5, zorder=3)
    if cz_map is not None:
        levels = [0, 1, 4, 8, 17, 29, 31]
        cz_colors = ['white', '#d78ab6', '#e9b68a', '#fdf798', '#83c5f7', 'white']
        try:
            cz_map.rio.reproject(map_proj.proj4_init).plot(ax=ax, levels=levels, colors=cz_colors, add_colorbar=False, add_labels=False, alpha=1, zorder=1)
        except:
            pass
    ax.set_title('')
    gridlines = ax.gridlines(draw_labels=True, linewidth=0, color='none')
    gridlines.xlines = False
    gridlines.ylines = False
    gridlines.top_labels = False
    gridlines.right_labels = False
    gridlines.xlabel_style = {'size': 10}
    gridlines.ylabel_style = {'size': 10}
    if vmin is None:
        vmin = df[urban_col].min()
    if vmax is None:
        vmax = df[urban_col].max()
    scatter = ax.scatter(df['lon'], df['lat'], c=df[urban_col], cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax), s=df['point_size'], marker='o', edgecolor='black', linewidth=0.3, alpha=0.8, transform=ccrs.PlateCarree(), zorder=4)
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.4, orientation='vertical', pad=0.02, aspect=20)
    cbar.set_label('Urban Wind Shear Coefficient ($\\alpha$)', fontsize=11, color='black')
    cbar.ax.tick_params(labelsize=10, colors='black')
    ax.set_extent([-180, 180, -60, 64], crs=ccrs.PlateCarree())
    pos = ax.get_position()
    left = pos.x1 + 0.08
    bottom = pos.y0 + 0.01
    height = pos.height - 0.02
    width = 0.1
    ax2 = fig.add_axes([left, bottom, width, height])
    lat_bins = np.arange(-40, 61, 5)
    df_calc = df.copy()
    df_calc['lat_bin'] = pd.cut(df_calc['lat'], bins=lat_bins, labels=lat_bins[:-1])
    urban_lat_mean = df_calc.groupby('lat_bin', observed=False)[urban_col].mean()
    urban_lat_std = df_calc.groupby('lat_bin', observed=False)[urban_col].std()
    rural_lat_mean = df_calc.groupby('lat_bin', observed=False)[rural_col].mean()
    rural_lat_std = df_calc.groupby('lat_bin', observed=False)[rural_col].std()
    ax2.plot(rural_lat_mean, rural_lat_mean.index, color=rural_color, linewidth=1.8, label='Rural', zorder=2)
    ax2.fill_betweenx(rural_lat_mean.index, rural_lat_mean - rural_lat_std, rural_lat_mean + rural_lat_std, color=rural_color, alpha=0.3, zorder=1)
    ax2.plot(urban_lat_mean, urban_lat_mean.index, color=urban_color, linewidth=1.8, label='Urban', zorder=4)
    ax2.fill_betweenx(urban_lat_mean.index, urban_lat_mean - urban_lat_std, urban_lat_mean + urban_lat_std, color=urban_color, alpha=0.3, zorder=3)
    ax2.set_ylim(-42, 60)
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position('right')
    ax2.tick_params(axis='y', which='both', left=False, right=True, labelleft=False, labelright=True)
    ax2.tick_params(axis='x', which='both', top=False, bottom=True)
    for spine in ax2.spines.values():
        spine.set_visible(True)
        spine.set_edgecolor('black')
        spine.set_linewidth(linewidth)
    ax2.grid(False)
    min_x = min(urban_lat_mean.min(), rural_lat_mean.min()) * 0.85
    max_x = max(urban_lat_mean.max(), rural_lat_mean.max()) * 1.15
    ax2.set_xlim(min_x, max_x)
    ax2.set_xlabel('Wind Shear Coefficient ($\\alpha$)', fontsize=11, color='black')
    ax2.set_ylabel('Latitude', fontsize=11)
    ax2.tick_params(axis='x', labelcolor='black', labelsize=9)
    yticks = lat_bins[::4]
    yticklabels = [f'{lat}°N' if lat > 0 else f'{abs(lat)}°S' if lat < 0 else '0°' for lat in yticks]
    ax2.set_yticks(yticks)
    ax2.set_yticklabels(yticklabels, fontsize=10)
    ax.legend(handles=[plt.matplotlib.patches.Patch(facecolor=color, label=label) for label, color in zip(['Tropical', 'Arid', 'Temperate', 'Cold'], ['#d78ab6', '#e9b68a', '#fdf798', '#83c5f7'])], loc='lower left', frameon=False, fontsize=8.5)
    plt.savefig(save_filename, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.show()
if 'reliable_data' in locals() and (not reliable_data.empty):
    vmin_val = reliable_data['alpha_urban'].quantile(0.02)
    vmax_val = reliable_data['alpha_urban'].quantile(0.98)
    plot_urban_map_with_combined_zonal(df=reliable_data, urban_col='alpha_urban', rural_col='alpha_rural', cmap='YlOrRd', vmin=vmin_val, vmax=vmax_val, urban_color='#EC8C8E', rural_color='#6B9ED9', save_filename='Urban_decay_with_contrast_profile.png')
else:
    print('Result: ')
