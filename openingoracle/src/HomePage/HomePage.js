import "./HomePage.css"
import React from 'react';
import axios from 'axios';

import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import { createTheme, ThemeProvider } from '@mui/material/styles';

import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';


//const baseURL = "http://localhost:8080";
const baseURL = "https://openingoracle.justinhealey.repl.co";

function HomePage() {
  const [responseCaption, setResponseCaption] = React.useState(null);
  const [responseBody, setResponseBody] = React.useState(null);

  const [oracleResponses, setOracleResponses] = React.useState(null);
  const [userColor, setColor] = React.useState('White');

  const handleColorChange = (event) => {
    setColor(event.target.value);
  };

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

    setResponseCaption("The Oracle is thinking...");
    setResponseBody(null);
    setOracleResponses(null);

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
            <p className="center"> How do <b>you</b> like to play chess? Describe your playing style below and let the Oracle find a opening for you!</p>
            <label>
              <TextField sx={{ minWidth: 1000 }} id="outlined-basic" label="Type your playstyle!" multiline variant="filled" name="userInput" defaultValue="" />
            </label>
            <div>
              <br />
              <p className="center">Which color do you want to play?</p>
              <FormControl variant="filled">
                <InputLabel id="demo-simple-select-label" label="Pick your color!">Pick your color!</InputLabel>
                <Select sx={{ minWidth: 1000 }}
                  labelId="demo-simple-select-label"
                  id="demo-simple-select" 
                  defaultValue={userColor}
                  value={userColor}
                  label="Color"
                  onChange={handleColorChange}
                >
                  <MenuItem value="White">White</MenuItem>
                  <MenuItem value="Black">Black</MenuItem>
                </Select>
              </FormControl>
            </div>

            <br />
            <Button variant="contained" color="chessBrown" type="submit"> Find my opening! </Button>
          </form>
        </div>
        <div id='Response'>
          {responseCaption != null ? <p><b>{responseCaption}</b></p> : <p></p>}
          {responseBody != null && oracleResponses != null ?
            <>
              <p>{responseBody}</p>
              <br></br>
              <p><b>Looking for something different? The Oracle also thinks...</b></p>
              <div>
                {
                  oracleResponses.map((m, i) => {
                    return <p key={i}>{m}</p>;
                  })
                }
              </div>
            </>
            : <p></p>}
        </div>
      </div>
    </ThemeProvider>
  );
}

export default HomePage;