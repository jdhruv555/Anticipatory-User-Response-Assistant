import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import CallView from './components/CallView';
import CustomerProfile from './components/CustomerProfile';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App min-h-screen bg-gray-100">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/call/:callId" element={<CallView />} />
          <Route path="/customer/:customerId" element={<CustomerProfile />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

