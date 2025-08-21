import React, { useState } from 'react';
import { BACKEND_URL } from '../config';

interface User {
  id: string;
  username: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  twofa_secret?: string | null;
}

interface Props {
  user: User;
  onClose: () => void;
  onUserUpdated: () => void;
}

const EditUserModal: React.FC<Props> = ({ user, onClose, onUserUpdated }) => {
  const [username, setUsername] = useState(user.username);
  const [email, setEmail] = useState(user.email);
  const [password, setPassword] = useState('');
  const [isActive, setIsActive] = useState(user.is_active);
  const [isAdmin, setIsAdmin] = useState(user.is_admin);
  const [enable2fa, setEnable2fa] = useState(!!user.twofa_secret);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const payload: any = {
      username,
      email,
      is_active: isActive,
      is_admin: isAdmin,
      enable_2fa: enable2fa,
    };
    if (password) {
      payload.password = password;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/users/${user.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Erro ao atualizar usuário');
      }

      onUserUpdated();
      onClose(); // Fechar após sucesso
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-xl">
        <h2 className="mb-6 text-2xl font-bold text-center text-gray-800">Editar Usuário</h2>
        <form onSubmit={handleSubmit}>
          {/* Campos do formulário (username, email, password, etc.) */}
          <div className="mb-4">
            <label className="block mb-2 text-sm font-bold text-gray-700">Nome de Usuário</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} className="w-full px-3 py-2 border rounded" required />
          </div>
          <div className="mb-4">
            <label className="block mb-2 text-sm font-bold text-gray-700">Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full px-3 py-2 border rounded" required />
          </div>
          <div className="mb-4">
            <label className="block mb-2 text-sm font-bold text-gray-700">Nova Senha (deixe em branco para não alterar)</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full px-3 py-2 border rounded" />
          </div>
          <div className="flex justify-between mb-4">
            <label className="flex items-center">
              <input type="checkbox" checked={isActive} onChange={(e) => setIsActive(e.target.checked)} className="mr-2" />
              Ativo
            </label>
            <label className="flex items-center">
              <input type="checkbox" checked={isAdmin} onChange={(e) => setIsAdmin(e.target.checked)} className="mr-2" />
              Admin
            </label>
            <label className="flex items-center">
              <input type="checkbox" checked={enable2fa} onChange={(e) => setEnable2fa(e.target.checked)} className="mr-2" />
              2FA Habilitado
            </label>
          </div>
          {error && <p className="mb-4 text-xs italic text-red-500">{error}</p>}

          <div className="flex items-center justify-between">
            <button type="submit" className="px-4 py-2 font-bold text-white bg-blue-600 rounded hover:bg-blue-700" disabled={loading}>
              {loading ? 'Salvando...' : 'Salvar Alterações'}
            </button>
            <button type="button" onClick={onClose} className="text-sm font-bold text-gray-600">
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditUserModal;
