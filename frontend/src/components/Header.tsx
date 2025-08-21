import React, { useState, useEffect } from 'react';
import { Menu, X } from 'lucide-react';

const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [hasScrolled, setHasScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setHasScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  return (
    <header className={`fixed top-0 left-0 right-0 bg-white/95 backdrop-blur-sm z-50 border-b border-gray-200 transition-shadow ${hasScrolled ? 'shadow-md' : ''}`}>
      <div className="container px-6 py-4 mx-auto">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="text-2xl font-bold text-blue-600">
              <span className="inline-block transform rotate-90">=</span>
              <span className="inline-block -ml-1 transform -rotate-90">=</span>
            </div>
            <span className="text-xl font-semibold text-gray-900">Equora Systems</span>
          </div>

          {/* Desktop Navigation */}
          <nav className="items-center hidden space-x-8 md:flex">
            <a href="#services" className="text-gray-700 transition-colors hover:text-blue-600">Serviços</a>
            <a href="#process" className="text-gray-700 transition-colors hover:text-blue-600">Processo</a>
            <a href="#results" className="text-gray-700 transition-colors hover:text-blue-600">Resultados</a>
            <a href="#technologies" className="text-gray-700 transition-colors hover:text-blue-600">Stack</a>
            <a href="#contact" className="px-6 py-2 text-white transition-colors bg-blue-600 rounded-lg hover:bg-blue-700">
              Agendar
            </a>
          </nav>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <nav className="pt-4 pb-4 mt-4 border-t border-gray-200 md:hidden">
            <div className="flex flex-col space-y-4">
              <a href="#services" className="text-gray-700 transition-colors hover:text-blue-600">Serviços</a>
              <a href="#process" className="text-gray-700 transition-colors hover:text-blue-600">Processo</a>
              <a href="#results" className="text-gray-700 transition-colors hover:text-blue-600">Resultados</a>
              <a href="#technologies" className="text-gray-700 transition-colors hover:text-blue-600">Stack</a>
              <a href="#contact" className="px-6 py-2 text-center text-white transition-colors bg-blue-600 rounded-lg hover:bg-blue-700">
                Agendar
              </a>
            </div>
          </nav>
        )}
      </div>
    </header>
  );
};

export default Header;
