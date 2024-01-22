import os
import json
from json.decoder import JSONDecodeError
from traceback import format_exc
from argparse import ArgumentParser

from utils.database import DocDatabaseWhoosh
# from utils.relevant_doc import RelevantDoc
from utils.ai_caller import VertexAICaller, DummyAICaller

CONTEXT_RECORD_DIR = './context_record'
DOCDATABASE_DIR = './database'

def ask_module(
        question_string: str,
        search_topk: int,
        ai_backend: str,
        channel_id: str,
        bind_channel: bool,
        is_debug: bool = False) -> str:
    """Handle higher-level logic of getting AI's reply"""
    database = DocDatabaseWhoosh(DOCDATABASE_DIR)
    assert channel_id != ''

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

    context_record_path = os.path.join(CONTEXT_RECORD_DIR, channel_id)
    context_record_exists = os.path.exists(context_record_path)
    if bind_channel or context_record_exists:
        os.makedirs(CONTEXT_RECORD_DIR, exist_ok=True)
        try:
            assert context_record_exists
            with open(context_record_path, 'r') as f:
                context = json.load(f)
        except (AssertionError, JSONDecodeError):
            context = ai_caller.make_context(relevant_doc_list)

        resp_string = ai_caller.send_request(context, question_string)
        resp_context = ai_caller.contextify_ai_response(resp_string)
        context += resp_context
        with open(context_record_path, 'w+') as f:
            json.dump(context, f)

    else:
        context = ai_caller.make_context(relevant_doc_list)
        resp_string = ai_caller.send_request(context, question_string)
        

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
        # default='dummy'
    )
    parser.add_argument(
        '--channel-id',
        type=str,
        required=True
    )
    parser.add_argument(
        '--bind-channel',
        action='store_true'
    )
    parser.add_argument(
        '--is-debug',
        action='store_true'
    )
    args = parser.parse_args()
    try:
        resp_string = ask_module(**vars(args))
        print(resp_string)
    except Exception as e:
        print(format_exc())
        raise e
