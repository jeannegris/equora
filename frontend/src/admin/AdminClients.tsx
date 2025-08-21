import React, { useEffect, useState } from 'react';
import { BACKEND_URL } from '../config';

interface Client {
  id: string;
  name: string;
  address?: string;
  phone?: string;
  email: string;
}

const AdminClients: React.FC = () => {
  const [clients, setClients] = useState<Client[]>([]);

  useEffect(() => {
  fetch(`${BACKEND_URL}/api/admin/clients`, { credentials: 'include' })
      .then(res => res.json())
      .then(data => setClients(data));
  }, []);

  return (
  <div className="p-6 text-blue-600 bg-white border border-gray-200 shadow rounded-2xl">
      <h2 className="mb-4 text-xl font-bold">Clientes</h2>
      <ul>
        {clients.map(c => (
          <li key={c.id} className="mb-2">
            <span className="font-bold">{c.name}</span> - {c.email} {c.phone && `- ${c.phone}`} {c.address && `- ${c.address}`}
          </li>
        ))}
      </ul>
      {/* Adicione cadastro/edição/exclusão conforme necessário */}
    </div>
  );
};

export default AdminClients;
