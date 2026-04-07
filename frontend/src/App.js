import React, { useState } from 'react';
import Header from './components/Header';
import DamMap from './components/DamMap';
import DamAnalysis from './components/DamAnalysis';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('map'); // 'map' or 'analysis'
  const [selectedDam, setSelectedDam] = useState(null);

  const handleSelectDam = (damName) => {
    setSelectedDam(damName);
    setCurrentPage('analysis');
  };

  const handleBackToMap = () => {
    setCurrentPage('map');
    setSelectedDam(null);
  };

  return (
    <div className="App">
      <Header />
      {currentPage === 'map' ? (
        <DamMap 
          onSelectDam={handleSelectDam}
          selectedDam={selectedDam}
        />
      ) : (
        <DamAnalysis 
          damName={selectedDam}
          onBack={handleBackToMap}
        />
      )}
    </div>
  );
}

export default App;
