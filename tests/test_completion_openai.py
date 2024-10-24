import os
import httpx
from openai import OpenAI

def request(request):
    print(f"Request: {request.method} {request.url}")
    print(f"Request headers: {request.headers}")
    if request.content:
        print(f"Request body: {request.content}")

def response(response):
    print(f"Response status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    print(f"Response content: {response.text}")

# As mentioned in the above Note try to setup Dell certificate in your environment to avoid verify=False(SSL verification is disabled).
http_client = httpx.Client(
    verify=False,
    # event_hooks={
    #     "request": [request],
    #     "response": [response]
    # }
)

client = OpenAI(
    base_url='https://genai-api-dev.dell.com/v1',
    # base_url="https://opensource-challenger-api.prdlvgpu1.aiaccel.dell.com/v1/",
    http_client=http_client,
    api_key=os.environ["DEV_GENAI_API_KEY"]
)

completion = client.completions.create(
        model="mixtral-8x7b-instruct-v01",
        max_tokens=2000,
        prompt=f'Can you explain who are the Los Angeles Dodgers and what are they known for is in less than {2000} tokens?',
        stream=False)

print(completion.choices[0].text)