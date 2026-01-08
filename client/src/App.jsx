import { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { dracula } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './App.css';

function App() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [ingesting, setIngesting] = useState(false); // State for the new button
  const [logs, setLogs] = useState([]);

  // --- NEW: Handle Ingest Click ---
  const handleIngest = async () => {
    setIngesting(true);
    setLogs(prev => [...prev, "🔄 Updating Knowledge Base..."]);
    try {
      await axios.post('http://localhost:8000/ingest');
      setLogs(prev => [...prev, "✅ Memory Updated! Agent is smarter now."]);
    } catch (error) {
      console.error(error);
      setLogs(prev => [...prev, "❌ Update Failed."]);
    }
    setIngesting(false);
  };

  const handleSubmit = async () => {
    if (!input) return;
    
    setLoading(true);
    setResponse(null);
    setLogs(["🚀 Connecting to Agent...", "🔍 Scanning Vector Database (Qdrant)..."]);

    try {
      const res = await axios.post('http://localhost:8000/debug', {
        error_message: input
      });

      setLogs(prev => [...prev, "🧠 Agent analyzing logic...", "✅ Solution Verified."]);
      setResponse(res.data);
    } catch (error) {
      console.error(error);
      setLogs(prev => [...prev, "❌ Error connecting to server."]);
    }
    setLoading(false);
  };

  return (
    <div className="app-container">
      <header className="header">
        <div className="header-content">
          <div>
            <h1>🐞 Agentic RAG Debugger</h1>
            <p>Powered by LangGraph, Qdrant & Qwen 2.5</p>
          </div>
          
          {/* THE NEW BUTTON */}
          <button 
            onClick={handleIngest} 
            disabled={ingesting || loading} 
            className="ingest-btn"
          >
            {ingesting ? 'Updating...' : '🔄 Update Memory'}
          </button>
        </div>
      </header>

      <div className="main-content">
        <div className="input-section">
          <h3>Paste Error Log / Code</h3>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Example: AttributeError: 'dict' object has no attribute 'price'..."
          />
          <button onClick={handleSubmit} disabled={loading} className="debug-btn">
            {loading ? 'Debugging...' : 'Start Agent'}
          </button>

          <div className="logs-area">
            {logs.map((log, index) => (
              <div key={index} className="log-item">
                <span className="dot"></span> {log}
              </div>
            ))}
          </div>
        </div>

        <div className="output-section">
          <h3>Agent Solution</h3>
          {loading && <div className="skeleton-loader">Thinking...</div>}
          
          {response && (
            <div className="solution-box">
              <div className="stats-badge">
                🔁 Self-Correction Loops: {response.iterations}
              </div>
              <div className="markdown-content">
                <ReactMarkdown
                  children={response.fix}
                  components={{
                    code({node, inline, className, children, ...props}) {
                      const match = /language-(\w+)/.exec(className || '')
                      return !inline && match ? (
                        <SyntaxHighlighter
                          style={dracula}
                          language={match[1]}
                          PreTag="div"
                          {...props}
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      ) : (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      )
                    }
                  }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;