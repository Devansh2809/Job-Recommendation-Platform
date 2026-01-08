import React from 'react';
import { motion } from 'framer-motion';
import './ProfilePage.css';

export default function ProfilePage({ profile, user, onClose, onUploadNew }) {
  if (!profile) return null;

  return (
    <motion.div 
      className="profile-page-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div 
        className="profile-page-content"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        onClick={(e) => e.stopPropagation()}
      >
        <button className="profile-close" onClick={onClose}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        <div className="profile-header-section">
          <div className="profile-avatar-large">
            {user.photo ? (
              <img src={user.photo} alt={user.name} />
            ) : (
              <div className="avatar-placeholder">
                {user.name?.charAt(0).toUpperCase()}
              </div>
            )}
          </div>
          <div className="profile-header-info">
            <h2>{profile.name || user.name}</h2>
            {profile.email && <p className="profile-email">{profile.email}</p>}
            {profile.phone && <p className="profile-phone">{profile.phone}</p>}
          </div>
        </div>

        <div className="profile-sections">
          <div className="profile-section">
            <h3>Experience Level</h3>
            <div className="exp-badge">{profile.experience_level}</div>
            <div className="exp-details">
              <p><strong>Years of Experience:</strong> {profile.years_experience}</p>
              {profile.is_student && <p className="badge-student">Student</p>}
              {profile.seeking_internship && <p className="badge-internship">Seeking Internship</p>}
            </div>
          </div>

          <div className="profile-section">
            <h3>Skills ({profile.skills?.length || 0})</h3>
            <div className="skills-grid">
              {profile.skills?.map((skill, idx) => (
                <span key={idx} className="skill-badge">{skill}</span>
              ))}
            </div>
          </div>

          {profile.education && profile.education.length > 0 && (
            <div className="profile-section">
              <h3>Education</h3>
              <div className="education-list">
                {profile.education.map((edu, idx) => (
                  <div key={idx} className="education-item">
                    <p className="edu-degree">{edu.degree}</p>
                    {edu.institution && <p className="edu-institution">{edu.institution}</p>}
                    {edu.details && <p className="edu-details">{edu.details}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {profile.projects && profile.projects.length > 0 && (
            <div className="profile-section">
              <h3>Projects</h3>
              <div className="projects-list">
                {profile.projects.map((project, idx) => (
                  <div key={idx} className="project-item">
                    <p className="project-title">{project.title}</p>
                    {project.technologies && <p className="project-tech">{project.technologies}</p>}
                    {project.description && <p className="project-desc">{project.description}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="profile-actions">
          <button className="btn-secondary" onClick={onUploadNew}>
            Upload New Resume
          </button>
          <button className="btn-primary" onClick={onClose}>
            Done
          </button>
        </div>

        <p className="profile-updated">Last updated: {new Date(profile.updated_at).toLocaleDateString()}</p>
      </motion.div>
    </motion.div>
  );
}