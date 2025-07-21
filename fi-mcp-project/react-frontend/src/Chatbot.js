import React, { useState } from 'react';
import axios from 'axios';

function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    try {
      const res = await axios.post('/chatbot', { message: input });
      // Use the full chat history from backend
      setMessages(res.data.history || []);
    } catch (err) {
      setMessages((msgs) => [...msgs, { role: 'assistant', text: 'Sorry, there was an error.' }]);
    }
    setInput('');
    setLoading(false);
  };

  return (
    <div style={{ border: '1px solid #ccc', padding: 24, borderRadius: 12, maxWidth: 700, margin: '32px auto', background: '#fafbfc', boxShadow: '0 2px 8px #eee' }}>
      <h2 style={{ textAlign: 'center', color: '#1976d2' }}>💬 Financial Chatbot</h2>
      <div style={{ minHeight: 180, marginBottom: 16, maxHeight: 350, overflowY: 'auto', background: '#fff', borderRadius: 8, padding: 12, border: '1px solid #e0e0e0' }}>
        {messages.length === 0 && <div style={{ color: '#888', textAlign: 'center' }}>Ask me anything about your finances!</div>}
        {messages.map((msg, idx) => (
          <div key={idx} style={{
            display: 'flex',
            justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            margin: '8px 0'
          }}>
            <div style={{
              background: msg.role === 'user' ? '#e3f2fd' : '#e8f5e9',
              color: '#222',
              padding: '10px 16px',
              borderRadius: 16,
              maxWidth: '70%',
              boxShadow: '0 1px 3px #eee',
              fontSize: 16
            }}>
              {msg.text}
            </div>
          </div>
        ))}
        {loading && <div style={{ color: '#888', textAlign: 'left' }}>Bot is typing...</div>}
      </div>
      <form onSubmit={sendMessage} style={{ display: 'flex', gap: 10 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask about your finances..."
          style={{ flex: 1, padding: 12, borderRadius: 8, border: '1px solid #bdbdbd', fontSize: 16 }}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()} style={{ padding: '0 24px', borderRadius: 8, background: '#1976d2', color: '#fff', border: 'none', fontSize: 16 }}>
          Send
        </button>
      </form>
    </div>
  );
}

export default Chatbot; 