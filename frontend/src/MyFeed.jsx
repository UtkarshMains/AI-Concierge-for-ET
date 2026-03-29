import React from "react";
import "./MyFeed.css";

export default function MyFeed({ categories, articles }) {

  if (!articles || articles.length === 0) {
    return (
      <div className="feed-container">
        <h2>No articles found</h2>
      </div>
    );
  }

  return (
    <div className="feed-container">

      {/* Recommended Categories */}
      <div className="category-section">
        <h2>Your Recommended Categories</h2>
        <div className="categories">
          {categories.map((cat) => (
            <span key={cat} className="category-tag">
              {cat}
            </span>
          ))}
        </div>
      </div>

      {/* Articles */}
      <div className="articles-section">
        <h2>Latest Articles</h2>

        <div className="articles-grid">
          {articles.map((article, index) => (
            <div key={index} className="article-card">

              <h3>{article.title}</h3>

              <a
                href={article.link}
                target="_blank"
                rel="noopener noreferrer"
                className="read-btn"
              >
                Read Full Article →
              </a>

            </div>
          ))}
        </div>

      </div>
    </div>
  );
}