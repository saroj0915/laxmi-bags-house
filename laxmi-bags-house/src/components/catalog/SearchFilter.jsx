import React from 'react';
import { FaSearch } from 'react-icons/fa';
import './SearchFilter.css';

const SearchFilter = ({ filters, setFilters, categories }) => {
  const handleSearch = (e) => {
    setFilters(prev => ({ ...prev, search: e.target.value }));
  };

  const handleCategoryChange = (e) => {
    setFilters(prev => ({ ...prev, category: e.target.value }));
  };

  const handleSortChange = (e) => {
    setFilters(prev => ({ ...prev, sort: e.target.value }));
  };

  return (
    <div className="search-filter-container">
      <div className="search-bar">
        <FaSearch className="search-icon" />
        <input 
          type="text" 
          placeholder="Search products..." 
          value={filters.search}
          onChange={handleSearch}
        />
      </div>
      
      <div className="filter-group">
        <select value={filters.category} onChange={handleCategoryChange}>
          {categories.map(cat => (
            <option key={cat.value} value={cat.value}>{cat.label}</option>
          ))}
        </select>
        
        <select value={filters.sort} onChange={handleSortChange}>
          <option value="default">Sort by: Default</option>
          <option value="price-low">Price: Low to High</option>
          <option value="price-high">Price: High to Low</option>
          <option value="rating">Rating: High to Low</option>
        </select>
      </div>
    </div>
  );
};

export default SearchFilter;