from typing import List, Union, TypeVar, Tuple

from .relevant_doc import RelevantDoc
from vertexai.preview.language_models import TextGenerationModel


class AICaller:
    ContextType = TypeVar('ContextType')
    def make_context(
            self,
            relevant_doc_list: List[RelevantDoc]) -> ContextType:
        raise NotImplementedError()

    def send_request(
            self,
            context: ContextType,
            question_string: str) -> Tuple[str, ContextType]:
        raise NotImplementedError()


# class OpenAICaller(AICaller):

#     def __init__(self) -> None:
#         super().__init__()
#         self.client = OpenAI()
#         self.MODEL_NAME = 'gpt-3.5-turbo'

#     def make_context(
#             self,
#             relevant_doc_list: List[RelevantDoc]) -> List[dict]:
#         context_prefix = """Answer user's question according to the provided \
# documents. Your answer should simple and straightforward. Each documents are \
# separated by "---". If the provided documents are empty or not relevant to \
# user's question, reply with an apology.

# Here's the provided documents:
# """
#         doc_sep = '---\n'

#         dummy_relevant_doc = RelevantDoc('n/a', 0, 'n/a')
#         if len(relevant_doc_list) == 0:
#             relevant_doc_list = [dummy_relevant_doc]
#         relevant_doc_list = [''] + relevant_doc_list + ['']

#         context_string = (
#             context_prefix
#             + '\n'
#             + doc_sep.join(map(str, relevant_doc_list))
#         )

#         return [{
#             'role': 'system',
#             'content': context_string
#         }]
    
#     def send_request(
#             self,
#             context: List[dict],
#             question_string: str) -> Tuple[List[dict], str]:
#         messages = context + [{
#             'role': 'user',
#             'content': question_string
#         }]
#         response = self.client.chat.completions.create(
#             model=self.MODEL_NAME,
#             messages=messages
#         )
#         return response['choices'][0]['content']
    
#     def contextify_ai_response(self, response_string) -> List[dict]:
#         return [{
#             'role': 'assistant',
#             'content': response_string
#         }]


class VertexAICaller():
    
    def __init__(self, parameters: Union[dict, None] = None) -> None:
        super().__init__()
        self.MODEL_NAME = 'text-bison@001'
        if parameters is None:
            self.PARAMETERS = {
                "temperature": 0.2,
                "max_output_tokens": 100,
                "top_p": 0.8,
                "top_k": 20
            }
        else:
            self.PARAMETERS = parameters
    
    def make_context(self, relevant_doc_list: List[RelevantDoc]) -> str:
        context_prefix = """Answer user's question according to the provided \
documents. Your answer should simple and straightforward. Each documents are \
separated by "---". If the provided documents are empty or not relevant to \
user's question, reply with an apology.

Here's the provided documents:
"""
        doc_sep = '---\n'

        dummy_relevant_doc = RelevantDoc('n/a', 0, 'n/a')
        if len(relevant_doc_list) == 0:
            relevant_doc_list = [dummy_relevant_doc]
        relevant_doc_list = [''] + relevant_doc_list + ['']

        prompt_list = [
            context_prefix,
            doc_sep.join(map(str, relevant_doc_list)),
        ]
        return '\n'.join(prompt_list)

    def send_request(self, context: str, question_string: str) -> str:
        model = TextGenerationModel.from_pretrained(self.MODEL_NAME)
        response = model.predict(
            f'{context}\nUSER: {question_string}',
            **self.PARAMETERS,
        )
        return response.text

    def contextify_ai_response(self, response_string) -> str:
        return f'\nAI: {response_string}'
    
class DummyAICaller():

    def make_context(
            self,
            relevant_doc_list: List[RelevantDoc]) -> int:
        return 1

    def send_request(
            self,
            context: int,
            question_string: str) -> str:
        return (
            'As an AI assistant, I cannot answer this question.'
            if context <= 1 else
            f'This is the {context} times I said this. '
            f'As an AI assistant, I cannot answer this question.'
        )
    
    def contextify_ai_response(self, response_string) -> int:
        return 1
