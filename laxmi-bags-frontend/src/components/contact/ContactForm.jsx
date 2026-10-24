import React, { useState } from 'react';
import './ContactForm.css';

const ContactForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
    setSubmitted(true);
    setTimeout(() => setSubmitted(false), 5000);
    setFormData({ name: '', email: '', phone: '', subject: '', message: '' });
  };

  return (
    <form className="contact-form" onSubmit={handleSubmit}>
      {submitted && (
        <div className="success-message">
          Thank you! We'll get back to you soon.
        </div>
      )}
      
      <div className="form-group">
        <input 
          type="text" 
          name="name"
          placeholder="Your Name" 
          value={formData.name}
          onChange={handleChange}
          required
        />
      </div>
      
      <div className="form-group">
        <input 
          type="email" 
          name="email"
          placeholder="Email Address" 
          value={formData.email}
          onChange={handleChange}
          required
        />
      </div>
      
      <div className="form-group">
        <input 
          type="tel" 
          name="phone"
          placeholder="Phone Number" 
          value={formData.phone}
          onChange={handleChange}
        />
      </div>
      
      <div className="form-group">
        <input 
          type="text" 
          name="subject"
          placeholder="Subject" 
          value={formData.subject}
          onChange={handleChange}
          required
        />
      </div>
      
      <div className="form-group">
        <textarea 
          name="message"
          placeholder="Your Message" 
          rows="5"
          value={formData.message}
          onChange={handleChange}
          required
        ></textarea>
      </div>
      
      <button type="submit" className="submit-btn">Send Message</button>
    </form>
  );
};

export default ContactForm;