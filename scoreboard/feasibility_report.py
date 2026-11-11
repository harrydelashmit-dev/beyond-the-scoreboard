"""Build the CFO feasibility report and publication figures from saved results."""
import html
import json
import math
import re
import hashlib

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .download import ROOT
from .cfo_scenarios import main as scenarios
from .hashes import text_sha256

NAVY='#15324f';TEAL='#008681';ORANGE='#c87826';GRAY='#6a7783'
EXPOSURE={'cup':'100 additional Cup points','fpi':'10 additional FPI points',
          'sweet16':'Sweet Sixteen appearance'}
SHORT={'cup':'Cup +100 points','fpi':'Football FPI +10','sweet16':'Basketball Sweet16'}
REVENUE_LABEL={'ticket_sales':'Ticket receipts','donor_contributions':'Athletics donations',
               'net_nonallocated_revenue_proxy':'Revenue after allocated support (proxy)'}


def percent(values):return 100*np.expm1(np.asarray(values,dtype=float))
def pvalue(value):return f'{value:.2e}' if value<.001 else f'{value:.3f}'
def signed(value):return f'{value:+.2f}'
def md_table(frame):
    def cell(x):return str(x).replace('|','/').replace('\n',' ')
    return '\n'.join(['| '+' | '.join(map(cell,frame.columns))+' |',
        '| '+' | '.join(['---']*len(frame.columns))+' |',
        *['| '+' | '.join(map(cell,row))+' |' for row in frame.itertuples(index=False,name=None)]])


def choose(models,name,term=None):
    d=models[models.model.eq(name)]
    if term is not None:d=d[d.term.eq(term)]
    else:d=d[d.exposure_term]
    if len(d)==0:raise ValueError(f'Result missing: {name}:{term}')
    return d.iloc[0]


def primary_table(models,family):
    rows=[]
    for r in models[models.primary&models.exposure_term&models.family.eq(family)].itertuples():
        values=np.array([r.coefficient,r.ci_low,r.ci_high])
        if r.model=='A_spend_cup':
            effect=values*np.log(1.1)*100;unit=' Cup points';label='Prior total expense +10% → Cup'
        elif r.model=='A_spend_fpi':
            effect=values*np.log(1.1)*10;unit=' FPI points';label='Prior football expense +10% → FPI'
        elif r.model=='A_spend_sweet16':
            effect=values*np.log(1.1)*100;unit=' percentage points';label='Prior basketball expense +10% → Sweet16 probability'
        else:
            effect=percent(values);unit='%'
            target=r.outcome.removeprefix('next_').removeprefix('log_')
            label=EXPOSURE[r.metric]+' → '+REVENUE_LABEL.get(target,target.replace('_',' '))
        rows.append({'Test':label,'Association':signed(effect[0])+unit,
            '95% interval':f'[{signed(effect[1])}, {signed(effect[2])}]'+unit,
            'Raw p':pvalue(r.p_value),'Holm p (family)':pvalue(r.holm_family_p),
            'N / schools':f'{r.n:,} / {r.schools}',
            'Exposure years':f'{r.year_min}–{r.year_max}'})
    return pd.DataFrame(rows)


def save_figure(fig,name,caption):
    fig.text(.06,.02,caption.replace('$',r'\$'),fontsize=9,color=GRAY,va='bottom')
    out=ROOT/'results/figures'
    fig.savefig(out/f'{name}.png',dpi=200,bbox_inches='tight')
    svg=out/f'{name}.svg'
    fig.savefig(svg,bbox_inches='tight',metadata={'Date':None})
    svg.write_bytes(('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n').encode('utf-8'))
    plt.close(fig)


def financial_chart(models):
    fig,axes=plt.subplots(1,3,figsize=(14,5.5),sharey=True)
    fig.subplots_adjust(bottom=.28,left=.16,wspace=.25,top=.78)
    titles=['Tickets, fiscal t+1','Athletics donations, fiscal t+1','Revenue after support, fiscal t+1\n(net-of-transfers proxy)']
    for ax,revenue,title in zip(axes,REVENUE_LABEL,titles):
        for pos,metric in enumerate(['cup','fpi','sweet16']):
            r=choose(models,f'B_{metric}_{revenue}')
            b,lo,hi=percent([r.coefficient,r.ci_low,r.ci_high])
            ax.errorbar(b,2-pos,xerr=[[b-lo],[hi-b]],fmt='o',capsize=4,
                color=TEAL if metric=='fpi' else NAVY,markersize=7,
                markerfacecolor=TEAL if r.holm_family_p<.05 else 'white')
        ax.axvline(0,color=GRAY,lw=1)
        ax.set_title(title,fontsize=11)
        ax.set_xlabel('Association (%)')
        ax.grid(axis='x',alpha=.12)
        ax.set_ylim(-.6,2.6)
    axes[0].set_yticks([2,1,0],labels=[SHORT[m] for m in ['cup','fpi','sweet16']])
    fig.suptitle('Football strength has the clearest association with subsequent receipts',fontsize=15,fontweight='bold',y=.96)
    save_figure(fig,'feasibility_financial_returns','Knight-Newhouse 2010–2019; school and conference-by-year effects; school-clustered 95% pointwise intervals.\nFilled markers pass Holm correction across nine financial tests. Original licensed financial observations remain local. Associations do not establish ROI.')


