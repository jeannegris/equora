import React, { useEffect, useState, useCallback } from 'react';
import { BACKEND_URL } from '../config';
import AddUserModal from './AddUserModal';
import EditUserModal from './EditUserModal';

interface User {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  twofa_secret?: string | null;
}

const AdminUsers: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [currentUser, setCurrentUser] = useState<User | null>(null);

  const fetchUsers = useCallback(() => {
    fetch(`${BACKEND_URL}/api/admin/users`, { credentials: 'include' })
      .then(res => res.ok ? res.json() : Promise.reject(res))
      .then(data => setUsers(data))
      .catch(() => setUsers([]));
  }, []);

  useEffect(() => {
    fetchUsers();
    // Buscar usuário logado
    fetch(`${BACKEND_URL}/api/admin/login/me`, { credentials: 'include' })
      .then(res => res.ok ? res.json() : Promise.reject(res))
      .then(data => setCurrentUser(data.user))
      .catch(() => setCurrentUser(null));
  }, [fetchUsers]);

  const handleDelete = async (userId: string) => {
    if (window.confirm('Tem certeza que deseja excluir este usuário?')) {
      await fetch(`${BACKEND_URL}/api/admin/users/${userId}`, {
        method: 'DELETE',
        credentials: 'include',
      });
      fetchUsers();
    }
  };

  return (
    <div className="p-6 bg-white border border-gray-200 shadow rounded-2xl">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-blue-600">Gerenciamento de Usuários</h2>
        <button
          onClick={() => setIsAddModalOpen(true)}
          className="px-4 py-2 font-bold text-white bg-blue-600 rounded-lg shadow-md hover:bg-blue-700"
        >
          Adicionar Usuário
        </button>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-2 text-left">Usuário</th>
              <th className="px-4 py-2 text-left">Status</th>
              <th className="px-4 py-2 text-left">2FA</th>
              <th className="px-4 py-2 text-right">Ações</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id} className="border-b">
                <td className="px-4 py-2">
                  <div className="font-bold">{u.username}</div>
                  <div className="text-sm text-gray-600">{u.email}</div>
                </td>
                <td className="px-4 py-2">
                  {u.is_admin && <span className="px-2 py-1 mr-2 text-xs font-semibold text-white bg-indigo-500 rounded-full">Admin</span>}
                  <span className={`px-2 py-1 text-xs font-semibold text-white rounded-full ${u.is_active ? 'bg-green-500' : 'bg-gray-400'}`}>
                    {u.is_active ? 'Ativo' : 'Inativo'}
                  </span>
                </td>
                <td className="px-4 py-2">
                  <span className={`px-2 py-1 text-xs font-semibold text-white rounded-full ${u.twofa_secret ? 'bg-blue-500' : 'bg-gray-400'}`}>
                    {u.twofa_secret ? 'Ativo' : 'Inativo'}
                  </span>
                </td>
                <td className="px-4 py-2 text-right">
                  {currentUser?.is_admin && (
                    <>
                      <button onClick={() => setEditingUser(u)} className="mr-2 text-sm text-blue-600 hover:underline">Editar</button>
                      <button onClick={() => handleDelete(u.id)} className="text-sm text-red-600 hover:underline">Excluir</button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {isAddModalOpen && (
        <AddUserModal
          onClose={() => setIsAddModalOpen(false)}
          onUserAdded={fetchUsers}
        />
      )}
      {editingUser && (
        <EditUserModal
          user={editingUser}
          onClose={() => setEditingUser(null)}
          onUserUpdated={fetchUsers}
        />
      )}
    </div>
  );
};

export default AdminUsers;
