import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { signOut } from 'firebase/auth';
import { auth } from '../config/firebase';
import ExpandableJobCards from './ExpandableJobCards';
import ProfilePage from './ProfilePage';
import Footer from './Footer';
import './Dashboard.css';
import { apiCall } from '../config/api';

export default function Dashboard({ user, onLogout }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [profile, setProfile] = useState(null);
  const [results, setResults] = useState(null);
  const [showProfilePage, setShowProfilePage] = useState(false);

  useEffect(() => {
    loadProfile();
  }, [user]);

  const loadProfile = async () => {
    try {
      const data = await apiCall(`/resume/profile/${user.uid}`);
      setProfile(data.profile);
    } catch (err) {
      console.log('No profile found');
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Step 1: Parse resume
      const parseData = await apiCall('/resume/quick-parse', {
        method: 'POST',
        body: formData,
      });
      console.log('Step 1 - Resume parsed:', parseData);

      // Step 2: Save profile
      const saveData = await apiCall('/resume/save-profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.uid,
          parsed_resume: parseData.resume
        }),
      });
      console.log('Step 2 - Profile saved:', saveData);
      setProfile(saveData.profile);

      // Step 3: Fetch jobs
      const jobsData = await apiCall('/resume/fetch-jobs?top_k=10', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parseData.resume),
      });
      console.log('Step 3 - Jobs fetched:', jobsData);

      // Step 4: Format and display results
      const formattedData = {
        resume: parseData.resume || {},
        matches: (jobsData.recommendations || []).map(job => ({
          job: {
            id: job.id || `${job.company}-${job.title}`.replace(/\s/g, '-'),
            title: job.title,
            company: job.company,
            location: job.location,
            description: job.description,
            employment_type: job.employment_type,
            experience_level: job.experience_level,
            requirements: job.requirements,
            url: job.url,
          },
          score: job.match_score || 0
        }))
      };

      setResults(formattedData);
      setFile(null);
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogoutClick = async () => {
    await signOut(auth);
    onLogout();
  };

  const handleUploadNew = () => {
    setShowProfilePage(false);
    setResults(null);
    setFile(null);
  };

  return (
    <div className="dashboard">
      <nav className="nav">
        <div className="nav-content">
          <div className="logo">Job Match</div>
          <div className="nav-right">
            {profile && (
              <button className="profile-btn" onClick={() => setShowProfilePage(true)}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                  <circle cx="12" cy="7" r="4"></circle>
                </svg>
                Profile
              </button>
            )}
            {user.photo && <img src={user.photo} alt="" className="user-avatar" />}
            <span className="user-name">{user.name}</span>
            <button onClick={handleLogoutClick} className="logout-btn">Logout</button>
          </div>
        </div>
      </nav>

      <div className="container">
        <div className="welcome">
          <h2>Welcome back, {user.name?.split(' ')[0]}</h2>
          <p>{profile ? 'Upload a new resume to get personalized job recommendations' : 'Upload your resume to get started'}</p>
        </div>

        <motion.div 
          className="upload-card" 
          initial={{ opacity: 0, y: 20 }} 
          animate={{ opacity: 1, y: 0 }}
        >
          <h3>Upload Your Resume</h3>
          <p>PDF, DOCX, or Image format supported</p>
          
          <div className="upload-area" onClick={() => document.getElementById('file-input').click()}>
            <input 
              id="file-input"
              type="file" 
              accept=".pdf,.docx,.jpg,.jpeg,.png"
              onChange={handleFileChange} 
              style={{ display: 'none' }}
            />
            {!file ? (
              <>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                <p className="upload-text">Click to upload</p>
                <p className="upload-hint">or drag and drop your resume here</p>
              </>
            ) : (
              <>
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                  <polyline points="13 2 13 9 20 9"></polyline>
                </svg>
                <p className="upload-text">{file.name}</p>
                <p className="upload-hint">Click to change file</p>
              </>
            )}
          </div>

          <button onClick={handleUpload} disabled={!file || loading} className="upload-btn">
            {loading ? 'Processing...' : 'Upload & Match Jobs'}
          </button>

          {error && <div className="error">{error}</div>}
        </motion.div>

        {results && results.matches.length > 0 && (
          <motion.div 
            className="results" 
            initial={{ opacity: 0, y: 20 }} 
            animate={{ opacity: 1, y: 0 }}
          >
            <div className="resume-summary">
              <h3>Your Resume</h3>
              <div className="resume-details">
                <span className="exp-level">{results.resume.experience_level?.level || 'N/A'}</span>
                <span>{results.resume.skills?.length || 0} skills detected</span>
              </div>
              <div className="skills">
                <h4>Top Skills</h4>
                <div className="skill-tags">
                  {results.resume.skills?.slice(0, 15).map((skill, idx) => (
                    <span key={idx} className="skill-tag">{skill}</span>
                  ))}
                </div>
              </div>
            </div>

            <div className="jobs">
              <h3>Top Matches ({results.matches.length})</h3>
              <ExpandableJobCards jobs={results.matches.map(m => ({ ...m.job, score: m.score }))} />
            </div>
          </motion.div>
        )}
      </div>

      <AnimatePresence>
        {showProfilePage && profile && (
          <ProfilePage 
            profile={profile} 
            user={user}
            onClose={() => setShowProfilePage(false)}
            onUploadNew={handleUploadNew}
          />
        )}
      </AnimatePresence>
    </div>
  );
}