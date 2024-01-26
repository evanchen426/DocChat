from typing import List, Union, TypeVar, Tuple

from .relevant_doc import RelevantDoc
from vertexai.preview.language_models import TextGenerationModel


class AICaller:
    PromptType = TypeVar('PromptType')
    def promptify_relevant_docs(
            self,
            relevant_doc_list: List[RelevantDoc]) -> PromptType:
        raise NotImplementedError()

    def promptify_question(question_string: str) -> PromptType:
        raise NotImplementedError()
    
    def promptify_response(response_string_string: str) -> PromptType:
        raise NotImplementedError()

    def send_request(self, prompt: PromptType) -> str:
        raise NotImplementedError()


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
    
    def promptify_relevant_docs(self, relevant_doc_list: List[RelevantDoc]) -> str:
        context_prefix = """You are an AI assistant. Your job is to answer \
user's question according to the provided spec documents. Your answer should be \
simple and straightforward. Each documents are separated by "---". If the there's \
no documents or the documents do not explicitly contain the answer to user's \
question, reply with an apology stating that no document answers the question.

Here's the provided documents:"""
        doc_sep = '---\n'

        dummy_relevant_doc = RelevantDoc('n/a', 0, 'n/a')
        if len(relevant_doc_list) == 0:
            relevant_doc_list = [dummy_relevant_doc]
        relevant_doc_list = [''] + relevant_doc_list + ['']

        prompt_list = [
            context_prefix,
            doc_sep.join(map(str, relevant_doc_list)),
        ]
        return '\n'.join(prompt_list) + '\n'

    def promptify_question(self, question_string: str) -> str:
        return f'USER: {question_string}\nASSISTANT: '

    def promptify_response(self, response_string: str) -> str:
        return f'{response_string}\n'

    def send_request(self, prompt: str) -> str:
        model = TextGenerationModel.from_pretrained(self.MODEL_NAME)
        response = model.predict(
            prompt,
            **self.PARAMETERS,
        )
        return response.text
        # return 'AAA'
    
class DummyAICaller():

    def promptify_relevant_docs(
            self,
            relevant_doc_list: List[RelevantDoc]) -> str:
        return 'Relevant Docs:\n' + '\n'.join(
            [f'- {d.filename}' for d in relevant_doc_list]
        )

    def promptify_question(self, question_string: str) -> str:
        return '\n' + question_string

    def promptify_response(self, response_string: str) -> str:
        return '\n' + response_string

    def send_request(self, prompt: str) -> str:
        response_count = prompt.count('As an AI assistant')
        return (
            'As an AI assistant, I cannot answer this question.'
            if response_count == 0 else
            f'This is the {response_count + 1} times I said this. '
            f'As an AI assistant, I cannot answer this question.'
        )
