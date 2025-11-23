import React from 'react';
import { Check, Plus, Search } from 'lucide-react';
import { clsx } from 'clsx';

const CATEGORIES = {
  "The Base": ["Oat Milk", "Almond Milk", "Coconut Milk", "Soy Milk", "Whole Milk"],
  "The Twist": ["Mango", "Strawberry", "Blueberries", "Vanilla Syrup", "Honey", "White Chocolate"],
  "The Boost": ["Collagen", "Protein Powder", "Cinnamon", "Ginger"]
};

export function Pantry({ selectedIngredients, toggleIngredient, customInput, setCustomInput }) {
  return (
    <div className="w-full mx-auto pt-8">
      <h2 className="text-2xl md:text-3xl font-serif italic mb-10 text-center text-luxury-cream/90 drop-shadow-md">
        Select Your Ingredients, or Fill In Below
      </h2>
      
      {/* Custom Input Section */}
      <div className="max-w-xl mx-auto mb-16 relative">
        <div className="relative group">
          <div className="absolute left-5 top-1/2 -translate-y-1/2 pointer-events-none">
            <Search 
              className="text-matcha-300 transition-colors group-focus-within:text-luxury-gold" 
              size={20} 
            />
          </div>
          <input
            type="text"
            value={customInput}
            onChange={(e) => setCustomInput(e.target.value)}
            placeholder="E.g., Matcha Ice Cream, Cardamom, Caramel..."
            className="w-full pl-14 pr-6 py-5 bg-forest-card border border-forest-light rounded-2xl shadow-lg text-luxury-cream placeholder:text-matcha-300/50 font-mono focus:outline-none focus:ring-1 focus:ring-luxury-gold focus:border-luxury-gold transition-all hover:border-matcha-500/50 appearance-none"
          />
        </div>
        <p className="text-center text-[10px] font-mono text-matcha-300/60 mt-3 tracking-[0.2em] uppercase">
          Add your own inspiration
        </p>
      </div>

      <div className="space-y-16">
        {Object.entries(CATEGORIES).map(([category, items]) => (
          <div key={category}>
            <div className="flex items-center gap-4 mb-6">
              <div className="h-px flex-1 bg-forest-light/50"></div>
              <h3 className="text-xs font-mono uppercase tracking-[0.3em] text-luxury-gold/90 shadow-black drop-shadow-sm">
                {category}
              </h3>
              <div className="h-px flex-1 bg-forest-light/50"></div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {items.map((item) => {
                const isSelected = selectedIngredients.includes(item);
                return (
                  <button
                    key={item}
                    onClick={() => toggleIngredient(item)}
                    className={clsx(
                      "relative p-4 rounded-xl border transition-all duration-200 flex flex-col items-center justify-center gap-3 h-36",
                      isSelected 
                        ? "bg-luxury-gold text-forest-dark border-luxury-gold shadow-[0_0_20px_rgba(212,196,168,0.4)] ring-1 ring-luxury-gold translate-y-[-2px]" 
                        : "bg-forest-card text-matcha-300 border-forest-light hover:border-matcha-500 hover:bg-forest-light/80 hover:text-luxury-cream hover:translate-y-[-2px]"
                    )}
                  >
                    {isSelected && (
                      <div className="absolute top-3 right-3">
                        <Check size={14} className="text-forest-dark" />
                      </div>
                    )}
                    <span className="text-center font-medium tracking-wide antialiased">{item}</span>
                    {!isSelected && <Plus size={14} className="text-matcha-500 opacity-30 group-hover:opacity-100" />}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
