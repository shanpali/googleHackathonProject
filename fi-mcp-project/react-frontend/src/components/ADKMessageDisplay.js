import React from 'react';

const ADKMessageDisplay = ({ message }) => {
  const hasADKData = message.analysis_type && message.analysis_type !== 'general';
  
  const getAnalysisTypeColor = (type) => {
    const colors = {
      'portfolio_analysis': '#1976d2',
      'tax_planning': '#388e3c',
      'investment_advice': '#f57c00',
      'risk_assessment': '#d32f2f',
      'goal_planning': '#7b1fa2',
      'scenario_modeling': '#1565c0',
      'general': '#757575'
    };
    return colors[type] || '#757575';
  };

  const getAnalysisTypeIcon = (type) => {
    const icons = {
      'portfolio_analysis': '📊',
      'tax_planning': '💰',
      'investment_advice': '📈',
      'risk_assessment': '⚠️',
      'goal_planning': '🎯',
      'scenario_modeling': '🔮',
      'general': '💬'
    };
    return icons[type] || '💬';
  };

  const formatConfidence = (confidence) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#4caf50';
    if (confidence >= 0.6) return '#ff9800';
    return '#f44336';
  };

  return (
    <div style={{ marginBottom: '16px' }}>
      {/* ADK Agent Analysis Header */}
      {hasADKData && (
        <div style={{
          background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
          border: `2px solid ${getAnalysisTypeColor(message.analysis_type)}`,
          borderRadius: '8px',
          padding: '12px',
          marginBottom: '12px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '20px' }}>{getAnalysisTypeIcon(message.analysis_type)}</span>
              <span style={{ 
                fontWeight: 700, 
                color: getAnalysisTypeColor(message.analysis_type),
                textTransform: 'capitalize'
              }}>
                {message.analysis_type.replace('_', ' ')} Analysis
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '12px', color: '#666' }}>Confidence:</span>
              <span style={{ 
                fontWeight: 600, 
                color: getConfidenceColor(message.confidence),
                fontSize: '14px'
              }}>
                {formatConfidence(message.confidence)}
              </span>
            </div>
          </div>
          
          {/* ADK Agent Capabilities */}
          <div style={{ 
            fontSize: '12px', 
            color: '#666',
            fontStyle: 'italic'
          }}>
            Powered by ADK Financial Advisor Agent - Advanced AI Analysis
          </div>
        </div>
      )}

      {/* Main Message Content */}
      <div style={{
        background: '#fff',
        borderRadius: '12px',
        padding: '16px',
        border: '1px solid #e0e0e0',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        position: 'relative'
      }}>
        {/* Message Text */}
        <div style={{ marginBottom: hasADKData ? '16px' : '0' }}>
          {formatResponse(message.text)}
        </div>

        {/* ADK Recommendations */}
        {hasADKData && message.recommendations && message.recommendations.length > 0 && (
          <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #e0e0e0' }}>
            <h4 style={{ 
              color: '#1976d2', 
              marginBottom: '12px', 
              fontSize: '16px',
              fontWeight: 600
            }}>
              💡 Key Recommendations
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {message.recommendations.map((rec, index) => (
                <div key={index} style={{
                  background: '#f8f9fa',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  borderLeft: `3px solid ${getAnalysisTypeColor(message.analysis_type)}`
                }}>
                  <div style={{ fontWeight: 600, color: '#333', marginBottom: '4px' }}>
                    {rec}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ADK Insights */}
        {hasADKData && message.insights && message.insights.length > 0 && (
          <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #e0e0e0' }}>
            <h4 style={{ 
              color: '#388e3c', 
              marginBottom: '12px', 
              fontSize: '16px',
              fontWeight: 600
            }}>
              🔍 Key Insights
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {message.insights.map((insight, index) => (
                <div key={index} style={{
                  background: '#f1f8e9',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  borderLeft: '3px solid #388e3c'
                }}>
                  <div style={{ fontWeight: 500, color: '#2e7d32' }}>
                    {insight}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper function to format response text (reused from Chatbot.js)
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

export default ADKMessageDisplay; 