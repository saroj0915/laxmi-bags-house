import React from 'react';
import Hero from '../components/home/Hero';
import Features from '../components/home/Features';
import ProductShowcase from '../components/home/ProductShowcase';

const HomePage = () => {
  return (
    <div>
      <Hero />
      <Features />
      <ProductShowcase />
    </div>
  );
};

export default HomePage;