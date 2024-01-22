
import os
from time import sleep
from typing import List, Iterable, Dict

from whoosh.collectors import TimeLimitCollector, TimeLimit
from whoosh.qparser import QueryParser
from whoosh.writing import LockError
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, ID, TEXT
from whoosh.scoring import TF_IDF, BM25F
from whoosh.analysis import (
    RegexAnalyzer, LowercaseFilter, StopFilter
)

from .relevant_doc import RelevantDoc

class DocDatabase:

    def __init__(self):
        self.COLUMN_NAMES = ('filename', 'title', 'content')

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

        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
            create_in(
                storage_dir,
                schema=self.MY_SCHEMA,
            )

        self.TRY_LIMIT = 40

    def add(self, **kwargs) -> None:
        assert os.path.exists(self.STORAGE_DIR)
        findex = open_dir(self.STORAGE_DIR)
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
        assert os.path.exists(self.STORAGE_DIR)
        findex = open_dir(self.STORAGE_DIR)
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
    
    def get_all(self, fieldnames) -> List[dict]:
        """get all documents with fields in `fieldnames`"""
        assert len(fieldnames) != 0
        assert os.path.exists(self.STORAGE_DIR)
        findex = open_dir(self.STORAGE_DIR)
        reader = findex.reader()
        all_items: List[dict] = list(reader.all_stored_fields())
        filtered_fieldnames = [
            {item[field] for field in fieldnames}
            for item in all_items
        ]
        return filtered_fieldnames

    def search(self, query: str, topk: int = 2, timelimit = 3.0) -> List[RelevantDoc]:
        assert os.path.exists(self.STORAGE_DIR)
        findex = open_dir(self.STORAGE_DIR)

        # process texts
        query = ' '.join([
            token.text
            for token in self.MY_ANALYZER(query)
        ])

        with findex.searcher(weighting=self.MY_SCORE_FUNC) as searcher:
            parser = QueryParser('content', findex.schema)
            query = parser.parse(query)
            collector = searcher.collector(limit=topk)
            tl_collector = TimeLimitCollector(collector, timelimit=timelimit)
            try:
                searcher.search_with_collector(query, tl_collector)
            except TimeLimit:
                pass
            results = tl_collector.results()
            relevant_doc_list = [
                RelevantDoc(res["title"], res.score, res["content"])
                for res in results
            ]
        return relevant_doc_list

