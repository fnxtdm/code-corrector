import httpx
from openai import OpenAI

def log_request(request):
    print(f"Request: {request.method} {request.url}")
    print(f"Request headers: {request.headers}")
    if request.content:
        print(f"Request body: {request.content}")

def log_response(response):
    print(f"Response status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response content: {response.text}")

class BaseAgent:
    def __init__(self, system_role, model_name, max_tokens):
        self.system_role = system_role
        self.model_name = model_name
        self.max_tokens = max_tokens

        self.chat_history = []

        self.logging = None
        self.answer_language = None
        self.url = None
        self.token = None

        self.http_client = httpx.Client(
            verify = False,
            event_hooks = {
                # "request": [log_request],
                # "response": [log_response]
            }
        )

    def set_parameter(self, language, url, api_key, csv_file, code_dir):
        self.answer_language = language
        self.url = url
        self.token = api_key
        self.csv_file = csv_file
        self.code_dir = code_dir

        self.client = OpenAI(
            base_url = self.url,
            api_key= self.token,
            http_client = self.http_client
        )

    def log(self, message: str):
        if (self.logging is not None):
            self.logging.info(message)

    def chat_completions(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def completion(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def embeddings(self):
        raise NotImplementedError("Subclass must implement abstract method")