import React from 'react';
import { Linkedin, Mail, MapPin } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-900 text-white py-16">
      <div className="container mx-auto px-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          {/* Logo and Description */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-3 mb-6">
              <div className="text-2xl font-bold text-blue-400">
                <span className="inline-block transform rotate-90">=</span>
                <span className="inline-block transform -rotate-90 -ml-1">=</span>
              </div>
              <span className="text-xl font-semibold">Equora Systems</span>
            </div>
            <p className="text-gray-400 mb-6 max-w-md leading-relaxed">
              Soluções de TI que equilibram performance e inovação. Consultoria, desenvolvimento e arquitetura para empresas que buscam excelência tecnológica.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-blue-600 transition-colors">
                <Linkedin className="w-5 h-5" />
              </a>
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-lg flex items-center justify-center hover:bg-blue-600 transition-colors">
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Services */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Serviços</h3>
            <ul className="space-y-3 text-gray-400">
              <li><a href="#" className="hover:text-white transition-colors">Arquitetura & Plataforma</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Desenvolvimento Sob Medida</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Sites & Web Performance</a></li>
              <li><a href="#" className="hover:text-white transition-colors">Consultoria Contínua</a></li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Contato</h3>
            <ul className="space-y-3 text-gray-400">
              <li className="flex items-center">
                <Mail className="w-4 h-4 mr-2" />
                contato@equorasystems.com
              </li>
              <li className="flex items-center">
                <MapPin className="w-4 h-4 mr-2" />
                Rio de Janeiro, Brasil
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 mb-4 md:mb-0">
              © 2024 Equora Systems. Todos os direitos reservados.
            </p>
            <div className="flex space-x-6 text-sm text-gray-400">
              <a href="#" className="hover:text-white transition-colors">Privacidade</a>
              <a href="#" className="hover:text-white transition-colors">Termos</a>
              <a href="#" className="hover:text-white transition-colors">Cookies</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;