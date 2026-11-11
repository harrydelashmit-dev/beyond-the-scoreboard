"""CFO report and scientific figures from aggregate Python estimation outputs."""
import html
import json

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from .download import ROOT
from .feasibility_report import md_table, pvalue, inline_markup, save_figure, NAVY, TEAL, ORANGE, GRAY
from .hashes import text_sha256

SUCCESS={'cup':'Cup +100 points','fpi':'Football FPI +10','sweet16':'Basketball Sweet16'}


def select(m,model,term=None):
    z=m[m.model.eq(model)]
    if term is None:z=z[z.primary]
    else:z=z[z.term.eq(term)]
    if len(z)!=1:raise ValueError(f'Expected one coefficient: {model}/{term}')
    return z.iloc[0]


def interval(r,scale=1.,percent=False):
    a=np.array([r.coefficient,r.ci_low,r.ci_high])*scale
    if percent:a=np.expm1(a)*100
    return f'{a[0]:+.2f}',f'[{a[1]:+.2f}, {a[2]:+.2f}]'


def cost_table(m):
    names=[('R_annual','Annual changes (primary)'),('R_three_year','Three-year cumulative (primary)'),
        ('R_levels_year','School/year levels'),('R_levels_conference_year','School/conference-year levels'),
        ('R_changes_school_effects','Changes with school effects'),('R_changes_year','Changes, year effects'),
        ('R_three_year_discounted','Three-year flows, 3% real discount'),
        ('R_three_year_school_effects','Three-year flows with school effects'),
        ('R_positive_increases_only','Only positive spending changes'),('R_trim_1_99','Exclude 1%/99% change tails'),
        ('R_exclude_2015_2017','Exclude 2015–2017'),('R_balanced','Ten-year financial reporters'),('R_nominal','Nominal-dollar sensitivity')]
    rows=[]
    for name,label in names:
        term='cumulative_expense_m' if 'three_year' in name else ('expense_m' if 'levels_' in name else ('nominal_expense_change' if name=='R_nominal' else 'change_expense_m'))
        r=select(m,name,term)
        against_one=2*stats.t.sf(abs((r.coefficient-1)/r.std_error),r.schools-1)
        rows.append({'Specification':label,'Revenue / spending dollar':f'{r.coefficient:.3f}',
            '95% interval':f'[{r.ci_low:.3f}, {r.ci_high:.3f}]','Raw p: slope = 1':pvalue(against_one),
            'N / schools':f'{r.n:,} / {r.schools}'})
    return pd.DataFrame(rows)


def group_table(m):
    rows=[]
    for group,label,zero,one in [('small_budget_all','Baseline athletics budget','Larger','Smaller'),
        ('high_support','Baseline support / expenses','Below 50%','At least 50%'),
        ('power_2014','2014 FBS membership','Other FBS','Power Five')]:
        r=select(m,'H_'+group);a=select(m,'H_'+group,'group0_slope');b=select(m,'H_'+group,'group1_slope')
        rows.append({'Comparison':label,zero:f'{a.coefficient:.3f} [{a.ci_low:.3f}, {a.ci_high:.3f}]',
            one:f'{b.coefficient:.3f} [{b.ci_low:.3f}, {b.ci_high:.3f}]',
            'Difference (second − first)':f'{r.coefficient:+.3f}',
            'Raw difference p':pvalue(r.test_p),'Holm difference p':pvalue(r.holm_family_p),
            'N / schools':f'{r.n:,} / {r.schools}'})
    # Common headings make the three distinct comparisons explicit.
    return pd.DataFrame([{'Comparison':r['Comparison'],
        'Reference group: slope [95% CI]':next(f'{k}: {v}' for k,v in r.items() if k in ['Larger','Below 50%','Other FBS']),
        'Comparison group: slope [95% CI]':next(f'{k}: {v}' for k,v in r.items() if k in ['Smaller','At least 50%','Power Five']),
        **{k:v for k,v in r.items() if k in ['Difference (second − first)','Raw difference p','Holm difference p','N / schools']}}
        for r in rows])


def support_table(m):
    rows=[]
    for metric in SUCCESS:
        for outcome,label in [('support_m','Support, millions of 2019 dollars'),('support_pct_expense','Support / expenses, percentage points')]:
            r=select(m,f'S_{metric}_{outcome}');b,ci=interval(r)
            rows.append({'Success measure':SUCCESS[metric],'Next-year outcome':label,
                'Association':b,'95% interval':ci,'Raw p':pvalue(r.test_p),
                'Holm p':pvalue(r.holm_family_p),'N / schools':f'{r.n:,} / {r.schools}'})
    return pd.DataFrame(rows)


