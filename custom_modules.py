import requests
from typing import Any
from opik.evaluation.models import OpikBaseModel
from langchain.chat_models import init_chat_model
from opik.integrations.openai import track_openai
class GenericCompatibleModel(OpikBaseModel):
    def __init__(self, model_name: str, api_key: str, model_provider: str):
        super().__init__(model_name)
        self.api_key = api_key
        self.model_provider = model_provider

        # Configure model with temperature 0 for less hallucination
        self.llm = init_chat_model(
            model=model_name,
            model_provider=model_provider,
            api_key=api_key,
            configurable_fields={"temperature": 0.0}
        )

    def generate_string(self, input: str, **kwargs: Any) -> str:
        """
        Used by Opik's LLM-as-a-Judge metric.
        Takes a user message (string), returns the LLM's response (string).
        """
        conversation = [{"role": "user", "content": input}]
        response = self.generate_provider_response(conversation, **kwargs)
        return response

    def generate_provider_response(self, messages: list[dict[str, Any]], **kwargs: Any) -> str:
        """
        Used by Opik's LLM-as-a-Judge metric.
        Sends a list of messages to the LLM, returns the model's string response.
        """
        response = self.llm.invoke(messages)
        return response.content
