from argparse import ArgumentParser
import os

from whoosh.qparser import QueryParser
from whoosh.index import open_dir

from utils.database import (
    MY_SCORE_FUNC, SEARCH_TOP_K, MY_ANALYZER
)

# discord's body length limit is 2000
MAX_OUTPUT_LENGTH = 1600

def ask_module(query_string: str):
    assert os.path.exists('database')
    storage = open_dir('database')

    output = f'I am ask_module\nYour question is "{query_string}"\n'

    # process texts
    query_string = ' '.join([
        token.text
        for token in MY_ANALYZER(query_string)
    ])

    with storage.searcher(weighting=MY_SCORE_FUNC) as searcher:
        parser = QueryParser('content', storage.schema)
        query = parser.parse(query_string)
        results = searcher.search(query, limit=SEARCH_TOP_K)

        output += f'I found {len(results)} article(s) regarding your question:\n'
        result_string = [
            '\n'.join([
                '---',
                f'Title: {res["title"]}',
                f'Relevant score: {res.score}',
                str(res['content'])
            ])
            for res in results
        ]
        output += '\n'.join(result_string)
    return output

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        'query_string',
        type=str
    )
    query_string = parser.parse_args().query_string
    try:
        print(ask_module(query_string)[:MAX_OUTPUT_LENGTH])
    except Exception as e:
        print(repr(e))
