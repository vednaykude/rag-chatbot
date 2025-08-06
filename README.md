# 🤖 RAG Chatbot

A complete Retrieval-Augmented Generation (RAG) chatbot system that lets you ask questions about AI, Machine Learning, and Computer Science topics. The system uses Wikipedia articles as its knowledge base and runs entirely locally for privacy.

![RAG Chatbot Demo](https://img.shields.io/badge/Status-Active-brightgreen) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![React](https://img.shields.io/badge/React-18+-61dafb) ![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688)

## 🌟 Features

- **🔒 Privacy-First**: Runs completely locally with Llama3 via Ollama
- **🧠 Intelligent Retrieval**: Uses ChromaDB for semantic search across knowledge base
- **📚 Rich Knowledge Base**: Automatically fetches Wikipedia articles on AI/ML topics
- **💬 Modern Chat Interface**: Beautiful React frontend with real-time status indicators
- **📖 Source Citations**: Every answer includes citations from source documents
- **🚀 Easy Setup**: Multiple deployment options including Docker
- **📱 Responsive Design**: Works great on desktop and mobile devices
- **⚡ Fast Responses**: Optimized retrieval and generation pipeline

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────┐
│   React Frontend │────│  FastAPI Backend │────│  ChromaDB      │
│   (Port 5173)   │    │   (Port 8000)    │    │  Vector Store  │
└─────────────────┘    └──────────────────┘    └────────────────┘
                                │
                                │
                       ┌────────────────┐
                       │  Ollama+Llama3 │
                       │  (Port 11434)  │
                       └────────────────┘
```

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

1. **Clone or download** all the project files
2. **Make the start script executable**:
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

The script will automatically:
- Check and install Ollama if needed
- Pull the Llama3 model
- Set up Python virtual environment
- Install all dependencies
- Start all services

### Option 2: Manual Setup

#### Prerequisites
- **Python 3.8+**
- **Node.js 16+** and npm
- **Ollama** ([Installation Guide](https://ollama.ai/download))

#### 1. Install Ollama and Llama3
```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# For Windows, download from https://ollama.ai/download

# Pull Llama3 model
ollama pull llama3

# Start Ollama server
ollama serve
```

#### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
python main.py
```

#### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### 4. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000

### Option 3: Docker Setup

```bash
# Start all services with Docker Compose
docker-compose up --build

# Pull Llama3 model in the container (run once)
docker-compose exec ollama ollama pull llama3
```

## 📁 Project Structure

```
rag-chatbot/
├── README.md
├── docker-compose.yml
├── start.sh
├── backend/
│   ├── main.py                 # FastAPI backend server
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Backend Docker config
│   └── chroma_db/             # Vector database (auto-created)
└── frontend/
    ├── src/
    │   ├── App.jsx            # Main React component
    │   ├── main.jsx           # React entry point
    │   └── styles.css         # Application styles
    ├── index.html             # HTML template
    ├── package.json           # Node.js dependencies
    ├── vite.config.js         # Vite configuration
    └── Dockerfile             # Frontend Docker config
```

## 💡 Usage

1. **Start the application** using one of the setup methods above
2. **Open your browser** to http://localhost:5173
3. **Check the status indicators** at the top:
   - 🟢 API: healthy
   - 📚 Documents: number loaded
   - 🤖 Ollama: Connected
4. **Ask questions** about AI, ML, or Computer Science topics

### Example Questions
- "What is machine learning?"
- "How do neural networks work?"
- "Explain deep learning and its applications"
- "What are transformer models?"
- "How does computer vision work?"
- "What is natural language processing?"

## 🔧 Configuration

### Adding More Topics
Edit the `topics` list in `backend/main.py`:

```python
topics = [
    "Artificial Intelligence",
    "Machine Learning",
    "Your Custom Topic",
    # Add more topics here
]
```

### Changing the LLM
Replace Ollama calls in `generate_answer()` function with any other LLM API:

```python
# Example: OpenAI integration
import openai

def generate_answer(question: str, context_docs: List[dict]) -> str:
    # Your custom LLM integration here
    pass
```

### UI Customization
Modify `frontend/src/styles.css` to change:
- Color schemes
- Layout
- Animations
- Responsive breakpoints

### Database Settings
Adjust retrieval parameters in `backend/main.py`:

```python
# Number of documents to retrieve
top_k = 5

# Chunk size for documents
chunk_size = 500

# Overlap between chunks
overlap = 50
```

## 🐛 Troubleshooting

### Backend Issues

**"Ollama connection failed"**
```bash
# Check if Ollama is running
ollama list

# Start Ollama server
ollama serve

# Pull Llama3 model
ollama pull llama3
```

**"No articles fetched"**
- Check internet connection
- Wikipedia API might be temporarily unavailable
- The system will use fallback content

**"ChromaDB errors"**
```bash
# Reset the database
rm -rf backend/chroma_db/
# Restart the backend
```

### Frontend Issues

**"Failed to fetch" errors**
- Ensure backend is running on http://localhost:8000
- Check browser console for detailed errors
- Verify CORS settings

**Port conflicts**
```bash
# Find what's using the port
lsof -i :8000  # or :5173

# Kill the process
kill -9 <PID>
```

### Performance Issues

**Slow responses**
- Reduce `chunk_size` for faster processing
- Decrease `top_k` for fewer retrieved documents
- Consider using a lighter embedding model

**High memory usage**
- Reduce the number of topics
- Use smaller chunk sizes
- Consider using quantized models

## 🔒 Security Considerations

### For Production Use
- Add authentication and authorization
- Implement rate limiting
- Use HTTPS
- Validate and sanitize all inputs
- Set specific CORS origins
- Use environment variables for sensitive config

### Privacy
- All data processing happens locally
- No data is sent to external APIs (except Wikipedia for initial fetch)
- Conversations are not stored permanently

## 📦 Deployment

### Production Backend
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Production Frontend
```bash
# Build for production
npm run build

# Serve with nginx or any static file server
# Built files will be in the 'dist' directory
```

### Cloud Deployment
- **Backend**: Deploy to AWS ECS, Google Cloud Run, or Heroku
- **Frontend**: Deploy to Vercel, Netlify, or AWS S3 + CloudFront
- **Database**: Use managed ChromaDB or migrate to Pinecone/Weaviate

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add some amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
# Backend development
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend development
cd frontend
npm run dev
```

## 📊 API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API status |
| GET | `/health` | Detailed health check |
| GET | `/debug` | Debug information |
| GET | `/test` | Simple test endpoint |
| POST | `/chat` | Main chat endpoint |
| GET | `/documents/count` | Number of documents |

### Chat Request Format
```json
{
  "question": "What is machine learning?",
  "top_k": 3
}
```

### Chat Response Format
```json
{
  "answer": "Machine learning is...",
  "sources": [
    "Machine Learning (https://en.wikipedia.org/wiki/Machine_learning)"
  ]
}
```

## 🔗 Dependencies

### Backend
- **FastAPI**: Modern web framework
- **ChromaDB**: Vector database
- **Sentence Transformers**: Text embeddings
- **Ollama**: Local LLM interface
- **Uvicorn**: ASGI server

### Frontend
- **React**: UI framework
- **Vite**: Build tool
- **Modern CSS**: Glassmorphism design

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Ollama Team** for local LLM infrastructure
- **ChromaDB** for vector database
- **Hugging Face** for sentence transformers
- **Wikipedia** for the knowledge base
- **FastAPI** and **React** communities

## 📞 Support

- **Issues**: Create an issue on GitHub
- **Questions**: Start a discussion
- **Documentation**: Check the setup guide artifacts

## 🔄 Version History

- **v1.0.0**: Initial release with basic RAG functionality
- **Current**: Enhanced error handling, Docker support, improved UI

---

**Built with ❤️ for the AI community**

*Happy chatting with your local RAG assistant! 🤖*
