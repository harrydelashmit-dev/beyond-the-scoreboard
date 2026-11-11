"""Readable presentation charts from saved aggregate results; no new estimation."""
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .download import ROOT
from .hashes import text_sha256

NAVY='#15324f';TEAL='#008681';ORANGE='#c87826';GRAY='#657482'
OUT=ROOT/'results/presentation_charts'
RECORDS=[]


def row(d,model,term):
    z=d[d.model.eq(model)&d.term.eq(term)]
    if len(z)!=1:raise ValueError(f'Ambiguous presentation coefficient: {model}/{term}')
    r=z.iloc[0]
    RECORDS.append(dict(model=model,term=term,coefficient=float(r.coefficient),
        ci_low=float(r.ci_low),ci_high=float(r.ci_high),n=int(r.n),schools=int(r.schools)))
    return r


def canvas(title,subtitle=''):
    fig,ax=plt.subplots(figsize=(12.8,7.2),facecolor='white')
    fig.subplots_adjust(left=.28,right=.95,bottom=.27,top=.70)
    fig.text(.07,.93,title,fontsize=23,weight='bold',color=NAVY,va='top')
    fig.text(.07,.85,subtitle,fontsize=15,color=GRAY,va='top')
    ax.spines[['top','right','left']].set_visible(False)
    ax.spines['bottom'].set_color('#bbc6cd')
    ax.tick_params(axis='both',labelsize=15,length=0,pad=12)
    ax.grid(axis='x',alpha=.15)
    ax.set_axisbelow(True)
    return fig,ax


