import React from 'react';
import { motion } from 'framer-motion';
import { Share2, Download, RefreshCw, Sparkles } from 'lucide-react';

export function RecipeCard({ recipe, onReset }) {
  // Simple parser to split the text
  const lines = recipe.split('\n');
  const title = lines.find(l => l.startsWith('Title:'))?.replace('Title: ', '') || 'Custom Recipe';

  const ingredientsStart = lines.findIndex(l => l.includes('Ingredients:'));
  const directionsStart = lines.findIndex(l => l.includes('Directions:'));

  const ingredients = lines.slice(ingredientsStart + 1, directionsStart).filter(l => l.trim().startsWith('-'));
  const directions = lines.slice(directionsStart + 1).filter(l => l.trim().match(/^\d+\./));

  const handleDownload = () => {
    const blob = new Blob([recipe], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.replace(/\s+/g, '_')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleShare = async () => {
    const shareData = {
      title: `${title} - TokiMono Matcha Lab`,
      text: recipe,
    };

    if (navigator.share) {
      try {
        await navigator.share(shareData);
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Error sharing:', err);
          copyToClipboard();
        }
      }
    } else {
      copyToClipboard();
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(recipe).then(() => {
      alert('Recipe copied to clipboard!');
    }).catch(err => {
      console.error('Failed to copy:', err);
    });
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="max-w-5xl mx-auto bg-forest-card rounded-3xl shadow-2xl overflow-hidden border border-forest-light flex flex-col md:flex-row min-h-[600px] transform-gpu"
    >
      {/* Visual Side (Left) */}
      <div className="md:w-1/3 bg-forest-dark relative flex items-center justify-center p-8 border-r border-forest-light">
        {/* Decorative pattern */}
        <div className="absolute inset-0 opacity-10 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCI+CjxwYXRoIGQ9Ik0xMCAxMEgwVjBoMTB6IiBmaWxsPSIjRDRDNEE4IiAvPgo8L3N2Zz4=')] pattern-grid-lg" />
        
        <div className="text-center z-10 relative">
          <motion.div 
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.3, duration: 0.8 }}
          >
            <h1 className="text-4xl md:text-5xl font-serif italic text-luxury-gold leading-tight drop-shadow-lg mb-4">
              {title}
            </h1>
            <span className="text-matcha-500 font-mono tracking-[0.2em] text-sm uppercase border-t border-b border-matcha-500/30 py-2 px-4 inline-block">
              Matcha Synthesis
            </span>
          </motion.div>
        </div>
      </div>

      {/* Content Side (Right) */}
      <div className="md:w-2/3 p-8 md:p-12 flex flex-col bg-forest-card text-luxury-cream">
        <div className="flex justify-between items-start mb-10">
          <div className="flex gap-3">
            <span className="px-3 py-1 rounded-full border border-matcha-500/30 text-matcha-300 text-[10px] font-mono uppercase tracking-wider flex items-center gap-2">
              <Sparkles size={10} /> AI Generated
            </span>
            <span className="px-3 py-1 rounded-full border border-forest-light text-luxury-gold/70 text-[10px] font-mono uppercase tracking-wider">
              T5 Model
            </span>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleShare}
              className="p-2 hover:bg-forest-light rounded-full text-luxury-gold transition-colors border border-transparent hover:border-luxury-gold/20"
              title="Share recipe"
            >
              <Share2 size={18} />
            </button>
            <button
              onClick={handleDownload}
              className="p-2 hover:bg-forest-light rounded-full text-luxury-gold transition-colors border border-transparent hover:border-luxury-gold/20"
              title="Download recipe"
            >
              <Download size={18} />
            </button>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-12 mb-12 flex-grow">
          <div>
            <h3 className="font-serif text-2xl mb-6 text-luxury-gold border-b border-forest-light pb-3 italic">Ingredients</h3>
            <ul className="space-y-4">
              {ingredients.map((ing, i) => (
                <li key={i} className="flex items-start gap-3 text-luxury-cream/80 font-light tracking-wide">
                  <span className="w-1.5 h-1.5 rounded-full bg-matcha-500 mt-2 shrink-0 shadow-[0_0_5px_rgba(76,175,80,0.5)]" />
                  <span>{ing.replace('-', '').trim()}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="font-serif text-2xl mb-6 text-luxury-gold border-b border-forest-light pb-3 italic">Method</h3>
            <ol className="space-y-6">
              {directions.map((step, i) => (
                <li key={i} className="flex gap-4 text-luxury-cream/80">
                  <span className="font-mono text-matcha-300 font-bold shrink-0 text-sm pt-1">{(i + 1).toString().padStart(2, '0')}</span>
                  <span className="font-light leading-relaxed">{step.replace(/^\d+\.\s*/, '')}</span>
                </li>
              ))}
            </ol>
          </div>
        </div>

        <button 
          onClick={onReset}
          className="self-start flex items-center gap-3 text-luxury-gold hover:text-white transition-colors font-mono text-xs tracking-widest uppercase group"
        >
          <div className="p-2 rounded-full border border-luxury-gold/30 group-hover:border-white transition-colors">
            <RefreshCw size={14} className="group-hover:rotate-180 transition-transform duration-500" />
          </div>
          Create New Synthesis
        </button>
      </div>
    </motion.div>
  );
}
