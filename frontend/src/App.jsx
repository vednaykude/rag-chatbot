// App.jsx
import { useState, useEffect } from 'react'
import './styles.css'

function App() {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [apiStatus, setApiStatus] = useState(null)
  const [documentCount, setDocumentCount] = useState(0)

  // Check API health on component mount
  useEffect(() => {
    checkApiHealth()
    getDocumentCount()
  }, [])

  const checkApiHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/health')
      const data = await response.json()
      setApiStatus(data)
    } catch (error) {
      setApiStatus({ status: 'error', error: error.message })
    }
  }

  const getDocumentCount = async () => {
    try {
      const response = await fetch('http://localhost:8000/documents/count')
      const data = await response.json()
      setDocumentCount(data.count)
    } catch (error) {
      console.error('Error fetching document count:', error)
    }
  }

  const sendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: inputMessage,
          top_k: 3
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.answer,
        sources: data.sources,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: `Error: ${error.message}. Please make sure the backend server is running on http://localhost:8000`,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => {
    setMessages([])
  }

  const formatTimestamp = (timestamp) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1 className="title">RAG Chatbot</h1>
          <p className="subtitle">Ask questions about AI, ML, and Computer Science topics</p>
          
          <div className="status-bar">
            <div className={`status-indicator ${apiStatus?.status === 'healthy' ? 'healthy' : 'error'}`}>
              API: {apiStatus?.status || 'checking...'}
            </div>
            <div className="document-count">
              Documents: {documentCount}
            </div>
            <div className={`ollama-status ${apiStatus?.ollama_available ? 'healthy' : 'error'}`}>
              Ollama: {apiStatus?.ollama_available ? 'Connected' : 'Disconnected'}
            </div>
          </div>
        </div>
      </header>

      <div className="chat-container">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <h2>Welcome to the RAG Chatbot!</h2>
              <p>Ask me questions about:</p>
              <ul>
                <li>Artificial Intelligence</li>
                <li>Machine Learning</li>
                <li>Deep Learning</li>
                <li>Natural Language Processing</li>
                <li>Computer Vision</li>
                <li>Python Programming</li>
                <li>Data Science</li>
              </ul>
              <p className="example-questions">
                <strong>Example questions:</strong><br/>
                "What is machine learning?"<br/>
                "How do neural networks work?"<br/>
                "What are transformers in AI?"
              </p>
            </div>
          )}

          {messages.map((message) => (
            <div key={message.id} className={`message ${message.type}`}>
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                {message.sources && message.sources.length > 0 && (
                  <div className="sources">
                    <strong>Sources:</strong>
                    <ul>
                      {message.sources.map((source, index) => (
                        <li key={index}>{source}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className="timestamp">{formatTimestamp(message.timestamp)}</div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="message bot">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="input-container">
          <div className="input-wrapper">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about AI, ML, or Computer Science..."
              className="message-input"
              rows="3"
              disabled={isLoading}
            />
            <div className="input-actions">
              <button 
                onClick={clearChat}
                className="clear-button"
                disabled={messages.length === 0}
              >
                Clear Chat
              </button>
              <button 
                onClick={sendMessage}
                className="send-button"
                disabled={isLoading || !inputMessage.trim()}
              >
                {isLoading ? 'Sending...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App