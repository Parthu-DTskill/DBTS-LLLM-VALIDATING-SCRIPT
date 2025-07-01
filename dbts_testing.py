import requests
import json
from opik import Opik, track
from opik.evaluation import evaluate
from opik.evaluation.metrics import Equals, Hallucination, AnswerRelevance, Moderation
from opik.integrations.openai import track_openai
from custom_modules import GenericCompatibleModel
from datetime import datetime
from langchain_community.agent_toolkits import SQLDatabaseToolkit, SparkSQLToolkit

time = datetime.now().strftime("%H:%M:%S")


class LLMTestingClient:
    API_ENDPOINTS = {
        "login": "https://vistaai-dev-api.dtskill.com/api/auth/login",
    }

    def __init__(self, scenario_id):
        self.token = None
        self.scenario_id = scenario_id
        self.client = Opik()
        self.dataset = self.client.get_or_create_dataset(
            name="DBTS Evaluation Dataset", description="Dataset for evaluating DBTS scenarios")
        self.hallucination_metric = Hallucination(model=GenericCompatibleModel(
            model_name="llama3-70b-8192", api_key="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", model_provider="groq"))
        self.answerRelevance_metric = AnswerRelevance(model=GenericCompatibleModel(
            model_name="llama3-70b-8192", api_key="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", model_provider="groq"))

    def login(self, email, password):
        payload = {
            "email": email,
            "password": password
        }
        self.token = self.make_api_request(
            "POST", "login", payload).get("token")

    def make_api_request(self, request_method, api_name, payload=None, custom_url=None):
        url = custom_url if custom_url else self.API_ENDPOINTS[api_name]
        headers = {
            'X-Frontend-Domain': 'https://vistaai-dev.dtskill.com',
            'Content-Type': 'application/json'
        }
        if api_name != "login":
            headers['X-Cluster-ID'] = '49c3b59a-814e-4906-8d91-a2161798b3bb'
            headers['Authorization'] = f"Bearer {self.token}"

        if request_method.upper() == "GET":
            response = requests.request(
                url=url, method=request_method, headers=headers)
        else:
            data = json.dumps(payload) if payload else None
            print(f"payload for {api_name} is {data}")
            response = requests.request(
                url=url, method=request_method, headers=headers, data=data)

        print(f"Response for {api_name}: {response.text}")
        return response.json()

    @track
    def evaluation_task(self, x):
        # DBTS conversation endpoint
        url = f"https://vistaai-dev-api.dtskill.com/api/vista_ai_services/dbts/conversation/{self.scenario_id}/"
        payload = {"user_response": x['input'], "model": "llama3-70b-8192"}
        return {
            "output": self.make_api_request("POST", "", payload, custom_url=url)
        }

#    def add_samples(self):
        samples = [
            {"input": "My pizza is late, what happened?"},
            {"input": "When will my order arrive?"},
            {"input": "I want to complain about a late delivery."}
        ]
        if hasattr(self.dataset, "add_samples"):
            self.dataset.add_samples(samples)
        else:
            print("Your Opik Dataset object does not support adding samples programmatically. Please add samples via the Opik UI.")

    def evaluate_data(self):
        evaluation = evaluate(
            dataset=self.dataset,
            task=self.evaluation_task,
            scoring_metrics=[self.hallucination_metric],
            task_threads=1,
            project_name=f"DBTS Evaluation - Scenario {self.scenario_id}",
            experiment_name=time
        )


if __name__ == "__main__":
    client = LLMTestingClient(
        scenario_id="603937b4-d5b8-4d04-86d7-a59ddcd97f1d")
    client.login(email="parthuprince112@gmail.com", password="mkml")
#    client.add_samples()
    client.evaluate_data()
