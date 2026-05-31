import React from 'react';
import { Link } from 'react-router-dom';
import './Hero.css';

const Hero = () => {
  return (
    <section className="hero">
      <div className="hero-overlay"></div>
      <div className="hero-content">
        <h1>Premium Quality Bags for Every Journey</h1>
        <p>Backpacks | Travel Bags | School Bags | Purses</p>
        <Link to="/catalog" className="btn-primary">Shop Now →</Link>
      </div>
    </section>
  );
};

export default Hero;