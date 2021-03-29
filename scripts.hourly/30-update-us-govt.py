#!/usr/bin/env python3

import requests, json
import os

if not os.path.exists('data_collation'):
    os.makedirs('data_collation')

datasets = {
    'cases_and_deaths_by_state.csv': 'https://data.cdc.gov/api/views/9mfq-cb36/rows.csv?accessType=DOWNLOAD',
    'lab_tests_by_state.csv': 'https://beta.healthdata.gov/api/views/j8mb-icvb/rows.csv?accessType=DOWNLOAD',
    'hospitalizations_by_state.csv': 'https://beta.healthdata.gov/api/views/g62h-syeh/rows.csv?accessType=DOWNLOAD',
}

for name, url in datasets.items():
    response = requests.get(url)
    response.raise_for_status()

    with open('data_collation/' + name, 'w') as f:
        if name.endswith('.json'):
            json.dump(response.json(), f, indent=2)
        else:
            f.write(response.content.decode('utf-8'))