def student_chart(models):
    fig,axes=plt.subplots(1,2,figsize=(12,5.2),sharey=True)
    fig.subplots_adjust(bottom=.30,left=.19,wspace=.28,top=.80)
    for ax,outcome,title in zip(axes,['applications','first_time_enrollment'],['Applications','First-time enrollment']):
        for pos,metric in enumerate(['cup','fpi','sweet16']):
            r=choose(models,f'C_{metric}_{outcome}')
            b,lo,hi=percent([r.coefficient,r.ci_low,r.ci_high])
            ax.errorbar(b,2-pos,xerr=[[b-lo],[hi-b]],fmt='o',capsize=4,color=NAVY,
                markerfacecolor='white',markersize=7)
        ax.axvline(0,color=GRAY,lw=1);ax.set_title(title,fontsize=12)
        ax.set_xlabel('Association (%)');ax.grid(axis='x',alpha=.12);ax.set_ylim(-.6,2.6)
    axes[0].set_yticks([2,1,0],labels=[SHORT[m] for m in ['cup','fpi','sweet16']])
    fig.suptitle('Primary student-demand estimates remain uncertain',fontsize=15,fontweight='bold',y=.96)
    save_figure(fig,'feasibility_student_demand','IPEDS + NACDA/ESPN, 2010–2019 source window; school and conference-by-year effects; 95% pointwise clustered intervals.\nFootball season t−1 → fall t; Cup/Sweet16 ending t → fall t+1. None of six primary demand tests passes family Holm correction.')


def correlation_chart(correlations):
    c=correlations[correlations['sample'].str.startswith('FY2014-2019')]
    keys=[('football_spending','fpi'),('football_coaching_salaries','fpi'),('fpi','ticket_sales')]
    fig,ax=plt.subplots(figsize=(11,5.8));fig.subplots_adjust(left=.27,bottom=.33)
    for offset,(relation,label,color) in zip([-.24,0,.24],[
        ('pooled_school_years','Pooled school-years',NAVY),
        ('between_school_means','Between-school averages',TEAL),
        ('within_school_demeaned','Within-school deviations',ORANGE)]):
        values=[float(c[(c.x.eq(x))&(c.y.eq(y))&c.relation.eq(relation)].pearson_r.iloc[0]) for x,y in keys]
        ax.barh(np.arange(3)+offset,values,height=.21,label=label,color=color)
    ax.set_yticks(range(3),labels=['Football spending / FPI','Coaching compensation / FPI','FPI / ticket receipts'])
    ax.set(xlabel='Pearson correlation',xlim=(min(-.05,float(c.pearson_r.min())-.05),1),title='Pooled correlations are stronger than within-school correlations')
    ax.axvline(0,color=GRAY,lw=1)
    ax.legend(frameon=False,fontsize=8,loc='upper center',bbox_to_anchor=(.5,-.18),ncol=3)
    save_figure(fig,'feasibility_pooled_within','Independent public-school data, FY2014–2019 matched to football seasons 2013–2018. Raw dollar correlations are descriptive.\nWithin bars remove school means only; the panel regressions additionally absorb time/conference effects. These are different statistical comparisons.')


def robustness_chart(models,kind):
    if kind=='football':
        base='B_fpi_ticket_sales'
        selected=[(base,'School + conference/year (primary)'),(base+'_school_year','School + year'),
            (base+'_prior_budget','Add prior athletics budget'),(base+'_first_differences','First differences'),
            (base+'_school_trends','School-specific trends'),(base+'_extra_year','Two-year revenue lag')]
        title='Football–ticket estimates vary with timing and specification'
        note='First differences compare annual changes; other rows use log receipt levels. These exploratory specifications estimate conditional associations.'
    else:
        base='C_sweet16_applications'
        selected=[(base,'School + conference/year (primary)'),(base+'_school_year','School + year'),
            (base+'_first_differences','First differences'),(base+'_school_trends','School-specific trends'),
            (base+'_extra_year','Two-year outcome lag')]
        title='Basketball application results depend on the growth specification'
        note='Exploratory: first differences relate changes in log applications to changes in Sweet16 status; trends allow different school growth paths.'
    fig,ax=plt.subplots(figsize=(11,5.8));fig.subplots_adjust(left=.33,bottom=.27)
    for pos,(model,label) in enumerate(selected):
        r=choose(models,model);b,lo,hi=percent([r.coefficient,r.ci_low,r.ci_high])
        ax.errorbar(b,len(selected)-1-pos,xerr=[[b-lo],[hi-b]],fmt='o',capsize=4,
            color=TEAL if pos==0 else NAVY,markersize=7,
            markerfacecolor=TEAL if bool(r.primary) and pd.notna(r.holm_family_p) and r.holm_family_p<.05 else 'white')
    ax.axvline(0,color=GRAY,lw=1)
    ax.set_yticks(range(len(selected)),labels=[label for _,label in selected][::-1])
    ax.set(xlabel='Percent association (levels or growth factor, as labeled)',title=title)
    ax.grid(axis='x',alpha=.12)
    family='financial' if kind=='football' else 'student-demand'
    save_figure(fig,'feasibility_'+kind+'_robustness',f'95% school-clustered pointwise intervals; primary {family} inference also uses the reported Holm-adjusted p value.\n'+note)


