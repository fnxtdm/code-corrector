import json
import requests
import os

streaming = True
max_output_tokens = 200

# Available Models list
available_models = ["mixtral-8x7b-instruct-v01", "llamaguard-7b", "mistral-7b-instruct-v03", "phi-3-mini-128k-instruct", "phi-3-5-moe-instruct", "llama-3-8b-instruct", "llama-3-1-8b-instruct", "llama-3-2-3b-instruct"]

# Let's select the model from available list
model_selected = available_models[0]

def stream_and_yield_response(response):
    for chunk in response.iter_lines():
        decoded_chunk = chunk.decode("utf-8")
        if decoded_chunk == "data: [DONE]":
            pass
        elif decoded_chunk.startswith("data: {"):
            payload = decoded_chunk.lstrip("data:")
            json_payload = json.loads(payload)

            if ('role' in json_payload['choices'][0]['delta'] and json_payload['choices'][0]['delta']['role'] != None): 
                yield json_payload['choices'][0]['delta']['role'] + ': '
            else:
                yield json_payload['choices'][0]['delta']['content']

# function from confluence
def llm_api(data):
    """
    Creates a request to Dev GenAI Text to Text model with API key in header.
    """

    url = f"https://genai-api-dev.dell.com/v1/chat/completions"

    headers = {
        'accept': 'application/json',
        'api-key': os.environ["DEV_GENAI_API_KEY"],
        'Content-Type': 'application/json'
    }

    try:
        print(headers, data)
        response = requests.post(url, headers=headers, json=data, stream=data['stream'], verify=False)
        response.raise_for_status()

        if data['stream']:
            for result in stream_and_yield_response(response):
                print(result, end='')
        else:
            response_dict = response.json()
            result = response_dict['choices'][0]['message']['role'] + ': ' + response_dict['choices'][0]['message']['content']
            print(result)

    except requests.exceptions.HTTPError as err:
        print('Error code:', err.response.status_code)
        print('Error message:', err.response.text)
    except Exception as err:
        print('Error:', err)

# Model instruction and Parameters
messages =  [{'role': 'user', 'content': f'You are a helpful assistant who needs to anser in less than {max_output_tokens} tokens'},
             {'role': 'assistant', 'content': 'The Los Angeles Dodgers won the World Series in 2020.'},
             {'role': 'user', 'content': 'Who are the Los Angeles Dodgers?'}]

data = {
    'messages': messages,
    'temperature': 0.5,
    'top_p': 0.95,
    'max_tokens': max_output_tokens,
    'stream': streaming,
    'model': model_selected
    }

# API Call
llm_api(data)