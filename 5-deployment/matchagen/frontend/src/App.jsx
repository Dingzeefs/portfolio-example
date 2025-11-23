import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Pantry } from './components/Pantry';
import { MissionControl } from './components/MissionControl';
import { RecipeCard } from './components/RecipeCard';
import { AmbientParticles } from './components/AmbientParticles';
import { Sparkles } from 'lucide-react';

function App() {
  const [selectedIngredients, setSelectedIngredients] = useState([]);
  const [customInput, setCustomInput] = useState("");
  const [temperature, setTemperature] = useState(0.8);
  const [isGenerating, setIsGenerating] = useState(false);
  const [recipe, setRecipe] = useState(null);
  const [error, setError] = useState(null);

  const toggleIngredient = (item) => {
    setSelectedIngredients(prev => 
      prev.includes(item) 
        ? prev.filter(i => i !== item)
        : [...prev, item]
    );
  };

  const handleGenerate = async () => {
    const ingredientsList = [...selectedIngredients];
    if (customInput.trim()) {
      ingredientsList.push(customInput.trim());
    }

    if (ingredientsList.length === 0) return;

    setIsGenerating(true);
    setError(null);

    try {
      const delayPromise = new Promise(resolve => setTimeout(resolve, 3500));
      
      const apiPromise = fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          inspiration: ingredientsList.join(', '),
          temperature: temperature
        })
      });

      const [_, response] = await Promise.all([delayPromise, apiPromise]);
      
      if (!response.ok) throw new Error('Failed to generate recipe');
      
      const data = await response.json();
      setRecipe(data.recipe);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-forest-dark text-luxury-cream selection:bg-matcha-500 selection:text-white relative overflow-x-hidden font-sans antialiased">
      <AmbientParticles />
      
      {isGenerating && <MissionControl />}

      <div className="relative z-10">
        <header className="pt-16 pb-8 text-center transform-gpu">
          <motion.div
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-6xl md:text-7xl font-serif text-luxury-gold mb-4 tracking-tight drop-shadow-lg">
              TokiMono Matcha Lab
            </h1>
            <p className="text-matcha-300 font-mono text-sm tracking-[0.2em] uppercase opacity-80">
              AI-Powered Recipe Synthesis
            </p>
            <p className="text-matcha-300/60 text-xs mt-3 max-w-md mx-auto leading-relaxed">
              Recipes are AI-generated and should be verified before use. We are not responsible for results.
            </p>
          </motion.div>
        </header>

        <main className="container mx-auto px-4 pb-24 max-w-6xl">
          {!recipe ? (
            <div>
              <Pantry 
                selectedIngredients={selectedIngredients} 
                toggleIngredient={toggleIngredient}
                customInput={customInput}
                setCustomInput={setCustomInput}
              />

              {/* Controls Section */}
              <div className="max-w-2xl mx-auto mt-16 p-8 bg-forest-card border border-forest-light rounded-2xl shadow-2xl backdrop-blur-md">
                <div className="flex items-center justify-between mb-6">
                  <label className="font-mono text-sm text-luxury-gold uppercase tracking-wider">
                    Creativity Level
                  </label>
                  <span className="font-mono text-matcha-300 text-lg">{temperature}</span>
                </div>
                
                <div className="relative h-2 bg-forest-dark rounded-full mb-2">
                   <input 
                    type="range" 
                    min="0.5" 
                    max="1.5" 
                    step="0.1" 
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
                  />
                  <div 
                    className="absolute top-0 left-0 h-full bg-luxury-gold rounded-full z-10 transition-all duration-100" 
                    style={{ width: `${((temperature - 0.5) / 1.0) * 100}%` }}
                  />
                  <div 
                    className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-luxury-gold rounded-full shadow-lg z-10 pointer-events-none transition-all duration-100"
                    style={{ left: `${((temperature - 0.5) / 1.0) * 100}%` }}
                  />
                </div>

                <div className="flex justify-between text-xs text-matcha-300/60 font-mono mt-4">
                  <span>PREDICTABLE</span>
                  <span>EXPERIMENTAL</span>
                </div>
              </div>

              {/* Button Container - Removed motion.div wrapper, increased z-index */}
              <div className="flex justify-center mt-16 relative z-20">
                <button
                  onClick={handleGenerate}
                  disabled={selectedIngredients.length === 0 && !customInput.trim()}
                  className="group relative px-10 py-5 bg-luxury-gold text-forest-dark rounded-full font-mono text-lg font-bold tracking-widest transition-all disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden shadow-[0_0_20px_rgba(212,196,168,0.2)] hover:shadow-[0_0_30px_rgba(212,196,168,0.4)] hover:-translate-y-1 hover:bg-white active:translate-y-0"
                >
                  <span className="relative z-10 flex items-center gap-3">
                    <Sparkles size={20} />
                    INITIATE GENERATION
                  </span>
                </button>
              </div>
              
              {error && (
                <div className="text-center mt-8 text-red-400 font-mono bg-red-900/20 py-2 rounded-lg border border-red-900/50">
                  {error}
                </div>
              )}
            </div>
          ) : (
            <RecipeCard 
              recipe={recipe} 
              onReset={() => {
                setRecipe(null);
                setSelectedIngredients([]);
                setCustomInput("");
              }} 
            />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
