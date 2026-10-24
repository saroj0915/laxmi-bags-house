import React from 'react';
import { FaFacebook, FaInstagram, FaWhatsapp, FaEnvelope, FaPhone, FaMapMarkerAlt } from 'react-icons/fa';
import './Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-content">
          <div className="footer-section">
            <h3>Laxmi Bags House</h3>
            <p>Premium quality bags since 1995. Your trusted partner for backpacks, travel bags, and more.</p>
          </div>
          
          <div className="footer-section">
            <h4>Quick Links</h4>
            <ul>
              <li><a href="/catalog">All Products</a></li>
              <li><a href="/catalog?category=backpack">Backpacks</a></li>
              <li><a href="/catalog?category=travel">Travel Bags</a></li>
              <li><a href="/catalog?category=school">School Bags</a></li>
            </ul>
          </div>
          
          <div className="footer-section">
            <h4>Contact Info</h4>
            <p><FaMapMarkerAlt /> Kathmandu, Nepal</p>
            <p><FaPhone /> +977-9800000000</p>
            <p><FaEnvelope /> info@laxmibags.com</p>
          </div>
          
          <div className="footer-section">
            <h4>Follow Us</h4>
            <div className="social-icons">
              <a href="#"><FaFacebook /></a>
              <a href="#"><FaInstagram /></a>
              <a href="#"><FaWhatsapp /></a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2026 Laxmi Bags House. All rights reserved. And Designed by Saroj</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;