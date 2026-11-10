"""Illustrative accounting scenarios, never estimates of causal athletics ROI."""
from itertools import product
import pandas as pd
from .download import ROOT

def annual_contribution(extra_students, net_collected_tuition, variable_cost):
    return extra_students*(net_collected_tuition-variable_cost)

def scenario_table():
    rows=[]
    for added,cost,athletic in product([0,50,100,250,500],[3000,6000,9000],[0,500000,1000000]):
        spend=5_000_000;net_tuition=12000
        tuition=annual_contribution(added,net_tuition,cost)
        rows.append(dict(scenario_type='hypothetical_not_causal',incremental_athletics_cost=spend,incremental_generated_revenue=athletic,extra_students=added,net_collected_tuition_per_student=net_tuition,variable_cost_per_student=cost,annual_tuition_contribution=tuition,annual_net_contribution=athletic+tuition-spend,break_even_students=(spend-athletic)/(net_tuition-cost)))
    return pd.DataFrame(rows)

def run():
    d=scenario_table();d.to_csv(ROOT/'results/return_scenarios.csv',index=False)
    return d

if __name__=='__main__':run()
