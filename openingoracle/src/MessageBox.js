import { useState } from "react";
//import './MessageBox.css';
import TextField from '@mui/material/TextField';
//import {styled} from '@mui/material/styles';
import { styled } from '@mui/system';



//This changes the MessageBox. Color changes the text of the box label, not the input 
const StyledTextField = styled(TextField)({
    '& .MuiInputLabel-root': {
      color: 'red',
      position: 'absolute',
      top: 0,
      left: 0,
    }
  });
  


// function MessageBox() {
//     let [message, setMessage] = useState("Test message")

//     return (<StyledTextField label="Type Here" />)
// }

function MessageBox() {
    let [message, setMessage] = useState("Test message");
  
    return (
      <TextField
        label="Type Here"
        InputLabelProps={{
          sx: {
            color: 'red',
            position: 'absolute',
            top: 0,
            left: 0,
          },
        }}
      />
    );
  }
export default MessageBox;