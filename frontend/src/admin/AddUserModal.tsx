import React, { useState } from 'react';
import { QRCodeCanvas } from 'qrcode.react';
import { BACKEND_URL } from '../config';

interface Props {
  onClose: () => void;
  onUserAdded: () => void;
}

const AddUserModal: React.FC<Props> = ({ onClose, onUserAdded }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [enable2fa, setEnable2fa] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [provisioningUri, setProvisioningUri] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username, email, password, enable_2fa: enable2fa }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Erro ao criar usuário');
      }

      if (data.provisioning_uri) {
        setProvisioningUri(data.provisioning_uri);
      }
      setSuccess(true);
      onUserAdded();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow-xl">
        {success ? (
          <div>
            <h2 className="mb-4 text-2xl font-bold text-center text-green-600">Usuário Criado!</h2>
            {provisioningUri ? (
              <>
                <p className="mb-4 text-center text-gray-700">
                  Peça para o usuário escanear o QR Code abaixo com o Microsoft Authenticator:
                </p>
                <div className="flex justify-center p-4 mb-6 bg-gray-100 border rounded">
                  <QRCodeCanvas value={provisioningUri} size={200} />
                </div>
              </>
            ) : (
              <p className="mb-6 text-center text-gray-700">O usuário foi criado com sucesso sem 2FA.</p>
            )}
            <button
              onClick={onClose}
              className="w-full px-4 py-2 font-bold text-white bg-blue-600 rounded hover:bg-blue-700 focus:outline-none focus:shadow-outline"
            >
              Fechar
            </button>
          </div>
        ) : (
          <>
            <h2 className="mb-6 text-2xl font-bold text-center text-gray-800">Adicionar Novo Usuário</h2>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block mb-2 text-sm font-bold text-gray-700" htmlFor="username">
                  Nome de Usuário
                </label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-3 py-2 leading-tight text-gray-700 border rounded shadow appearance-none focus:outline-none focus:shadow-outline"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block mb-2 text-sm font-bold text-gray-700" htmlFor="email">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 leading-tight text-gray-700 border rounded shadow appearance-none focus:outline-none focus:shadow-outline"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block mb-2 text-sm font-bold text-gray-700" htmlFor="password">
                  Senha
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-3 py-2 leading-tight text-gray-700 border rounded shadow appearance-none focus:outline-none focus:shadow-outline"
                  required
                />
              </div>
              <div className="mb-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={enable2fa}
                    onChange={(e) => setEnable2fa(e.target.checked)}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700">Habilitar Autenticação de Dois Fatores (2FA)</span>
                </label>
              </div>
              {error && <p className="mb-4 text-xs italic text-red-500">{error}</p>}
              <div className="flex items-center justify-between">
                <button
                  type="submit"
                  className="px-4 py-2 font-bold text-white bg-blue-600 rounded hover:bg-blue-700 focus:outline-none focus:shadow-outline"
                  disabled={loading}
                >
                  {loading ? 'Salvando...' : 'Salvar'}
                </button>
                <button
                  type="button"
                  onClick={onClose}
                  className="inline-block text-sm font-bold text-gray-600 align-baseline hover:text-gray-800"
                >
                  Cancelar
                </button>
              </div>
            </form>
          </>
        )}
      </div>
    </div>
  );
};

export default AddUserModal;
