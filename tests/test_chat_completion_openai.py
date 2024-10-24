from openai import OpenAI
import httpx
import os

# As mentioned in the above Note try to setup Dell certificate in your environment to avoid verify=False(SSL verification is disabled).
http_client=httpx.Client(verify=False)
client = OpenAI(
    base_url='https://genai-api-dev.dell.com/v1',
    http_client=http_client,
    api_key=os.environ["DEV_GENAI_API_KEY"]
)

streaming = False # To enable streaming, set streaming to True
available_models = ["mixtral-8x7b-instruct-v01", "llamaguard-7b", "mistral-7b-instruct-v03", "phi-3-mini-128k-instruct", "phi-3-5-moe-instruct", "llama-3-8b-instruct", "llama-3-1-8b-instruct", "llama-3-2-3b-instruct","codellama-13b-instruct", "codestral-22b-v0-1"]
selected_model = available_models[5]

completion = client.chat.completions.create(
    model=selected_model,
    messages = [
            {"role": "user", "content": "What is your favourite condiment?"},
            {"role": "assistant", "content": "Well, I'm quite partial to a good squeeze of fresh lemon juice. It adds just the right amount of zesty flavour to whatever I'm cooking up in the kitchen!"},
            {"role": "user", "content": "Do you have mayonnaise recipes?"}
        ],
    stream=streaming
)

if streaming:
    for chunk in completion:
        if chunk.id:
            if chunk.choices[0].delta.content == None and chunk.choices[0].delta.role != None:
                print(chunk.choices[0].delta.role+': ', end='')
            elif chunk.choices[0].delta.content != None:
                print(chunk.choices[0].delta.content, end='')
else:
    print(completion.choices[0].message.role + ': ' + completion.choices[0].message.content)