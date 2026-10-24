import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { products } from '../../data/products';
import ProductCard from '../catalog/ProductCard';
import './ProductShowcase.css';

const ProductShowcase = () => {
  const featuredProducts = products.slice(0, 4);

  return (
    <section className="product-showcase">
      <div className="container">
        <h2 className="section-title">Our Collections</h2>
        <div className="product-grid">
          {featuredProducts.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
        <div className="showcase-footer">
          <Link to="/catalog" className="btn-primary">View All Products →</Link>
        </div>
      </div>
    </section>
  );
};

export default ProductShowcase;