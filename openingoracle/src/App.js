import './App.css';

import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import HeaderTest from './HeaderTest'
import HomePage from './HomePage';
import About from './About'
import NoPage from './NoPage'

import React from 'react';

function App() {
  return (
    <BrowserRouter>
      <Routes>
          <Route path="/" element={<HeaderTest />}>
          <Route index element={<HomePage />} />
          <Route path="about" element={<About />} />
          <Route path="*" element={<NoPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);

export default App;
