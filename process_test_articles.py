import pandas as pd
import os
import re
from python_src.utils.database import DocDatabaseWhoosh

data = pd.read_csv('articles.csv', )
data = data.astype(str)
row_num, col_num = data.shape

doc_database = DocDatabaseWhoosh('./database')

doc_database.add_batch((
    {'filename': id, 'title': row['title'], 'body': row['body']}
    for id, row in data.iterrows()
))
