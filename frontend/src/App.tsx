import Header from './components/Header';
import Hero from './components/Hero';
import Services from './components/Services';
import Process from './components/Process';
import ProjectExamples from './components/ProjectExamples';
import Results from './components/Results';
import Technologies from './components/Technologies';
import CTA from './components/CTA';
import Footer from './components/Footer';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import AdminLayout from './admin/AdminLayout';
import BackToTopButton from './components/BackToTopButton';
import React, { useEffect } from 'react';
import { BACKEND_URL } from './config';

function App() {

  useEffect(() => {
    // Enviar estatística de acesso sempre que a aplicação montar
    fetch('https://api.ipify.org?format=json')
      .then(res => res.json())
      .then(({ ip }) => {
        fetch(`${BACKEND_URL}/api/admin/stats/access`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ip })
        }).catch(() => {});
      }).catch(() => {});
  }, []);

  return (
    <BrowserRouter basename="/equora">
      <Routes>
        <Route path="/admin" element={<AdminLayout />} />
        <Route path="/" element={
          <div className="min-h-screen">
            <Header />
            <Hero />
            <Services />
            <Process />
            <ProjectExamples />
            <Results />
            <Technologies />
            <CTA />
            <Footer />
          </div>
        } />
      </Routes>
      <BackToTopButton />
    </BrowserRouter>
  );
}

export default App;
