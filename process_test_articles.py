import pandas as pd
import re
import shutil
from python_src.utils.database import DocDatabaseWhoosh

data = pd.read_csv('articles.csv', )
data = data.astype(str)
row_num, col_num = data.shape

shutil.rmtree('./database')
doc_database = DocDatabaseWhoosh('./database')

doc_database.add_batch((
    {
        'filename': str(id),
        'title': row['title'],
        'content': re.sub(r'\{.+\}', '', re.sub(r'\n+', '\n', row['body']))
    }
    for id, row in data.iterrows()
))
