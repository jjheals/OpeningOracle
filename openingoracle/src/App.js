import logo from './logo.svg';
import './App.css';
import MessageBox from './MessageBox.js';
import React from 'react';
import ReactDOM from 'react-dom';
//import { ThemeProvider, createTheme } from '@mui/material/styles';
import axios from 'axios'; 

const theme = createTheme();
const baseURL = "https://jsonplaceholder.typicode.com/posts";


function App() {
  const [post, setPost] = React.useState(null);

  function createPost() {
    axios
      .post(baseURL, {
        title: "Hello World!",
        body: "This is a new post."
      })
      .then((response) => {
        setPost(response.data);
      });
  }
  
  if (!post) return "No post!"

  return (
    <div className="App">
      <header className="App-header">
        <p style={{color: "red"}}>OpeningOracle</p>
        <MessageBox id="InputBox" />
      </header>
     <h1>{post.title}</h1>
     <p>{post.body}</p>
     <button onClick={createPost}>Create Post</button>
   </div>
  );
}

ReactDOM.render(
  document.getElementById('root')
);

export default App;
