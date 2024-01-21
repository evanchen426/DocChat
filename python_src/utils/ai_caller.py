import os
from typing import List, Callable

from .relevant_doc import RelevantDoc 
from openai import OpenAI
from vertexai.preview.language_models import TextGenerationModel


def openai_caller(
        relevant_doc_list: List[RelevantDoc],
        question_string: str) -> str:

    client = OpenAI()
    context_prefix = """
Answer user's question according to the provided documents. Each \
documents are seperated by a "---". If the provided documents are not \
relevant to user's question, reply with an apology.

Here's the provided documents:
"""
    doc_sep = '---\n'

    context_string = (
        context_prefix
        + '\n'
        + doc_sep.join(map(str, relevant_doc_list))
    )

    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {
                'role': 'system',
                'content': context_string
            },
            {
                'role': 'user',
                'content': question_string
            }
        ]
    )

    response_text = response['choices'][0]['message']['content']

    return response_text

def vertexai_caller(
        relevant_doc_list: List[RelevantDoc],
        question_string: str) -> str:
    
    context_prefix = """
Answer user's question according to the provided documents. Each \
documents are seperated by a "---". If the provided documents are not \
relevant to user's question, reply with an apology.

Here's the provided documents:
"""

    question_prefix = "Here's the user's question:"

    doc_sep = '---\n'

    dummy_relevant_doc = RelevantDoc('n/a', 0, 'n/a')

    if len(relevant_doc_list) == 0:
        relevant_doc_list = [dummy_relevant_doc]

    prompt_list = [
        context_prefix,
        doc_sep.join(map(str, relevant_doc_list)),
        question_prefix,
        question_string
    ]
    prompt_text = '\n'.join(prompt_list)

    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 400,
        "top_p": 0.8,
        "top_k": 50
    }
    model = TextGenerationModel.from_pretrained('text-bison@001')
    response = model.predict(
        prompt_text,
        **parameters,
    )
    return response.text

def dummy_ai_caller(
        relevant_doc_list: List[RelevantDoc],
        question_string: str) -> str:
    return 'As an AI assistant, I cannot answer this question.'

ai_caller: Callable[[str], str] = dummy_ai_caller
