import os
from typing import List, Union, TypeVar

from .relevant_doc import RelevantDoc 
from openai import OpenAI
from vertexai.preview.language_models import TextGenerationModel


class AICaller:
    PromptType = TypeVar("PromptType")
    def make_prompt(
            self,
            relevant_doc_list: List[RelevantDoc],
            question_string: str) -> PromptType:
        raise NotImplementedError()

    def send_request(self, prompt: PromptType) -> str:
        raise NotImplementedError()


class OpenAICaller(AICaller):

    def __init__(self) -> None:
        super().__init__()
        self.client = OpenAI()
        self.MODEL_NAME = 'gpt-3.5-turbo'

    def make_prompt(
            self,
            relevant_doc_list: List[RelevantDoc],
            question_string: str) -> List[dict]:
        
        context_prefix = """Answer user's question according to the provided \
documents. Your answer should simple and straightforward. Each documents are \
separated by "---". If the provided documents are not relevant to user's \
question, reply with an apology.

Here's the provided documents:
"""
        doc_sep = '---\n'

        dummy_relevant_doc = RelevantDoc('n/a', 0, 'n/a')
        if len(relevant_doc_list) == 0:
            relevant_doc_list = [dummy_relevant_doc]
        relevant_doc_list = [''] + relevant_doc_list + ['']

        context_string = (
            context_prefix
            + '\n'
            + doc_sep.join(map(str, relevant_doc_list))
        )

        return [
            {
                'role': 'system',
                'content': context_string
            },
            {
                'role': 'user',
                'content': question_string
            }
        ]
    
    def send_request(self, prompt: List[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.MODEL_NAME,
            messages=prompt
        )
        response_text = response['choices'][0]['message']['content']
        return response_text


class VertexAICaller():
    
    def __init__(self, parameters: Union[dict, None] = None) -> None:
        super().__init__()
        self.MODEL_NAME = 'text-bison@001'
        if parameters is None:
            self.PARAMETERS = {
                "temperature": 0.2,
                "max_output_tokens": 100,
                "top_p": 0.8,
                "top_k": 50
            }
        else:
            self.PARAMETERS = parameters
    
    def make_prompt(
            self,
            relevant_doc_list: List[RelevantDoc],
            question_string: str) -> str:

        context_prefix = """Answer user's question according to the provided \
documents. Your answer should simple and straightforward. Each documents are \
separated by "---". If the provided documents are not relevant to user's \
question, reply with an apology.

Here's the provided documents:
"""
        question_prefix = "\nUSER:"
        doc_sep = '---\n'

        dummy_relevant_doc = RelevantDoc('n/a', 0, 'n/a')
        if len(relevant_doc_list) == 0:
            relevant_doc_list = [dummy_relevant_doc]
        relevant_doc_list = [''] + relevant_doc_list + ['']

        prompt_list = [
            context_prefix,
            doc_sep.join(map(str, relevant_doc_list)),
            question_prefix,
            question_string
        ]
        return '\n'.join(prompt_list)

    def send_request(self, prompt: str) -> str:
        
        model = TextGenerationModel.from_pretrained(self.MODEL_NAME)
        response = model.predict(
            prompt,
            **self.PARAMETERS,
        )
        return response.text

    
class DummyAICaller():

    def make_prompt(
            self,
            relevant_doc_list: List[RelevantDoc],
            question_string: str) -> None:
        return None

    def send_request(
            self,
            prompt: None = None):
        return 'As an AI assistant, I cannot answer this question.'
