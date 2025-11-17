import React from 'react';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ResourceManagementPage from './ResourceManagementPage';

function App() {
  return (
    <div>
      <Router>
        <Routes>
          <Route path="/resource-management" element={<ResourceManagementPage />} />
          {/* Optionally, make it the default route */}
          <Route path="/" element={<ResourceManagementPage />} />
        </Routes>
      </Router>
    </div>
  );
}

export default App;
