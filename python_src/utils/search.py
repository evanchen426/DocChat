import os
from typing import List

from whoosh.qparser import QueryParser
from whoosh.index import open_dir

from .database import (
    MY_SCORE_FUNC, SEARCH_TOP_K, MY_ANALYZER
)
from .relevant_doc import RelevantDoc

def search_module(question_string: str) -> List[RelevantDoc]:
    """Find relevant docs w.r.t the user question
    The result list may be empty"""

    # print('I am search_module')
    assert os.path.exists('database')
    storage = open_dir('database')

    # process texts
    question_string = ' '.join([
        token.text
        for token in MY_ANALYZER(question_string)
    ])

    with storage.searcher(weighting=MY_SCORE_FUNC) as searcher:
        parser = QueryParser('content', storage.schema)
        query = parser.parse(question_string)
        results = searcher.search(query, limit=SEARCH_TOP_K)
        relevant_doc_list = [
            RelevantDoc(res["title"], res.score, res["content"])
            for res in results
        ]
    
    return relevant_doc_list