def scenario_chart():
    fig,ax=plt.subplots(figsize=(10,5.5));fig.subplots_adjust(bottom=.25)
    students=np.arange(0,1001,5)
    for receipts,color in [(0,NAVY),(1_000_000,TEAL),(3_000_000,ORANGE)]:
        ax.plot(students,(receipts+students*6000-5_000_000)/1e6,
            label=f'Extra annual athletics receipts ${receipts/1e6:.0f}m',color=color,lw=2)
    ax.axhline(0,color=GRAY,lw=1)
    ax.axvline(500,color=GRAY,lw=1,linestyle='--',label='500-student cap in NPV scenarios')
    ax.set(xlabel='Hypothetical extra enrolled student stock each year',
        ylabel='Annual incremental contribution ($ millions)',title='Break-even requires cash benefits sufficient to cover incremental cost')
    ax.legend(frameon=False,fontsize=9)
    save_figure(fig,'feasibility_cfo_break_even','Illustrative: $5m extra annual athletics cash cost and $6,000 net tuition contribution per extra enrolled student.\nStudent stock differs from new first-time intake. Neither the receipts nor students are identified causal effects; capital outlays are modeled separately in the NPV tables.')


def selected_table(models,items):
    rows=[]
    for name,label in items:
        r=choose(models,name);b,lo,hi=percent([r.coefficient,r.ci_low,r.ci_high])
        rows.append({'Specification':label,'Association':signed(b)+'%',
            '95% interval':f'[{signed(lo)}, {signed(hi)}]%',
            'Raw p':pvalue(r.p_value),'N / schools':f'{int(r.n):,} / {int(r.schools)}'})
    return pd.DataFrame(rows)


def inline_markup(text):
    escaped=html.escape(text)
    escaped=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',escaped)
    escaped=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',escaped)
    escaped=re.sub(r'`([^`]+)`',r'<code>\1</code>',escaped)
    return escaped


