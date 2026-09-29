from project import input_file, output_dir
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from venn_boundaries import panel
from plot_exposure_venn import save, REGIONS

def main():
    data = pd.read_csv(input_file('fixed_thresholds_pm10_city_details.csv'))
    cols = ['urban_wind_10m_m_s', 'urban_utci_C', 'urban_pm25_ug_m3']
    if data.city_id.duplicated().any() or not np.isfinite(data[cols]).all().all():
        raise ValueError('Duplicate cities or missing threshold inputs')
    if not data.NSclass.isin([0, 1]).all():
        raise ValueError('Unknown North/South classification')
    data['combination'] = (data[cols[0]] < 2).astype(int) * 4 + (data[cols[1]] > 26).astype(int) * 2 + (data[cols[2]] > 10).astype(int)
    records = []
    for code, region in enumerate(REGIONS):
        subset = data.loc[data.NSclass.eq(code)]
        if subset.empty:
            raise ValueError('Empty regional sample')
        for category in range(8):
            n = int(subset.combination.eq(category).sum())
            records.append(dict(region=region, scheme='combination', category=category, city_count=n, city_denominator=len(subset), city_percent=100 * n / len(subset)))
    summary = pd.DataFrame(records)
    summary.to_csv(output_dir() / 'fig4_region_summary.csv', index=False)
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 5.8))
    fig.subplots_adjust(left=0.035, right=0.965, top=0.9, bottom=0.04, wspace=0.1)
    for ax, region in zip(axes, REGIONS):
        panel(ax, summary, region, 'Cities', 'square')
    save(fig, 'Fig4_compound_stress')
if __name__ == '__main__':
    main()
