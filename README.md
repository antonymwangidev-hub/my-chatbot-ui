🧠 RAG-Based AI Chatbot (Claude + Vector Search)
A production-ready Retrieval-Augmented Generation (RAG) chatbot that allows users to ask questions about custom documents (PDFs) and receive accurate, context-aware answers powered by Claude.
The system embeds documents into a vector store, retrieves the most relevant context at query time, and uses an LLM to generate grounded responses.
✨ Features
📄 PDF document ingestion
🔍 Semantic search with vector embeddings
🧠 Retrieval-Augmented Generation (RAG)
🤖 Claude API integration
💾 Persistent vector store
🗂️ Conversation memory
🌐 Web-based chat interface
🚀 Backend connected to live Render deployment
🏗️ Architecture
Text
Copy code
User Query
   ↓
Vector Store (Similarity Search)
   ↓
Relevant Context Chunks
   ↓
Claude LLM
   ↓
Final Answer
🛠️ Tech Stack
Backend
Python
Claude (Anthropic API)
Vector embeddings
RAG pipeline
Frontend
HTML
JavaScript
Infrastructure
Render (backend hosting)
📁 Project Structure
Text
Copy code
.
├── main.py                # Application entry point
├── config.py              # Configuration & environment variables
├── index.html             # Chat UI
│
├── document_loader.py     # PDF loading and text chunking
├── vector_store.py        # Embedding and similarity search
├── rag_engine.py          # Core RAG logic
│
├── model.py               # LLM wrapper
├── claude_client.py       # Claude API client
├── memory.py              # Conversation memory
│
├── start_chatbot.sh       # Startup script
├── My-CV.pdf              # Sample document
└── README.md
🚀 Getting Started
1. Prerequisites
Python 3.9+
Claude API key (Anthropic)
2. Clone the Repository
Bash
Copy code
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
3. Install Dependencies
Bash
Copy code
pip install -r requirements.txt
4. Environment Variables
Create a .env file:
Env
Copy code
CLAUDE_API_KEY=your_api_key_here
5. Run the Application
Bash
Copy code
python main.py
Then open index.html in your browser.
🧪 Example Use Cases
Resume / CV Q&A
Document-based chatbot
Internal knowledge assistant
Research and study assistant
Personal AI assistant with memory
🧠 How It Works
Documents are loaded and split into chunks
Chunks are embedded and stored in a vector database
User queries are embedded
Most relevant chunks are retrieved
Claude generates an answer using retrieved context
This approach reduces hallucinations and improves factual accuracy.
📌 Roadmap
[ ] Streaming responses
[ ] Multiple document uploads
[ ] Vector store persistence (FAISS / Chroma)
[ ] Authentication
[ ] Improved UI
[ ] Docker support
🔐 Security Notes
API keys are stored in environment variables
Never commit .env files
Add rate limiting for public deployment
📄 License
MIT License
⭐ Project Highlights
This project demonstrates:
Real-world RAG implementation
LLM integration with Claude
Semantic search
Backend deployment
Modular, readable codebase
Ideal for portfolio, startup prototypes, or production foundations.
