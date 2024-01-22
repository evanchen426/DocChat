
import os
from time import sleep
from typing import List, Iterable, Dict

from whoosh.qparser import QueryParser
from whoosh.writing import LockError
from whoosh.index import open_dir
from whoosh.fields import Schema, ID, TEXT
from whoosh.scoring import TF_IDF, BM25F
from whoosh.analysis import (
    RegexAnalyzer, StemmingAnalyzer, LowercaseFilter, StopFilter
)

from .relevant_doc import RelevantDoc

DOCDATABASE_DIR = './database'

class DocDatabase:

    def __init__(self):
        self.COLUMN_NAMES = ('filename', 'title', 'content')

    def add(self, **kwargs) -> None:
        raise NotImplementedError()

    def add_batch(self, _iterable: Iterable[Dict]) -> None:
        raise NotImplementedError()


    def update(self, old_kwargs: Dict, new_kwargs: Dict) -> None:
        raise NotImplementedError()

    def delete(self, filename: str) -> None:
        raise NotImplementedError()

    def search(query: str) -> List[RelevantDoc]:
        raise NotImplementedError()


class DocDatabaseWhoosh(DocDatabase):

    def __init__(self, storage_dir):
        super().__init__()
        self.STORAGE_DIR = storage_dir

        # self.MY_SCORE_FUNC = TF_IDF()
        self.MY_SCORE_FUNC = BM25F()

        self.MY_ANALYZER = (
            RegexAnalyzer()
            | LowercaseFilter()
            | StopFilter()
        )

        self.MY_SCHEMA = Schema(
            filename=ID(),
            title=TEXT(stored=True),
            content=TEXT(
                stored=True,
                sortable=True,
                analyzer=self.MY_ANALYZER
            )
        )

        self.TRY_LIMIT = 40

    def add(self, **kwargs) -> None:
        assert os.path.exists(self.STORAGE_DIR)
        storage = open_dir(self.STORAGE_DIR)
        try_count = 0
        while try_count < self.TRY_LIMIT:
            try:
                writer = storage.writer()
                writer.add_document(**kwargs)
                writer.commit()
                return
            except LockError:
                sleep(0.01)
        raise LockError()
        

    def add_batch(self, _iterable: Iterable[Dict]) -> None:
        assert os.path.exists(self.STORAGE_DIR)
        storage = open_dir(self.STORAGE_DIR)
        try_count = 0
        while try_count < self.TRY_LIMIT:
            try:
                writer = storage.writer()
                for new_doc in _iterable:
                    writer.add_document(**new_doc)
                writer.commit()
                return
            except LockError:
                sleep(0.01)
        raise LockError()

    def search(self, query: str, topk: int = 2) -> List[RelevantDoc]:
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
