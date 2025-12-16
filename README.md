# Backend-Only AI Chatbot

## Project Overview
This project is a backend-only AI chatbot built with Django and Django REST Framework. It leverages a Retrieval-Augmented Generation (RAG) pipeline to provide accurate, context-aware responses. The system integrates with Pinecone for vector storage and Hugging Face for LLM inference (specifically Mistral-7B). It includes secure user authentication via JWT and background tasks for maintenance.

## Technologies Used
*   **Framework**: Django, Django REST Framework (DRF)
*   **Authentication**: JSON Web Tokens (JWT) via `djangorestframework-simplejwt`
*   **Vector Database**: Pinecone
*   **LLM & Embeddings**: Hugging Face Hub (Mistral-7B-Instruct, Sentence Transformers), LangChain
*   **Task Scheduling**: APScheduler
*   **Database**: SQLite (Default Django DB)
*   **Environment Management**: python-dotenv

## API Documentation

### Authentication
*   **POST /api/signup/**
    *   **Description**: Register a new user.
    *   **Body**: `{"email": "user@example.com", "username": "user", "password": "securepassword"}`
    *   **Response**: `201 Created` with user details.

*   **POST /api/login/**
    *   **Description**: Authenticate and receive JWT tokens.
    *   **Body**: `{"email": "user@example.com", "password": "securepassword"}`
    *   **Response**: `{"refresh": "...", "access": "..."}`

### Chat
*   **POST /api/chat/**
    *   **Headers**: `Authorization: Bearer <access_token>`
    *   **Description**: Send a message to the chatbot.
    *   **Body**: `{"message": "What is the capital of France?"}`
    *   **Response**: `{"response": "The capital of France is Paris."}`

*   **GET /api/chat-history/**
    *   **Headers**: `Authorization: Bearer <access_token>`
    *   **Description**: Retrieve past chat messages for the authenticated user.
    *   **Response**: List of message objects `[{"id": 1, "role": "user", "content": "...", "timestamp": "..."}, ...]`

## Setup Instructions

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd chatbot
    ```

2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**:
    Create a `.env` file in the `chatbot` directory with the following keys:
    ```
    PINECONE_API_KEY=your_pinecone_key
    HUGGINGFACE_API_KEY=your_huggingface_key
    ```

5.  **Apply Migrations**:
    ```bash
    python manage.py migrate
    ```

6.  **Run the Server**:
    ```bash
    python manage.py runserver
    ```

## Background Task Setup
The project uses **APScheduler** to handle background tasks. The scheduler is initialized in `api/apps.py` and starts automatically when the Django application loads.

*   **Task**: `cleanup_old_chats`
*   **Schedule**: Runs daily (every 24 hours).
*   **Function**: Deletes chat messages older than 30 days to maintain database performance.

## Technical Details & Q&A

### How did you integrate the RAG pipeline for the chatbot, and what role does document retrieval play in the response generation?
The RAG pipeline is implemented in `api/rag_service.py`.
1.  **Embeddings**: User queries are converted into vector embeddings using `HuggingFaceInferenceAPIEmbeddings` (sentence-transformers model).
2.  **Retrieval**: These embeddings are used to query the **Pinecone** vector database to find the top 3 most relevant document chunks.
3.  **Role**: Document retrieval provides the "Ground Truth" or context. This context is injected into the prompt sent to the LLM, ensuring the model generates answers based on specific knowledge rather than just its training data.

### What database and model structure did you use for storing user and chat history, and why did you choose this approach?
*   **Database**: SQLite is used for simplicity and ease of local development.
*   **User Model**: Extends `AbstractUser` to use `email` as the unique identifier, which is a modern standard for web apps.
*   **ChatMessage Model**: Stores `user` (ForeignKey), `role` ('user'/'bot'), `content`, and `timestamp`. This relational structure allows for efficient querying of history per user (`filter(user=request.user)`).

### How did you implement user authentication using JWT? What security measures did you take for handling passwords and tokens?
*   **Implementation**: Used `djangorestframework-simplejwt`.
*   **Security**:
    *   **Passwords**: Django's default hashing (PBKDF2) is used; passwords are never stored in plain text.
    *   **Tokens**: Access tokens are short-lived. Refresh tokens are used to obtain new access tokens. Endpoints are protected using `IsAuthenticated` permission class.

### How does the chatbot generate responses using the AI model after retrieving documents?
*   **Model**: The project uses **Mistral-7B-Instruct-v0.2** via the Hugging Face Inference API (an open-source alternative to GPT-3).
*   **Process**:
    1.  Retrieved context strings are joined together.
    2.  A prompt is constructed: `Context: {context} \n Question: {query}`.
    3.  This prompt is sent to the Inference Client, which returns the generated text.

### How did you schedule and implement background tasks for cleaning up old chat history, and how often do these tasks run?
*   **Implementation**: Used `APScheduler`'s `BackgroundScheduler`.
*   **Scheduling**: The task `cleanup_old_chats` is added as an interval job running `days=1` (daily).
*   **Startup**: The scheduler is started in the `ready()` method of `api/apps.py` to ensure it runs as long as the server is active.

### What testing strategies did you use to ensure the functionality of the chatbot, authentication, and background tasks?
*   **Unit Testing**: Django's `TestCase` can be used to verify model constraints and view logic.
*   **API Testing**: `APITestCase` ensures endpoints return correct status codes (200, 201, 401) and JSON structures.
*   **Manual Verification**: Endpoints were verified using tools like Postman/cURL to ensure the RAG pipeline connects to external APIs correctly.

### What external services (APIs, databases, search engines) did you integrate, and how did you set up and configure them?
*   **Pinecone**: Used as the Vector Database. Configured via `PINECONE_API_KEY` in `.env`. Initialized in `rag_service.py`.
*   **Hugging Face**: Used for Embeddings and LLM Inference. Configured via `HUGGINGFACE_API_KEY`. This avoids hosting heavy models locally.

### How would you expand this chatbot to support more advanced features, such as real-time knowledge base updates or multi-user chat sessions?
*   **Real-time Updates**: Implement an endpoint to upload documents that immediately generates embeddings and upserts them to Pinecone.
*   **WebSockets**: Use **Django Channels** to support real-time, bi-directional communication for a smoother chat experience (streaming responses).
*   **Scalability**: Migrate from SQLite to **PostgreSQL** and use **Celery** with Redis for more robust, distributed background task processing.