def main():
    models=pd.read_csv(ROOT/'results/feasibility_models.csv')
    status=pd.read_csv(ROOT/'results/feasibility_model_status.csv')
    coverage=pd.read_csv(ROOT/'results/feasibility_coverage.csv')
    correlations=pd.read_csv(ROOT/'results/pilot_correlations.csv')
    pilot=pd.read_csv(ROOT/'results/pilot_models.csv')
    influence=pd.read_csv(ROOT/'results/feasibility_influence.csv')
    support=pd.read_csv(ROOT/'results/feasibility_event_support.csv')
    validation_path=ROOT/'data/provenance/feasibility_validation.json'
    analysis_path=ROOT/'data/provenance/feasibility_analysis_manifest.json'
    validated=False
    if validation_path.exists() and analysis_path.exists():
        verification=json.loads(validation_path.read_text(encoding='utf-8'))
        execution=json.loads(analysis_path.read_text(encoding='utf-8'))
        validated=(verification.get('panel_sha256')==execution.get('panel_sha256') and
            verification.get('results_sha256')==text_sha256(ROOT/'results/feasibility_models.csv'))
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,
        'axes.spines.right':False,'axes.titleweight':'bold','axes.labelcolor':NAVY,'text.color':NAVY,
        'axes.edgecolor':'#c7d2dc','savefig.facecolor':'white','svg.hashsalt':'ac547-feasibility'})
    (ROOT/'results/figures').mkdir(exist_ok=True)
    financial_chart(models);student_chart(models);correlation_chart(correlations)
    robustness_chart(models,'football');robustness_chart(models,'basketball');scenario_chart()
    break_even,npvs=scenarios()
    primary=models[models.primary&models.exposure_term].copy()
    primary.to_csv(ROOT/'results/feasibility_primary_coefficients.csv',index=False)
    primary[['model','term','coefficient','std_error','ci_low','ci_high','p_value','holm_family_p',
        'holm_all_primary_p','n','schools','year_min','year_max','controls','fixed_effects','cluster']].to_csv(
            ROOT/'results/feasibility_primary_summary.csv',index=False)
    tables={family:primary_table(models,family) for family in ['spending_success','success_finance','flutie']}
    ticket=choose(models,'B_fpi_ticket_sales');net=choose(models,'B_fpi_net_nonallocated_revenue_proxy')
    ticket_pct=percent([ticket.coefficient,ticket.ci_low,ticket.ci_high])
    net_pct=percent([net.coefficient,net.ci_low,net.ci_high])
    later_ticket=choose(models,'B_fpi_ticket_sales_extra_year')
    later_pct=percent([later_ticket.coefficient,later_ticket.ci_low,later_ticket.ci_high])
    sections=[]
    def section(title,*elements):sections.append((title,list(elements)))
    section('Feasibility decision',
        '**Proceed with the project as a conditional financial-return study.** The strongest validated relationship is football strength predicting subsequent athletics receipts. The available data do not establish that additional spending causes better performance or a positive university-wide return.',
        f'In the primary model, 10 more FPI points are associated with **{ticket_pct[0]:.2f}% higher next-year ticket receipts** (95% interval {ticket_pct[1]:.2f}% to {ticket_pct[2]:.2f}%; raw p={pvalue(ticket.p_value)}; financial-family Holm p={pvalue(ticket.holm_family_p)}; N={int(ticket.n)}, {int(ticket.schools)} schools). Revenue after reported allocated support is associated with a **{net_pct[0]:.2f}% increase** (interval {net_pct[1]:.2f}% to {net_pct[2]:.2f}%; Holm p={pvalue(net.holm_family_p)}), subject to the transfer-definition qualification below.',
        'None of the three primary spending-success tests or six primary student-demand tests passes the family-adjusted 5% threshold. Basketball nevertheless shows a positive applications association in first-difference and school-trend models. That is a useful, specification-sensitive finding to investigate—not a reason to claim either a universal Flutie Effect or no Flutie Effect.',
        'The proposed spending → success → receipts/student demand → financial return chain remains a pathway to test. The regressions do not identify causal mediation and their coefficients must not be multiplied into an ROI estimate.')
    section('Dataset and merge audit',
        'The registered workbook contains 2,400 rows for 240 listed institutions. There are 2,289 rows with total revenue and expense data. Historical subdivision eligibility yields 2,322 Division I school-years; excluding three programs with consolidation/scope changes leaves 2,292 primary-eligible rows before model-specific missingness and lags. Missing financial observations and Cup scores remain missing.',
        'All 2,400 source rows retain their original financial values and join to an IPEDS institution. The stable athletics-program key is distinct from the retained original source IDs. Kennesaw’s former ID 140164 maps to program 486840; the fall-2015 duplicate is resolved to the active consolidated IPEDS entity. Kennesaw, UTRGV, and Purdue Fort Wayne are excluded from primary models and included in a sensitivity analysis.',
        'ESPN football season s maps to academic/fiscal ending year s+1; each FPI snapshot is verified to occur after the season in January/February. Fall IC conference collection t−1 maps to the season ending t, checked against Nebraska’s Big12-to-BigTen transition. IPEDS pre-2014 APPDATE cohort rules and reported/imputed flags use the original dictionaries.',
        'Football student demand uses fall t following football season t−1. Cup/Sweet16 demand uses fall t+1 following the spring season ending t. Financial returns use fiscal t+1. Alternate-fall and extra-year lags are reported. No outcomes after 2019 are invented. Early and late source years are lost where a required lag/outcome is unavailable.',
        'Sweet16 and main64 indicators come from exhaustive annual NACDA ledgers: exactly 16 and 64 matched schools each year. A negative event-membership indicator is derived only after that completeness check; it is not a fabricated zero Cup score. Final/opening AP polls are checked against their own year/type; opening polls require all ranked teams to have played zero games.',
        ('table',coverage[['year','listed','di_eligible','primary_eligible','financial_expenses','cup_observed','fpi_observed']].rename(
            columns={'year':'Year','listed':'Listed schools','di_eligible':'DI schools','primary_eligible':'Primary eligible',
                     'financial_expenses':'Expense reports','cup_observed':'Cup matches','fpi_observed':'FPI schools'})),
        f'Validation: {"source-cell preservation, exact future-cohort joins, all 18 primary sample sizes, and three independent full-rank dummy-OLS comparisons passed" if validated else "final independent execution checks pending"}. The saved coefficients, standard errors and p-values agree with the independent implementation. Audit details are in `data/provenance/feasibility_validation.json`; school-level licensed join/sample files remain local.')
    section('Specifications and inference',
        'The expanded plan was recorded before the new estimation in `config/feasibility_plan.json`. There are 18 primary exposure tests: three spending-success, nine success-finance, and six student-demand tests. Primary models absorb school and contemporaneous basketball-conference-by-year effects. This controls stable school differences and common annual conference conditions; lagged log total enrollment is included throughout. Spending models also control the lagged EADA sport participation-category count, a proxy for sponsored teams rather than an exact NCAA team count.',
        'All uncertainty is clustered by school, with a Student t reference using schools minus one degrees of freedom; absorbed parameter rank enters the covariance correction. Singleton cells are removed recursively. Reported intervals are pointwise 95% intervals. Holm p-values adjust within the three primary families; the CSV also provides Holm adjustment across all 18. Secondary tests are exploratory and their displayed p-values are unadjusted.',
        f'All **{status.model.nunique()} primary/secondary specifications** executed; status and complete-case exclusions are recorded in `results/feasibility_model_status.csv` and `feasibility_sample_flow.csv`. Raw coefficients, controls, fixed effects, N, schools, years, intervals and p-values are in `feasibility_models.csv`. This is an internal research plan, not an externally registered protocol; the earlier EADA results were already known. Additional audit checks are fully reported and the primary grid was retained. Some specifications estimate different comparisons; a lower p-value does not make one the preferred causal model.')
    section('1. Athletic spending and competitive success',
        'These are changes within the same program after the stated controls. Monetary predictors are logged; the table scales the result to 10% higher prior spending. Basketball uses EADA sport-specific expense because the registered Knight report does not provide that measure. Its binary Sweet16 outcome uses a linear probability model.',
        ('table',tables['spending_success']),
        'The positive point estimates are compatible with spending helping performance, but these primary intervals include zero. Strong pooled spending/performance correlations mostly compare programs with different established resources. They cannot show that increasing a particular program’s budget will generate the same improvement. Current-spending, Cup-rank/percentile, pre-2018 scoring, balanced-Cup and coaching-reporting checks are included in the complete results.')
    section('2. Competitive success and subsequent athletics finances',
        ('table',tables['success_finance']),
        ('figure','feasibility_financial_returns'),
        'Exploratory actual-win and visibility checks are below. Actual winning percentage also has a positive ticket association, so the financial pattern is not confined to the FPI definition. Coarser AP/breakthrough indicators are less conclusive. These p-values are unadjusted and the success units are different.',
        ('table',selected_table(models,[
            ('football_win_pct_10pp_next_log_ticket_sales','Win percentage +10 points → tickets'),
            ('football_win_pct_10pp_next_log_net_nonallocated_revenue_proxy','Win percentage +10 points → revenue-after-support proxy'),
            ('football_ap_top20_next_log_ticket_sales','Final AP top20 → tickets'),
            ('football_preseason_unranked_breakthrough_next_log_ticket_sales','Opening-unranked → final top20 → tickets')])),
        'Football’s ticket and revenue-after-support associations pass both within-financial-family Holm correction and the all-18-primary correction. Its donor association is positive at the raw 5% level but does not pass the nine-test financial-family correction. Cup/ticket and Sweet16/donation or revenue-proxy associations also fail that family correction. A small raw p-value is not labeled confirmatory evidence when its adjusted test does not pass.',
        'The success measures have different units and samples. A smaller p-value for football does not by itself establish a statistically larger effect than basketball/Cup success or a superior return per dollar spent. The common-sample models address sample comparability; causal cost-effectiveness remains unidentified.',
        'The receipt components are all-sports ticket receipts and athletics-designated donations, not football-only ticket receipts or all university philanthropy. Donations can contain restricted or in-kind support. Revenue after support is **exported total revenues minus the separate institutional/government-support and student-fee fields**. Total revenue already nets transfers to the institution; source expense definitions can include excess transfers. This is a qualified accounting proxy, not gross externally generated revenue, cash operating profit, or the university’s economic return. The [Knight methodology](https://knightnewhousedata.org/about-the-data) explains the reporting categories.',
        ('figure','feasibility_football_robustness'),
        f'The next-year football/ticket result remains positive after prior-budget controls, first differencing and school-specific trends. At a two-year financial lag, the estimate is {later_pct[0]:.2f}% (interval {later_pct[1]:.2f}% to {later_pct[2]:.2f}%; raw p={pvalue(later_ticket.p_value)}), which includes zero. The annual association must not be projected automatically into a permanent revenue gain.')
    section('3. The Flutie Effect: applications and first-time enrollment',
        ('table',tables['flutie']),
        ('figure','feasibility_student_demand'),
        'No primary demand measure clears the six-test Holm correction. Football’s first-time-enrollment coefficient has a raw p just below .05 but not an adjusted p below .05. Cup estimates are comparatively small; FPI/application and Sweet16/application intervals still admit meaningful positive or negative associations. Failure to reject zero does not prove no effect or identify whether measurement, capacity, omitted changes, or limited identifying variation explains the result.',
        ('table',selected_table(models,[
            ('C_sweet16_applications','Sweet16, primary level model'),
            ('C_sweet16_applications_first_differences','Sweet16, annual changes'),
            ('C_sweet16_applications_school_trends','Sweet16, school-specific trends'),
            ('C_sweet16_applications_extra_year','Sweet16, two-year outcome lag'),
            ('football_ap_top20_log_applications','Final AP top20, following fall'),
            ('football_preseason_unranked_breakthrough_log_applications','Opening-unranked → final AP top20'),
            ('basketball_main64_next_log_applications','Main64 basketball appearance') ])),
        ('figure','feasibility_basketball_robustness'),
        'The Sweet16 annual-change coefficient is approximately .0334 log points (about 3.4% in the application-growth factor), while allowing school-specific trends gives roughly 3.5% higher application levels. Both are exploratory, unadjusted findings. The primary level model and extra-year model remain inconclusive. These results suggest that growth assumptions matter; they do not justify selecting the favorable model as proof. AP top20, preseason-unranked breakthroughs, main64 participation, football win percentage and other lags are all reported, including their insignificant results.',
        'The following diagnostic holds the school-year cases fixed to separate sample composition from the growth/control choices. Differences are calculated on the full calendar panel before applying the common-case restriction. The table varies level versus annual-change outcomes, conference/year versus year controls, and school-specific trends; it does not replace the primary model.',
        ('table',selected_table(models,[
            ('C_sweet16_common_fd_level_conference_year','Same cases: levels, school + conference/year'),
            ('C_sweet16_common_fd_level_year','Same cases: levels, school + year'),
            ('C_sweet16_common_fd_changes_year','Same cases: annual changes, year'),
            ('C_sweet16_common_fd_changes_conference_year','Same cases: annual changes, conference/year'),
            ('C_sweet16_common_fd_school_trends','Same cases: levels, school-specific trends')])),
        'On these identical cases, the annual-change estimate remains positive with conference/year controls. Level models remain inconclusive, and the school-trend interval now includes zero. Thus sample composition alone does not explain the change-model signal, but the favorable trend result is not stable across the two samples. No one model is promoted after seeing its significance.',
        'Same-sample aggregate-only, football-only, basketball-only and joint comparisons use identical FBS school-years and the same subsequent fall. A joint coefficient holds total Cup performance—including the high-profile sports—fixed, so it is a conditional composition comparison, not the sport’s total effect. These comparisons are in the `common_` models.')
    corr=correlations[correlations['sample'].str.startswith('FY2014-2019')]
    corr_rows=[]
    for x,y,label in [('football_spending','fpi','Football expense / FPI'),
                      ('football_coaching_salaries','fpi','Coaching compensation / FPI'),
                      ('fpi','ticket_sales','FPI / ticket receipts')]:
        g=corr[corr.x.eq(x)&corr.y.eq(y)]
        pooled=g[g.relation.eq('pooled_school_years')].iloc[0]
        corr_rows.append({'Relationship':label,'Earlier claim':f'{pooled.prior_claim:.3f}',
            'Independent pooled r':f'{pooled.pearson_r:.3f}',
            'Between-school r':f'{g[g.relation.eq("between_school_means")].pearson_r.iloc[0]:.3f}',
            'Within-school r':f'{g[g.relation.eq("within_school_demeaned")].pearson_r.iloc[0]:.3f}',
            'Pooled N / schools':f'{int(pooled.n)} / {int(pooled.schools)}'})
    pilot_row=pilot[pilot.model.eq('pilot_fpi_ticket')&pilot.term.eq('fpi_10')].iloc[0]
    pb,pl,ph=percent([pilot_row.coefficient,pilot_row.ci_low,pilot_row.ci_high])
    section('Independent audit of the earlier football pilot',
        ('table',pd.DataFrame(corr_rows)),('figure','feasibility_pooled_within'),
        f'The independently assembled FY2014–2019 data show positive pooled correlations in the same directions, with different magnitudes and about 111 schools rather than the unknown original 52. The school/year-only following-year ticket model gives **{pb:.2f}% per 10 FPI points** (interval {pl:.2f}% to {ph:.2f}%, p={pvalue(pilot_row.p_value)}, N={int(pilot_row.n)}, {int(pilot_row.schools)} schools), compared with the earlier conversational claim of 3.2%. Its usable fiscal exposure years are {int(pilot_row.year_min)}–{int(pilot_row.year_max)} because next-year receipts must exist.',
        'This independently supports the directional football/receipt relationship. **It does not reproduce the original numerical pilot.** Its 52-school membership, raw data, precise period alignment and complete specification were not supplied. Our coaching field measures total compensation for all football coaches; the original field definition is unavailable. No schools were selected to match its coefficients. FY2014–2019 aligns to football seasons 2013–2018; a season-2014-onward subset and an explicitly incorrect same-printed-label timing diagnostic are retained in `pilot_models.csv` and `pilot_correlations.csv`. The aligned 2019 football season would require FY2020 financial data, outside the historical export.')
    influence_summary=influence.groupby('model').agg(omissions=('omitted_unitid','size'),
        coefficient_min=('coefficient','min'),coefficient_max=('coefficient','max'),largest_raw_p=('p_value','max')).reset_index()
    influence_summary.to_csv(ROOT/'results/feasibility_influence_summary.csv',index=False)
    concise=influence_summary.copy()
    for col in ['coefficient_min','coefficient_max']:concise[col]=concise[col].map(lambda x:f'{x:.4f}')
    concise['largest_raw_p']=concise.largest_raw_p.map(pvalue)
    fragile=support[support.model.eq('heterogeneity_sweet16_next_log_applications')&support.term.eq('sweet16')]
    section('Sensitivity, influence and subgroup limits',
        'The full specification grid includes school/year effects, conference/year effects, prior-budget controls, first differences, school trends, extra-year lags, positive-log versus inverse-hyperbolic-sine financial outcomes, reported-only IPEDS values, merger inclusion, expense-tail trimming, scoring-period restrictions and balanced Cup coverage. None is selected as the headline because of its p-value.',
        ('table',concise),
        ('The omission table reports raw log-scale coefficients: each school is omitted once, with remaining singleton cells removed again. The football ticket and revenue-proxy coefficients remain positive and raw-significant throughout; the Sweet16 annual-change signal also survives each omission. This is an influence diagnostic, not independent replication or a multiplicity-adjusted causal test.' if len(influence) else
         'Influence checks were omitted in this execution; no leave-one-school-out conclusion is available. Rerun without --no-influence to generate those diagnostics.'),
        'Historical Power Five versus other-FBS differences are tested directly using interaction terms on the 2015–2019 sample, excluding independents. The broad FPI/application and revenue-proxy interaction tests do not establish different returns by group. Some Sweet16 subgroup interactions have small raw p-values, but the smaller-program cell below has only one success school/event. Those estimates cannot support a general recommendation for smaller universities.',
        ('table',fragile[['group','n','schools','event_rows','event_schools','switching_schools']]),
        'Historical prominence is based only on 2005–2008 FPI. Expanding-window AR(1) forecasts use past seasons only, but the historical rating vintage was retrieved in 2026; these are not real-time forecast vintages. Their residuals measure statistical outperformance, not known student expectations. A separate opening-unranked-to-final-top20 indicator uses actual AP poll ledgers. Results and interaction intervals are reported in the `outperformance_` and `breakthrough_prominence_` models. Sparse events and exploratory testing limit subgroup conclusions.')
    comparison=choose(models,'published_comparison_winpct_conference_year',term='effect_other_fbs')
    cb,cl,ch=percent([comparison.coefficient,comparison.ci_low,comparison.ci_high])
    section('Comparison with published Flutie Effect research',
        '[Pope and Pope (2009), Southern Economic Journal](https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf) studied roughly 330 Division I schools over 1983–2002. They reported application increases around 2–8% for top-20 football and top-16 basketball success, with larger responses at private schools. Their broader population, earlier period and outcome definitions differ from this public-school financial sample. Their findings motivate the visibility measures; they do not guarantee the same result here.',
        '[McFarland, Groothuis and Guignet (2024), Contemporary Economic Policy](https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642) used 121 FBS institutions, football 2014–2018 and applications 2015–2019. They estimated roughly 2.1% more Group-of-Five applications per 10 percentage points of winning percentage. Their Table 2 marks that total-applications result at the **10% significance level, not 5%**. Their specification reports year effects and institutional/state controls; ours also absorbs school effects and uses different controls/sample.',
        f'Our public-school, conference/year-controlled comparison gives **{cb:.2f}%** for other FBS schools per 10 winning-percentage points (interval {cl:.2f}% to {ch:.2f}%; raw p={pvalue(comparison.p_value)}; N={int(comparison.n)}, {int(comparison.schools)} schools). The group-difference test is also inconclusive. This is a comparison of research questions, not a reproduction or refutation of the published model. Its private-school coverage and faculty-pay, state-income and high-school-graduate controls are not duplicated.')
    simple=break_even[(break_even.extra_annual_athletics_cost.eq(5_000_000))&break_even.net_tuition_contribution.eq(6000)][
        ['extra_generated_receipts','required_whole_students']].copy()
    simple.columns=['Hypothetical extra annual receipts','Extra enrolled student stock to break even']
    simple[simple.columns[0]]=simple.iloc[:,0].map(lambda x:f'${x:,.0f}')
    example=npvs[npvs.planned_extra_first_time_intake_each_year.eq(100)&npvs.retention.eq(.9)&
        npvs.extra_generated_receipts.eq(1_000_000)&npvs.discount_rate.eq(.06)&npvs.capital_outlay.eq(0)].iloc[0]
    npv_text=('-' if example.npv<0 else '')+f'${abs(example.npv)/1e6:.2f}m'
    section('CFO interpretation and cautious financial scenarios',
        'The evidence supports treating football success as relevant to an athletics receipt forecast, conditional on the model. It does not give the CFO an identified spending-to-success conversion, attributable enrollment response, or causal return on a proposed investment. Funding should not be justified by multiplying pooled correlations, adding applicants as tuition-paying students, or counting athletics donations twice.',
        ('table',simple),('figure','feasibility_cfo_break_even'),
        'With a 500-student capacity limit and $6,000 contribution per student, the student channel supplies at most $3m annually. The zero- and $1m-receipt cases in this $5m-cost example therefore cannot break even within that capacity; the unconstrained student requirements exceed 500.',
        f'The separate ten-year cohort scenarios distinguish **planned new first-time intake** from the extra enrolled stock: four study years, explicit retention and a 500-student capacity limit determine how many additional students are actually in attendance. As one purely hypothetical example, 100 planned extra entrants annually, 90% retention, $6,000 net tuition contribution, $1m extra annual athletics receipts and $5m extra annual athletics cash cost yield a ten-year NPV of **{npv_text}** at a 6% rate with no initial capital outlay. This is scenario arithmetic, not an empirical estimate of an athletics-induced enrollment increase.',
        'The tables vary receipts, student intake, retention, discount rates and initial capital outlay. Capacity limits can reduce admitted extra intake. Tuition contribution is after aid/discounts and incremental student-service cost; annual athletics cash cost excludes the separately modeled initial capital expenditure. Constant-dollar flows require a consistent real discount rate. Persistence of demand, displaced students, restrictions on gifts, opportunity costs and program-specific financing would need institution-level review. See `cfo_break_even_scenarios.csv` and `cfo_npv_scenarios.csv`.')
    section('Deliverables, reproduction and actual remaining limits',
        'The Python implementation, public source URLs, hashes, data dictionaries, period/ID rules, model outputs, exclusion counts, six new PNG/SVG figure pairs and this report are available in the project repository. Expanded descriptive statistics, annual nominal financial summaries and aggregate EADA/Knight reconciliation are in `feasibility_descriptive_statistics.csv`, `feasibility_annual_financial_summary.csv` and `source_reconciliation_summary.csv`. Large source changes are flagged for review, without automatic deletion or treating a genuine demand jump as an error. The registered workbook and school-level finances remain local under `data/private/`; no access credentials or registrations are fabricated or committed.',
        'Full local study: `python -m scoreboard.performance --download`, stage the registered workbook as documented, then `python -m scoreboard.feasibility --build`. Independent verification: `python -m scoreboard.validate_feasibility`. Report-only reproduction from saved aggregate results: `python -m scoreboard.feasibility --report-only`. The earlier EADA-only results remain a separate starter analysis, not the preferred financial evidence.',
        '**Remaining research limits:** exact original 52-school replication requires its missing sample/specification; the transfer-netted financial proxy cannot establish gross cash profit; real sponsored-team counts are proxied; private-school generalizability is limited; only observed Cup scorers enter Cup models; some applications precede final postseason information; reporting changes, admissions marketing/platform changes, pricing/capacity and reverse causality remain possible. More observations cannot by themselves solve causal identification.',
        '**Remaining assignment actions:** the group must review the feasibility conclusions, confirm the assignment PDF revision, obtain topic approval, arrange instructor consultation, invite the four other members/instructor to the shared repository, contribute their own substantive commits, and produce/rehearse final slides. This report is a completed feasibility analysis, not a claim that those human collaboration and submission requirements are complete.')
    title='Beyond the Scoreboard — expanded feasibility report'
    md=[f'# {title}','\nAC 547 Track A · Python-only analysis · Historical 2010–2019 source window\n']
    web=[f'<header><p class="eyebrow">AC 547 · TRACK A · PYTHON ANALYTICS</p><h1>{html.escape(title)}</h1><p>Historical 2010–2019 sources · Observational evidence and CFO scenarios</p></header>']
    for heading,elements in sections:
        md.append('## '+heading+'\n');web.append('<section><h2>'+html.escape(heading)+'</h2>')
        for element in elements:
            if isinstance(element,tuple) and element[0]=='table':
                frame=element[1];md.append(md_table(frame)+'\n')
                web.append('<div class="table-wrap">'+frame.to_html(index=False,escape=True,border=0)+'</div>')
            elif isinstance(element,tuple) and element[0]=='figure':
                name=element[1]
                md.append(f'![{name.replace("_"," ")}](results/figures/{name}.png)\n')
                web.append(f'<figure><img src="figures/{name}.png" alt="{html.escape(name.replace("_"," "))}"></figure>')
            else:
                md.append(element+'\n');web.append('<p>'+inline_markup(element)+'</p>')
        web.append('</section>')
    (ROOT/'FEASIBILITY_REPORT.md').write_text('\n'.join(md),encoding='utf-8')
    css='''body{font:16px/1.65 system-ui,sans-serif;color:#15324f;max-width:1200px;margin:0 auto;padding:32px}header{border-bottom:5px solid #008681;padding:20px 0 28px;margin-bottom:40px}.eyebrow{letter-spacing:.12em;font-size:12px;color:#008681;font-weight:700}h1{font-size:36px;line-height:1.2;max-width:900px}h2{font-size:24px;line-height:1.3;margin-top:48px}section{margin-bottom:40px}a{color:#00736f}code{font-size:13px;background:#eef3f5;padding:2px 5px;overflow-wrap:anywhere}table{border-collapse:collapse;font-size:13px;width:100%}th,td{padding:10px 12px;border-bottom:1px solid #d8e1e5;text-align:left}th{background:#15324f;color:white}tr:nth-child(even){background:#f2f6f7}.table-wrap{overflow-x:auto;margin:24px 0}figure{margin:32px 0}img{width:100%;height:auto}strong{font-weight:750}@media print{body{max-width:none;font-size:10pt;padding:0}figure,table{break-inside:avoid}h2{break-after:avoid}}'''
    (ROOT/'results/feasibility_report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Beyond the Scoreboard — Feasibility</title><style>'+css+'</style>'+''.join(web)+'</html>',encoding='utf-8')
    print('Wrote expanded feasibility report, aggregate tables, CFO scenarios, and six new PNG/SVG chart pairs.')


if __name__=='__main__':main()
