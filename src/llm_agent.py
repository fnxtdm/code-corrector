import json
import requests
from src.base_agent import BaseAgent

model_max_tokens = {
    "mixtral-8x7b-instruct-v01": 32*1024,
    "mistral-7b-instruct-v03": 32*1024,
    "mistral-7b-instruct-v03-fc": 32*1024,
    "llama-3-8b-instruct": 8*1024,
    "phi-3-mini-128k-instruct": 128*1024,
    "llamaguard-7b": 4*1024,
    "phi-3-5-moe-instruct": 128*1024,
    "codellama-13b-instruct": 16*1024,
    "codestral-22b-v0-1": 32*1024,
    "llama-3-sqlcoder-8b": 8*1024,
    "llava-v1-6-34b-hf": 4*1024,
}

def get_max_tokens(model_name):
    return model_max_tokens.get(model_name, 4*1024)

class LLMAgent(BaseAgent):
    def __init__(self,
                 system_role,
                 model_name="llama-3-8b-instruct", 
                 max_tokens=1024):

        # model_name = "mixtral-8x7b-instruct-v01" # Conversation roles must alternate user/assistant/user/assistant/
        # model_name = "mistral-7b-instruct-v03"
        # model_name = "mistral-7b-instruct-v03-fc"
        # model_name = "codellama-13b-instruct"
        # model_name = "phi-3-mini-128k-instruct"
        # model_name = "phi-3-5-moe-instruct"
        # model_name = "llamaguard-7b" # Conversation roles must alternate user/assistant/user/assistant/
        # model_name = "codestral-22b-v0-1"

        max_tokens = get_max_tokens(model_name)
        super().__init__(system_role, model_name, max_tokens/2)

    def chat_completions(self, prompt="", temperature=0.5, top_p=0.95, max_tokens=999999999):
        self.log("CC: " + prompt)

        # Add system role to the history
        if not self.chat_history:
            self.chat_history.append({"role": "system", "content": self.system_role})
        self.chat_history.append({"role": "user", "content": prompt})

        # Ensure total tokens are within the limit
        total_tokens = sum(len(message['content'].split()) for message in self.chat_history)

        if total_tokens > self.max_tokens:
            # Handle truncation
            while total_tokens > self.max_tokens and self.chat_history:
                # Remove the oldest message
                self.chat_history.pop(1)
                # Recalculate
                total_tokens = sum(len(message['content'].split()) for message in self.chat_history)

        completion = self.client.chat.completions.create(
            model=self.model_name,
            temperature=temperature,
            top_p=top_p,
            max_tokens=min(max_tokens, self.max_tokens - total_tokens),
            messages = self.chat_history,
            timeout=60,
            stream=False
        )

        # chatCompletion
        print(completion.choices[0].message.role + ': ' + completion.choices[0].message.content)
        response_text = completion.choices[0].message.content

        self.chat_history.append({"role": "assistant", "content": response_text})

        self.log("GenAI: " + response_text)

        return response_text

    def completions(self, prompt="", temperature=0.5, top_p=0.95, max_tokens=100):
        self.log("CC: " + prompt)

        # Add system role to the history
        if not self.chat_history:
            self.chat_history.append({"role": "system", "content": self.system_role})
        self.chat_history.append({"role": "user", "content": prompt})

        # Ensure total tokens are within the limit
        total_tokens = sum(len(message['content'].split()) for message in self.chat_history)

        if total_tokens > self.max_tokens:
            # Handle truncation
            while total_tokens > self.max_tokens and self.chat_history:
                # Remove the oldest message
                self.chat_history.pop(1)
                # Recalculate
                total_tokens = sum(len(message['content'].split()) for message in self.chat_history)

        history_prompt = ""
        for message in self.chat_history:
            role = message["role"]
            content = message["content"]
            history_prompt += f"{role}: {content}\n"

        # print(history_prompt)
        completion = self.client.chat.completions.create(
            model=self.model_name,
            temperature=temperature,
            top_p=top_p,
            max_tokens=min(max_tokens, self.max_tokens - total_tokens),
            prompt=history_prompt,
            timeout=60,
            stream=False
        )

        # Completions
        response_text = completion.choices[0].text.strip()
        self.chat_history.append({"role": "assistant", "content": response_text})
        self.log("GenAI: " + response_text)

        return response_text

    # def generate_response_request(self, prompt="", temperature=0.5, top_p=0.95, max_tokens=9999999):
    #     headers = {
    #         "Content-Type": "application/json",
    #         "Accept": "application/json",
    #         "Authorization": f"Bearer {self.token}"
    #     }
    #     messages = [
    #         {
    #             "role": "system",
    #             "content": self.system_role
    #         },
    #         {
    #             "role": "user",
    #             "content": prompt
    #         }
    #     ]
    #     for past_message in self.chat_history:
    #         messages.insert(-1, past_message)

    #     # Add user's request to the history
    #     self.chat_history.append(messages[-1])
    #     query = {
    #         "model": self.model_name,
    #         "temperature": str(temperature),
    #         "top_p": str(top_p),
    #         # "max_tokens": str(self.max_tokens),
    #         "stream": "false",
    #         "messages": messages
    #     }
    #     print(self.url)
    #     print("Request headers:", headers)
    #     print("Request payload:", json.dumps(query, indent=2))
    #     self.log("\n\n[CC]: " + prompt)
    #     # response = requests.post(
    #     response = self.session.post(
    #         self.url, 
    #         headers=headers,
    #         data=json.dumps(query),
    #         verify=False
    #     )
    #     print("Response status code:", response.status_code)
    #     print("Response content:", response.content)
    #     try:
    #         response.raise_for_status()
    #         # Add response to the history
    #         choice = response.json().get("choices", [{}])[0]
    #         message = choice.get("message", {})
    #         content = message.get("content", "").replace("\\n", "\n")
    #         self.history.append({
    #             "role": "assistant",
    #             "content": content
    #         })
    #         self.log("\n\n[GenAI]: " + content)
    #         return content
    #     except requests.exceptions.HTTPError as err:
    #         print(f"HTTP error occurred: {err}")
    #     except Exception as err:
    #         print(f"An error occurred: {err}")
    #     return None

    def clean_history(self):
        self.chat_history.clear()
        self.log("LLMAgent history has been cleared.")
