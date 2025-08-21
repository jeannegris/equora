import React from 'react';
import { Search, PenTool, Rocket, BarChart } from 'lucide-react';
import { motion } from 'framer-motion';

const Process: React.FC = () => {
  const steps = [
    {
      icon: Search,
      title: 'Diagnóstico',
      description: 'Análise completa do cenário atual, identificação de gargalos e oportunidades de melhoria.',
      number: '01'
    },
    {
      icon: PenTool,
      title: 'Desenho',
      description: 'Criação da solução ideal, arquitetura técnica e definição de escopo detalhado.',
      number: '02'
    },
    {
      icon: Rocket,
      title: 'Entrega',
      description: 'Desenvolvimento ágil com entregas incrementais e acompanhamento contínuo.',
      number: '03'
    },
    {
      icon: BarChart,
      title: 'Medição',
      description: 'Monitoramento de métricas, análise de performance e otimização contínua.',
      number: '04'
    }
  ];

  return (
    <section id="process" className="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="container px-6 mx-auto">
        <div className="mb-16 text-center">
          <h2 className="mb-4 text-4xl font-bold text-gray-900">
            Como Trabalhamos
          </h2>
          <p className="max-w-3xl mx-auto text-xl text-gray-600">
            Nossa metodologia comprovada garante resultados efetivos e mensuráveis em cada projeto.
          </p>
        </div>

        <motion.div 
          className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.3 }}
          variants={{
            visible: {
              transition: {
                staggerChildren: 0.2
              }
            }
          }}
        >
          {steps.map((step, index) => (
            <motion.div 
              key={index} 
              className="relative"
              variants={{
                hidden: { opacity: 0, y: 20 },
                visible: { opacity: 1, y: 0 }
              }}
            >
              {/* Connector Line */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-12 left-full w-full h-0.5 bg-gradient-to-r from-blue-200 to-blue-300 z-0"></div>
              )}
              
              <div className="relative z-10 h-full p-6 transition-shadow bg-white border border-gray-100 shadow-sm rounded-2xl hover:shadow-lg">
                {/* Step Number */}
                <div className="absolute flex items-center justify-center w-8 h-8 text-sm font-bold text-white bg-blue-600 rounded-full -top-3 -right-3">
                  {step.number}
                </div>

                {/* Icon */}
                <div className="flex items-center justify-center w-12 h-12 mb-4 bg-blue-100 rounded-xl">
                  <step.icon className="w-6 h-6 text-blue-600" />
                </div>

                {/* Content */}
                <h3 className="mb-3 text-xl font-semibold text-gray-900">
                  {step.title}
                </h3>
                <p className="leading-relaxed text-gray-600">
                  {step.description}
                </p>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Process Flow Visualization */}
        <div className="p-8 mt-16 bg-white border border-gray-100 shadow-sm rounded-2xl">
          <div className="flex items-center justify-center space-x-4 text-sm text-gray-500">
            <span className="font-medium">Diagnóstico</span>
            <div className="w-8 h-0.5 bg-blue-200"></div>
            <span className="font-medium">Desenho</span>
            <div className="w-8 h-0.5 bg-blue-300"></div>
            <span className="font-medium">Entrega</span>
            <div className="w-8 h-0.5 bg-blue-400"></div>
            <span className="font-medium">Medição</span>
          </div>
          <p className="mt-4 text-center text-gray-600">
            Processo iterativo com feedback contínuo e melhorias incrementais
          </p>
        </div>
      </div>
    </section>
  );
};

export default Process;
