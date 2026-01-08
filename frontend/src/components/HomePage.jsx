import React from 'react';
import { motion } from 'framer-motion';
import Dock from './Dock';
import Footer from './Footer';
import './HomePage.css';

export default function HomePage({ onLogin }) {
  return (
    <div className="home-page">
      <Dock onLogin={onLogin} />
      
      <div className="content">
        <motion.div
          className="hero"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <motion.div 
            className="hero-badge"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            NLP-Powered Matching
          </motion.div>
          <h1>Find Your Perfect Job Match</h1>
          <p className="subtitle">
            Stop endlessly scrolling through job boards. Our intelligent platform analyzes your resume, 
            understands your unique skills and experience, then surfaces opportunities that actually align 
            with your career goals. No more guesswork-just relevant matches, delivered instantly.
          </p>
        </motion.div>

        <motion.div
          className="how-it-works"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.8 }}
        >
          <h2>How It Works</h2>
          <div className="steps">
            <div className="step">
              <div className="step-number">01</div>
              <h3>Upload Your Resume</h3>
              <p>Simply upload your PDF or DOCX resume. Our system supports multiple formats and handles complex layouts.</p>
            </div>
            
            <div className="step">
              <div className="step-number">02</div>
              <h3>AI Analysis</h3>
              <p>Our advanced NLP models parse your resume, extracting skills, experience level, and key qualifications with precision.</p>
            </div>
            
            <div className="step">
              <div className="step-number">03</div>
              <h3>Get Matched</h3>
              <p>Receive a curated list of job opportunities ranked by relevance score. Each match is personalized to your profile.</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="features"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.8 }}
        >
          <h2>Why Choose Our Platform</h2>
          <div className="feature-grid">
            <div className="feature">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                  <path d="M2 17l10 5 10-5M2 12l10 5 10-5"></path>
                </svg>
              </div>
              <h3>Neural Parsing Engine</h3>
              <p>State-of-the-art machine learning models understand context, not just keywords. We extract meaningful insights from your resume that traditional parsers miss.</p>
            </div>
            
            <div className="feature">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
              </div>
              <h3>Real-Time Matching</h3>
              <p>Processing happens in milliseconds. Upload your resume and instantly see your top matches with detailed relevance scores and reasoning.</p>
            </div>
            
            <div className="feature">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                  <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                  <line x1="12" y1="22.08" x2="12" y2="12"></line>
                </svg>
              </div>
              <h3>Semantic Understanding</h3>
              <p>We go beyond surface-level matching. Our vector embeddings capture the semantic meaning of skills and job requirements for smarter recommendations.</p>
            </div>
            
            <div className="feature">
              <div className="feature-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                </svg>
              </div>
              <h3>Transparent Scoring</h3>
              <p>Every job match comes with a clear relevance percentage. Understand exactly why a position is recommended for your unique background.</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="cta-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.7, duration: 0.8 }}
        >
          <div className="cta-content">
            <h2>Ready to Find Your Next Opportunity?</h2>
            <p>Join professionals who trust AI to accelerate their job search</p>
            <div className="cta-action">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="9 18 15 12 9 6"></polyline>
              </svg>
              <span>Click the login button in the top right corner to begin</span>
            </div>
          </div>
        </motion.div>
      </div>

      <Footer />
    </div>
  );
}