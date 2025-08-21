import React from 'react';
import { TrendingDown, TrendingUp, DollarSign } from 'lucide-react';

const Results: React.FC = () => {
  const results = [
    {
      icon: TrendingDown,
      metric: 'Latência',
      improvement: '65% redução',
      description: 'Otimização de APIs e cache distribuído reduziram o tempo de resposta médio de 1.2s para 420ms.',
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600'
    },
    {
      icon: TrendingUp,
      metric: 'Conversão',
      improvement: '43% aumento',
      description: 'Melhorias na UX e performance resultaram em aumento significativo nas conversões do e-commerce.',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600'
    },
    {
      icon: DollarSign,
      metric: 'Custo Cloud',
      improvement: '38% economia',
      description: 'Otimização da arquitetura AWS com auto-scaling inteligente e right-sizing de recursos.',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600'
    }
  ];

  return (
    <section id="results" className="py-20 bg-white">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Resultados Comprovados
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Nossos projetos entregam impacto mensurável nos principais indicadores de performance e negócio.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {results.map((result, index) => (
            <div
              key={index}
              className="group p-8 bg-gray-50 rounded-2xl hover:shadow-xl transition-all duration-300 border border-gray-100 hover:border-gray-200"
            >
              {/* Icon */}
              <div className={`w-14 h-14 ${result.bgColor} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                <result.icon className={`w-7 h-7 ${result.iconColor}`} />
              </div>

              {/* Metric */}
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {result.metric}
                </h3>
                <div className={`text-3xl font-bold ${result.color}`}>
                  {result.improvement}
                </div>
              </div>

              {/* Description */}
              <p className="text-gray-600 leading-relaxed">
                {result.description}
              </p>

              {/* Visual indicator */}
              <div className="mt-6 flex items-center space-x-2">
                <div className={`w-2 h-2 ${result.bgColor} rounded-full`}></div>
                <div className={`w-4 h-2 ${result.bgColor} rounded-full opacity-60`}></div>
                <div className={`w-6 h-2 ${result.bgColor} rounded-full opacity-30`}></div>
              </div>
            </div>
          ))}
        </div>

        {/* Stats Summary */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-8 p-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">50+</div>
            <div className="text-gray-600">Projetos Entregues</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">98%</div>
            <div className="text-gray-600">Satisfação Cliente</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">2.5x</div>
            <div className="text-gray-600">ROI Médio</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">24/7</div>
            <div className="text-gray-600">Suporte Contínuo</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Results;