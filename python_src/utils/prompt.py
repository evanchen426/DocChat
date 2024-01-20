from typing import List

from .relevant_doc import RelevantDoc

CONTEXT_PREFIX = """
Answer user's question according to the provided documents. Each \
documents are seperated by a "---". If the provided documents are not \
relevant to user's question, reply with an apology.

Here's the provided documents:
"""

QUESTION_PREFIX = "Here's the user's question:"

DOC_SEP = '---\n'

DUMMY_RELEVANTDOC = RelevantDoc('n/a', 0, 'n/a')

def make_prompt(
        relevant_doc_list: List[RelevantDoc],
        question_string: str) -> str:
    """Combine relevant docs and user question into a prompt string"""

    # print('I am make_prompt')
    if len(relevant_doc_list) == 0:
        relevant_doc_list = [DUMMY_RELEVANTDOC]
    prompt_list = [
        CONTEXT_PREFIX,
        DOC_SEP.join(map(str, relevant_doc_list)),
        QUESTION_PREFIX,
        question_string
    ]
    return '\n'.join(prompt_list)

