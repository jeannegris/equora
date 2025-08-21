import React, { useState } from 'react';
import { BACKEND_URL } from '../config';

interface TwoFactorAuthData {
  tempToken: string;
  provisioningUri: string | null;
}

interface Props {
  onAuthSuccess: () => void;
  onTwoFactorRequired: (data: TwoFactorAuthData) => void;
}

const AdminLogin: React.FC<Props> = ({ onAuthSuccess, onTwoFactorRequired }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${BACKEND_URL}/api/admin/login/password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Erro de conexão');

      if (data['2fa_required']) {
        onTwoFactorRequired({
          tempToken: data.temp_token,
          provisioningUri: data.provisioning_uri,
        });
      } else {
        onAuthSuccess();
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-500 to-indigo-600">
      <div className="w-full max-w-sm p-8 space-y-8 bg-white rounded-lg shadow-xl">
        <h2 className="text-3xl font-extrabold text-center text-gray-900">Login Admin</h2>
        <form className="space-y-6" onSubmit={handlePasswordSubmit}>
          <input
            type="text"
            placeholder="Usuário"
            value={username}
            onChange={e => setUsername(e.target.value)}
            className="w-full px-4 py-3 text-gray-700 bg-gray-100 border-transparent rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
            required
            autoComplete="username"
          />
          <input
            type="password"
            placeholder="Senha"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="w-full px-4 py-3 text-gray-700 bg-gray-100 border-transparent rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
            required
            autoComplete="current-password"
          />
          {error && <p className="text-sm text-center text-red-500">{error}</p>}
          <button type="submit" disabled={loading} className="w-full px-4 py-3 font-bold text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            {loading ? 'Verificando...' : 'Entrar'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AdminLogin;
