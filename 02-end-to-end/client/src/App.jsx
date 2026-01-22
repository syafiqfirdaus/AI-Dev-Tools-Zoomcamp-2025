import React, { useState, useEffect, useRef } from 'react';
import Editor from '@monaco-editor/react';
import io from 'socket.io-client';

import { loadPyodide } from 'pyodide';

const socket = io('http://localhost:3001');

function App() {
  const [code, setCode] = useState('// Start coding here...');
  const [language, setLanguage] = useState('javascript');
  const [output, setOutput] = useState('');
  const [pyodide, setPyodide] = useState(null);
  const isRemoteUpdate = useRef(false);

  useEffect(() => {
    socket.on('code-update', (newCode) => {
      isRemoteUpdate.current = true;
      setCode(newCode);
    });

    async function initPyodide() {
      try {
        const pyodideInstance = await loadPyodide({
          indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.1/full/"
        });
        setPyodide(pyodideInstance);
      } catch (e) {
        console.error("Error loading pyodide:", e);
      }
    }
    initPyodide();

    return () => {
      socket.off('code-update');
    };
  }, []);

  const handleEditorChange = (value) => {
    if (isRemoteUpdate.current) {
      isRemoteUpdate.current = false;
      return;
    }
    setCode(value);
    socket.emit('code-update', value);
  };

  const runCode = async () => {
    setOutput('');
    if (language === 'python') {
      if (!pyodide) {
        setOutput('Pyodide is loading...');
        return;
      }
      try {
        pyodide.setStdout({ batched: (msg) => setOutput((prev) => prev + msg + '\n') });
        await pyodide.runPythonAsync(code);
      } catch (error) {
        setOutput(error.toString());
      }
    } else if (language === 'javascript') {
      try {
        const logs = [];
        const originalLog = console.log;
        console.log = (...args) => logs.push(args.join(' '));
        // eslint-disable-next-line no-eval
        eval(code);
        console.log = originalLog;
        setOutput(logs.join('\n'));
      } catch (error) {
        setOutput(error.toString());
      }
    }
  };

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '10px', background: '#333', color: '#fff', display: 'flex', alignItems: 'center' }}>
        <select value={language} onChange={(e) => setLanguage(e.target.value)} style={{ marginRight: '10px' }}>
          <option value="javascript">JavaScript</option>
          <option value="python">Python</option>
        </select>
        <span style={{ flexGrow: 1 }}>Collaborative Editor</span>
        <button onClick={runCode} style={{ padding: '5px 10px', cursor: 'pointer' }}>Run Code</button>
      </div>
      <div style={{ display: 'flex', flexGrow: 1 }}>
        <Editor
          height="100%"
          width="50%"
          defaultLanguage="javascript"
          language={language}
          value={code}
          onChange={handleEditorChange}
          theme="vs-dark"
        />
        <div style={{ width: '50%', background: '#1e1e1e', color: '#fff', padding: '10px', borderLeft: '1px solid #333', whiteSpace: 'pre-wrap', overflow: 'auto' }}>
          <h3>Output:</h3>
          {output}
        </div>
      </div>
    </div>
  );
}

export default App;
