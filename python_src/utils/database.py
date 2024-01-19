from whoosh.fields import Schema, ID, TEXT
from whoosh.scoring import TF_IDF, BM25F
from whoosh.analysis import (
    RegexAnalyzer, StemmingAnalyzer, LowercaseFilter, StopFilter
)

SEARCH_TOP_K = 5

# MY_SCORE_FUNC = TF_IDF()
MY_SCORE_FUNC = BM25F()

MY_ANALYZER = (
    RegexAnalyzer()
    | LowercaseFilter()
    | StopFilter()
)

MY_SCHEMA = Schema(
    title=TEXT(stored=True),
    content=TEXT(stored=True, sortable=True, analyzer=MY_ANALYZER),
    id=ID(stored=True)
)