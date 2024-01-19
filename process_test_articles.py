import pandas as pd
import os
import re
from whoosh.index import create_in
from whoosh.fields import Schema, ID, TEXT

data = pd.read_csv('articles.csv', )
data = data.astype(str)
row_num, col_num = data.shape

schema = Schema(
    title=TEXT(stored=True),
    content=TEXT(stored=True, sortable=True),
    id=ID(stored=True)
)
if not os.path.exists("database"):
    os.mkdir("database")
storage = create_in('database', schema)
writer = storage.writer()

for id, row in data.iterrows():
    title, article = row['title'], row['body']
    writer.add_document(title=title, content=article)
writer.commit()
