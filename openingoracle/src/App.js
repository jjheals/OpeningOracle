import logo from './logo.svg';
import './App.css';
import MessageBox from './MessageBox.js';
import React from 'react';
import ReactDOM from 'react-dom';
//import { ThemeProvider, createTheme } from '@mui/material/styles';
import axios from 'axios'; 

//const theme = createTheme();
const baseURL = "http://localhost:8080";

function App() {
  const [userMessage, setUserMessage] = React.useState(null);
  const [responseBody, setResponseBody] = React.useState(null);

  function clickSubmitButton(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const userMessage = Object.fromEntries(formData.entries()).userInput;

    setResponseBody("...");

    axios
      .post(baseURL + "/postRequestOpening", {
        message: userMessage
      })
      .then((response) => {
        console.log(response.data.message)
        setResponseBody(response.data.message);
    });
  }
  
  return (
    <div className="App">
      <header className="App-header">
        <p style={{color: "red"}}>OpeningOracle</p>
        
        <form method="post" onSubmit={clickSubmitButton}>
          <label>
            Type here: <input name="userInput" defaultValue="" />
          </label>
          <button type="submit">Send Message</button>
        </form>

        { responseBody != null ? <p>{responseBody}</p> : <p></p> }
      </header>
   </div>
  );
}

/* ReactDOM.render(
  document.getElementById('root')
); */

export default App;
