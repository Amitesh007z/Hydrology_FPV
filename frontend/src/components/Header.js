import React from 'react';
import '../styles/Header.css';

function Header() {
  return (
    <div className="header-container">
      <div className="header-content">
        <img 
          src="https://upload.wikimedia.org/wikipedia/en/thumb/4/4f/National_Institute_of_Technology%2C_Tiruchirappalli.svg/1280px-National_Institute_of_Technology%2C_Tiruchirappalli.svg.png"
          alt="NIT Trichy Logo" 
          className="nit-logo"
        />
        <div className="header-text">
          <h1>FPV Nexus</h1>
          <p className="attribution">
            A Project by <strong>Dr. S. Saravanan</strong> & Students
            <br />
            <span className="institute">National Institute of Technology Trichy</span>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Header;
