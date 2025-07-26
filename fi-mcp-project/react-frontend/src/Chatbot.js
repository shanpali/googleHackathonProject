import React, { useState } from 'react';
import axios from 'axios';

// Helper function to format AI response text
function formatResponse(text) {
  if (!text) return '';
  
  // Split into lines and process each line
  const lines = text.split('\n');
  const formattedLines = lines.map((line, index) => {
    line = line.trim();
    
    // Headers (### or **)
    if (line.startsWith('### ')) {
      return <h3 key={index} style={{ color: '#1976d2', fontSize: '18px', fontWeight: 700, margin: '16px 0 8px 0', borderBottom: '2px solid #e3f2fd', paddingBottom: '4px' }}>{line.substring(4)}</h3>;
    }
    if (line.startsWith('## ')) {
      return <h2 key={index} style={{ color: '#1565c0', fontSize: '20px', fontWeight: 800, margin: '20px 0 12px 0' }}>{line.substring(3)}</h2>;
    }
    if (line.startsWith('# ')) {
      return <h1 key={index} style={{ color: '#0d47a1', fontSize: '22px', fontWeight: 900, margin: '24px 0 16px 0' }}>{line.substring(2)}</h1>;
    }
    
    // Bold text (**text**)
    if (line.includes('**')) {
      const parts = line.split('**');
      const formattedParts = parts.map((part, partIndex) => {
        if (partIndex % 2 === 1) {
          return <strong key={partIndex} style={{ fontWeight: 700, color: '#1976d2' }}>{part}</strong>;
        }
        return part;
      });
      return <p key={index} style={{ margin: '8px 0', lineHeight: 1.6 }}>{formattedParts}</p>;
    }
    
    // Bullet points (* or -)
    if (line.startsWith('* ') || line.startsWith('- ')) {
      return <li key={index} style={{ margin: '4px 0', lineHeight: 1.5, paddingLeft: '8px' }}>{line.substring(2)}</li>;
    }
    
    // Numbered lists
    if (/^\d+\.\s/.test(line)) {
      return <li key={index} style={{ margin: '4px 0', lineHeight: 1.5, paddingLeft: '8px' }}>{line}</li>;
    }
    
    // Horizontal rule (---)
    if (line === '---') {
      return <hr key={index} style={{ border: 'none', borderTop: '2px solid #e3f2fd', margin: '16px 0' }} />;
    }
    
    // Regular paragraph
    if (line) {
      return <p key={index} style={{ margin: '8px 0', lineHeight: 1.6 }}>{line}</p>;
    }
    
    // Empty line
    return <br key={index} />;
  });
  
  // Group consecutive list items
  const groupedLines = [];
  let currentList = [];
  
  formattedLines.forEach((line, index) => {
    if (line.type === 'li') {
      currentList.push(line);
    } else {
      if (currentList.length > 0) {
        groupedLines.push(
          <ul key={`list-${index}`} style={{ margin: '8px 0', paddingLeft: '20px' }}>
            {currentList}
          </ul>
        );
        currentList = [];
      }
      groupedLines.push(line);
    }
  });
  
  // Handle any remaining list items
  if (currentList.length > 0) {
    groupedLines.push(
      <ul key="list-final" style={{ margin: '8px 0', paddingLeft: '20px' }}>
        {currentList}
      </ul>
    );
  }
  
  return groupedLines;
}

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastInput, setLastInput] = useState('');
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [loadingQuestions, setLoadingQuestions] = useState(false);

  // Load initial questions when component mounts
  React.useEffect(() => {
    loadInitialQuestions();
  }, []);

  const loadInitialQuestions = async () => {
    setLoadingQuestions(true);
    try {
      const res = await axios.post('/generate-questions', { 
        is_initial: true,
        context: ''
      }, { withCredentials: true });
      if (res.data && res.data.questions) {
        // Add questions as assistant messages
        const questionMessages = res.data.questions.map((question, index) => ({
          role: 'assistant',
          text: question,
          isQuestion: true,
          questionIndex: index
        }));
        setMessages(questionMessages);
      }
    } catch (err) {
      console.error('Failed to load initial questions:', err);
      // Set default questions if API fails
      const defaultQuestions = [
        "What if I increase my SIP by ₹5,000?",
        "What if I retire at 50?",
        "What if I invest ₹10,000 more in mutual funds?"
      ];
      const questionMessages = defaultQuestions.map((question, index) => ({
        role: 'assistant',
        text: question,
        isQuestion: true,
        questionIndex: index
      }));
      setMessages(questionMessages);
    }
    setLoadingQuestions(false);
  };

  const loadFollowUpQuestions = async (conversationContext) => {
    setLoadingQuestions(true);
    try {
      const res = await axios.post('/generate-questions', { 
        is_initial: false,
        context: conversationContext
      }, { withCredentials: true });
      if (res.data && res.data.questions) {
        // Add questions as assistant messages
        const questionMessages = res.data.questions.map((question, index) => ({
          role: 'assistant',
          text: question,
          isQuestion: true,
          questionIndex: index
        }));
        setMessages(prev => [...prev, ...questionMessages]);
      }
    } catch (err) {
      console.error('Failed to load follow-up questions:', err);
      // Set default follow-up questions if API fails
      const defaultQuestions = [
        "What if I increase my SIP by ₹3,000 more?",
        "What if I invest ₹5 lakhs in stocks?",
        "What if I retire at 45?"
      ];
      const questionMessages = defaultQuestions.map((question, index) => ({
        role: 'assistant',
        text: question,
        isQuestion: true,
        questionIndex: index
      }));
      setMessages(prev => [...prev, ...questionMessages]);
    }
    setLoadingQuestions(false);
  };

  const handleQuestionClick = (question) => {
    // Add user message
    setMessages(prev => [...prev, { role: 'user', text: question }]);
    // Send the question
    sendMessage(null, question);
  };

  const sendMessage = async (e, retryInput) => {
    if (e) e.preventDefault();
    const messageToSend = retryInput !== undefined ? retryInput : input;
    if (!messageToSend.trim()) return;
    setLoading(true);
    setError(null);
    setLastInput(messageToSend);
    try {
      const res = await axios.post('/chatbot', { message: messageToSend }, { withCredentials: true });
      if (res.data && res.data.history) {
        setMessages(res.data.history);
        
        // Load follow-up questions after response
        const recentMessages = res.data.history.slice(-4); // Last 4 messages for context
        const conversationContext = recentMessages.map(msg => `${msg.role}: ${msg.text}`).join('\n');
        loadFollowUpQuestions(conversationContext);
      } else if (res.data && res.data.error) {
        setError(res.data.error + (res.data.details ? ': ' + res.data.details : ''));
        setMessages((msgs) => [...msgs, { role: 'assistant', text: 'Sorry, there was an error.' }]);
      } else {
        setError('Unexpected response from server.');
      }
    } catch (err) {
      let msg = 'Sorry, there was an error connecting to the server.';
      if (err.response && err.response.data && err.response.data.error) {
        msg = err.response.data.error + (err.response.data.details ? ': ' + err.response.data.details : '');
      }
      setError(msg);
      setMessages((msgs) => [...msgs, { role: 'assistant', text: msg }]);
    }
    setInput('');
    setLoading(false);
  };

  const loadChatHistory = async () => {
    setLoadingHistory(true);
    setError(null);
    try {
      const res = await axios.get('/chat-history', { withCredentials: true });
      if (res.data && Array.isArray(res.data.history)) {
        setMessages(res.data.history);
      } else {
        setError('No chat history found.');
      }
    } catch (err) {
      let msg = 'Could not load chat history.';
      if (err.response && err.response.data && err.response.data.error) {
        msg = err.response.data.error;
      }
      setError(msg);
    }
    setLoadingHistory(false);
  };

  return (
    <div style={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      padding: '24px',
      background: 'linear-gradient(135deg, #e3f2fd 0%, #f5f7fa 100%)'
    }}>
      <div style={{ flexShrink: 0 }}>
        <h2 style={{ textAlign: 'center', color: '#1976d2', fontWeight: 800, letterSpacing: 1, marginBottom: 8 }}>💬 ArthaPandit - The financial expert</h2>
        <div style={{ color: '#1976d2', textAlign: 'center', marginBottom: 12, fontSize: 15, fontWeight: 500 }}>
          Try scenario simulation: <b>What if I increase my SIP by ₹5,000?</b> or <b>What if I retire at 50?</b>
        </div>
        <div style={{ textAlign: 'center', marginBottom: 16 }}>
          <button
            onClick={loadChatHistory}
            disabled={loadingHistory}
            style={{
              padding: '8px 16px',
              borderRadius: 8,
              background: loadingHistory ? '#bdbdbd' : '#4caf50',
              color: '#fff',
              border: 'none',
              fontSize: 14,
              fontWeight: 600,
              cursor: loadingHistory ? 'not-allowed' : 'pointer',
              transition: 'background 0.2s',
              boxShadow: '0 2px 4px rgba(76, 175, 80, 0.3)'
            }}
          >
            {loadingHistory ? 'Loading...' : '📚 Load Old Chat'}
          </button>
        </div>
      </div>
      
      <div style={{ 
        flex: 1, 
        background: '#fff', 
        borderRadius: 12, 
        padding: 16, 
        border: '1px solid #e0e0e0', 
        boxShadow: '0 2px 8px #e3f2fd',
        overflowY: 'auto',
        marginBottom: 16
      }}>
        {messages.length === 0 && <div style={{ color: '#888', textAlign: 'center' }}>Ask me anything about your finances!</div>}
        {messages.map((msg, idx) => (
          <div key={idx} style={{
            display: 'flex',
            justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            margin: '10px 0'
          }}>
            <div 
              style={{
                background: msg.role === 'user' ? 'linear-gradient(90deg, #bbdefb 0%, #e3f2fd 100%)' : 
                           msg.isQuestion ? 'linear-gradient(90deg, #f3e5f5 0%, #e8f5e8 100%)' : 'linear-gradient(90deg, #c8e6c9 0%, #f1f8e9 100%)',
                color: '#222',
                padding: msg.isQuestion ? '8px 12px' : '12px 18px',
                borderRadius: msg.isQuestion ? 8 : 18,
                maxWidth: '70%',
                boxShadow: '0 1px 6px #e3f2fd',
                fontSize: msg.isQuestion ? 14 : 16,
                fontWeight: msg.isQuestion ? 500 : 500,
                transition: 'background 0.3s',
                border: msg.role === 'assistant' && error ? '1.5px solid #e57373' : 
                       msg.isQuestion ? '1px solid #bbdefb' : 'none',
                cursor: msg.isQuestion ? 'pointer' : 'default'
              }}
              onClick={msg.isQuestion ? () => handleQuestionClick(msg.text) : undefined}
              onMouseOver={msg.isQuestion ? (e) => {
                e.target.style.background = 'linear-gradient(90deg, #bbdefb 0%, #e1bee7 100%)';
                e.target.style.transform = 'translateY(-1px)';
                e.target.style.boxShadow = '0 2px 6px rgba(25, 118, 210, 0.3)';
              } : undefined}
              onMouseOut={msg.isQuestion ? (e) => {
                e.target.style.background = 'linear-gradient(90deg, #f3e5f5 0%, #e8f5e8 100%)';
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 1px 6px #e3f2fd';
              } : undefined}
            >
              {msg.isQuestion ? (
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 8,
                  color: '#7b1fa2',
                  fontWeight: 600
                }}>
                  <span style={{ fontSize: 16 }}>💡</span>
                  {msg.text}
                </div>
              ) : (
                msg.role === 'assistant' ? formatResponse(msg.text) : msg.text
              )}
            </div>
          </div>
        ))}
        {loading && <div style={{ color: '#888', textAlign: 'left', fontStyle: 'italic' }}>Bot is typing...</div>}
        {loadingQuestions && (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'flex-start', 
            margin: '10px 0' 
          }}>
            <div style={{
              background: 'linear-gradient(90deg, #f3e5f5 0%, #e8f5e8 100%)',
              color: '#7b1fa2',
              padding: '12px 18px',
              borderRadius: 18,
              maxWidth: '70%',
              boxShadow: '0 1px 6px #e3f2fd',
              fontSize: 16,
              fontWeight: 500,
              border: '1px solid #bbdefb'
            }}>
              💭 Thinking of questions...
            </div>
          </div>
        )}
      </div>
      
      {/* Suggested Questions Section */}
      {/* This section is now integrated into the chat window */}
      
      <div style={{ flexShrink: 0 }}>
        {error && (
          <div style={{ color: '#d32f2f', background: '#fff3e0', border: '1px solid #ffccbc', borderRadius: 8, padding: 12, marginBottom: 12, textAlign: 'center', fontWeight: 600 }}>
            {error}
            {lastInput && (
              <button
                onClick={() => sendMessage(null, lastInput)}
                style={{ marginLeft: 16, padding: '4px 16px', borderRadius: 6, background: '#1976d2', color: '#fff', border: 'none', fontWeight: 600, cursor: 'pointer' }}
              >
                Retry
              </button>
            )}
          </div>
        )}
        <form onSubmit={sendMessage} style={{ display: 'flex', gap: 12 }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask about your finances..."
            style={{ flex: 1, padding: 14, borderRadius: 10, border: '1.5px solid #90caf9', fontSize: 17, background: '#f7fbff', fontWeight: 500 }}
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()} style={{ padding: '0 28px', borderRadius: 10, background: loading ? '#bdbdbd' : '#1976d2', color: '#fff', border: 'none', fontSize: 17, fontWeight: 700, boxShadow: '0 2px 8px #90caf9', cursor: loading ? 'not-allowed' : 'pointer', transition: 'background 0.2s' }}>
            {loading ? 'Sending...' : 'Send'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Chatbot; 