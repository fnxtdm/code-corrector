import os
import httpx
from openai import OpenAI
from typing import List
from langchain_core.embeddings import Embeddings
from langchain.vectorstores.pgvector import PGVector, DistanceStrategy

# from langchain.embeddings.base import Embeddings
# from langchain.chains import RetrievalQA

from langchain.docstore.document import Document
  
class CustomBGEEmbeddings(Embeddings):
    def __init__(self, url, model_name, api_key):
        self. client = OpenAI(
            base_url=url,
            http_client=httpx.Client(verify=False),
            api_key=api_key,
        )
        self.model_name = model_name

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        resp = self.client.embeddings.create(model=self.model_name,
                                             input=texts)
        return [a.embedding for a in  resp.data]
  
    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        return self.embed_documents([text])[0]
  
embeddings = CustomBGEEmbeddings(
    url="https://genai-api-dev.dell.com/v1",
    model_name="bge-large-en-v1-5",
    api_key=os.environ["DEV_GENAI_API_KEY"]
)

documents = [Document(page_content="This is a test document 1."),
             Document(page_content="This is a test document 2."),
             Document(page_content="This is a test document 3.")]
  
COLLECTION_NAME = "cc_collection"
  
store = PGVector.from_documents(
    embedding=embeddings,
    documents=documents,
    distance_strategy = DistanceStrategy.COSINE, # The distance strategy to use. (default: COSINE)
    collection_name=COLLECTION_NAME, # The name of the collection to use. (default: langchain)
    connection_string=os.getenv("PGVECTOR_CONNECTION_STRING"),
)
