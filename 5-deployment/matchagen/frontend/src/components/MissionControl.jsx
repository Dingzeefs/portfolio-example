import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Cpu } from 'lucide-react';

export function MissionControl() {
  const [status, setStatus] = useState("INITIALIZING");
  const [logs, setLogs] = useState([]);
  const [fillLevel, setFillLevel] = useState(0);

  useEffect(() => {
    const messages = [
      "SCANNING INGREDIENTS...",
      "ANALYZING FLAVOR PROFILE...",
      "WARMING OAT MILK...",
      "SIFTING MATCHA POWDER...",
      "WHISKING...",
      "SYNTHESIZING RECIPE...",
      "PLATING...",
    ];
    
    let i = 0;
    const interval = setInterval(() => {
      if (i < messages.length) {
        setStatus(messages[i]);
        setLogs(prev => [messages[i], ...prev].slice(0, 5));
        i++;
      }
    }, 600);

    // Fill up the cup over 3.5s
    const fillInterval = setInterval(() => {
      setFillLevel(prev => Math.min(prev + 2, 100));
    }, 50);

    return () => {
      clearInterval(interval);
      clearInterval(fillInterval);
    };
  }, []);

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-matcha-900 z-50 flex flex-col items-center justify-center text-matcha-100 font-mono overflow-hidden"
    >
      {/* Background Grid Effect */}
      <div className="absolute inset-0 opacity-10 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCI+CjxwYXRoIGQ9Ik0wIDBoNDB2NDBIMHoiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIwLjUiLz4KPC9zdmc+')]"></div>

      {/* Central Animation: The Matcha Cup */}
      <div className="relative w-64 h-80 mb-12 flex items-end justify-center">
        
        {/* Whisking Action (Particles) */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full pointer-events-none">
           {[...Array(8)].map((_, i) => (
             <motion.div
               key={i}
               className="absolute w-2 h-2 bg-matcha-300 rounded-full"
               initial={{ x: 0, y: 100, opacity: 0 }}
               animate={{ 
                 y: [-20, -100], 
                 x: Math.sin(i) * 40, 
                 opacity: [1, 0],
                 scale: [1, 0.5]
               }}
               transition={{ 
                 duration: 1.5, 
                 repeat: Infinity, 
                 delay: i * 0.2,
                 ease: "easeOut" 
               }}
               style={{ left: "50%" }}
             />
           ))}
        </div>

        {/* Cup Container */}
        <div className="relative w-40 h-56 border-4 border-matcha-100 rounded-b-3xl rounded-t-lg overflow-hidden bg-matcha-900/50 backdrop-blur-sm z-10">
          {/* Liquid Fill */}
          <motion.div 
            className="absolute bottom-0 left-0 right-0 bg-matcha-500/80"
            style={{ height: `${fillLevel}%` }}
          >
             {/* Wave Effect on top of liquid */}
             <motion.div 
               className="absolute -top-4 left-0 right-0 h-8 bg-matcha-300/50 rounded-full blur-md"
               animate={{ scaleX: [1, 1.2, 1] }}
               transition={{ duration: 2, repeat: Infinity }}
             />
          </motion.div>
          
          {/* Bubbles inside liquid */}
          <motion.div 
            className="absolute inset-0"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            {[...Array(5)].map((_, i) => (
               <div 
                 key={i}
                 className="absolute bg-white/30 rounded-full"
                 style={{
                   width: Math.random() * 10 + 5,
                   height: Math.random() * 10 + 5,
                   left: `${Math.random() * 80 + 10}%`,
                   bottom: `${Math.random() * 80 + 10}%`,
                 }}
               />
            ))}
          </motion.div>
        </div>

        {/* Cup Reflection/Shine */}
        <div className="absolute w-40 h-56 rounded-b-3xl rounded-t-lg z-20 shadow-[inset_0_0_20px_rgba(255,255,255,0.1)] pointer-events-none border-t-0 border-x-0 border-b-0"></div>

        {/* Scanner Line */}
        <motion.div 
          className="absolute top-0 left-1/2 -translate-x-1/2 w-56 h-1 bg-matcha-300 shadow-[0_0_15px_rgba(136,176,75,0.8)] z-30"
          animate={{ top: ["0%", "100%", "0%"] }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
        />
      </div>

      {/* Status Text */}
      <div className="z-10 text-center">
        <motion.h2 
          key={status}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-2xl font-bold tracking-[0.2em] mb-6 text-matcha-100"
        >
          {status}
        </motion.h2>
        
        {/* Terminal Logs */}
        <div className="w-[500px] bg-black/40 backdrop-blur-md border border-matcha-500/30 rounded-xl p-6 font-xs text-matcha-300/80 shadow-2xl">
          <AnimatePresence mode="popLayout">
            {logs.map((log, idx) => (
              <motion.div 
                key={`${log}-${idx}`}
                layout
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0 }}
                className="mb-2 flex items-center gap-3 border-l-2 border-matcha-500 pl-3"
              >
                <Cpu size={12} className="text-matcha-500 shrink-0" />
                <span className="font-mono text-sm">{log}</span>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>
    </motion.div>
  );
}
