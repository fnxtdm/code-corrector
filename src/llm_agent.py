import json
import requests
from src.base_agent import BaseAgent

MAX_TOKENS = 5000

class LLMAgent(BaseAgent):
    def __init__(self, 
                 model_name="llama-3-8b-instruct", 
                 temperature=0.95,
                 top_p=0.95, 
                 max_tokens=MAX_TOKENS):
        super().__init__()
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.history = []

        # Create a session object
        self.session = requests.Session()

    def generate_response(self, prompt):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

        messages = [
            {
                "role": "system",
                "content": self.system_role
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        for past_message in self.history:
            messages.insert(-1, past_message)

        # Add user's request to the history
        self.history.append(messages[-1])

        query = {
            "model": self.model_name,
            "temperature": str(self.temperature),
            "top_p": str(self.top_p),
            # "max_tokens": str(self.max_tokens),
            "stream": "false",
            "messages": messages
        }

        print(self.url)
        print("Request headers:", headers)
        print("Request payload:", json.dumps(query, indent=2))
        self.log("\n\n[CC]: " + prompt)

        # response = requests.post(
        response = self.session.post(
            self.url, 
            headers=headers,
            data=json.dumps(query),
            verify=False
        )

        print("Response status code:", response.status_code)
        print("Response content:", response.content)

        try:
            response.raise_for_status()

            # Add response to the history
            choice = response.json().get("choices", [{}])[0]
            message = choice.get("message", {})
            content = message.get("content", "").replace("\\n", "\n")

            self.history.append({
                "role": "assistant",
                "content": content
            })
            self.log("\n\n[GenAI]: " + content)
            return content
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None

    def clean_history(self):
        self.history.clear()
        self.log("LLMAgent history has been cleared.")
