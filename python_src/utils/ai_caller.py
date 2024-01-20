import os
from vertexai.preview.language_models import TextGenerationModel

MODEL_ID = 'text-bison@001'

def vertex_ai_caller(prompt_string: str) -> str:
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 400,
        "top_p": 0.8,
        "top_k": 50
    }
    model = TextGenerationModel.from_pretrained(MODEL_ID)
    response = model.predict(
        prompt_string,
        **parameters,
    )
    return response.text

def dummy_ai_caller(prompt_string: str) -> str:
    return 'As an AI assistant, I cannot anwer this question.'

ai_caller = dummy_ai_caller
