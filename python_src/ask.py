import os
import json
from json.decoder import JSONDecodeError
from traceback import format_exc
from argparse import ArgumentParser

from utils.database import storage_configs, MyDocDatabase
from utils.ai_caller import VertexAICaller, DummyAICaller

with open('storage_config.json', 'r') as f:
    storage_configs = json.load(f)
    context_record_dir = storage_configs['channel_records_dir']
    doc_database_dir = storage_configs['doc_database_dir']

def ask_module(
        question_string: str,
        search_topk: int,
        ai_backend: str,
        channel_id: str,
        is_debug: bool = False) -> str:
    """Handle higher-level logic of getting AI's reply"""
    if ai_backend == 'dummy':
        ai_caller = DummyAICaller()
    elif ai_backend == 'vertexai':
        ai_caller = VertexAICaller()

    if channel_id != '':
        context_record_path = os.path.join(context_record_dir, channel_id)
        context_record_exists = os.path.exists(context_record_path)
        os.makedirs(context_record_dir, exist_ok=True)
        try:
            assert context_record_exists
            with open(context_record_path, 'r') as f:
                context = json.load(f)
        except (AssertionError, JSONDecodeError):
            database = MyDocDatabase(doc_database_dir)
            relevant_doc_list = database.search(
                question_string,
                topk=search_topk
            )
            context = ai_caller.promptify_relevant_docs(
                relevant_doc_list
            )

        question_prompt = ai_caller.promptify_question(question_string)
        if is_debug:
            print(context + question_prompt)
        response_string = ai_caller.send_request(context + question_prompt)
        response_prompt = ai_caller.promptify_response(response_string)
        new_context = context + question_prompt + response_prompt
        with open(context_record_path, 'w+') as f:
            json.dump(new_context, f)

    else:
        database = MyDocDatabase(doc_database_dir)
        relevant_doc_list = database.search(
            question_string,
            topk=search_topk
        )
        relevent_docs_prompt = ai_caller.promptify_relevant_docs(
            relevant_doc_list
        )
        question_prompt = ai_caller.promptify_question(question_string)
        if is_debug:
            print(relevent_docs_prompt + question_prompt)
        response_string = ai_caller.send_request(
            relevent_docs_prompt + question_prompt
        )

    return response_string

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        'question_string',
        type=str
    )
    parser.add_argument(
        '--search-topk',
        type=int,
        default=1
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
        default=''
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
