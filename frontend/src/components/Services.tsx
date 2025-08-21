import React from 'react';
import { Building2, Code, Globe, Users } from 'lucide-react';

const Services: React.FC = () => {
  const services = [
    {
      icon: Building2,
      title: 'Arquitetura & Plataforma',
      description: 'Guardrails, escalabilidade e segurança para sistemas robustos e preparados para crescimento.',
      features: ['Desenho de arquitetura', 'Padrões de segurança', 'Escalabilidade automática'],
      imageUrl: 'https://images.unsplash.com/photo-1556155092-490a1ba16284?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
    },
    {
      icon: Code,
      title: 'Desenvolvimento Sob Medida',
      description: 'APIs, integrações e produtos end-to-end desenvolvidos especificamente para suas necessidades.',
      features: ['APIs customizadas', 'Integrações complexas', 'Produtos completos'],
      imageUrl: 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
    },
    {
      icon: Globe,
      title: 'Sites & Web Performance',
      description: 'Vitrine rápida, SEO técnico e Lighthouse verde para máxima performance e visibilidade.',
      features: ['Performance otimizada', 'SEO técnico', 'Core Web Vitals'],
      imageUrl: 'https://images.unsplash.com/photo-1618477388954-7852f32655ec?q=80&w=764&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
    },
    {
      icon: Users,
      title: 'Consultoria Contínua',
      description: 'Revisões mensais, métricas e roadmap para manter seus projetos sempre atualizados.',
      features: ['Revisões mensais', 'Análise de métricas', 'Roadmap estratégico'],
      imageUrl: 'https://images.unsplash.com/photo-1552664730-d307ca884978?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
    }
  ];

  return (
    <section id="services" className="py-20 bg-white">
      <div className="container px-6 mx-auto">
        <div className="mb-16 text-center">
          <h2 className="mb-4 text-4xl font-bold text-gray-900">
            Nossos Serviços
          </h2>
          <p className="max-w-3xl mx-auto text-xl text-gray-600">
            Soluções completas em TI, desde consultoria estratégica até desenvolvimento de sistemas complexos.
          </p>
        </div>

        <div className="space-y-16">
          {services.map((service, index) => (
            <div
              key={index}
              className={`flex flex-col md:flex-row items-center gap-8 md:gap-12 ${
                index % 2 !== 0 ? 'md:flex-row-reverse' : ''
              }`}
            >
              <div className="w-full md:w-1/2">
                <img 
                  src={service.imageUrl} 
                  alt={service.title} 
                  className="object-cover w-full h-full shadow-lg rounded-2xl"
                />
              </div>
              <div className="w-full md:w-1/2">
                <div className="flex items-start space-x-4">
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center w-12 h-12 transition-colors bg-blue-100 rounded-xl">
                      <service.icon className="w-6 h-6 text-blue-600" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="mb-3 text-xl font-semibold text-gray-900">
                      {service.title}
                    </h3>
                    <p className="mb-4 leading-relaxed text-gray-600">
                      {service.description}
                    </p>
                    <ul className="space-y-2">
                      {service.features.map((feature, featureIndex) => (
                        <li key={featureIndex} className="flex items-center text-sm text-gray-500">
                          <div className="w-1.5 h-1.5 bg-blue-600 rounded-full mr-3"></div>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Services;
