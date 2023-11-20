import logo from './logo.svg';
import './App.css';
import './MessageBox.css';
import MessageBox from './MessageBox.js';
import React from 'react';
import ReactDOM from 'react-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';

const theme = createTheme();

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <p style={{color: "red"}}>OpeningOracle</p>
        <MessageBox id="InputBox" />
      </header>
    </div>
  );
}

ReactDOM.render(
  <ThemeProvider theme={theme}>
    <App /> 
  </ThemeProvider>,
  document.getElementById('root')
);

export default App;
