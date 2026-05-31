import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import ProductGrid from '../components/catalog/ProductGrid';
import SearchFilter from '../components/catalog/SearchFilter';
import { products } from '../data/products';
import './CatalogPage.css';

const CatalogPage = () => {
  const location = useLocation();
  const [filteredProducts, setFilteredProducts] = useState(products);
  const [filters, setFilters] = useState({
    search: '',
    category: new URLSearchParams(location.search).get('category') || 'all',
    sort: 'default'
  });

  useEffect(() => {
    let result = [...products];
    
    if (filters.search) {
      result = result.filter(p => 
        p.name.toLowerCase().includes(filters.search.toLowerCase())
      );
    }
    
    if (filters.category && filters.category !== 'all') {
      result = result.filter(p => p.category === filters.category);
    }
    
    switch(filters.sort) {
      case 'price-low':
        result.sort((a, b) => a.price - b.price);
        break;
      case 'price-high':
        result.sort((a, b) => b.price - a.price);
        break;
      case 'rating':
        result.sort((a, b) => b.rating - a.rating);
        break;
      default:
        break;
    }
    
    setFilteredProducts(result);
  }, [filters]);

  const categories = [
    { value: 'all', label: 'All Products' },
    { value: 'backpack', label: 'Backpacks' },
    { value: 'travel', label: 'Travel Bags' },
    { value: 'school', label: 'School Bags' },
    { value: 'purse', label: 'Purses' }
  ];

  return (
    <div className="catalog-page">
      <div className="container">
        <h1 className="page-title">Our Catalog</h1>
        <SearchFilter 
          filters={filters}
          setFilters={setFilters}
          categories={categories}
        />
        <ProductGrid products={filteredProducts} />
      </div>
    </div>
  );
};

export default CatalogPage;