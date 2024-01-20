from argparse import ArgumentParser
import os

from utils.search import search_module
from utils.prompt import prompt_module
from utils.ai_caller import ai_caller

# discord's body length limit is 2000
MAX_OUTPUT_LENGTH = 1800

def ask_module(question_string: str) -> str:
    """Handle higher-level logic"""

    # print('I am ask_module')
    relevant_doc_list = search_module(question_string)

    prompt = prompt_module(relevant_doc_list, question_string)

    response_string = ai_caller(prompt)

    return response_string

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        'question_string',
        type=str
    )
    question_string = parser.parse_args().question_string
    try:
        response_string = ask_module(question_string)
        if len(response_string) > MAX_OUTPUT_LENGTH:
            response_string = response_string[:MAX_OUTPUT_LENGTH]
            response_string += '[truncated because reply length limit]'
        print(response_string)
    except Exception as e:
        print(repr(e))
