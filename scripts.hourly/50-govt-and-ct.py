#!/usr/bin/env python3

import json
import datetime
import math
from collections import defaultdict
import itertools
import os
import csv

if not os.path.exists('by_state'):
    os.makedirs('by_state')

first_date = datetime.date(2020, 1, 13)
last_date = datetime.date.today()

global_dates = []
curr = first_date
while curr <= last_date:
    global_dates.append(str(curr))
    curr = curr + datetime.timedelta(days=1)

print(global_dates)

## pull data from govt CSVs
govt_state_data = defaultdict(lambda: defaultdict(lambda: {}))
with open('data_collation/cases_and_deaths_by_state.csv', 'r') as f:
    for row in csv.DictReader(f):
        date = str(datetime.datetime.strptime(row['submission_date'], '%m/%d/%Y').date())
        state = row['state']
        total_cases = row['tot_cases']
        total_deaths = row['tot_death']
        govt_state_data[state]['confirmed'][date] = int(total_cases)
        govt_state_data[state]['deaths'][date] = int(total_deaths)
with open('data_collation/lab_tests_by_state.csv', 'r') as f:
    for row in csv.DictReader(f):
        date = str(datetime.datetime.strptime(row['date'], '%Y/%m/%d').date())
        state = row['state']
        total_tested_for_result = row['total_results_reported']
        if date not in govt_state_data[state]['tested']:
            govt_state_data[state]['tested'][date] = 0
        govt_state_data[state]['tested'][date] += int(total_tested_for_result)
with open('data_collation/hospitalizations_by_state.csv', 'r') as f:
    for row in csv.DictReader(f):
        date = str(datetime.datetime.strptime(row['date'], '%Y/%m/%d').date() - datetime.timedelta(days=1)) # record this for the previous day since the data is for the previous day
        state = row['state']
        total_new_hospitalized = 0
        for k in ['previous_day_admission_adult_covid_suspected', 'previous_day_admission_pediatric_covid_confirmed', 'previous_day_admission_adult_covid_confirmed', 'previous_day_admission_pediatric_covid_suspected']:    
            try:
                total_new_hospitalized += int(row[k])
            except ValueError:
                pass
        govt_state_data[state]['hospitalized'][date] = total_new_hospitalized

## load CT data and merge with govt data
us_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'] + ['AS', 'GU', 'MP', 'PR', 'VI']
for state in us_states:
    with open('by_state_ct/' + state.lower() + '.json', 'r') as f:
        state_data = json.load(f)

    assert state_data['timeseries_dates'][0] == global_dates[0]

    govt_first_date_index = len(state_data['timeseries_dates'])
    govt_first_date = state_data['timeseries_dates'][-1]

    state_data['timeseries_dates'] = global_dates

    for govt_date in global_dates[govt_first_date_index:]:
        for field in ['confirmed', 'deaths', 'tested', 'hospitalized']:
            if field not in state_data['total']: continue # skip fields that covidtracking didn't have for now
            new_value = govt_state_data[state][field].get(govt_date, None)
            if new_value is not None and field == 'hospitalized':
                # we need to accumulate this
                new_value += state_data['total'][field][-1]
            state_data['total'][field].append(new_value)
    
    while state_data['total']['confirmed'][-1] is None:
        for field in state_data['total'].keys():
            state_data['total'][field].pop()
        state_data['timeseries_dates'].pop()
    
    with open('by_state/' + state.lower() + '.json', 'w') as f:
        json.dump(state_data, f, indent=2)