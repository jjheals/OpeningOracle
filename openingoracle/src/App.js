import './App.css';
import Header from './Header';
import React from 'react';
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
      <Header/>
      <header className="App-header">
        <p id="Heading"> OpeningOracle</p>

        <form id="Input" method="post" onSubmit={clickSubmitButton}>
          <p> How do you like to play chess? <br></br> Describe your playing style below <br></br> and enter to find a opening for you!</p>
          <label>
            Type here: <input name="userInput" defaultValue="" />
          </label>
          <button type="submit"> Find my opening! </button>
        </form>
      </header>
      <div id='Response'>
        <p>Based on your response, <br></br> you should play: </p>
        {responseBody != null ? <p>{responseBody}</p> : <p></p>}
      </div>
    </div>

  );
}

/* ReactDOM.render(
  document.getElementById('root')
); */

export default App;
