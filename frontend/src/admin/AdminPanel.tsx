import React, { useState } from 'react';
import AdminTabs from './AdminTabs';

interface Props {
  onLogout: () => void;
}

const AdminPanel: React.FC<Props> = ({ onLogout }) => {
  const [activeTabContent, setActiveTabContent] = useState<React.ReactNode>(null);

  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* O componente AdminTabs será nossa sidebar */}
      <AdminTabs onTabChange={setActiveTabContent} />

      {/* Conteúdo Principal */}
      <div className="flex flex-col flex-1">
        <header className="flex items-center justify-between p-4 bg-white border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-800">Painel Administrativo</h1>
          <button
            onClick={onLogout}
            className="px-4 py-2 font-semibold text-white bg-blue-600 rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75"
          >
            Sair
          </button>
        </header>
        <main className="flex-1 p-6">
          {/* O conteúdo da aba ativa será renderizado aqui, gerenciado pelo AdminTabs */}
          {activeTabContent}
        </main>
      </div>
    </div>
  );
};

export default AdminPanel;
