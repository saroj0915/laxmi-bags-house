import React from 'react';
import { FaShippingFast, FaExchangeAlt, FaQrcode, FaStore } from 'react-icons/fa';
import './Features.css';

const features = [
  { icon: <FaShippingFast />, title: 'Free Shipping', desc: 'On orders over NPR 2000' },
  { icon: <FaExchangeAlt />, title: '7-Day Exchange', desc: 'Hassle-free returns' },
  { icon: <FaQrcode />, title: 'QR Payment', desc: 'eSewa, Khalti, Cash' },
  { icon: <FaStore />, title: 'Multiple Branches', desc: 'Across Nepal' },
];

const Features = () => {
  return (
    <section className="features">
      <div className="container">
        <div className="features-grid">
          {features.map((feature, index) => (
            <div className="feature-card" key={index}>
              <div className="feature-icon">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;