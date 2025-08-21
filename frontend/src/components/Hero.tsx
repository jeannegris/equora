import React from 'react';
import { ArrowRight, Code2, Globe, Settings } from 'lucide-react';

const Hero: React.FC = () => {
  const heroStyle = {
    backgroundImage: `url('https://images.unsplash.com/photo-1574790398664-0cb03682ed1c?q=80&w=871&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D')`
  };

  return (
    <section 
      className="relative pt-24 pb-16 text-white bg-center bg-cover"
      style={heroStyle}
    >
      <div className="absolute inset-0 bg-black opacity-50"></div>
      <div className="container relative z-10 px-6 mx-auto">
        <div className="max-w-4xl mx-auto text-center">
          {/* Logo Symbol */}
          <div className="mb-8">
            <div className="inline-flex items-center justify-center w-24 h-24 shadow-lg bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl">
              <div className="text-4xl font-bold text-white">
                <span className="inline-block transform rotate-90">=</span>
                <span className="inline-block -ml-2 transform -rotate-90">=</span>
              </div>
            </div>
          </div>

          {/* Headline */}
          <h1 className="mb-6 text-5xl font-bold leading-tight text-white md:text-6xl">
            Soluções de TI que
            <span className="text-blue-300"> equilibram</span>
            <br />performance e inovação
          </h1>

          {/* Subtitle */}
          <p className="max-w-3xl mx-auto mb-8 text-xl leading-relaxed text-gray-200">
            Consultoria, desenvolvimento sob medida, arquitetura e sites otimizados para empresas que buscam excelência tecnológica e resultados mensuráveis.
          </p>

          {/* Services Preview */}
          <div className="grid grid-cols-2 gap-6 mb-10 md:grid-cols-4">
            <div className="flex flex-col items-center p-4 transition-shadow bg-white/10 backdrop-blur-sm rounded-xl hover:bg-white/20">
              <Settings className="w-8 h-8 mb-2 text-blue-300" />
              <span className="text-sm font-medium text-white">Consultoria</span>
            </div>
            <div className="flex flex-col items-center p-4 transition-shadow bg-white/10 backdrop-blur-sm rounded-xl hover:bg-white/20">
              <Code2 className="w-8 h-8 mb-2 text-blue-300" />
              <span className="text-sm font-medium text-white">Dev Sob Medida</span>
            </div>
            <div className="flex flex-col items-center p-4 transition-shadow bg-white/10 backdrop-blur-sm rounded-xl hover:bg-white/20">
              <Settings className="w-8 h-8 mb-2 text-blue-300" />
              <span className="text-sm font-medium text-white">Arquitetura</span>
            </div>
            <div className="flex flex-col items-center p-4 transition-shadow bg-white/10 backdrop-blur-sm rounded-xl hover:bg-white/20">
              <Globe className="w-8 h-8 mb-2 text-blue-300" />
              <span className="text-sm font-medium text-white">Sites</span>
            </div>
          </div>

          {/* CTA */}
          <div className="flex flex-col justify-center gap-4 sm:flex-row">
            <a
              href="#contact"
              className="inline-flex items-center px-8 py-4 font-semibold text-white transition-colors bg-blue-600 rounded-lg shadow-lg hover:bg-blue-700 hover:shadow-xl"
            >
              Agendar Conversa
              <ArrowRight className="w-5 h-5 ml-2" />
            </a>
            <a
              href="#results"
              className="inline-flex items-center px-8 py-4 font-semibold text-gray-700 transition-colors bg-white border border-gray-200 rounded-lg shadow-sm hover:bg-gray-50"
            >
              Ver Resultados
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
