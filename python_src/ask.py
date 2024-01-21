from argparse import ArgumentParser
import os

from utils.database import DocDatabaseWhoosh
# from utils.relevant_doc import RelevantDoc
from utils.ai_caller import VertexAICaller, OpenAICaller, DummyAICaller

# discord's body length limit is 2000
MAX_OUTPUT_LENGTH = 1800


def ask_module(
        question_string: str,
        ai_backend: str,
        is_debug: bool = False) -> str:
    """Handle higher-level logic"""
    database = DocDatabaseWhoosh()
    relevant_doc_list = database.search(question_string)
    if is_debug:
        print('---\n'.join(
            map(str, relevant_doc_list)
        ))

    if ai_backend == 'dummy':
        ai_caller = DummyAICaller()
    elif ai_caller == 'openai':
        ai_caller = OpenAICaller()
    elif ai_caller == 'vertexai':
        ai_caller = VertexAICaller()
    prompt = ai_caller.make_prompt(relevant_doc_list, question_string)
    response_string = ai_caller.send_request(prompt)

    return response_string

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        'question_string',
        type=str
    )
    parser.add_argument(
        '--ai-backend',
        type=str,
        choices=['dummy', 'vertexai', 'openai'],
        default='vertexai'
    )
    parser.add_argument(
        '--debug',
        action='store_true'
    )
    args = parser.parse_args()
    question_string = args.question_string
    is_debug = args.debug
    try:
        response_string = ask_module(
            args.question_string,
            ai_backend=args.ai_backend,
            is_debug=args.debug
        )

        if len(response_string) > MAX_OUTPUT_LENGTH:
            response_string = response_string[:MAX_OUTPUT_LENGTH]
            response_string += '[truncated because of reply length limit]'
        print(response_string)
    except Exception as e:
        print(repr(e))
