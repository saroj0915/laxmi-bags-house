import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { products } from '../data/products';
import './ProductDetailPage.css';

const ProductDetailPage = () => {
  const { id } = useParams();
  const product = products.find(p => p.id === parseInt(id));

  if (!product) {
    return (
      <div className="container">
        <div className="not-found">
          <h2>Product not found</h2>
          <Link to="/catalog" className="btn-primary">Back to Catalog</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="product-detail-page">
      <div className="container">
        <div className="product-detail">
          <div className="product-detail-image">
            <img src={product.image} alt={product.name} />
          </div>
          <div className="product-detail-info">
            <h1>{product.name}</h1>
            <div className="product-detail-price">
              <span className="price-current">₹{product.price}</span>
              {product.originalPrice && (
                <span className="price-original">₹{product.originalPrice}</span>
              )}
            </div>
            <p className="product-description">{product.description}</p>
            <div className="product-meta">
              <p><strong>Category:</strong> {product.category}</p>
              <p><strong>Availability:</strong> {product.inStock ? 'In Stock' : 'Out of Stock'}</p>
            </div>
            <button className="add-to-cart-btn" disabled={!product.inStock}>
              {product.inStock ? 'Add to Cart' : 'Out of Stock'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetailPage;