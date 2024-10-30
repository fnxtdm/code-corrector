import json
import requests
from src.base_agent import BaseAgent

class LLMAgent(BaseAgent):
    def __init__(self,
                 system_role,
                 model_name="llama-3-8b-instruct"):
        super().__init__(system_role, model_name)

    def chat_completions(self, prompt="", temperature=0.95, top_p=0.95, max_tokens=999999999):
        self.log("\nPrompt:\n" + prompt)

        # Add system role to the history
        if not self.chat_history:
            self.chat_history.append({"role": "system", "content": self.system_role})
        self.chat_history.append({"role": "user", "content": prompt})

        # Ensure total tokens are within the limit
        total_tokens = sum(len(message['content'].split()) for message in self.chat_history)

        THRESHOLD_MAX_TOKENS = self.max_tokens
        max_tokens = THRESHOLD_MAX_TOKENS - total_tokens

        # Handle truncation
        while total_tokens > THRESHOLD_MAX_TOKENS/3 and len(self.chat_history) > 2:
            # Remove the oldest message
            self.chat_history.pop(1)
            total_tokens = sum(len(message['content'].split()) for message in self.chat_history)
            max_tokens = THRESHOLD_MAX_TOKENS - total_tokens

        print("max_tokens: " + str(max_tokens), total_tokens, self.max_tokens, len(self.chat_history))

        completion = self.client.chat.completions.create(
            model=self.model_name,
            temperature=temperature,
            top_p=top_p,
            # max_tokens=int(max_tokens),
            messages = self.chat_history,
            timeout=60,
            stream=False
        )

        # chatCompletion
        print(completion.choices[0].message.role + ': ' + completion.choices[0].message.content)
        response_text = completion.choices[0].message.content

        self.chat_history.append({"role": "assistant", "content": response_text})

        self.log("\nAssistant:\n" + response_text)

        return response_text

    def completions(self, prompt="", temperature=0.5, top_p=0.95, max_tokens=100):
        self.log("\nCC:\n" + prompt)

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

    def request(self, prompt="", temperature=0.5, top_p=0.95, max_tokens=9999999):
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
        for past_message in self.chat_history:
            messages.insert(-1, past_message)

        # Add user's request to the history
        self.chat_history.append(messages[-1])
        query = {
            "model": self.model_name,
            "temperature": str(temperature),
            "top_p": str(top_p),
            # "max_tokens": str(self.max_tokens),
            "stream": "false",
            "messages": messages
        }
        print(self.url)
        print("Request headers:", headers)
        print("Request payload:", json.dumps(query, indent=2))
        self.log("\n\n[CC]: " + prompt)
        response = requests.post(
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
        self.chat_history.clear()
        self.log("LLMAgent history has been cleared.")