def surprise_table(m):
    rows=[]
    for label in ['revenue','applications','enrollment']:
        name='U_small_'+label;r=select(m,name)
        a=select(m,name,'larger_slope');b=select(m,name,'smaller_slope')
        aa,aci=interval(a,percent=True);bb,bci=interval(b,percent=True)
        rows.append({'Outcome':'Next-year revenue proxy' if label=='revenue' else 'Following-fall '+label,
            'Larger-budget FBS: % [95% CI]':aa+'% '+aci,
            'Smaller-budget FBS: % [95% CI]':bb+'% '+bci,
            'Difference in log slopes':f'{r.coefficient:+.4f}',
            'Raw difference p':pvalue(r.test_p),'Holm difference p':pvalue(r.holm_family_p),
            'N / schools':f'{r.n:,} / {r.schools}'})
    return pd.DataFrame(rows)


def charts(m,endpoints):
    # Show the important contrary level specification, not just favorable fits.
    pairs=[('R_annual','change_expense_m','Annual changes: primary'),
        ('R_three_year','cumulative_expense_m','Three-year flows: primary'),
        ('R_changes_year','change_expense_m','Annual changes: year effects'),
        ('R_changes_school_effects','change_expense_m','Annual changes: school effects'),
        ('R_levels_conference_year','expense_m','Levels: conference-year effects'),
        ('R_levels_year','expense_m','Levels: year effects'),
        ('R_trim_1_99','change_expense_m','Trim 1%/99% change tails')]
    fig,ax=plt.subplots(figsize=(11,6.3));fig.subplots_adjust(left=.34,bottom=.24,top=.82)
    for pos,(name,term,label) in enumerate(pairs):
        r=select(m,name,term);y=len(pairs)-1-pos
        ax.errorbar(r.coefficient,y,xerr=[[r.coefficient-r.ci_low],[r.ci_high-r.coefficient]],
            fmt='o',capsize=4,color=TEAL if pos<2 else NAVY,markerfacecolor=TEAL if pos<2 else 'white')
    ax.set_yticks(range(len(pairs)),labels=[p[2] for p in pairs][::-1]);ax.axvline(1,color=ORANGE,lw=2,label='Dollar-for-dollar coverage')
    ax.set_xlabel('Additional revenue proxy per additional spending dollar');ax.grid(axis='x',alpha=.15)
    ax.legend(loc='lower right',fontsize=9)
    fig.suptitle('Revenue growth generally falls short of spending growth',fontsize=15,fontweight='bold')
    save_figure(fig,'returns_cost_recovery','Knight-Newhouse public DI, 2010–2019; 2019 CPI-U dollars; school-clustered 95% pointwise intervals.\nSchool/year level specification includes dollar-for-dollar coverage in its interval. All specifications are observational budget relationships.')
    fig,ax=plt.subplots(figsize=(11,6.3));fig.subplots_adjust(left=.33,bottom=.25,top=.83)
    labels=[]
    for i,(group,names) in enumerate([('high_support',['Support <50%','Support ≥50%']),
        ('small_budget_all',['Larger DI budget','Smaller DI budget']),('power_2014',['Other FBS','2014 Power Five'])]):
        for j in [0,1]:
            r=select(m,'H_'+group,'group'+str(j)+'_slope');y=5-(2*i+j)
            ax.errorbar(r.coefficient,y,xerr=[[r.coefficient-r.ci_low],[r.ci_high-r.coefficient]],fmt='o',capsize=4,
                color=TEAL if j==0 else NAVY)
            labels.append(names[j])
    ax.set_yticks(range(6),labels=labels[::-1]);ax.axvline(1,color=ORANGE,lw=2)
    ax.set_xlabel('Additional revenue proxy per additional spending dollar');ax.grid(axis='x',alpha=.15)
    fig.suptitle('Prior support dependence separates cost-recovery slopes',fontsize=15,fontweight='bold')
    save_figure(fig,'returns_school_types','Groups frozen before evaluation: budgets/support in 2010–2012; Power Five membership in 2014.\nOnly the high-support slope difference passes Holm correction across the three primary group comparisons. Intervals are pointwise; groups overlap.')
    fig,axes=plt.subplots(1,2,figsize=(12,5.3),sharey=True);fig.subplots_adjust(left=.18,bottom=.28,wspace=.35,top=.80)
    for ax,outcome,title in zip(axes,['support_m','support_pct_expense'],['Support dollars (millions, 2019)','Support / expenses (percentage points)']):
        for i,metric in enumerate(SUCCESS):
            r=select(m,f'S_{metric}_{outcome}')
            ax.errorbar(r.coefficient,2-i,xerr=[[r.coefficient-r.ci_low],[r.ci_high-r.coefficient]],fmt='o',capsize=4,color=NAVY,markerfacecolor='white')
        ax.axvline(0,color=GRAY);ax.set_title(title,fontsize=11);ax.grid(axis='x',alpha=.15)
    axes[0].set_yticks([2,1,0],labels=list(SUCCESS.values()))
    fig.suptitle('Success does not reliably predict lower allocated support',fontsize=15,fontweight='bold')
    save_figure(fig,'returns_self_support','School and conference-year effects; school-clustered 95% pointwise intervals; following fiscal-year outcomes.\nNone of these six primary tests passes family-adjusted 5% significance. Support includes government/institutional allocations and student fees.')
    fig,axes=plt.subplots(1,3,figsize=(13,5.2),sharey=True);fig.subplots_adjust(left=.18,bottom=.30,wspace=.35,top=.79)
    for ax,outcome,title in zip(axes,['revenue','applications','enrollment'],['Next-year revenue proxy','Following-fall applications','Following-fall enrollment']):
        for j,(term,label) in enumerate([('larger_slope','Larger FBS budget'),('smaller_slope','Smaller FBS budget')]):
            r=select(m,'U_small_'+outcome,term)
            b,lo,hi=100*np.expm1([r.coefficient,r.ci_low,r.ci_high])
            ax.errorbar(b,1-j,xerr=[[b-lo],[hi-b]],fmt='o',capsize=4,color=TEAL if j else NAVY,markerfacecolor='white')
        ax.axvline(0,color=GRAY);ax.set_title(title,fontsize=10);ax.set_xlabel('Association (%)');ax.grid(axis='x',alpha=.15)
    axes[0].set_yticks([1,0],labels=['Larger FBS budget','Smaller FBS budget'])
    fig.suptitle('Smaller-program breakthrough advantage remains unconfirmed',fontsize=15,fontweight='bold')
    save_figure(fig,'returns_breakthrough','Per 10 points above a past-seasons-only AR(1) FPI forecast; 2013–2019 evaluation; pointwise 95% intervals.\nNo direct smaller-versus-larger primary interaction passes Holm correction. Statistical outperformance is not a measured surprise to fans or applicants.')
    z=endpoints[endpoints.period.eq('Full historical period')].set_index('measure')
    start=z.start_sum_m;end=z.end_sum_m
    support_percent=[100*start.support_m/start.expense_m,100*end.support_m/end.expense_m]
    fig,axes=plt.subplots(1,2,figsize=(11,5.4));fig.subplots_adjust(bottom=.27,wspace=.35,top=.80)
    axes[0].bar(['2010','2019'],[start.support_m/1000,end.support_m/1000],color=[NAVY,TEAL])
    axes[0].set_ylabel('Allocated support, billions of 2019 dollars')
    for i,v in enumerate([start.support_m/1000,end.support_m/1000]):axes[0].text(i,v+.05,f'{v:.2f}',ha='center')
    axes[0].set_ylim(0,max(start.support_m,end.support_m)/1000*1.2)
    axes[1].bar(['2010','2019'],support_percent,color=[NAVY,TEAL]);axes[1].set_ylabel('Support as percentage of athletics expenses')
    for i,v in enumerate(support_percent):axes[1].text(i,v+.6,f'{v:.1f}%',ha='center')
    axes[1].set_ylim(0,max(support_percent)*1.2)
    fig.suptitle('A smaller support share can conceal a larger dollar burden',fontsize=15,fontweight='bold')
    save_figure(fig,'returns_support_dollars_share',f'Matched 2010/2019 endpoints for {int(z.schools.iloc[0])} public DI programs; source-reported support plus student fees.\nDescriptive aggregates, not a causal effect of success. Calendar-year CPI-U approximates the fiscal-year price level.')


