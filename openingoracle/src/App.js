import React from 'react';
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Header from './Header/Header'
import HomePage from './HomePage/HomePage';
import About from './About/About'
import NoPage from './NoPage/NoPage'

function App() {
  return (
    <BrowserRouter basename="/OpeningOracle">
      <Routes>
        <Route path="/" element={<Header />}>
          <Route index path ="/" element={<HomePage />} />
          <Route path="about" element={<About />} />
          <Route path="*" element={<NoPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
