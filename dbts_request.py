import requests
import json

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

    def make_api_request(self, request_method, api_name, payload=None, custom_url=None):
        url = custom_url if custom_url else self.API_ENDPOINTS.get(api_name)
        headers = {
            'X-Frontend-Domain': 'https://vistaai-dev.dtskill.com',
            'Content-Type': 'application/json'
        }
        if api_name != "login":
            headers['X-Cluster-ID'] = '5b1d38d4-27a6-4baf-8dc1-7ed60f2be00d'
            headers['Authorization'] = f"Bearer {self.token}"

        try:
            if request_method.upper() == "GET":
                response = requests.request(url=url, method=request_method, headers=headers)
            else:
                data = json.dumps(payload) if payload else None
                print(f"payload for {api_name if api_name else custom_url} is {data}")
                response = requests.request(url=url, method=request_method, headers=headers, data=data)

            response.raise_for_status()
            print(f"Response for {api_name if api_name else custom_url}: {response.text}")
            return response.json()
        except Exception as e:
            print(f"API request failed: {e}")
            return {}

    def login(self, email, password):
        payload = {
            "email": email,
            "password": password
        }
        self.token = self.make_api_request("POST", "login", payload).get("token")

    def get_or_create_document(self, name="DBTS_Testing_Document"):
        documents = self.make_api_request("GET", "documents_list")
        if any(item.get('name') == name for item in documents):
            self.document_id = next(doc["id"] for doc in documents if doc["name"] == name)
        else:
            payload = {"name": name}
            document = self.make_api_request("POST", "document_create", payload)
            self.document_id = document.get("id")

    def get_or_create_scenario(self, name="Late Delivery_v1", scenario_prompt="customer is calling to enquire about late delivery."):
        scenarios = self.make_api_request("GET", "scenarios_list")
        if any(item.get('name') == name for item in scenarios):
            self.scenario_id = next(scenario["id"] for scenario in scenarios if scenario["name"] == name)
        else:
            payload = {
                "name": name,
                "prompt": scenario_prompt,
                "document": self.document_id,
                "support_type": "Chat",
                "scorecard": "13f82a6e-4166-4bb5-9c79-fe51c6082ad6"
            }
            scenario = self.make_api_request("POST", "scenario_create", payload)
            self.scenario_id = scenario.get("id")

    def scenario_add_user(self, user_list=None):
        if user_list is None:
            user_list = ["bd7b16ed-4f14-4949-88d1-c013d8e27f21"]
        url = f"https://vistaai-dev-api.dtskill.com/api/vista_ai_services/dbts/scenario/{self.scenario_id}/assign-users/"
        payload = {
            "users": user_list,
            "document_id": self.document_id
        }
        self.make_api_request("POST", "", payload, custom_url=url)

if __name__ == "__main__":
    client = DBTSClient()
    client.login(email="vistadevsa@yopmail.com", password="india@dec1225")
    client.get_or_create_document()
    client.get_or_create_scenario()
    client.scenario_add_user()