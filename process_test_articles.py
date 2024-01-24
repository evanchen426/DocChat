import pandas as pd
import re
import json
import os
import shutil
from python_src.utils.database import DocDatabaseWhoosh

data = pd.read_csv('test_articles.csv', )
data = data.astype(str)
row_num, col_num = data.shape

with open('./storage_path_config.json') as f:
    storage_paths = json.load(f)
doc_database_dir = storage_paths['doc_database_dir']
original_doc_files_dir = storage_paths['original_doc_files_dir']

if os.path.exists(original_doc_files_dir):
    shutil.rmtree(original_doc_files_dir)
os.makedirs(original_doc_files_dir, exist_ok=True)

if os.path.exists(doc_database_dir):
    shutil.rmtree(doc_database_dir)
doc_database = DocDatabaseWhoosh(doc_database_dir)

all_articles = [
    {
        'filename': row['title'] + '.txt',
        'content': re.sub(r'\{.+\}', '', re.sub(r'\n+', '\n', row['body']))
    }
    for id, row in data.iterrows()
]
print(f'processed {len(all_articles)} articles')
doc_database.add_batch(all_articles)
for file in all_articles:
    filepath = os.path.join(original_doc_files_dir, file['filename'])
    with open(filepath, 'w+') as f:
        f.write(file['content'])
