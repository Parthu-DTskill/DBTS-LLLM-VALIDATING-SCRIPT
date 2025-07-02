import requests
import json
import logging
from datetime import datetime
from opik import Opik, track
from opik.evaluation import evaluate
from opik.evaluation.metrics import Hallucination
from custom_modules import GenericCompatibleModel

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(levelname)s | %(message)s')
time_now = datetime.now().strftime("%H:%M:%S")


class DBTSEvaluator:
    def __init__(self, scenario_id, email, password):
        self.token = None
        self.scenario_id = scenario_id
        self.email = email
        self.password = password
        self.login_url = "https://vistaai-dev-api.dtskill.com/api/auth/login"
        self.workspace_name = "v-partha-sarathi"

        self.client = Opik(workspace=self.workspace_name)

        self.dataset = self.client.get_or_create_dataset(
            name="DBTS Updated Evaluation",
            description="Dataset for evaluating DBTS with gold questions"
        )

        self.hallucination_metric = Hallucination(
            model=GenericCompatibleModel(
                model_name="llama3-70b-8192",
                api_key="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",
                model_provider="groq"
            )
        )

    def login(self):
        payload = {"email": self.email, "password": self.password}
        headers = {
            'Content-Type': 'application/json',
            'X-Frontend-Domain': 'https://vistaai-dev.dtskill.com'
        }
        response = requests.post(
            self.login_url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        self.token = response.json().get("token")
        logging.info("Login successful.")

    @track
    def evaluation_task(self, x):
        question = x.get("question", "")

        logging.info(f"Calling model with: {json.dumps({'query': question})}")

        model_response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama3-70b-8192",
                "messages": [{"role": "user", "content": question}]
            }
        )

        try:
            response_data = model_response.json()
            user_answer = response_data['choices'][0]['message']['content']
        except Exception as e:
            logging.error(f"Error parsing model response: {e}")
            user_answer = "Invalid response"

        return {
            "input": question,
            "output": user_answer
        }

    def evaluate_data(self):
        logging.info("Starting evaluation...")
        evaluate(
            dataset=self.dataset,
            task=self.evaluation_task,
            scoring_metrics=[self.hallucination_metric],
            scoring_key_mapping={
                "input": "input",
                "output": "output",
                "reference": "correct_answer"
            },
            task_threads=1,
            project_name=f"DBTS Updated Evaluation {self.scenario_id}",
            experiment_name=time_now
        )


if __name__ == "__main__":
    client = DBTSEvaluator(
        scenario_id="0f1b2e27-8935-4d03-8c13-d7ca309d4c1e",
        email="parthuprince112@gmail.com",
        password="mkml"
    )
    client.login()
    client.evaluate_data()
