import requests
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

class DBTSClient:
    API_ENDPOINTS = {
        "login": "https://vistaai-dev-api.dtskill.com/api/auth/login",
        "documents_list": "https://vistaai-dev-api.dtskill.com/api/vista_ai_services/dbts/document/",
        "document_create": "https://vistaai-dev-api.dtskill.com/api/vista_ai_services/dbts/document/",
        "scenarios_list": "https://vistaai-dev-api.dtskill.com/api/vista_ai_services/dbts/scenario/",
        "scenario_create": "https://vistaai-dev-api.dtskill.com/api/vista_ai_services/dbts/scenario/",
    }

    def __init__(self):
        self.token = None
        self.document_id = None
        self.scenario_id = None
        self.cluster_id = '49c3b59a-814e-4906-8d91-a2161798b3bb'
        self.domain = 'https://vistaai-dev.dtskill.com'

    def make_api_request(self, method, api_name, payload=None, custom_url=None):
        url = custom_url or self.API_ENDPOINTS.get(api_name)
        headers = {
            'X-Frontend-Domain': self.domain,
            'Content-Type': 'application/json'
        }

        if api_name != "login":
            headers['X-Cluster-ID'] = self.cluster_id
            headers['Authorization'] = f"Bearer {self.token}"

        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                data=json.dumps(payload) if payload and method.upper() != "GET" else None
            )
            response.raise_for_status()
            logging.info(f"{api_name or url} - {response.status_code}")
            return response.json()
        except Exception as e:
            logging.error(f"API request failed for {api_name or url}: {e}")
            return {}

    def login(self, email, password):
        logging.info("Logging in...")
        payload = {"email": email, "password": password}
        response = self.make_api_request("POST", "login", payload)
        self.token = response.get("token")
        if self.token:
            logging.info("Login successful.")
        else:
            raise ValueError("Login failed, token not received.")

    def get_or_create_document(self, name, file_path):
        logging.info(f"Checking for document: {name}")
        documents = self.make_api_request("GET", "documents_list")
        matching_doc = next((doc for doc in documents if doc["name"] == name), None)

        if matching_doc:
            self.document_id = matching_doc["id"]
            logging.info(f"Document already exists with ID: {self.document_id}")
        else:
            logging.info("Uploading new document...")
            if not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            with open(file_path, "rb") as f:
                files = {"file": f}
                data = {"name": name}
                headers = {
                    'X-Frontend-Domain': self.domain,
                    'X-Cluster-ID': self.cluster_id,
                    'Authorization': f"Bearer {self.token}"
                }
                response = requests.post(self.API_ENDPOINTS["document_create"], headers=headers, files=files, data=data)
                print("Document upload response:", response.text) 
                response.raise_for_status()
                created_doc = response.json()
                self.document_id = created_doc.get("id")
                logging.info(f"Document created with ID: {self.document_id}")

    def get_or_create_scenario(self, name="Python_Tutorials_1", number_of_questions=3, score_per_question=2):
        logging.info(f"Checking for scenario: {name}")
        scenarios = self.make_api_request("GET", "scenarios_list")
        matching_scenario = next((s for s in scenarios if s["name"] == name), None)

        if matching_scenario:
            self.scenario_id = matching_scenario["id"]
            logging.info(f"Scenario already exists with ID: {self.scenario_id}")
        else:
            logging.info("Creating new scenario...")
            payload = {
                "name": name,
                "document": self.document_id,
                "number_of_questions": number_of_questions,
                "score_per_question": score_per_question,
                "topics": [],
                "scenario_type": "multiple_choice",
                "level": "Default"
            }
            created = self.make_api_request("POST", "scenario_create", payload)
            self.scenario_id = created.get("id")
            logging.info(f"Scenario created with ID: {self.scenario_id}")

    def assign_users_to_scenario(self, user_list):
        logging.info(f"Assigning users to scenario {self.scenario_id}")
        if not self.scenario_id or not self.document_id:
            raise ValueError("Document or Scenario not initialized.")
        url = f"https://vistaai-dev-api.dtskill.com/api/vista_ai_services/dbts/scenario/{self.scenario_id}/assign-users/"
        payload = {
            "users": user_list,
            "document_id": self.document_id
        }
        self.make_api_request("POST", "", payload, custom_url=url)
        logging.info("Users assigned to scenario.")

if __name__ == "__main__":
    client = DBTSClient()
    client.login(email="vistadevsa@yopmail.com", password="india@dec1225")

    client.get_or_create_document(
        name="DBTS_Testing_Document1",
        file_path=r"C:\\Users\\parth\\Documents\\Downloads\\Sets - Assignments.pdf"
    )

    client.get_or_create_scenario(
        name="Python_Tutorials_1",
        number_of_questions=3,
        score_per_question=2
    )

    client.assign_users_to_scenario(
        user_list=["95b6de82-c989-4ae7-936b-700c49290097"]
    )
