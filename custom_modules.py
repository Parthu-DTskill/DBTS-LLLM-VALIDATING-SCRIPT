import requests
from typing import Any

from opik.evaluation.models import OpikBaseModel
from langchain.chat_models import init_chat_model
from opik.integrations.openai import track_openai



class GenericCompatibleModel(OpikBaseModel):
    def __init__(self, model_name: str, api_key: str,model_provider:str):
        super().__init__(model_name)
        self.api_key = api_key
        self.llm = init_chat_model(model=model_name, model_provider=model_provider,configurable_fields="any",api_key=api_key)
        
        

    def generate_string(self, input: str, **kwargs: Any) -> str:
        """
        This method is used as part of LLM as a Judge metrics to take a string prompt, pass it to
        the model as a user message and return the model's response as a string.
        """
        conversation = [
            {
                "content": input,
                "role": "user",
            },
        ]

        provider_response = self.generate_provider_response(messages=conversation, **kwargs)
        return provider_response

    def generate_provider_response(self, messages: list[dict[str, Any]], **kwargs: Any) -> Any:
        """
        This method is used as part of LLM as a Judge metrics to take a list of AI messages, pass it to
        the model and return the full model response.
        """
        payload = {
            "model": self.model_name,
            "messages": messages,
        }

        response = self.llm.invoke(messages)

        
        return response.content


