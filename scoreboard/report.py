"""Create static presentation charts and a results narrative entirely in Python."""
import html
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from .download import ROOT
from .models import run as run_models
from .scenarios import run as run_scenarios
from .finance import run as run_finance

NAVY='#15324f';TEAL='#008681';ORANGE='#df8332'

def markdown_table(frame):
    return '\n'.join(['| '+' | '.join(map(str,frame.columns))+' |','| '+' | '.join(['---']*len(frame.columns))+' |',*['| '+' | '.join(map(str,row))+' |' for row in frame.itertuples(index=False,name=None)]])

def main():
    data,models=run_models();scenarios=run_scenarios();finance_status=run_finance(data)
    d=data[data.public & data.cup_observed].copy()
    out=ROOT/'results/figures';out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.labelcolor':NAVY,'text.color':NAVY,'axes.edgecolor':'#c7d2dc','savefig.facecolor':'white','svg.hashsalt':'ac547-scoreboard'})
    def save(fig,name,caption):
        fig.text(.08,.025,caption.replace('$',r'\$'),fontsize=9,color='#526579',va='bottom')
        fig.savefig(out/f'{name}.png',dpi=200,bbox_inches='tight')
        svg=out/f'{name}.svg'
        fig.savefig(svg,bbox_inches='tight',metadata={'Date':None})
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
        plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,6));fig.subplots_adjust(bottom=.20)
    for code,label,color in [(1,'FBS',TEAL),(2,'FCS',ORANGE),(3,'Division I without football',NAVY)]:
        s=d[d.division_code==code]
        ax.scatter(s.expenses/1e6,s.cup_points,s=16,alpha=.35,label=label,color=color,edgecolors='none')
    ax.set_xscale('log');ax.set_xticks([5,10,20,50,100,200],labels=['5','10','20','50','100','200'])
    ax.set(xlabel='Annual athletic expenses ($ millions, nominal; log scale)',ylabel="Directors' Cup points",title='Spending and performance across public universities')
    ax.legend(frameon=False,fontsize=9);ax.grid(axis='y',alpha=.15)
    save(fig,'spending_performance',f'Source: EADA + NACDA, 2010–2019; {len(d):,} observed public school-years.\nPooled descriptive relationship; stable school differences are not controlled in this chart.')
    primary=models[(models.family=='primary')&models.term.isin(['lag_log_expenses','cup_100'])]
    all_cross_zero=((primary.ci_low<=0)&(primary.ci_high>=0)).all()
    interpretation=('The primary estimates have 95% confidence intervals that include zero.' if all_cross_zero else 'Some primary intervals exclude zero; inspect the complete coefficient table and adjusted tests before interpreting the chain.')
    significance=f'{int((primary.p_value<.05).sum())} of {len(primary)} primary exposure tests have unadjusted p < .05; {int((primary.holm_p_value<.05).sum())} have Holm-adjusted p < .05.'
    demand=primary[primary.term=='cup_100'].copy()
    fig,ax=plt.subplots(figsize=(9,3.8));fig.subplots_adjust(bottom=.28,left=.22)
    for pos,row in enumerate(demand.itertuples()):
        effect=100*np.expm1(row.coefficient);lo=100*np.expm1(row.ci_low);hi=100*np.expm1(row.ci_high)
        ax.errorbar(effect,pos,xerr=[[effect-lo],[hi-effect]],fmt='o',color=TEAL,capsize=5,markersize=8)
    ax.axvline(0,color=NAVY,lw=1);ax.set_yticks([0,1],labels=['Applications','First-time enrollment'])
    ax.set_ylim(-.6,1.6)
    ax.set(xlabel='Association with 100 additional Cup points (%)',title='Subsequent student demand: estimates remain uncertain')
    app_n=int(demand.loc[demand.model=='cup_to_applications','n'].iloc[0]);enr_n=int(demand.loc[demand.model=='cup_to_enrollment','n'].iloc[0])
    save(fig,'student_demand',f'Public universities; school and year effects; lagged enrollment control.\n95% clustered intervals; applications N={app_n:,}, enrollment N={enr_n:,}. Associations are not causal effects.')
    coverage=pd.read_csv(ROOT/'results/coverage.csv')
    fig,ax=plt.subplots(figsize=(10,5));fig.subplots_adjust(bottom=.22)
    ax.plot(coverage.year,coverage.public_di,'o-',color=NAVY,label='Public DI financial records')
    matches=data[data.public & data.cup_observed].groupby('year').size()
    ax.plot(matches.index,matches.values,'o-',color=TEAL,label='Also matched to final Cup standings')
    ax.set(xlabel='Athletic academic-year ending',ylabel='Universities',title='Coverage is audited before estimating relationships',xticks=range(2010,2020));ax.legend(frameon=False)
    save(fig,'coverage','Sources: EADA, IPEDS and NACDA. Missing Cup observations remain missing.\nRegression complete-case samples are smaller because exact-year lags and outcomes must be observed.')
    fig,ax=plt.subplots(figsize=(10,5.5));fig.subplots_adjust(bottom=.23)
    students=np.arange(0,1001,10)
    for cost,color in [(3000,TEAL),(6000,NAVY),(9000,ORANGE)]:
        ax.plot(students,(students*(12000-cost)-5e6)/1e6,label=f'Variable service cost ${cost:,}/student',color=color,lw=2)
    ax.axhline(0,color='#6c7884',lw=1);ax.set(xlabel='Hypothetical additional enrolled students',ylabel='Annual net contribution ($ millions)',title='Break-even depends on incremental enrollment and costs');ax.legend(frameon=False,fontsize=9)
    save(fig,'break_even','Illustrative assumptions: $5m extra annual athletics cost; $12,000 net tuition collected/student;\n$0 additional generated athletics revenue. These are scenarios, not estimated university ROI.')
    residual=pd.read_csv(ROOT/'results/residuals_cup_to_applications.csv')
    fig,ax=plt.subplots(figsize=(8.5,5));fig.subplots_adjust(bottom=.22)
    ax.scatter(residual.fitted_within,residual.residual,s=15,alpha=.25,color=TEAL);ax.axhline(0,color=NAVY,lw=1)
    ax.set(xlabel='Fitted within-university log applications',ylabel='Residual (log applications)',title='Model diagnostic: substantial unexplained variation')
    save(fig,'residuals','Applications model: after removing school and year effects.\nA residual diagnostic does not establish causal identification or validate an omitted-variable assumption.')
    # Findings use actual saved coefficients and N, never hand-entered optimistic results.
    rows=[]
    for r in primary.itertuples():
        if r.term=='lag_log_expenses':
            b=r.coefficient*np.log(1.1)*100;lo=r.ci_low*np.log(1.1)*100;hi=r.ci_high*np.log(1.1)*100
            effect=f'{b:+.2f} Cup points per 10% higher prior expenses';interval=f'[{lo:+.2f}, {hi:+.2f}] points'
        else:
            effect=f'{100*np.expm1(r.coefficient):+.2f}% per 100 Cup points';interval=f'[{100*np.expm1(r.ci_low):+.2f}%, {100*np.expm1(r.ci_high):+.2f}%]'
        rows.append({'Test':r.model,'Association':effect,'95% interval':interval,'p':f'{r.p_value:.3f}','Holm p':f'{r.holm_p_value:.3f}','N':r.n,'Schools':r.schools})
    pooled=d[['expenses','log_expenses','cup_points']].corr()
    profile=models[(models.model=='profile_vs_aggregate')&models.term.isin(['cup_100','fbs_10','mbb_10'])]
    profile_text='The football/basketball success comparison remains pending source validation.'
    if len(profile):
        ptable=pd.DataFrame([{'Measure':r.term,'Coefficient (log applications)':f'{r.coefficient:.5f}','95% interval':f'[{r.ci_low:.5f}, {r.ci_high:.5f}]','p':f'{r.p_value:.3f}','N':r.n,'Schools':r.schools} for r in profile.itertuples()])
        profile_text='Exploratory common-sample FBS model, with all three success measures included together. Aggregate units are 100 Cup points; sport units are 10 sport-specific Cup points. These coefficients cannot be compared directly as equal increments of success.\n\n'+markdown_table(ptable)+'\n\nSport points come from the archived fall/winter releases, which can be revised by the final spring standings. This is a visibility proxy, not regular-season win percentage. The football coefficient is conditional on overall Cup success, which itself contains football points; it describes a composition difference at fixed aggregate success, not the total effect of football. Secondary tests are exploratory and their p values are unadjusted.'
        labels={'cup_100':'Overall athletics (100 Cup points)','fbs_10':'Football (10 sport points)','mbb_10':"Men’s basketball (10 sport points)"}
        fig,ax=plt.subplots(figsize=(10,4.5));fig.subplots_adjust(left=.35,bottom=.28)
        for pos,row in enumerate(profile.itertuples()):
            effect=100*np.expm1(row.coefficient);lo=100*np.expm1(row.ci_low);hi=100*np.expm1(row.ci_high)
            ax.errorbar(effect,pos,xerr=[[effect-lo],[hi-effect]],fmt='o',color=TEAL,capsize=5)
        ax.set_yticks(range(len(profile)),labels=[labels[x] for x in profile.term]);ax.set_ylim(-.6,2.6);ax.axvline(0,color=NAVY,lw=1)
        ax.set(xlabel='Conditional association with fall t+1 applications (%)',title='High-profile sports and aggregate success')
        save(fig,'sport_comparison',f'Common FBS sample; N={int(profile.n.min()):,}; 95% school-clustered intervals.\nExposure units differ. Joint model holds other success measures fixed. Exploratory, not causal.')
    text=f'''# Beyond the Scoreboard: working empirical findings

**Historical EADA-only starter:** use `FEASIBILITY_REPORT.md` for the audited Knight/ESPN financial and Flutie analysis. This page preserves the earlier public-source model results separately.

## Decision finding

This historical panel does **not establish a causal athletics spending → success → student-demand payoff**. {interpretation} This does not prove there is no effect. No causal university ROI has been estimated.

## What was actually analyzed

- {len(data):,} EADA Division I institution-years, 2010–2019, representing {data.unitid.nunique()} distinct UNITIDs.
- {int(data.public.sum()):,} public institution-years; {len(d):,} also matched to final Directors' Cup standings.
- Exact-year lags and complete-case exclusions produce the smaller model samples below. Admissions models use fall t+1 and end before the pandemic; all outcomes stop in 2019.
- Every acquisition, transformation, calculation, model and chart is implemented in Python.

## Primary estimates

{markdown_table(pd.DataFrame(rows))}

Models include university and year effects, lagged total enrollment, and school-clustered standard errors. The spending model also controls for prior sport-participation categories. {significance} Intervals and p values are not probabilities that a hypothesis is true.

The pooled correlation between log expenses and Cup points is **{pooled.loc['log_expenses','cup_points']:.3f}**; the raw-dollar correlation is **{pooled.loc['expenses','cup_points']:.3f}**. These cross-university correlations should not be substituted for the within-university estimates. Wealth, program breadth and persistent reputation can explain between-school patterns.

## High-profile sports versus aggregate success

{profile_text}

## Accounting conclusions

EADA reported revenue is not subsidy-adjusted generated revenue. The secondary EADA reported-revenue regression therefore tests a different measure and cannot establish direct financial self-sufficiency. Financial model status: **{finance_status['status']}**. The registered 2010–2019 Knight workbook has now been acquired, joined with audited source IDs/calendars and analyzed in the separate `FEASIBILITY_REPORT.md`. Its revenue-after-support measure remains qualified by transfer/reporting definitions. This page preserves the earlier EADA estimates; it does not present them as Knight financial estimates. The original workbook and school-level financial observations remain in ignored data/private.

In the explicit hypothetical scenario, a $5m annual increase in athletics cost, no added generated athletics revenue, and $6,000 annual net contribution per extra student would require **{math.ceil(5_000_000/6000):,} additional students** to cover the cost ({5_000_000/6000:,.2f} before rounding). The project does not identify that many students attributable to athletics. Alternative assumptions are in `return_scenarios.csv`.

## Robustness and limits

`models.csv` contains all planned estimated sensitivity models, including timing, application growth, changes in performance, expense-tail trimming, balanced Cup coverage, a pre-scoring-change restriction, and FBS/FCS/nonfootball subsamples. These exploratory comparisons are not a search for a significant result. The finding above is tied to the primary tests and is not changed by selectively choosing another model.

The Cup sample conditions on observed scorers. Financial reporting, school/system boundaries, shifting sport counts, scoring rules, imputation, admissions policy and conference changes can matter. Fixed effects do not eliminate time-varying confounding or reverse causality. University finance fields are downloaded for context; they are not used to claim a marginal tuition contribution. Post-2021 NIL/pandemic analysis, causal mediation, and a complete NPV model remain outside this starter's validated scope.

Earlier football/FPI pilot claims from the prior conversation have not been independently reproduced and are **not** evidence from this analysis.

## Review and reproduce

See `README.md`, `docs/methods.md`, `docs/sources.md`, `docs/assignment_checklist.md`, and the source/hash manifest. The final slides, five-member contributions, instructor consultation, and teammate/instructor repository invitations remain group actions.
'''
    (ROOT/'FINDINGS.md').write_text(text,encoding='utf-8')
    # A static browsable report; all content and numbers are produced in Python.
    body=''.join(f'<p>{html.escape(p)}</p>' for p in text.split('\n\n'))
    chart_names=['spending_performance','student_demand','coverage','break_even','residuals']+(['sport_comparison'] if len(profile) else [])
    images=''.join(f'<figure><img src="figures/{name}.png" alt="{name.replace("_"," ")}"/></figure>' for name in chart_names)
    (ROOT/'results/report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Beyond the Scoreboard</title><style>body{font:16px/1.6 system-ui;max-width:1050px;margin:40px auto;color:#15324f;padding:24px}p{white-space:pre-wrap}img{width:100%}figure{margin:50px 0}</style>'+body+images+'</html>',encoding='utf-8')
    print(f'Wrote findings, static report and {len(chart_names)} chart pairs.')

if __name__=='__main__':main()
