import os
import json
from argparse import ArgumentParser
from typing import Union

from utils.database import DOCDATABASE_DIR, DocDatabaseWhoosh
# from utils.relevant_doc import RelevantDoc
from utils.ai_caller import VertexAICaller, OpenAICaller, DummyAICaller

CONTEXT_RECORD_DIR = './context_record'

def ask_module(
        question_string: str,
        search_topk: int,
        ai_backend: str,
        channel_id: Union[str, None],
        is_debug: bool = False) -> str:
    """Handle higher-level logic of getting AI's reply"""
    database = DocDatabaseWhoosh(DOCDATABASE_DIR)
    relevant_doc_list = database.search(
        question_string,
        search_topk
    )
    if is_debug:
        print('---\n'.join(
            map(str, relevant_doc_list)
        ))

    if ai_backend == 'dummy':
        ai_caller = DummyAICaller()
    elif ai_backend == 'openai':
        ai_caller = OpenAICaller()
    elif ai_backend == 'vertexai':
        ai_caller = VertexAICaller()

    if channel_id is None:
        context = ai_caller.make_context(relevant_doc_list)
        resp_context, resp_string = ai_caller.send_request(
            context,
            question_string
        )

    else:
        context_record_path = os.path.join(CONTEXT_RECORD_DIR, channel_id)
        if os.path.exists(context_record_path):
            with open(context_record_path, 'r') as f:
                context = json.load(f)
        else:
            context = ai_caller.make_context(relevant_doc_list)
        resp_context, resp_string = ai_caller.send_request(
            context,
            question_string
        )
        context += resp_context
        with open(context_record_path, 'r') as f:
            json.dump(context, context_record_path)

    return resp_string

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        'question_string',
        type=str
    )
    parser.add_argument(
        '--search-topk',
        type=int,
        default=2
    )
    parser.add_argument(
        '--ai-backend',
        type=str,
        choices=['dummy', 'vertexai', 'openai'],
        default='vertexai'
    )
    parser.add_argument(
        '--channel-id',
        type=int,
        default=None
    )
    parser.add_argument(
        '--debug',
        action='store_true'
    )
    args = parser.parse_args()
    try:
        resp_string = ask_module(**args)
        print(resp_string)
    except Exception as e:
        print(repr(e))
        raise e
