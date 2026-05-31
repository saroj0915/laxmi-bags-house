import React from 'react';
import ContactForm from '../components/contact/ContactForm';
import './ContactPage.css';

const ContactPage = () => {
  return (
    <div className="contact-page">
      <div className="container">
        <h1 className="page-title">Get In Touch</h1>
        <div className="contact-wrapper">
          <div className="contact-info">
            <h3>Laxmi Bags House</h3>
            <div className="info-item">
              <span className="icon">📍</span>
              <p>Kathmandu, Nepal</p>
            </div>
            <div className="info-item">
              <span className="icon">📞</span>
              <p>+977-9800000000</p>
            </div>
            <div className="info-item">
              <span className="icon">✉️</span>
              <p>info@laxmibags.com</p>
            </div>
            <div className="business-hours">
              <h4>Business Hours</h4>
              <p>Monday - Saturday: 9 AM - 7 PM</p>
              <p>Sunday: Closed</p>
            </div>
          </div>
          <ContactForm />
        </div>
      </div>
    </div>
  );
};

export default ContactPage;