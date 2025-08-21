import React from 'react';
import { Cloud, Server, Monitor, Eye, ArrowRight, Database, Globe, BarChart3 } from 'lucide-react';

const ProjectExamples: React.FC = () => {
  const examples = [
    {
      category: 'Cloud Architecture',
      icon: Cloud,
      title: 'E-commerce Multi-Region',
      description: 'Arquitetura AWS com alta disponibilidade, auto-scaling e disaster recovery para plataforma de e-commerce.',
      imageUrl: 'https://images.unsplash.com/photo-1522204523234-8729aa6e3d5f?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
      color: 'from-blue-500 to-cyan-500',
      bgColor: 'bg-blue-50'
    },
    {
      category: 'Backend Architecture',
      icon: Server,
      title: 'Microserviços Financeiros',
      description: 'API Gateway com microserviços Node.js, message queues e padrões de resiliência para sistema financeiro.',
      imageUrl: 'https://images.pexels.com/photos/6801648/pexels-photo-6801648.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
      color: 'from-green-500 to-emerald-500',
      bgColor: 'bg-green-50'
    },
    {
      category: 'Frontend Architecture',
      icon: Globe,
      title: 'SPA Enterprise',
      description: 'React + Next.js com SSR, micro-frontends, state management e otimizações de performance.',
      imageUrl: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
      color: 'from-purple-500 to-pink-500',
      bgColor: 'bg-purple-50'
    },
    {
      category: 'Observability',
      icon: Eye,
      title: 'Monitoring Stack',
      description: 'Stack completa de observabilidade com métricas, logs, traces e alertas para sistemas distribuídos.',
      imageUrl: 'https://images.unsplash.com/photo-1587620962725-abab7fe55159?q=80&w=1031&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
      color: 'from-orange-500 to-red-500',
      bgColor: 'bg-orange-50'
    }
  ];

  return (
    <section className="py-20 bg-white">
      <div className="container px-6 mx-auto">
        <div className="mb-16 text-center">
          <h2 className="mb-4 text-4xl font-bold text-gray-900">
            Exemplos de Arquiteturas
          </h2>
          <p className="max-w-3xl mx-auto text-xl text-gray-600">
            Conheça alguns exemplos de projetos que desenvolvemos, desde arquiteturas cloud até sistemas de observabilidade completos.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
          {examples.map((example, index) => (
            <div
              key={index}
              className="overflow-hidden transition-all duration-300 bg-white border border-gray-200 shadow-lg group rounded-2xl hover:shadow-xl"
            >
              {/* Header */}
              <div className={`p-6 bg-gradient-to-r ${example.color} text-white`}>
                <div className="flex items-center mb-2 space-x-3">
                  <example.icon className="w-6 h-6" />
                  <span className="text-sm font-medium opacity-90">{example.category}</span>
                </div>
                <h3 className="mb-2 text-xl font-bold">{example.title}</h3>
                <p className="text-sm leading-relaxed opacity-90">
                  {example.description}
                </p>
              </div>

              {/* Mockup Image */}
              <div className={`relative h-64 ${example.bgColor}`}>
                <img 
                  src={example.imageUrl} 
                  alt={example.title} 
                  className="object-cover w-full h-full"
                />
              </div>

              {/* Footer */}
              <div className="p-6 bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <div className="flex items-center space-x-1">
                      <Database className="w-4 h-4" />
                      <span>Escalável</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Monitor className="w-4 h-4" />
                      <span>Monitorado</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <BarChart3 className="w-4 h-4" />
                      <span>Otimizado</span>
                    </div>
                  </div>
                  <button className="flex items-center space-x-2 text-sm font-medium text-blue-600 transition-transform hover:text-blue-700 group-hover:translate-x-1">
                    <span>Ver detalhes</span>
                    <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Call to Action */}
        <div className="mt-16 text-center">
          <div className="p-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl">
            <h3 className="mb-4 text-2xl font-bold text-gray-900">
              Precisa de uma arquitetura customizada?
            </h3>
            <p className="max-w-2xl mx-auto mb-6 text-gray-600">
              Cada projeto é único. Desenvolvemos soluções sob medida que atendem exatamente às suas necessidades de negócio e requisitos técnicos.
            </p>
            <a
              href="#contact"
              className="inline-flex items-center px-6 py-3 font-semibold text-white transition-colors bg-blue-600 rounded-lg hover:bg-blue-700"
            >
              Discutir meu projeto
              <ArrowRight className="w-5 h-5 ml-2" />
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ProjectExamples;
