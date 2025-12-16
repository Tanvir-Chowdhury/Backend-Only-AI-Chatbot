import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from mistralai import Mistral
from mistralai.models import UserMessage

load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
PINECONE_INDEX_NAME = 'chatbot-index'

def get_pinecone_index():
    """
    Initializes and returns the Pinecone index.
    Checks if the index exists; if not, creates it with the specified dimension and metric.
    """
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Check if index exists, if not create it
    existing_indexes = [index.name for index in pc.list_indexes()]
    if PINECONE_INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=384, # Dimension for all-MiniLM-L6-v2
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
        )
        
    return pc.Index(PINECONE_INDEX_NAME)

def get_embeddings():
    """
    Returns the HuggingFace embedding model instance.
    Uses 'sentence-transformers/all-MiniLM-L6-v2' for generating vector embeddings.
    """
    return HuggingFaceEndpointEmbeddings(
        huggingfacehub_api_token=HUGGINGFACE_API_KEY,
        model="sentence-transformers/all-MiniLM-L6-v2"
    )

def retrieve_context(query):
    """
    Retrieves relevant context from the Pinecone vector database based on the user's query.
    
    Args:
        query (str): The user's input question.
        
    Returns:
        list: A list of text chunks (strings) that are most relevant to the query.
    """
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

def get_rag_response(query, context, chat_history=None):
    """
    Generates a response from the LLM (Mistral AI) using the retrieved context and chat history.
    
    Args:
        query (str): The user's question.
        context (list): List of relevant text chunks retrieved from the vector DB.
        chat_history (list, optional): List of previous ChatMessage objects for context.
        
    Returns:
        str: The generated response from the AI.
    """
    
    client = Mistral(api_key=MISTRAL_API_KEY)
    
    context_str = "\n\n".join(context)
    
    history_str = ""
    if chat_history:
        for msg in chat_history:
            role = "User" if msg.role == 'user' else "Assistant"
            history_str += f"{role}: {msg.content}\n"
    
    prompt = f"""You are a helpful assistant. Use the following context and chat history to answer the user's question.

Context:
{context_str}

Chat History:
{history_str}

Question:
{query}"""

    response = client.chat.complete(
        model="mistral-large-latest",
        messages=[UserMessage(content=prompt)],
    )
    
    return response.choices[0].message.content
