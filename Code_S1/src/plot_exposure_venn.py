from project import input_file, output_dir
from pathlib import Path
import sys
OUT = output_dir()
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np
import pandas as pd
from matplotlib_venn import venn3, venn3_circles
REGIONS = ['Global South', 'Global North']
SET_COLORS = ['#72ADC5', '#E7B760', '#DA8B96']
REGION_COLORS = ['#C65D4B', '#287D9B']
SET_LABELS = ['Low Ventilation', 'Heat Stress', 'Elevated Pollution']
IDS = ['100', '010', '110', '001', '101', '011', '111']
CATEGORY_MAP = {code: int(code, 2) for code in IDS}
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Times New Roman', 'DejaVu Serif'], 'mathtext.fontset': 'stix', 'mathtext.default': 'it', 'font.size': 11, 'axes.titlesize': 14, 'pdf.fonttype': 42, 'svg.fonttype': 'none'})

def draw_panel(ax, data, region, metric, palette=None, outer_circle=False):
    subset = data.loc[data['region'].eq(region) & data['scheme'].eq('combination')].set_index('category')
    field = 'city_percent' if metric == 'Cities' else 'population_percent'
    assert np.isclose(subset[field].sum(), 100)
    colors = SET_COLORS if palette is None else palette['colors']
    alpha = 0.42 if palette is None else palette['alpha']
    diagram = venn3((1, 1, 1, 1, 1, 1, 1), set_labels=SET_LABELS, set_colors=colors, alpha=alpha, ax=ax)
    venn3_circles((1, 1, 1, 1, 1, 1, 1), ax=ax, linewidth=0.7, color='#777777')
    for code, category in CATEGORY_MAP.items():
        record = subset.loc[category]
        label = f'{record[field]:.1f}%'
        text = diagram.get_label_by_id(code)
        text.set_text(label)
        text.set_fontsize(12.5)
        text.set_color('#252525')
        if code == '111':
            text.set_fontweight('bold')
            text.set_fontsize(13)
            diagram.get_patch_by_id(code).set_facecolor('#C47C88' if palette is None else palette['center'])
            diagram.get_patch_by_id(code).set_alpha(0.65)
    for text in diagram.set_labels:
        text.set_fontsize(12)
    none = subset.loc[0]
    if outer_circle:
        for text, position in zip(diagram.set_labels[:2], [(-0.45, 0.56), (0.45, 0.56)]):
            text.set_position(position)
            text.set_ha('center')
            text.set_va('center')
        ax.add_patch(Circle((0, -0.03), 1.0, facecolor='none', edgecolor='#92999D', linewidth=1.0, zorder=0))
        ax.set_xlim(-1.06, 1.06)
        ax.set_ylim(-1.09, 1.02)
        ax.set_aspect('equal', adjustable='box')
        ax.text(0, 0.81, '100%', ha='center', va='center', fontsize=13, color='#555555')
        ax.text(0, -0.81, 'None Of The Three', ha='center', va='center', fontsize=12, color='#444444')
        ax.text(0, -0.94, f'{none[field]:.1f}%', ha='center', va='center', fontsize=13, color='#252525')
    else:
        none_label = f'No Stress Thresholds Met: {none[field]:.1f}%'
        ax.text(0.5, -0.11, none_label, transform=ax.transAxes, ha='center', va='center', fontsize=12.5, color='#444444')
    ax.set_title(region, pad=15, fontsize=13, color=REGION_COLORS[REGIONS.index(region)] if palette is None else '#303030')

def save(fig, stem):
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for text in fig.findobj(matplotlib.text.Text):
        if text.get_visible() and text.get_text():
            bounds = text.get_window_extent(renderer)
            if bounds.x0 < -1 or bounds.y0 < -1 or bounds.x1 > fig.bbox.width + 1 or (bounds.y1 > fig.bbox.height + 1):
                raise ValueError(f'Text outside canvas: {text.get_text()}')
    for extension in ['png', 'pdf', 'svg']:
        fig.savefig(OUT / f'{stem}.{extension}', dpi=400, facecolor='white')
    plt.close(fig)

def footer(fig, y, metric=None):
    if metric is not None:
        formula = 'City Share = Cities in the Exact Combination / All Studied Cities in the Same Region' if metric == 'Cities' else 'Population Share = Population Weight in the Exact Combination / Total Population Weight in the Same Region'
        fig.text(0.5, y + 0.035, formula, ha='center', fontsize=9.5, color='#444444')
    fig.text(0.5, y, 'Percentages Within Each Region; Parentheses: City Counts; Circle Areas Not to Scale.' if metric != 'Population' else 'City-Level Stress Classification; Percentages Within Each Region; Circle Areas Not to Scale.', ha='center', fontsize=10, color='#555555')
