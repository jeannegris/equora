import React, { useState } from 'react';
import AdminServices from './AdminServices';
import AdminStatistics from './AdminStatistics';
import AdminClients from './AdminClients';
import AdminUsers from './AdminUsers';

const TABS = [
  { label: 'Serviços', component: <AdminServices /> },
  { label: 'Estatísticas', component: <AdminStatistics /> },
  { label: 'Clientes', component: <AdminClients /> },
  { label: 'Usuários', component: <AdminUsers /> },
];

interface AdminTabsProps {
  onTabChange: (component: React.ReactNode) => void;
}

const AdminTabs: React.FC<AdminTabsProps> = ({ onTabChange }) => {
  const [active, setActive] = useState(0);

  const handleTabClick = (index: number) => {
    setActive(index);
    onTabChange(TABS[index].component);
  };

  // Efeito para definir a aba inicial
  React.useEffect(() => {
    onTabChange(TABS[0].component);
  }, [onTabChange]);

  return (
    <aside className="w-64 p-4 text-white bg-gray-800">
      <h2 className="mb-6 text-2xl font-bold">Equora</h2>
      <nav className="flex flex-col gap-2">
        {TABS.map((tab, i) => (
          <button
            key={tab.label}
            onClick={() => handleTabClick(i)}
            className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
              active === i
                ? 'bg-blue-600'
                : 'hover:bg-gray-700'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </nav>
    </aside>
  );
};

export default AdminTabs;
