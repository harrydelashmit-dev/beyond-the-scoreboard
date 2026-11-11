"""Transparent hypothetical cash-flow scenarios; no causal coefficients used."""
import math

import pandas as pd

from .download import ROOT


def cohort_stock(new_students,retention,years_of_study,year,capacity):
    if new_students<0 or not 0<=retention<=1 or years_of_study<1 or year<1 or capacity<0:
        raise ValueError('Invalid cohort/capacity assumptions')
    cohorts=[]
    for _ in range(year):
        continuing=[count*retention for count in cohorts[:years_of_study-1]]
        admitted=min(new_students,max(0,capacity-sum(continuing)))
        cohorts=[admitted,*continuing]
    return sum(cohorts)


def npv_from_cohorts(new_students=100,retention=.9,years_of_study=4,capacity=500,
                     net_tuition_contribution=6000,generated_receipts=1_000_000,
                     annual_athletics_cost=5_000_000,capital_outlay=0,discount_rate=.06,horizon=10):
    if discount_rate<=-1 or horizon<1 or min(net_tuition_contribution,generated_receipts,annual_athletics_cost,capital_outlay)<0:
        raise ValueError('Invalid financial assumptions')
    flows=[]
    for year in range(1,horizon+1):
        stock=cohort_stock(new_students,retention,years_of_study,year,capacity)
        cash=generated_receipts+stock*net_tuition_contribution-annual_athletics_cost
        flows.append(dict(year=year,extra_enrolled_stock=stock,annual_cash_flow=cash,
                          discounted_cash_flow=cash/(1+discount_rate)**year))
    return -capital_outlay+sum(f['discounted_cash_flow'] for f in flows),flows


def main():
    breakeven=[]
    for cost in [2_000_000,5_000_000,10_000_000]:
        for receipts in [0,1_000_000,3_000_000]:
            for margin in [3000,6000,9000]:
                required=max(0,cost-receipts)/margin
                breakeven.append(dict(extra_annual_athletics_cost=cost,
                    extra_generated_receipts=receipts,net_tuition_contribution=margin,
                    required_extra_enrolled_stock=required,
                    required_whole_students=math.ceil(required),assumptions='Hypothetical; no causal attribution identified'))
    pd.DataFrame(breakeven).to_csv(ROOT/'results/cfo_break_even_scenarios.csv',index=False)
    scenarios=[]
    for new in [0,25,50,100,200]:
        for retention in [.8,.9,1.]:
            for receipts in [0,1_000_000,3_000_000]:
                for rate in [.03,.06,.09]:
                    for capital in [0,10_000_000]:
                        value,flows=npv_from_cohorts(new_students=new,retention=retention,
                            generated_receipts=receipts,discount_rate=rate,capital_outlay=capital)
                        scenarios.append(dict(planned_extra_first_time_intake_each_year=new,retention=retention,
                            extra_generated_receipts=receipts,discount_rate=rate,capital_outlay=capital,
                            horizon=10,years_of_study=4,capacity=500,net_tuition_contribution=6000,
                            annual_athletics_cost=5_000_000,year10_extra_student_stock=flows[-1]['extra_enrolled_stock'],
                            npv=value,interpretation='Illustrative sustained annual intake and receipts; not an estimated athletics effect'))
    pd.DataFrame(scenarios).to_csv(ROOT/'results/cfo_npv_scenarios.csv',index=False)
    return pd.DataFrame(breakeven),pd.DataFrame(scenarios)


if __name__=='__main__':main()
