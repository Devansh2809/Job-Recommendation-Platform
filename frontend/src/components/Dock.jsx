import React, { useRef } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import './Dock.css';

function DockIcon({ icon, label, onClick }) {
  const ref = useRef(null);
  const distance = useMotionValue(Infinity);
  const widthTransform = useTransform(distance, [-150, 0, 150], [40, 80, 40]);
  const width = useSpring(widthTransform, { mass: 0.1, stiffness: 150, damping: 12 });

  return (
    <motion.button
      ref={ref}
      style={{ width, height: width }}
      className="dock-icon"
      onClick={onClick}
      whileHover={{ y: -10 }}
      whileTap={{ scale: 0.95 }}
    >
      {icon}
    </motion.button>
  );
}

export default function Dock({ onLogin }) {
  return (
    <div className="dock-container">
      <motion.div
        className="dock"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <DockIcon
          icon={
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M13.8 12H3"/>
            </svg>
          }
          label="Login"
          onClick={onLogin}
        />
      </motion.div>
    </div>
  );
}