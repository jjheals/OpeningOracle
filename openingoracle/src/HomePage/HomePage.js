import "./HomePage.css"
import React from 'react';
import axios from 'axios';

import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import { createTheme, ThemeProvider } from '@mui/material/styles';

//const baseURL = "http://localhost:8080";
const baseURL = "https://openingoracle.justinhealey.repl.co";

function HomePage() {
  const [responseCaption, setResponseCaption] = React.useState(null);
  const [responseBody, setResponseBody] = React.useState(null);

  const[oracleResponses, setOracleResponses] = React.useState(null);

  let theme = createTheme({
  
  });
  theme = createTheme(theme, {
    palette: {
      chessBrown: theme.palette.augmentColor({
        color: {
          main: '#806944',
        },
        name: 'chessBrown',
      }),
    },
  });

  function clickSubmitButton(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const userMessage = Object.fromEntries(formData.entries()).userInput;
    const userColor = "white";

    setResponseCaption("The Oracle is thinking...");
    setResponseBody(null);

    axios
      .post(baseURL + "/postRequestOpening", {
        message: userMessage,
        color: userColor
      })
      .then((response) => {
        console.log(response.data)
        setOracleResponses(response.data.messages.slice(1));
        setResponseCaption("Based on your response, the Oracle thinks: ");
        setResponseBody(response.data.messages[0]);
      });
  }

    return (
    <ThemeProvider theme={theme}>
      <div className="App">
        <div id='Prompt'>
          <form id="Input" method="post" onSubmit={clickSubmitButton}>
              <p> How do <b>you</b> like to play chess? Describe your playing style below and enter to find a opening for you!</p>
              <label>
                <TextField id="outlined-basic" label="Type your playstyle!" multiline fullWidth variant="filled" name="userInput" defaultValue="" />
              </label>
              <Button variant="contained" color="chessBrown" type="submit"> Find my opening! </Button>
            </form>
        </div>
        <div id='Response'>
          {responseCaption != null ? <p><b>{responseCaption}</b></p> : <p></p>}
          {responseBody != null && oracleResponses != null ?
            <>
              <p>{responseBody}</p>
              <br></br>
              <p><b>Alternatively, the Oracle also thinks...</b></p>
              <p>
                  {
                    oracleResponses.map((m) => {
                     return <p>{m}</p>;
                    })
                }
              </p>
            </>
            : <p></p>}
        </div>
      </div>
    </ThemeProvider>
    );
}

export default HomePage;