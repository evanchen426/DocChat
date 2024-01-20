
import os
from typing import List, Iterable, Dict

from whoosh.qparser import QueryParser
from whoosh.index import open_dir
from whoosh.fields import Schema, ID, TEXT
from whoosh.scoring import TF_IDF, BM25F
from whoosh.analysis import (
    RegexAnalyzer, StemmingAnalyzer, LowercaseFilter, StopFilter
)

from relevant_doc import RelevantDoc


class DocDatabase:

    def __init__(self):
        self.COLUMN_NAMES = ('title', 'content', 'id')

    def add(self, **kwargs) -> None:
        pass

    def update(self, _iterable: Iterable[Dict]) -> None:
        pass

    def search(query: str) -> List[RelevantDoc]:
        pass


class DocDatabaseWhoosh(DocDatabase):

    def __init__(self):
        self.STORAGE_DIR = './database'

        self.SEARCH_TOP_K = 5

        # self.MY_SCORE_FUNC = TF_IDF()
        self.MY_SCORE_FUNC = BM25F()

        self.MY_ANALYZER = (
            RegexAnalyzer()
            | LowercaseFilter()
            | StopFilter()
        )

        self.MY_SCHEMA = Schema(
            title=TEXT(stored=True),
            content=TEXT(
                stored=True,
                sortable=True,
                analyzer=self.MY_ANALYZER
            ),
            id=ID(stored=True)
        )

    def add(self, **kwargs) -> None:
        assert os.path.exists(self.STORAGE_DIR)
        storage = open_dir(self.STORAGE_DIR)
        writer = storage.writer()
        writer.add_document(**kwargs)

    def update(self, _iterable: Iterable[Dict]) -> None:
        assert os.path.exists(self.STORAGE_DIR)
        storage = open_dir(self.STORAGE_DIR)
        writer = storage.writer()
        for new_doc in _iterable:
            writer.add_document(**new_doc)

    def search(self, query: str) -> List[RelevantDoc]:
        assert os.path.exists(self.STORAGE_DIR)
        storage = open_dir(self.STORAGE_DIR)

        # process texts
        query = ' '.join([
            token.text
            for token in self.MY_ANALYZER(query)
        ])

        with storage.searcher(weighting=self.MY_SCORE_FUNC) as searcher:
            parser = QueryParser('content', storage.schema)
            query = parser.parse(query)
            results = searcher.search(query, limit=self.SEARCH_TOP_K)
            relevant_doc_list = [
                RelevantDoc(res["title"], res.score, res["content"])
                for res in results
            ]
        return relevant_doc_list
