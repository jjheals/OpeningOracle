import { useState } from "react";
import './MessageBox.css';
import TextField from '@mui/material/TextField';
import {styled} from '@mui/material/styles';


const StyledTextField = styled(TextField)({
"& label": {
    color: "white"
}
})


function MessageBox() {
    let [message, setMessage] = useState("Test message")

    return (<StyledTextField label="Type Here" />)
}

export default MessageBox;