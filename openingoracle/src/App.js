import logo from './logo.svg';
import './App.css';
import './MessageBox.css';
import MessageBox from './MessageBox.js'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <p>OpeningOracle</p>
        <MessageBox id = "InputBox"> </MessageBox>
        
      </header>
    </div>
  );
}

export default App;
