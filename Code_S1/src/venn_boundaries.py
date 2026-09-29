import plot_exposure_venn as base
from matplotlib.patches import Circle, Polygon, Rectangle
from shapely.geometry import Point
from shapely.ops import unary_union

def panel(ax, data, region, metric, style):
    base.draw_panel(ax, data, region, metric)
    for text in list(ax.texts):
        if text.get_text().startswith('No Stress Thresholds Met:'):
            text.remove()
    labels = {text.get_text(): text for text in ax.texts}
    for label, position in zip(base.SET_LABELS, [(-0.34, 0.58), (0.34, 0.58), (0, -0.67)]):
        text = labels[label]
        text.set_position(position)
        text.set_ha('center')
        text.set_va('center')
    for text in ax.texts:
        if text.get_text().endswith('%') and text.get_position()[1] < -0.4:
            text.set_y(-0.44)
    circles = [patch for patch in ax.patches if isinstance(patch, Circle)]
    if style == 'contour':
        union = unary_union([Point(*circle.center).buffer(circle.radius, resolution=192) for circle in circles])
        outline = union.buffer(0.23, resolution=192)
        boundary = Polygon(list(outline.exterior.coords), closed=True)
    else:
        boundary = Rectangle((-0.85, -0.9), 1.7, 1.7)
    boundary.set(facecolor='none', edgecolor='#92999D', linewidth=1.0, zorder=0)
    ax.add_patch(boundary)
    field = 'city_percent' if metric == 'Cities' else 'population_percent'
    none = data.loc[data.region.eq(region) & data.scheme.eq('combination') & data.category.eq(0), field].item()
    ax.text(0, -0.8, f'No Stress Thresholds Met: {none:.1f}%', ha='center', va='center', fontsize=12, color='#666666')
    ax.set_xlim(-0.91, 0.91)
    ax.set_ylim(-0.95, 0.84)
    ax.set_aspect('equal', adjustable='box')