def main():
    m=pd.read_csv(ROOT/'results/return_models.csv');status=pd.read_csv(ROOT/'results/return_model_status.csv')
    end=pd.read_csv(ROOT/'results/return_matched_endpoints.csv')
    observed=pd.read_csv(ROOT/'results/return_observed_coverage.csv')
    rules=json.loads((ROOT/'data/provenance/return_period_rules.json').read_text(encoding='utf-8'))
    execution=json.loads((ROOT/'data/provenance/return_execution.json').read_text(encoding='utf-8'))
    if execution['hashes']['results/return_models.csv']!=text_sha256(ROOT/'results/return_models.csv'):
        raise ValueError('Saved model coefficients do not match the execution manifest')
    validation_path=ROOT/'data/provenance/return_validation.json'
    validated=False
    if validation_path.exists():
        v=json.loads(validation_path.read_text(encoding='utf-8'))
        validated=v.get('status')=='passed' and v.get('models_sha256')==text_sha256(ROOT/'results/return_models.csv')
    charts(m,end)
    cost=cost_table(m);groups=group_table(m);support=support_table(m);surprise=surprise_table(m)
    for name,frame in [('cost_recovery',cost),('school_types',groups),('self_support',support),('breakthrough',surprise)]:
        frame.to_csv(ROOT/f'results/return_summary_{name}.csv',index=False)
    primary=m[m.primary].copy()
    primary['null_interpretation']=np.where(primary.family.eq('cost_recovery'),'Slope = 1 dollar','Interaction/effect = 0')
    tests=primary[['model','family','coefficient','ci_low','ci_high','primary_null','test_p','holm_family_p','holm_all_primary_p','n','schools']]
    annual=select(m,'R_annual');three=select(m,'R_three_year');high=select(m,'H_high_support')
    z=end[end.period.eq('Full historical period')].set_index('measure')
    dollars_growth=(z.loc['support_m','end_sum_m']/z.loc['support_m','start_sum_m']-1)*100
    share_start=100*z.loc['support_m','start_sum_m']/z.loc['expense_m','start_sum_m']
    share_end=100*z.loc['support_m','end_sum_m']/z.loc['expense_m','end_sum_m']
    all_observed=observed[observed.group.eq('All eligible DI')].iloc[0]
    inf=pd.read_csv(ROOT/'results/return_influence_summary.csv')
    joint_support=select(m,'H_joint_budget_support','spend_x_high_support')
    joint_budget=select(m,'H_joint_budget_support','spend_x_small_budget_all')
    ap_apps=select(m,'U_ap_small_budget_fbs_applications','ap_breakthrough_x_small_budget_fbs')
    ap_enroll=select(m,'U_ap_small_budget_fbs_enrollment','ap_breakthrough_x_small_budget_fbs')
    sections=[]
    def section(name,*elements):sections.append((name,elements))
    section('Presentation decision',
        '**These four directions provide a worthwhile presentation.** The clearest new finding is a positive but incomplete financial recovery relationship, with materially weaker recovery among programs previously dependent on institutional/government support and student fees. The smaller-program surprise advantage remains uncertain. A stronger project question is: **When does athletics revenue growth keep up with spending, and who carries the remaining financial burden?**',
        f'Annual real-dollar changes imply **{annual.coefficient:.2f} dollars of additional revenue proxy per additional spending dollar** (95% interval {annual.ci_low:.2f}–{annual.ci_high:.2f}; N={annual.n:,}, {annual.schools} schools). The three-year cumulative budget-flow slope is **{three.coefficient:.2f}** ({three.ci_low:.2f}–{three.ci_high:.2f}; N={three.n:,}, {three.schools} schools). Both slopes are below one after adjustment across all fourteen primary extension tests.',
        'These are conditional associations between reported budgets. They do not estimate what would happen if a CFO randomly increased spending. Revenue can fund spending, reporting rules can link the measures, and omitted pricing, facilities and institutional strategy can affect both. No causal ROI, profit-maximizing budget, or guaranteed future payoff is identified.',
        '**Scope:** the original feasibility report remains intact. This extension tests cost recovery, school differences, support dependence and statistical football outperformance using the same audited source window. Every planned primary comparison and all sensitivity statuses are retained; favorable and unfavorable results appear together.')
    section('Data, definitions and the recorded plan',
        'The registered Knight-Newhouse export has 2,400 listed school-years for 240 institutions in 2010–2019. The prior public-DI eligibility and institutional-merger exclusions are retained. All original values remain unchanged; no missing financial observation, Cup score or institutional outcome is invented. Raw finances, joined panels, exact model cases and finance-based school classifications remain in ignored `data/private/`.',
        '**R = exported total revenues − institutional/government support − student fees. E = exported total expenses. S = institutional/government support + student fees.** R is a net nonallocated-revenue proxy: total revenues already net transfers to the institution, and expenses may include excess transfers. Gifts can be restricted/in-kind. E−R is an accounting gap proxy; S is observed allocated support. They differ by E−total revenues. Neither is a verified cash deficit or audited economic profit.',
        'All new dollar comparisons use published BLS CPI-U annual averages (series CUUR0000SA0), independently checked against all twelve months per year, in 2019 dollars. Calendar-year CPI approximates fiscal-year prices and does not measure athletics-specific cost inflation. Zero support and decreases are retained.',
        f'`config/return_plan.json` was committed at **a45a7a6** before extension estimation; the earlier feasibility results were already known. There are **14 primary null tests** in families of 2 cost-recovery, 3 school-type, 6 self-support and 3 smaller-program-outperformance comparisons. This is exploratory project development, not an independent externally preregistered replication. After the first estimates, joint budget/support interactions, shared-case dollar outperformance bridges and influence checks of negative AP results were added as disclosed secondary follow-ups.',
        f'Baseline groups require three observed years, 2010–2012. The all-DI budget median is **{rules["all_DI_budget_median_2019_dollars"]/1e6:.2f} million** and the FBS-specific median is **{rules["FBS_budget_median_2019_dollars"]/1e6:.2f} million**, in 2019 dollars. Group outcomes begin in 2013. Support dependence is fixed at baseline S/E ≥50%; Power Five membership is frozen in 2014 for evaluation in 2015–2019, excluding independents. Smaller athletics budgets and smaller enrollment are separate definitions.',
        f'All **{len(status)} specifications** ran; **{status.status.eq("estimated").sum()} estimated**, {status.status.ne("estimated").sum()} not estimable. Status, exclusions, controls, fixed effects, school counts, exact years, pointwise 95% intervals, raw and adjusted p-values are in `results/return_*.csv`. Numerical/source validation: **{"passed" if validated else "not yet verified for these coefficients"}**. Four annual flows must be observed for the three-year comparisons; late anchors are lost to future outcomes. No post-2019 outcome is supplied.')
    section('1. Does additional revenue cover additional spending?',
        'Primary annual model: ΔR_t = βΔE_t + enrollment-growth control + conference-by-year indicators + error. Differences use exact prior calendar years and include spending decreases. The test is **H0: β=1**, not H0: β=0. Errors cluster by school with cluster-count-minus-one t inference. Time cells with one case are excluded.',
        'Primary three-year model: [R_t+R_(t+1)+R_(t+2)−3R_(t−1)] is regressed on the identical expression for E, with the end-to-pre enrollment log change and conference-by-year indicators. Every component is observed for an eligible program; incomplete windows remain missing. Windows overlap, so school clustering is essential. This compares accumulated budget flows relative to the preceding annual budget; it is not a return on a one-time investment. A fixed 3% real discount sensitivity discounts both revenue and expense flows.',
        ('table',cost),('figure','returns_cost_recovery'),
        f'The primary annual coefficient corresponds to **{100*annual.coefficient:.1f} cents of additional R and {100*(1-annual.coefficient):.1f} cents of additional E−R gap per extra spending dollar**. The latter is an exact same-case coefficient identity. It does not imply the university immediately funds that entire gap: the same-case observed support slope is {select(m,"R_bridge_change_support_m","change_expense_m").coefficient:.3f}; changes in reported total balance account for the remainder.',
        '**Material sensitivity:** the simpler school/year level model has a confidence interval that includes one. Conference-year effects remove common changes such as conference media distributions, while school/year effects retain those differences. Annual-change models remain below one with either time control. The primary recovery result is therefore robust across the stated change specifications, while a universal claim across every possible financial model would be too strong. Shared revenue/expense funding decisions and measurement error can bias the slopes.',
        f'Descriptively, **{all_observed.fraction_increases_covered*100:.1f}% of {int(all_observed.expense_increase_rows):,} observed spending-increase years** had revenue growth at least as large as expense growth in the annual-model cases. The ratio of total associated revenue growth to total positive expense growth is {all_observed.observed_recovery_ratio:.3f}, with a school-bootstrap interval [{all_observed.bootstrap_ratio_low:.3f}, {all_observed.bootstrap_ratio_high:.3f}]. This selected positive-increase descriptive comparison is different from the all-change adjusted regression. It is not a probability that a new investment will pay off. Group coverage ratios, decreases and sample counts are fully reported in `return_observed_coverage.csv`.',
        'The distributed-lag check includes current and previous spending changes together; its coefficients are reported in the full CSV. The previous change adds no detectable independent association in this window. It cannot resolve the longer-run return to facilities or recruit development.')
    section('2. Which types of schools appear to benefit most?',
        'The table reports direct group interactions in annual-change models. Fixed baseline group indicators also allow different average growth. A higher slope means revenue growth more closely accompanies spending growth; it does not establish that the group has a positive net return or a larger causal payoff.',
        ('table',groups),('figure','returns_school_types'),
        f'**The clearest separator is prior support dependence.** The high-support slope is {select(m,"H_high_support","group1_slope").coefficient:.3f}, versus {select(m,"H_high_support","group0_slope").coefficient:.3f} for less-dependent programs. The direct difference is {high.coefficient:+.3f} (95% interval [{high.ci_low:+.3f}, {high.ci_high:+.3f}]; raw p={pvalue(high.test_p)}, family-Holm p={pvalue(high.holm_family_p)}, all-14-Holm p={pvalue(high.holm_all_primary_p)}). This is consistent with weaker commercial cost recovery in programs that historically relied more on allocations.',
        f'Smaller-budget programs also have a lower point estimate, but their direct difference does not clear family adjustment. The Power Five comparison points toward stronger recovery in Power Five schools, but the confidence interval for the direct difference includes zero. Neither is presented as a confirmed group advantage. Groups overlap and are not randomly assigned. In the secondary joint budget/support model, the high-support difference remains negative ({joint_support.coefficient:+.3f}, raw p={pvalue(joint_support.p_value)}), while the budget interaction is uncertain ({joint_budget.coefficient:+.3f}, p={pvalue(joint_budget.p_value)}). These secondary results suggest support dependence is more informative than budget size alone in this panel; every coefficient is retained.',
        'These comparisons can help a CFO choose a relevant reference group. They do not justify a school league table or extrapolation to private universities, which have different reporting coverage and can have different admissions responses. Participation, education, campus culture and other mission benefits are outside this financial measurement; incomplete commercial recovery does not establish that those benefits have no value.')
    section('6. Does success make athletics more self-supporting?',
        'Success at ending-year t predicts actual allocated support S in fiscal t+1 and S/E as a percentage. Models absorb school and contemporaneous conference-by-year effects and control prior log enrollment. Football FPI belongs to season t−1; Cup and Sweet16 belong to the season ending t. Six primary exposure tests receive one family adjustment.',
        ('table',support),('figure','returns_self_support'),
        '**None of the six tests survives the family-adjusted 5% threshold.** Football has a negative support-share point estimate with an unadjusted p-value below .05, but that evidence does not survive correction and actual support dollars remain uncertain. Tickets rising after football success, as in the earlier study, therefore does not establish that the institution reduces its contribution. Expenses, support and gap responses on identical cases, student-fee dollars per enrolled student and year-effect variants appear in the full output.',
        f'**An additional useful accounting finding:** among {int(z.schools.iloc[0])} programs with complete matched endpoints, real allocated support rose **{dollars_growth:.1f}%** from 2010 to 2019, even as support fell from **{share_start:.1f}% to {share_end:.1f}% of expenses**. A program can appear less dependent as a percentage while the dollar burden still grows. This is descriptive evidence about the panel, not an estimated consequence of winning.',
        ('figure','returns_support_dollars_share'),
        'The sum of E−R increased over these matched endpoints. A gap increase and an allocated-support increase should be reconciled, not equated: the reported total-revenue/expense balance also changed. `return_matched_endpoints.csv` contains the full four-measure bridge.')
    section('3. Does unexpected success benefit smaller programs more?',
        'The main measure is FPI per ten points above an expanding AR(1) forecast trained only on previous seasons. Smaller-budget FBS programs are defined before evaluation using their 2010–2012 budgets. Models absorb school and conference-year effects and control prior FPI and prior enrollment. This controls earlier strength but cannot turn statistical outperformance into an exogenous surprise. Historical FPI was downloaded at the present vintage; revisions may mean it differs from information known at the time. Inference is conditional on the estimated forecast rule.',
        ('table',surprise),('figure','returns_breakthrough'),
        '**The hypothesized smaller-program advantage is not established.** Smaller-budget schools have a positive within-group revenue association, but the direct smaller-versus-larger revenue difference does not clear the raw 5% threshold or family adjustment. A significant subgroup slope alongside an insignificant other subgroup slope would not prove a difference. Applications and enrollment interactions are also inconclusive. Percentage changes do not imply equal dollar gains across different revenue bases.',
        f'Secondary comparisons use smaller enrollment, lower 2005–2008 historical FPI prominence, non-Power FBS membership, and preseason-unranked-to-final-AP-top20 breakthroughs. All outcomes and group differences are retained. The AP budget interaction for applications and enrollment is **negative**, rather than the proposed smaller-program advantage: log-slope differences {ap_apps.coefficient:+.3f} (raw p={pvalue(ap_apps.p_value)}) and {ap_enroll.coefficient:+.3f} (p={pvalue(ap_enroll.p_value)}). The smaller-program samples have 11 application-event rows across 10 schools and 12 enrollment-event rows across 11 schools. Events remain sparse and this is an exploratory, unadjusted family. These results are reported without implying that surprise wins cause lower demand.',
        'A shared-case secondary bridge estimates following-year expense, revenue, gap and support dollar responses to outperformance for each budget group. These clarify why a positive percentage revenue response alone cannot establish that an unexpected strong season finances its associated costs.')
    section('Robustness, inference and numerical validation',
        ('table',inf),
        ('The influence table omits one program at a time; null p refers to slope=1 for recovery and interaction=0 otherwise. Omission identities and individual source amounts are not published. Cost-recovery estimates remain below one throughout these omissions; AP interactions remain negative. This is a robustness check, not independent replication. The AP/high-support influence rows are secondary diagnostics added after viewing the first extension estimates.' if len(inf) else 'Influence fits were omitted in this execution. No prior omission results are silently retained or asserted for these coefficients.'),
        'Independent full-rank dummy-variable OLS checks cover annual recovery, cumulative recovery, high-support interaction, FPI/support and the smaller-budget outperformance/revenue model. Source-cell preservation, exact-year CPI and accounting identities are checked separately. The actual validation record is `data/provenance/return_validation.json`; stale coefficient hashes do not count as passed.',
        'Fourteen primary tests use Holm adjustments within their recorded families and across all fourteen; all pointwise intervals and raw p-values remain visible. The secondary specifications are exploratory and unadjusted, including AP negative interactions. The complete primary table follows; cost-recovery test p-values refer to β=1. Primary results from the earlier feasibility study are a separate previously examined family, not pooled into these extension corrections.',
        ('table',tests))
    section('What to present and what more data would improve',
        'A defensible presentation has four findings: (1) stronger football performance predicts later ticket receipts in the earlier analysis; (2) in this extension, spending and revenue move together but primary adjusted cost-recovery slopes are below one; (3) historically support-dependent programs have weaker recovery; (4) success does not reliably predict lower actual support or a larger smaller-program admissions benefit. The matched-endpoint dollars-versus-share example makes the accounting implication concrete. A worthwhile research result does not require every step of the proposed pathway to be significant.',
        'The existing four directions have enough value to present; there is no need to search the other four ideas merely to obtain a small p-value. The extra descriptive risk check finds different revenue-growth volatility across baseline-support groups, but that is a cross-program descriptive comparison and is not claimed as an insurance effect. Full risk counts are in `return_revenue_volatility.csv`.',
        '**Best next acquisition:** additional Knight report fields for media/conference distributions, transfers, capital/debt and operating categories would help separate conference windfalls, transfers and expense composition. Earlier consistent pre-NIL years would improve baseline history, long lags and precision, provided corresponding public outcomes can be aligned. More years by themselves do not solve endogeneity. 2020–2021 COVID years and later NIL/revenue-sharing years belong in explicitly separate regime analyses; pooling them to increase N could obscure structural changes. No additional Knight login is required for the completed historical pass.',
        'A university-specific causal investment case would additionally need project-level operating/capital cash flows, ticket price/capacity, gift restrictions, actual net tuition contribution, capacity and displacement, and an identification strategy. The current source supports an accounting risk/feasibility study. Student demand remains a possible benefit rather than a budget offset presumed to occur.',
        'Reproduction: `python run_project.py --returns --download --test` uses the existing audited private feasibility panel and retrieves/validates CPI. `python -m scoreboard.validate_returns` reruns independent checks. `python run_project.py --returns --report-only` rebuilds this report and its five chart pairs from aggregate outputs without registered financial data. All analytic logic, models, tests and charts are Python. Human group commits, consultation and the final presentation remain assignment requirements.')
    section('Primary sources and definitions',
        '[Knight-Newhouse methodology](https://knightnewhousedata.org/about-the-data) defines financial years, transfers, allocations and reporting limitations. The registered workbook/report provenance remains in the original acquisition documents. [BLS public API](https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true) supplies the actual CPI values, with the [official historical CPI-U table](https://www.bls.gov/cpi/tables/supplemental-files/historical-cpi-u-202310.pdf) documenting the series. ESPN/NACDA/IPEDS URLs, source vintage and matching rules are retained in `docs/sources.md` and the feasibility manifests.',
        'For external context, [GAO’s 2026 athletics-finance study](https://www.gao.gov/products/gao-26-108640) independently reports widespread gaps between generated revenue and expenses in NCAA data, including a 2014–2015 comparison. It uses a different sample, definitions and period; it does not validate our coefficients or supply missing observations. The earlier feasibility report compares the project with published Flutie Effect studies.')
    section('Published research: winning benefits versus spending returns',
        'A separate public-data [Anderson replication](ANDERSON_REPLICATION_REPORT.md) reproduces all ten estimates, standard errors and sample sizes from the study’s STE model in Python. Athletic alumni gifts increase with additional football wins in that historical model, while the applications estimate remains uncertain. The IV matching translation remains partial, with numerical differences disclosed. This does not overturn the later-period accounting findings or establish a causal spending return.',
        'The presentation should say that published evidence supports some benefits from winning, while dependable recruitment payoffs and full cost recovery remain unestablished in our analysis. The zero-sum nature of wins on a fixed schedule is an economic interpretation, not an estimated explanation of our recovery slope. All athletics benefits need not be zero-sum. Do not add coefficients across different studies, periods or revenue definitions.')
    title='Beyond the Scoreboard — cost recovery and who benefits'
    md=['# '+title,'\nAC 547 Track A · Python-only · Historical 2010–2019 extension\n']
    web=[f'<header><p>AC 547 · PYTHON ANALYTICS</p><h1>{html.escape(title)}</h1><p>Four selected research directions · Accounting evidence and limits</p></header>']
    for heading,elements in sections:
        md.append('## '+heading+'\n');web.append('<section><h2>'+html.escape(heading)+'</h2>')
        for element in elements:
            if isinstance(element,tuple):
                kind,value=element
                if kind=='table':
                    md.append(md_table(value)+'\n');web.append('<div class="table-wrap">'+value.to_html(index=False,border=0,escape=True)+'</div>')
                else:
                    md.append(f'![{value.replace("_"," ")}](results/figures/{value}.png)\n')
                    web.append(f'<figure><img src="figures/{value}.png" alt="{html.escape(value.replace("_"," "))}"></figure>')
            else:
                md.append(element+'\n');web.append('<p>'+inline_markup(element).replace('href="ANDERSON_REPLICATION_REPORT.md"','href="anderson_report.html"')+'</p>')
        web.append('</section>')
    (ROOT/'CFO_RETURN_REPORT.md').write_text('\n'.join(md),encoding='utf-8')
    css='body{font:16px/1.6 system-ui,sans-serif;color:#15324f;max-width:1200px;margin:auto;padding:32px}h1{font-size:36px;line-height:1.2}h2{margin-top:48px}header{border-bottom:5px solid #008681;padding-bottom:24px}table{border-collapse:collapse;font-size:13px;width:100%}td,th{padding:9px;border-bottom:1px solid #d8e1e5;text-align:left}th{background:#15324f;color:white}tr:nth-child(even){background:#f2f6f7}.table-wrap{overflow:auto;margin:24px 0}img{width:100%;height:auto}figure{margin:30px 0}code{font-size:13px;background:#eef3f5;overflow-wrap:anywhere}a{color:#00736f}@media print{body{font-size:10pt;padding:0}figure,table{break-inside:avoid}}'
    (ROOT/'results/return_report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CFO cost recovery</title><style>'+css+'</style>'+''.join(web)+'</html>',encoding='utf-8')
    print('Wrote CFO return report, four summary tables and five PNG/SVG figure pairs.')


if __name__=='__main__':main()
