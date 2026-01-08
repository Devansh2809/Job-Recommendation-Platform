import React, { useEffect, useId, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useOutsideClick } from '../hooks/useOutsideClick';
import './ExpandableJobCards.css';

const CloseIcon = () => {
  return (
    <motion.svg
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, transition: { duration: 0.05 } }}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M18 6l-12 12" />
      <path d="M6 6l12 12" />
    </motion.svg>
  );
};

export default function ExpandableJobCards({ jobs }) {
  const [active, setActive] = useState(null);
  const id = useId();
  const ref = useRef(null);

  useEffect(() => {
    function onKeyDown(event) {
      if (event.key === 'Escape') {
        setActive(null);
      }
    }

    if (active) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }

    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [active]);

  useOutsideClick(ref, () => setActive(null));

  return (
    <>
      <AnimatePresence>
        {active && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="overlay"
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {active && (
          <div className="modal-container">
            <motion.button
              key={`button-${active.id}-${id}`}
              layout
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, transition: { duration: 0.05 } }}
              className="close-btn-mobile"
              onClick={() => setActive(null)}
            >
              <CloseIcon />
            </motion.button>

            <motion.div
              layoutId={`card-${active.id}-${id}`}
              ref={ref}
              className="expanded-card"
            >
              <div className="expanded-content">
                <div className="expanded-header">
                  <div className="expanded-info">
                    <motion.h3
                      layoutId={`title-${active.id}-${id}`}
                      className="expanded-title"
                    >
                      {active.title}
                    </motion.h3>
                    <motion.p
                      layoutId={`company-${active.id}-${id}`}
                      className="expanded-company"
                    >
                      {active.company}
                    </motion.p>
                    <motion.p className="expanded-location">
                      {active.location} • {active.employment_type}
                    </motion.p>
                  </div>

                  <div className="expanded-actions">
                    <motion.div
                      layout
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      className="expanded-score"
                    >
                      {(active.score * 100).toFixed(0)}% Match
                    </motion.div>
                    <motion.a
                      layout
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      href={active.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="apply-btn"
                    >
                      Apply Now
                    </motion.a>
                  </div>
                </div>

                <div className="expanded-body">
                  <motion.div
                    layout
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="expanded-details"
                  >
                    <div className="detail-section">
                      <h4>Job Description</h4>
                      <p>{active.description}</p>
                    </div>

                    {active.requirements && (
                      <div className="detail-section">
                        <h4>Requirements</h4>
                        <p>{active.requirements}</p>
                      </div>
                    )}

                    <div className="detail-section">
                      <h4>Details</h4>
                      <div className="detail-grid">
                        <div className="detail-item">
                          <span className="detail-label">Experience Level</span>
                          <span className="detail-value">{active.experience_level}</span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">Job Type</span>
                          <span className="detail-value">{active.employment_type}</span>
                        </div>
                        <div className="detail-item">
                          <span className="detail-label">Location</span>
                          <span className="detail-value">{active.location}</span>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      <div className="job-grid">
        {jobs.map((job) => (
          <motion.div
            layoutId={`card-${job.id}-${id}`}
            key={job.id}
            onClick={() => setActive(job)}
            className="job-card-compact"
            whileHover={{ scale: 1.02 }}
            transition={{ duration: 0.2 }}
          >
            <div className="card-content">
              <div className="card-header">
                <motion.h3
                  layoutId={`title-${job.id}-${id}`}
                  className="card-title"
                >
                  {job.title}
                </motion.h3>
                <div className="card-score">
                  {(job.score * 100).toFixed(0)}%
                </div>
              </div>
              <motion.p
                layoutId={`company-${job.id}-${id}`}
                className="card-company"
              >
                {job.company}
              </motion.p>
              <p className="card-location">{job.location}</p>
              <p className="card-description">{job.description.substring(0, 120)}...</p>
            </div>
          </motion.div>
        ))}
      </div>
    </>
  );
}