
import os
from time import sleep
from typing import List, Iterable, Dict, Union

from jieba.analyse import ChineseAnalyzer
from whoosh.analysis import (
    RegexTokenizer, LowercaseFilter, StopFilter
)
from whoosh.collectors import TimeLimitCollector, TimeLimit
from whoosh.fields import Schema, ID, TEXT
from whoosh.index import create_in, open_dir, EmptyIndexError
from whoosh.scoring import TF_IDF, BM25F
from whoosh.qparser import QueryParser, OrGroup
from whoosh.writing import LockError

from .relevant_doc import RelevantDoc

class DocDatabase:

    def __init__(self):
        self.COLUMN_NAMES = ('filename', 'content')

    def add(self, **kwargs) -> None:
        raise NotImplementedError()

    def add_batch(self, _iterable: Iterable[Dict]) -> None:
        raise NotImplementedError()

    def get_all(self, fieldnames) -> List[dict]:
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

        # self.MY_ANALYZER = (
        #     RegexTokenizer()
        #     | LowercaseFilter()
        #     | StopFilter()
        # )

        self.MY_ANALYZER = (
            ChineseAnalyzer()
            | LowercaseFilter()
        )

        self.MY_SCHEMA = Schema(
            filename=ID(stored=True),
            content=TEXT(
                stored=True,
                sortable=True,
                analyzer=self.MY_ANALYZER
            )
        )

        self.TRY_LIMIT = 40
    
    def get_indexer(self):
        if not os.path.exists(self.STORAGE_DIR):
            os.makedirs(self.STORAGE_DIR)
        try:
            findex = open_dir(self.STORAGE_DIR)
        except EmptyIndexError:
            findex = create_in(
                self.STORAGE_DIR,
                schema=self.MY_SCHEMA,
            )
        return findex

    def add(self, **kwargs) -> None:
        findex = self.get_indexer()
        try_count = 0
        while try_count < self.TRY_LIMIT:
            try:
                writer = findex.writer()
                writer.add_document(**kwargs)
                writer.commit()
                return
            except LockError:
                sleep(0.01)
        raise LockError()
        

    def add_batch(self, _iterable: Iterable[Dict]) -> None:
        findex = self.get_indexer()
        try_count = 0
        while try_count < self.TRY_LIMIT:
            try:
                writer = findex.writer()
                for new_doc in _iterable:
                    writer.add_document(**new_doc)
                writer.commit()
                return
            except LockError:
                sleep(0.01)
        raise LockError()
    
    def get_all(self) -> List[dict]:
        """get all documents with fields in `fieldnames`"""
        findex = self.get_indexer()
        reader = findex.reader()
        all_items: List[dict] = list(reader.all_stored_fields())
        return all_items

    def search(
            self,
            query: str,
            fieldname :str = 'content',
            topk: int = 2,
            timelimit: Union[float, None] = 3.0) -> List[RelevantDoc]:
        findex = self.get_indexer()
        parser = QueryParser(fieldname, findex.schema, group=OrGroup)
        query = parser.parse(query)
        # print(query)
        relevant_doc_list = []
        with findex.searcher() as searcher:
            # results = searcher.search(query, limit=topk)
            collector = searcher.collector(limit=topk)
            if timelimit is not None:
                collector = TimeLimitCollector(
                    collector,
                    timelimit=timelimit
                )
            try:
                searcher.search_with_collector(query, collector)
            except TimeLimit:
                pass
            results = collector.results()

            relevant_doc_list = [
                RelevantDoc(res["filename"], res.score, res["content"])
                for res in results
            ]
        return relevant_doc_list

