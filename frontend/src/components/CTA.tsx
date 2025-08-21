import React from 'react';
import { Calendar, Mail, Phone } from 'lucide-react';

const CTA: React.FC = () => {
  return (
    <section id="contact" className="py-20 bg-gradient-to-r from-blue-600 to-indigo-700">
      <div className="container px-6 mx-auto">
        <div className="max-w-6xl mx-auto">
          <div className="grid items-center gap-12 md:grid-cols-2">
            <div className="text-center md:text-left">
              <h2 className="mb-6 text-4xl font-bold text-white md:text-5xl">
                Pronto para Transformar sua TI?
              </h2>
              <p className="max-w-3xl mx-auto mb-10 text-xl text-blue-100 md:mx-0">
                Agende uma conversa gratuita e descubra como podemos otimizar seus sistemas, reduzir custos e acelerar seu crescimento.
              </p>
              <a
                href="#"
                className="inline-flex items-center px-8 py-4 text-lg font-semibold text-blue-600 transition-colors bg-white rounded-lg shadow-lg hover:bg-gray-50 hover:shadow-xl"
              >
                <Calendar className="w-6 h-6 mr-3" />
                Agendar Consulta Gratuita
              </a>
            </div>
            <div className="flex items-center justify-center">
              <img 
                src="https://plus.unsplash.com/premium_photo-1675731938738-f477ac955955?q=80&w=870&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" 
                alt="Consultor Equora Systems"
                className="object-cover w-64 h-64 rounded-full shadow-2xl ring-4 ring-white/20"
              />
            </div>
          </div>

          {/* Contact Options */}
          <div className="grid grid-cols-1 gap-6 mt-16 mb-10 md:grid-cols-3">
            <div className="flex flex-col items-center p-6 border bg-white/10 backdrop-blur-sm rounded-xl border-white/20">
              <Phone className="w-8 h-8 mb-3 text-white" />
              <h3 className="mb-2 text-lg font-semibold text-white">Telefone</h3>
              <p className="text-blue-100">(21) 97939-6699</p>
            </div>
            
            <div className="flex flex-col items-center p-6 border bg-white/10 backdrop-blur-sm rounded-xl border-white/20">
              <Mail className="w-8 h-8 mb-3 text-white" />
              <h3 className="mb-2 text-lg font-semibold text-white">Email</h3>
              <p className="text-blue-100">contato@equorasystems.com</p>
            </div>
            
            <div className="flex flex-col items-center p-6 border bg-white/10 backdrop-blur-sm rounded-xl border-white/20">
              <Calendar className="w-8 h-8 mb-3 text-white" />
              <h3 className="mb-2 text-lg font-semibold text-white">Calendly</h3>
              <p className="text-blue-100">Disponível 24/7</p>
            </div>
          </div>

          {/* Value Proposition */}
          <div className="grid grid-cols-1 gap-8 text-center md:grid-cols-3">
            <div>
              <div className="mb-2 text-3xl font-bold text-white">15 min</div>
              <div className="text-blue-100">Consulta inicial gratuita</div>
            </div>
            <div>
              <div className="mb-2 text-3xl font-bold text-white">24h</div>
              <div className="text-blue-100">Resposta garantida</div>
            </div>
            <div>
              <div className="mb-2 text-3xl font-bold text-white">0%</div>
              <div className="text-blue-100">Compromisso até aprovação</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTA;
