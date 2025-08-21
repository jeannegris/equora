import React from 'react';
import { Cloud, Database, Globe, Monitor } from 'lucide-react';

const Technologies: React.FC = () => {
  const techStacks = [
    {
      icon: Cloud,
      category: 'Cloud Platforms',
      technologies: ['AWS', 'Azure', 'Google Cloud', 'Oracle Cloud', 'Vercel', 'Firebase'],
      color: 'bg-blue-50 text-blue-600'
    },
    {
      icon: Database,
      category: 'Backend',
      technologies: ['Node.js', '.NET Core', 'Python', 'Go', 'Rust', 'GraphQL', 'Docker', 'Kubernetes'],
      color: 'bg-green-50 text-green-600'
    },
    {
      icon: Globe,
      category: 'Frontend',
      technologies: ['React', 'Next.js', 'TypeScript', 'Vue.js', 'Svelte', 'Remix'],
      color: 'bg-purple-50 text-purple-600'
    },
    {
      icon: Monitor,
      category: 'Observabilidade',
      technologies: ['DataDog', 'New Relic', 'Grafana', 'Prometheus', 'OpenTelemetry', 'Dynatrace'],
      color: 'bg-orange-50 text-orange-600'
    }
  ];

  return (
    <section id="technologies" className="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="container px-6 mx-auto">
        <div className="mb-16 text-center">
          <h2 className="mb-4 text-4xl font-bold text-gray-900">
            Nossa Stack Tecnológica
          </h2>
          <p className="max-w-3xl mx-auto text-xl text-gray-600">
            Utilizamos as tecnologias mais modernas e confiáveis do mercado para garantir soluções robustas e escaláveis.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-8 mb-12 md:grid-cols-2 lg:grid-cols-4">
          {techStacks.map((stack, index) => (
            <div
              key={index}
              className="p-6 transition-shadow bg-white border border-gray-100 shadow-sm rounded-2xl hover:shadow-lg"
            >
              <div className={`w-12 h-12 ${stack.color} rounded-xl flex items-center justify-center mb-4`}>
                <stack.icon className="w-6 h-6" />
              </div>
              <h3 className="mb-3 text-lg font-semibold text-gray-900">
                {stack.category}
              </h3>
              <div className="space-y-2">
                {stack.technologies.map((tech, techIndex) => (
                  <div
                    key={techIndex}
                    className="inline-block px-3 py-1 mb-1 mr-2 text-sm text-gray-700 bg-gray-100 rounded-full"
                  >
                    {tech}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Featured Technologies Grid */}
        <div className="p-8 bg-white border border-gray-100 shadow-sm rounded-2xl">
          <h3 className="mb-6 text-2xl font-semibold text-center text-gray-900">
            Tecnologias Destacadas
          </h3>
          <div className="grid grid-cols-3 gap-4 md:grid-cols-6">
            {['AWS', 'Azure', 'GCP', 'Node.js', '.NET', 'React', 'Next.js', 'TypeScript', 'Docker', 'Kubernetes', 'MongoDB', 'PostgreSQL'].map((tech, index) => (
              <div
                key={index}
                className="flex items-center justify-center p-4 transition-colors cursor-pointer bg-gray-50 rounded-xl hover:bg-blue-50 hover:text-blue-600"
              >
                <span className="text-sm font-medium">{tech}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Certifications */}
        <div className="mt-12 text-center">
          <p className="mb-4 text-gray-600">Certificações e Parcerias</p>
          <div className="flex flex-wrap items-center justify-center gap-8 text-gray-400">
            <div className="px-6 py-3 bg-white border border-gray-200 rounded-lg">
              <span className="font-semibold">AWS Partner</span>
            </div>
            <div className="px-6 py-3 bg-white border border-gray-200 rounded-lg">
              <span className="font-semibold">Microsoft Gold</span>
            </div>
            <div className="px-6 py-3 bg-white border border-gray-200 rounded-lg">
              <span className="font-semibold">Google Cloud</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Technologies;
