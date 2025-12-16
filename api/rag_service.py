import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from huggingface_hub import InferenceClient

load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
PINECONE_INDEX_NAME = 'chatbot-index'

def get_pinecone_index():
    pc = Pinecone(api_key=PINECONE_API_KEY)
    return pc.Index(PINECONE_INDEX_NAME)

def get_embeddings():
    return HuggingFaceInferenceAPIEmbeddings(
        api_key=HUGGINGFACE_API_KEY,
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

def retrieve_context(query):
    embeddings = get_embeddings()
    query_embedding = embeddings.embed_query(query)
    
    index = get_pinecone_index()
    results = index.query(vector=query_embedding, top_k=3, include_metadata=True)
    
    contexts = []
    for match in results['matches']:
        if match.get('metadata'):
            text = match['metadata'].get('text') or match['metadata'].get('content')
            if text:
                contexts.append(text)
                
    return contexts

def get_rag_response(query, context):
    
    client = InferenceClient(token=HUGGINGFACE_API_KEY)
    
    context_str = "\n\n".join(context)
    
    prompt = f"""<s>[INST] You are a helpful assistant. Use the following context to answer the user's question.

Context:
{context_str}

Question:
{query} [/INST]"""

    response = client.text_generation(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        prompt=prompt,
        max_new_tokens=512,
        temperature=0.7,
        return_full_text=False
    )
    
    return response
