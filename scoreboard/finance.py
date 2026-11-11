"""Complete the preferred revenue model only when a validated export exists."""
import pandas as pd
from .clean import unique,positive_log,calendar_join
from .download import ROOT
from .models import fixed_effects

def run(panel):
    path=ROOT/'data/private/knight_normalized.csv'
    if not path.exists():
        pending='pending_knight_merge_and_definition_review' if (ROOT/'data/private/knight_source_panel.csv').exists() else 'pending_registered_knight_export'
        status=pd.DataFrame([dict(link='cup_to_generated_revenue',status=pending,n=0,schools=0)])
        status.to_csv(ROOT/'results/finance_model_status.csv',index=False)
        return status.iloc[0].to_dict()
    k=pd.read_csv(path);unique(k,['unitid','year'])
    k['log_generated_revenue']=positive_log(k.generated_revenue)
    k=calendar_join(k,['log_generated_revenue'],1,'next_')
    d=panel.merge(k[['unitid','year','next_log_generated_revenue','total_expenses','generated_revenue','direct_balance']],on=['unitid','year'],how='left',validate='one_to_one')
    d=d[d.public & d.cup_observed].copy()
    rows,residuals=fixed_effects(d,'next_log_generated_revenue',['cup_100'],['lag_log_total_enrollment'])
    pd.DataFrame(rows).to_csv(ROOT/'results/knight_generated_revenue_model.csv',index=False)
    # School-level licensed financial values remain outside the Git repository.
    reconciliation=d[['unitid','year','expenses','total_expenses','generated_revenue','direct_balance']].copy()
    reconciliation['expense_difference']=reconciliation.total_expenses-reconciliation.expenses
    reconciliation.to_csv(ROOT/'data/private/eada_knight_reconciliation.csv',index=False)
    status=dict(link='cup_to_generated_revenue',status='estimated_export_requires_definition_review',n=rows[0]['n'],schools=rows[0]['schools'])
    pd.DataFrame([status]).to_csv(ROOT/'results/finance_model_status.csv',index=False)
    return status
