"""Slide 5 chart from the saved, fully reproduced STE estimates."""
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

from .download import ROOT
from .hashes import text_sha256
from .presentation_charts import OUT, NAVY, TEAL, GRAY, point, save


def main():
    OUT.mkdir(exist_ok=True)
    path = ROOT / 'results/anderson_replication.csv'
    result = pd.read_csv(path)
    ste = result.loc[result.estimator.eq('STE')].set_index('outcome')
    gift = ste.loc['alumni_ops_athletics']; apps = ste.loc['applicants']
    if not ste[['coefficient_matches_printed', 'std_error_matches_printed', 'n_matches_printed']].to_numpy().all():
        raise ValueError('Presentation requires the validated STE replication')
    plt.rcParams['svg.hashsalt'] = 'beyond-the-scoreboard-donations'
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 7.2), facecolor='white')
    fig.subplots_adjust(left=.10, right=.95, bottom=.32, top=.65, wspace=.32)
    fig.text(.07, .93, 'Football wins: donation evidence, uncertain recruitment',
             fontsize=22, weight='bold', color=NAVY, va='top')
    fig.text(.07, .85, 'Earlier football study reproduced in Python; estimate per additional win',
             fontsize=15, color=GRAY, va='top')
    for ax, row, title, limit in zip(axes, [gift, apps], ['Athletic alumni gifts ($1,000s)', 'Applications'], [(-30, 350), (-70, 240)]):
        b, lo, hi = point(ax, row, 0)
        label = f'${b:.0f}k  (${lo:.0f}k–${hi:.0f}k)' if row.name == 'alumni_ops_athletics' else f'+{b:.0f}  ({lo:.0f} to +{hi:.0f})'
        ax.text(b, .34, label, ha='center', fontsize=17, color=NAVY)
        ax.axvline(0, color=GRAY, lw=1.5)
        ax.set_ylim(-.6, .7); ax.set_xlim(*limit); ax.set_yticks([])
        ax.set_xlabel(title, fontsize=17, labelpad=14)
        ax.tick_params(axis='x', labelsize=15, length=0, pad=12)
        ax.spines[['top', 'right', 'left']].set_visible(False)
        ax.spines['bottom'].set_color('#bbc6cd'); ax.grid(axis='x', alpha=.15)
    note = (f'Donations: N={int(gift.n)}, {int(gift.schools)} schools. Applications: N={int(apps.n)}, {int(apps.schools)} schools. Lines: unadjusted 95% ranges.\n'
            f'Donation adjusted p: {gift.holm_ten_outcomes_p:.3f} across 10 outcomes; {gift.holm_all_twenty_p:.3f} across 20 tests. Broader correction is inconclusive.\n'
            'Anderson historical data; source-period dollars. All 10 STE estimates match; IV remains partial.\n'
            'Gifts fund athletics; they are not verified unrestricted university income. This does not identify returns to spending.')
    save(fig, '05_winning_donations', note)
    manifest = dict(source='results/anderson_replication.csv', sha256=text_sha256(path),
                    estimator='STE', purpose='Presentation of saved results; no new estimates',
                    outcomes={name: ste.loc[name].to_dict() for name in ['alumni_ops_athletics', 'applicants']},
                    qualification='Unadjusted coefficient intervals; ten-outcome and twenty-test Holm values both displayed; IV translation partial')
    (ROOT / 'data/provenance/presentation_donations.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('Built the donations/applications presentation chart from saved STE results.')


if __name__ == '__main__': main()
