"""Prepare named speaker notes and content for the saved presentation.

All numerical charts come from the existing Python-generated assets. This
module creates plain content/configuration, without re-estimating models.
"""
import json
import re

from .download import ROOT
from .hashes import text_sha256

SPEAKERS={1:'Evan West',2:'Luis Ramos',3:'Harrison Delashmit',4:'Robert Philyaw',5:'Morgan Beckler'}
ROLES={1:'Opening and research question',2:'Data and recruitment evidence',
       3:'Core financial findings: tickets and cost recovery',
       4:'Funding-model comparisons and support dollars',5:'Breakthroughs, limitations and CFO implications'}


def plain(text):
    text=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'\1 (\2)',text)
    text=text.replace('**','').replace('`','')
    return text.strip()


def build():
    path=ROOT/'docs/20_minute_outline.md'
    outline=path.read_text(encoding='utf-8')
    headings=list(re.finditer(r'^## Slide (\d+) — (.+)$',outline,re.M))
    if len(headings)!=12:raise ValueError('Expected twelve timed outline sections')
    sections={}
    for i,h in enumerate(headings):
        end=headings[i+1].start() if i+1<len(headings) else outline.index('## Backup slides')
        sections[int(h.group(1))]=plain(outline[h.end():end])
    times=[('0:00–1:15',75,1),('1:15–2:30',75,1),('2:30–4:00',90,1),
        ('4:00–6:00',120,2),('6:00–8:00',120,2),('8:00–10:00',120,3),
        ('10:00–12:00',120,3),('12:00–14:00',120,4),('14:00–16:00',120,4),
        ('16:00–17:30',90,5),('17:30–18:30',60,5),('18:30–20:00',90,5)]
    slides=[
        dict(kind='cover',title='Beyond the Scoreboard'),
        dict(kind='question',title='What would make athletics a worthwhile investment?',
            lead='When spending grows, do the financial benefits keep up?',
            lines=['More athletics revenue','More applications and enrolled students','Less need for institutional support and student fees'],
            footer='Potential benefits require evidence. Educational and campus benefits are outside our dollar estimates.'),
        dict(kind='text',title='We tested each connection separately',
            lines=['Does higher spending predict better performance?',
                   'Does athletic success predict revenue or student demand?',
                   'Does revenue growth keep pace with spending?'],
            footer='These are hypotheses. Initial spending-to-success results remain uncertain after adjustment.'),
        dict(kind='sources',title='We followed public universities over time',lead='2010–2019 historical source window',
            lines=['Money: Knight-Newhouse and EADA','Athletic results: Directors’ Cup, ESPN and tournament outcomes',
                   'Students: NCES IPEDS','Inflation: BLS CPI-U'],
            footer='Export: 240 institutions, 2,400 school-years. Annual recovery model: 2,002 cases, 227 schools. Samples vary.'),
        dict(kind='chart',title='Applications and the Flutie Effect',image='05_applications.png'),
        dict(kind='chart',title='Football strength and ticket receipts',image='06_football_tickets.png'),
        dict(kind='chart',title='Annual and cumulative cost recovery',image='07_cost_recovery.png'),
        dict(kind='chart',title='Cost recovery by support dependence',image='08_support_groups.png'),
        dict(kind='chart',title='Support dollars versus percentages',image='09_support_dollars_share.png'),
        dict(kind='chart',title='Smaller-program breakthroughs',image='10_breakthrough.png'),
        dict(kind='limits',title='Checks strengthen the analysis, with limits',
            checks=['Correct schools and reporting years','Independent recalculation','Remove one university at a time'],
            limits=['Associations do not identify causal returns','Revenue is a qualified accounting measure','Historical public-school sample'],
            footer='32 local tests passed at the analysis build. Current NIL/revenue-sharing outcomes require separate study.'),
        dict(kind='close',title='What should a university CFO take from this?',
            lines=['Compare additional revenue with additional costs.',
                   'Benchmark against comparable funding models.',
                   'Track support dollars alongside percentages.',
                   'Require evidence before budgeting for recruitment gains.'],
            footer='Stronger football performance predicts higher receipts. Cost recovery and the funding burden still matter.')]
    bibliography='''KEY SOURCES
Knight-Newhouse financial methodology: https://knightnewhousedata.org/about-the-data
NCES IPEDS: https://nces.ed.gov/ipeds/
EADA: https://ope.ed.gov/athletics/
NACDA Directors' Cup ledgers and ESPN historical performance endpoints: exact annual URLs and hashes in docs/sources.md and data/provenance.
BLS CPI-U series CUUR0000SA0: https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2010&endyear=2019&annualaverage=true
GAO context: https://www.gao.gov/products/gao-26-108640
Pope and Pope (2009): https://devingpope.com/assets/files/Website_SEJ%20Sports.pdf
McFarland, Groothuis and Guignet (2024): https://onlinelibrary.wiley.com/doi/full/10.1111/coep.12642
Anderson replication archive: https://doi.org/10.7910/DVN/ASXOBS; author manuscript: https://anderson.are.berkeley.edu/pdf/Anderson%202017.pdf
Our new Python STE replication and partial IV comparison: ANDERSON_REPLICATION_REPORT.md. Optional paired literature chart: results/figures/anderson_replication.png (not in the previously saved presentation).
Our results and exact model IDs: FEASIBILITY_REPORT.md, CFO_RETURN_REPORT.md, results/feasibility_models.csv and results/return_models.csv.
Repository: https://github.com/harrydelashmit-dev/beyond-the-scoreboard
'''
    for i,(slide,(period,duration,member)) in enumerate(zip(slides,times),start=1):
        body=re.sub(r'Member [1-5]',SPEAKERS[member],sections[i])
        notes=f'{SPEAKERS[member].upper()}\nSLIDE {i} OF 12 | {period} | {duration} seconds\nROLE: {ROLES[member]}\n\n{body}'
        if i==6:
            notes+='''\nHARRISON: CORE FINANCIAL INTERPRETATION
This is the clearest financial association from the first study. Explain FPI once, then focus on receipts. The outcome is next-year all-athletics ticket receipts, not ticket attendance and not football-only sales. A 10-point change is on the FPI strength scale. Our estimate is 6.41%, with 95% interval 3.99% to 8.89%, based on 817 observations and 109 schools. Related-test correction does not remove the association. Ticket price, capacity and pricing strategy are not fully measured. We cannot infer that a particular coaching hire or budget increase produces this result.
Spend about 30 seconds explaining the measure, 45 seconds walking through the dot and range, and 45 seconds on interpretation and the handoff to costs.
SOURCE ROW: B_fpi_ticket_sales / fpi_10, results/feasibility_models.csv.
'''
        if i==7:
            notes+='''\nHARRISON: THE CENTRAL COST-RECOVERY RESULT
The annual model relates real-dollar revenue changes to real-dollar spending changes, with enrollment growth and conference-year controls. The financial benchmark is 1 dollar, not a zero correlation. The coefficient is 0.6424, with pointwise 95% interval 0.4997 to 0.7852; 2,002 cases and 227 schools. Three-year cumulative annual-flow changes give 0.6809, interval 0.5489 to 0.8128; 1,545 overlapping windows and 225 schools. These windows compare t, t+1 and t+2 with three times the preceding annual budget. They are not returns on one initial cash payment.
Both primary tests remain below one after adjustment across all fourteen extension tests. One-school omission ranges remain below one. Positive-spending-only, balanced-reporting and several time-control variants agree directionally. The school/year LEVEL sensitivity is less conclusive: 0.929, interval 0.821 to 1.037. We disclose it in backup slide 13.
R equals exported total revenues minus institutional/government support and student fees. Transfers already netted from revenue, restricted/in-kind donations and expense definitions limit a cash interpretation. The 36-cent residual is an accounting-gap slope, not an immediate taxpayer bill or a causal loss. Actual allocated support is measured separately. Revenue can fund spending, and omitted strategy affects both.
SOURCE ROWS: R_annual / change_expense_m; R_three_year / cumulative_expense_m; R_levels_year / expense_m, results/return_models.csv.
HANDOFF TO ROBERT: The average also hides differences between universities' funding models.
'''
        notes+='\n\n'+bibliography
        slide.update(number=i,speaker=SPEAKERS[member],member=member,time=period,duration_seconds=duration,hidden=False,notes=notes)
    backups=[
        dict(kind='backup_text',title='Sensitivity: full coverage depends on the comparison',
            lines=['Annual changes: 0.64 [0.50, 0.79]',
                   'Three-year budget flows: 0.68 [0.55, 0.81]',
                   'School/year financial levels: 0.93 [0.82, 1.04]'],
            footer='Revenue per spending dollar; pointwise 95% intervals. The level-model interval includes 1.',
            notes='BACKUP | HARRISON DELASHMIT\nThese specifications estimate different comparisons and use different samples. The school/year level model includes dollar-for-dollar coverage in its interval. Conference-year controls remove shared annual conference changes; school/year controls retain those differences. Annual changes remain below one with either time control. Do not imply that every possible model proves incomplete recovery. Original rows: R_annual (N=2002/G=227), R_three_year (N=1545/G=225), R_levels_year (N=2258/G=228). '+bibliography),
        dict(kind='backup_chart',title='Complete primary recruitment results',
            image='results/figures/feasibility_student_demand.png',
            notes='BACKUP | LUIS RAMOS\nShow all six primary applications/enrollment comparisons. Pointwise 95% intervals are not multiplicity-adjusted confidence intervals. A raw football enrollment interval can exclude zero while its six-test family-adjusted p-value is inconclusive (approximately 0.267). None of the six primary demand tests survives family adjustment. Some Sweet16 annual-change specifications are positive and exploratory. We do not claim that the Flutie Effect has been disproved. Published samples, periods, success definitions and private/public composition differ. '+bibliography),
        dict(kind='backup_text',title='Alternative breakthrough tests also give contrary results',
            lines=['AP-poll breakthroughs give negative smaller-program differences.',
                   'Applications: 11 smaller-program event rows across 10 schools.',
                   'Enrollment: 12 event rows across 11 schools.'],
            footer='Exploratory, sparse-event comparisons. These do not establish that surprise wins cause lower student demand.',
            notes='BACKUP | MORGAN BECKLER\nAP breakthrough means preseason-unranked and final AP top20. Smaller-budget versus larger-budget log-slope differences are -0.143 (raw p about 0.00166) for applications and -0.095 (raw p about 0.00103) for enrollment. These secondary comparisons are unadjusted, observational and based on sparse events. The sample has 651 cases/99 schools for applications and 681/100 for enrollment. School-omission checks retain negative interaction signs. This does not identify a causal decline in demand, and does not support the proposed smaller-program advantage. Models: U_ap_small_budget_fbs_applications and U_ap_small_budget_fbs_enrollment. '+bibliography),
        dict(kind='references',title='Sources and five-member speaking plan',
            lines=['Finance: Knight-Newhouse and EADA','Athletic success: NACDA and ESPN','Student outcomes: NCES IPEDS; inflation: BLS',
                   'Context: GAO 2026; Pope & Pope 2009; McFarland et al. 2024'],
            footer='Full source URLs, model specifications and qualifications appear in speaker notes and the repository reports.',
            notes='BACKUP | ALL MEMBERS\n'+bibliography)]
    for i,s in enumerate(backups,start=13):s.update(number=i,hidden=True,speaker='Backup / see notes',duration_seconds=0)
    result=dict(title='Beyond the Scoreboard',subtitle='Does athletics revenue growth keep up with spending?',
        main_slide_count=12,total_slide_count=16,total_seconds=1200,
        speakers=[dict(member=m,name=n,role=ROLES[m],seconds=240) for m,n in SPEAKERS.items()],
        palette={'navy':'#15324f','teal':'#008681','orange':'#c87826','gray':'#657482'},
        font='Arial',slides=slides+backups,
        outline_sha256=text_sha256(path),
        chart_manifest_sha256=text_sha256(ROOT/'data/provenance/presentation_charts.json'),
        scope='Presentation content only. All chart calculations and source analysis remain Python.')
    if sum(s['duration_seconds'] for s in slides)!=1200:raise ValueError('Timing differs from twenty minutes')
    for m in SPEAKERS:
        if sum(s['duration_seconds'] for s in slides if s['member']==m)!=240:raise ValueError('Speaker time differs from four minutes')
    (ROOT/'config/presentation_deck.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    text=['# Speaker notes: Beyond the Scoreboard','\n12 main slides, 20 minutes; four hidden backup slides.\n']
    for s in result['slides']:
        text.extend([f'## Slide {s["number"]}: {s["title"]}',s['notes'],''])
    (ROOT/'docs/speaker_notes.md').write_text('\n'.join(text).rstrip()+'\n',encoding='utf-8')
    print('Prepared 12 timed slides, 4 hidden backups and named notes for five members.')


if __name__=='__main__':build()
