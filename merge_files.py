import os
import csv

from pathlib import Path
from datetime import datetime as dt

month = str(dt.now().date().month)
year = str(dt.now().date().year)

file_path = Path('merged_files') / f'Mann scraped data({month}-{year}).csv'
with open(file=file_path, mode='w', encoding='UTF-8', newline='\n') as fp:
    writer = None
    header_names = list()
    for idx, filename in enumerate(os.listdir('scraped-data')):
        if filename.endswith('.csv'):
            model_name = filename.split('_', 1)[0].strip()
            variant_name = filename.split('_', 1)[-1].rsplit('(', 1)[0].strip()
            file_path = os.path.join(Path('scraped-data'), filename)
            with open(file=file_path, mode='r', encoding='UTF-8') as csv_file:
                reader = csv.reader(csv_file)
                for i, row in enumerate(reader):
                    if i == 0 and idx == 0:
                        row.extend(['model', 'variant'])
                        header_names = row
                        writer = csv.DictWriter(f=fp, fieldnames=header_names)
                        writer.writeheader()
                    elif i == 0:
                        continue
                    else:
                        data = dict(zip(header_names, row))
                        data['model'], data['variant'] = model_name, variant_name
                        writer.writerow(data)
                        # print(row)


