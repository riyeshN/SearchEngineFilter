import { useState} from 'react'
import React from 'react'
import './App.css'
import { Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import GetUrls from './components/GetUrls'
import ScrapeUrls from './components/ScrapeUrls'

function App() {

  return (
    <>
      <Header />
      <Routes>
        <Route path="/" element={<GetUrls />} />
        <Route path="/ScrapeUrls" element={<ScrapeUrls />} />
      </Routes>
    </>
  )
}

export default App