def save(fig,name,note):
    fig.text(.07,.06,note,fontsize=11.5,color=GRAY,va='bottom')
    fig.savefig(OUT/f'{name}.png',dpi=160,facecolor='white')
    path=OUT/f'{name}.svg'
    fig.savefig(path,metadata={'Date':None},facecolor='white')
    path.write_text('\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
    plt.close(fig)


def point(ax,r,y,*,scale=1.,percent=False,color=TEAL):
    b,lo,hi=np.array([r.coefficient,r.ci_low,r.ci_high])*scale
    if percent:b,lo,hi=100*np.expm1([r.coefficient,r.ci_low,r.ci_high])
    ax.errorbar(b,y,xerr=[[b-lo],[hi-b]],fmt='o',capsize=7,lw=3,
        markersize=10,color=color,markeredgecolor='white',markeredgewidth=1.)
    return b,lo,hi


def main():
    OUT.mkdir(exist_ok=True)
    RECORDS.clear()
    paths=['results/feasibility_models.csv','results/return_models.csv','results/return_matched_endpoints.csv']
    f=pd.read_csv(ROOT/paths[0]);r=pd.read_csv(ROOT/paths[1]);e=pd.read_csv(ROOT/paths[2])
    # Applications are the main admissions visual; full enrollment results are
    # retained in the feasibility report and designated as a backup slide.
    fig,ax=canvas('Applications: no consistent increase in our main tests',
        'Estimated change after athletic success; lines show 95% uncertainty ranges')
    for y,metric,x in [(2,'cup','cup_100'),(1,'fpi','fpi_10'),(0,'sweet16','sweet16')]:
        rr=row(f,'C_'+metric+'_applications',x)
        point(ax,rr,y,percent=True,color=NAVY)
    ax.axvline(0,color=GRAY,lw=1.5);ax.set_ylim(-.5,2.5)
    ax.set_yticks([2,1,0],labels=['Overall athletics\nCup +100 points','Football\nFPI +10 points','Basketball\nSweet Sixteen'])
    ax.set_xlabel('Change in applications (%)',fontsize=16,labelpad=16)
    save(fig,'05_applications','Public universities, 2010–2019 source window; school and conference-year controls.\nDifferent success measures use different units. Football: following fall; Cup/basketball: fall after spring success.\nAll three application intervals span zero; none of the six primary application/enrollment tests passes adjustment.')
    fig,ax=canvas('Stronger football seasons predict higher ticket receipts',
        '10 additional FPI points → approximately 6.4% higher following-year receipts')
    rr=row(f,'B_fpi_ticket_sales','fpi_10');b,lo,hi=point(ax,rr,0,percent=True)
    ax.set_yticks([0],labels=['Following-year\nathletics tickets']);ax.set_ylim(-.8,.8);ax.set_xlim(0,10)
    ax.axvline(0,color=GRAY,lw=1.5);ax.set_xlabel('Change in ticket receipts (%)',fontsize=16,labelpad=16)
    ax.text(b,.30,f'+{b:.1f}%\n95% range: +{lo:.1f}% to +{hi:.1f}%',ha='center',fontsize=18,color=NAVY)
    save(fig,'06_football_tickets','817 school-years across 109 public universities; 2010–2019 financial source window.\nFPI is ESPN’s football strength rating. Receipts cover all athletics; they are not football-only ticket sales.\nSchool/conference-year controls; association survives related-test adjustment; causation is not established.')
    fig,ax=canvas('Revenue growth generally falls short of spending growth',
        'Revenue after institutional/government support and student fees are removed')
    for y,name,term in [(1,'R_annual','change_expense_m'),(0,'R_three_year','cumulative_expense_m')]:
        rr=row(r,name,term);b,lo,hi=point(ax,rr,y,scale=100)
        ax.text(b,y+.22,f'{b:.0f}¢  ({lo:.0f}–{hi:.0f}¢)',ha='center',fontsize=17,color=NAVY)
    ax.axvline(100,color=ORANGE,lw=2);ax.text(99.2,1.45,'100¢ = full coverage',ha='right',color=ORANGE,fontsize=14)
    ax.set_yticks([1,0],labels=['Annual changes','Three-year\nbudget flows']);ax.set_ylim(-.5,1.65);ax.set_xlim(0,110)
    ax.set_xlabel('Additional revenue per additional spending dollar (cents)',fontsize=16,labelpad=16)
    save(fig,'07_cost_recovery','Annual: 2,002 school-years / 227 schools. Three-year: 1,545 overlapping windows / 225 schools.\n2019 CPI-U dollars; lines are 95% pointwise ranges; both primary slopes are below 1 after adjustment.\nConditional budget relationships, not causal ROI. Simpler school/year level sensitivity includes full coverage.')
    fig,ax=canvas('Prior support dependence separates financial recovery',
        'Compare programs by the share of earlier expenses financed through support')
    for y,term,label in [(1,'group0_slope','Lower support\nbelow 50%'),(0,'group1_slope','Higher support\nat least 50%')]:
        rr=row(r,'H_high_support',term);b,lo,hi=point(ax,rr,y,scale=100,color=TEAL if y else NAVY)
        ax.text(b,y+.22,f'{b:.0f}¢  ({lo:.0f}–{hi:.0f}¢)',ha='center',fontsize=17,color=NAVY)
    ax.axvline(100,color=ORANGE,lw=2);ax.set_xlim(0,110);ax.set_ylim(-.5,1.6)
    ax.set_yticks([1,0],labels=['Lower support\nbelow 50%','Higher support\nat least 50%'])
    ax.set_xlabel('Additional revenue per additional spending dollar (cents)',fontsize=16,labelpad=16)
    save(fig,'08_support_groups','Groups fixed using 2010–2012 support/expenses; evaluate 2013–2019. N=1,521; 219 schools.\nSupport includes institutional/government allocations and student fees. Direct slope difference survives adjustment.\nBudget-size and Power Five comparisons are less conclusive. Educational/mission value is outside this measure.')
    z=e[e.period.eq('Full historical period')].set_index('measure')
    fig,axes=plt.subplots(1,2,figsize=(12.8,7.2),facecolor='white')
    fig.subplots_adjust(left=.10,right=.94,bottom=.25,top=.70,wspace=.34)
    fig.text(.07,.93,'A lower support percentage can conceal a larger dollar burden',fontsize=22,weight='bold',color=NAVY,va='top')
    fig.text(.07,.85,'Same 222 public universities, comparing 2010 with 2019',fontsize=16,color=GRAY,va='top')
    values=[z.loc['support_m',['start_sum_m','end_sum_m']].to_numpy(float)/1000,
        100*z.loc['support_m',['start_sum_m','end_sum_m']].to_numpy(float)/z.loc['expense_m',['start_sum_m','end_sum_m']].to_numpy(float)]
    for ax,v,title,unit in zip(axes,values,['Actual support dollars','Support as share of expenses'],['B','%']):
        ax.bar(['2010','2019'],v,color=[NAVY,TEAL],width=.55)
        ax.set_title(title,fontsize=17,color=NAVY,pad=17);ax.set_ylim(0,max(v)*1.25)
        ax.tick_params(labelsize=15);ax.spines[['top','right']].set_visible(False)
        for i,value in enumerate(v):ax.text(i,value+max(v)*.035,f'{value:.2f}{unit}' if unit=='B' else f'{value:.1f}%',ha='center',fontsize=18,color=NAVY)
    axes[0].set_ylabel('Billions of 2019 dollars',fontsize=15);axes[1].set_ylabel('Percent',fontsize=15)
    save(fig,'09_support_dollars_share','Allocated support plus student fees, matched endpoints with all four financial measures reported.\nSupport dollars rose 31.7%; support/expenses fell from 31.2% to 28.0%. Inflation-adjusted descriptive totals.\nThis is an accounting comparison, not an estimated consequence of athletic success.')
    fig,ax=canvas('A larger breakthrough benefit for smaller programs is uncertain',
        'Revenue after a season stronger than a model based on past seasons predicted')
    for y,term,color in [(1,'larger_slope',NAVY),(0,'smaller_slope',TEAL)]:
        rr=row(r,'U_small_revenue',term);b,lo,hi=point(ax,rr,y,percent=True,color=color)
        ax.text(b,y+.22,f'{b:+.1f}%',ha='center',fontsize=17,color=NAVY)
    ax.axvline(0,color=GRAY,lw=1.5);ax.set_ylim(-.5,1.6)
    ax.set_yticks([1,0],labels=['Larger FBS\nathletics budgets','Smaller FBS\nathletics budgets'])
    ax.set_xlabel('Following-year revenue proxy change (%)',fontsize=16,labelpad=16)
    save(fig,'10_breakthrough','Per 10 FPI points above a past-seasons-only model prediction. N=571; 98 schools; evaluation 2013–2019.\nGroups fixed using 2010–2012 athletics budgets. Direct smaller-versus-larger difference remains inconclusive.\nThis is statistical outperformance, not measured fan expectations. Admissions/enrollment advantage is also unconfirmed.')
    manifest=dict(purpose='Presentation simplification of existing aggregate results; no new models or observations',
        sources={path:text_sha256(ROOT/path) for path in paths},
        plotted_coefficients=RECORDS,figures=sorted(p.name for p in OUT.glob('*.png')),
        transformations='Log-outcome coefficients and endpoints: 100*expm1(b); dollar/dollar slopes: 100*b cents; endpoint millions / 1000 = billions',
        uncertainty='Original pointwise 95% school-clustered intervals. Primary decision wording uses the original Holm-adjusted tests.')
    (ROOT/'data/provenance/presentation_charts.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Generated six presentation PNG/SVG pairs from saved aggregate coefficients and matched totals.')


if __name__=='__main__':main()
