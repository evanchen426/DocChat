
import io
import json
import os
import zipfile
from time import sleep
from typing import List, Iterable, Dict, Union

import numpy as np
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import semantic_search

from torch import Tensor
from jieba.analyse import ChineseAnalyzer
from whoosh.analysis import (
    RegexTokenizer, LowercaseFilter, StopFilter
)
from whoosh.collectors import TimeLimitCollector, TimeLimit
from whoosh.fields import Schema, ID, TEXT
from whoosh.index import create_in, open_dir, EmptyIndexError
from whoosh.qparser import QueryParser, OrGroup
from whoosh.writing import LockError

from .relevant_doc import RelevantDoc

storage_configs = {}
try:
    with open('./storage_config.json') as f:
        storage_configs = json.load(f)
except json.decoder.JSONDecodeError as e:
    raise e

class DocDatabase:

    def __init__(self):
        self.COLUMN_NAMES = ('filename', 'content')

    def add(self, **kwargs) -> None:
        raise NotImplementedError()

    def add_batch(self, _iterable: Iterable[Dict]) -> None:
        raise NotImplementedError()

    def get_all(self) -> List[dict]:
        raise NotImplementedError()

    def search(query: str, topk: int = 2) -> List[RelevantDoc]:
        raise NotImplementedError()


class DocDatabaseWhoosh(DocDatabase):

    def __init__(self, storage_dir):
        super().__init__()
        self.STORAGE_DIR = storage_dir

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
            topk: int,
            fieldname :str = 'content',
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


class DocDatabaseSBERT(DocDatabase):

    def __init__(self, storage_dir: str):
        self.STORAGE_DIR = storage_dir
        self.NPZ_PATH = os.path.join(storage_dir, 'vectors.npz')
        self.CONTENT_PATH = os.path.join(storage_dir, 'contents.zip')
        self.model = SentenceTransformer(
            storage_configs['sentence_transformer_model']
        )
        os.makedirs(storage_dir, exist_ok=True)
        
    def get_vector_file(self):
        if os.path.exists(self.NPZ_PATH):
            return zipfile.ZipFile(self.NPZ_PATH, 'a')
        else:
            return zipfile.ZipFile(self.NPZ_PATH, 'w')
    
    def get_content_file(self):
        if os.path.exists(self.CONTENT_PATH):
            return zipfile.ZipFile(self.CONTENT_PATH, 'a')
        else:
            return zipfile.ZipFile(self.CONTENT_PATH, 'w')

    def add(self, **kwargs) -> None:
        filename: str = kwargs['filename']
        content: str = kwargs['content'], 
        vec = self.model.encode(content)
        vec_bytes_io = io.BytesIO()
        np.save(vec_bytes_io, vec)
        with self.get_vector_file() as vectorf, \
                self.get_content_file() as contentf:
            contentf.writestr(
                f'{filename}.txt',
                content.encode()
            )
            vectorf.writestr(
                f'{filename}.npy',
                vec_bytes_io.getbuffer().tobytes()
            )

    def add_batch(self, _iterable: Iterable[Dict]) -> None:
        with self.get_vector_file() as vectorf, \
                self.get_content_file() as contentf:
            for item in _iterable:
                filename: str = item['filename']
                content: str = item['content']
                vec = self.model.encode(content)
                vec_bytes_io = io.BytesIO()
                np.save(vec_bytes_io, vec)
                contentf.writestr(
                    f'{filename}',
                    content.encode()
                )
                vectorf.writestr(
                    f'{filename}.npy',
                    vec_bytes_io.getbuffer().tobytes()
                )

    def get_all(self) -> List[dict]:
        all_items = []
        with self.get_content_file() as contentf:
            for infos in contentf.infolist():
                with contentf.open(infos) as file:
                    all_items.append({
                        'filename': infos.filename,
                        'content': file.read().decode()
                    })
        return all_items

    def search(self, query: str, topk: int) -> List[RelevantDoc]:
        relevant_docs = []
        query_vec = self.model.encode(query)
        if not os.path.exists(self.NPZ_PATH):
            return relevant_docs
        npzf = np.load(self.NPZ_PATH)
        filenames = [filename for filename in npzf.keys()]
        doc_vecs = Tensor(np.array([doc_vec for doc_vec in npzf.values()]))
        hits_list = semantic_search(query_vec, doc_vecs, top_k=topk)[0]
        with self.get_content_file() as contentf:
            relevant_docs = [
                RelevantDoc(
                    filenames[hit['corpus_id']],
                    hit['score'],
                    contentf.open(filenames[hit['corpus_id']]).read().decode()
                )
                for hit in hits_list
            ]
        return relevant_docs

MyDocDatabase = globals().get(storage_configs['doc_database_impl'], None)
# create a instance for loading the model
MyDocDatabase(storage_configs['doc_database_dir'])
