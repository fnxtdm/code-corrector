import httpx
from openai import OpenAI

model_max_tokens = {
    "mixtral-8x7b-instruct-v01": 32*1024,
    "mistral-7b-instruct-v03": 32*1024,
    "mistral-7b-instruct-v03-fc": 32*1024,
    "llama-3-8b-instruct": 8*1024,
    "llama-3-1-8b-instruct": 128*1024,
    "llama-3-2-3b-instruct": 128*1024,
    "llama-3-2-11b-vision-instruct": 128*1024,
    "phi-3-mini-128k-instruct": 128*1024,
    "llamaguard-7b": 4*1024,
    "phi-3-5-moe-instruct": 128*1024,
    "codellama-13b-instruct": 16*1024,
    "codestral-22b-v0-1": 32*1024,
    "llama-3-sqlcoder-8b": 8*1024,
    "llava-v1-6-34b-hf": 4*1024,
}
def get_max_tokens(model_name):
    return int(model_max_tokens.get(model_name, 4*1024) *0.8)

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
    def __init__(self, system_role, model_name="llama-3-8b-instruct"):
        self.system_role = system_role

        # model_name = "mixtral-8x7b-instruct-v01"
        # model_name = "mistral-7b-instruct-v03"
        # model_name = "mistral-7b-instruct-v03-fc"
        # model_name = "codellama-13b-instruct"
        # model_name = "llama-3-2-11b-vision-instruct"
        # model_name = "phi-3-mini-128k-instruct"
        # model_name = "phi-3-5-moe-instruct"
        # model_name = "llamaguard-7b"
        # model_name = "codestral-22b-v0-1"

        self.model_name = model_name
        self.max_tokens = get_max_tokens(model_name)

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

    def set_parameter(self, language, model_name, url, api_key, csv_file, code_dir):
        self.answer_language = language
        self.model_name = model_name
        self.max_tokens = get_max_tokens(model_name)
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