import React from 'react';

function App() {
  return (
    <div style={{ padding: '20px', backgroundColor: '#f0f0f0', minHeight: '100vh' }}>
      <h1 style={{ color: '#333' }}>MyHub Local - Test</h1>
      <p style={{ color: '#666' }}>If you can see this, React is working!</p>
      <div style={{ backgroundColor: 'white', padding: '10px', marginTop: '10px', border: '1px solid #ccc' }}>
        <p>This is a simple test component with inline styles.</p>
        <button style={{ padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px' }}>
          Test Button
        </button>
      </div>
    </div>
  );
}

export default App;
