import React, { useState } from 'react';
import { QRCodeCanvas } from 'qrcode.react';
import { BACKEND_URL } from '../config';

interface Props {
  tempToken: string;
  provisioningUri: string | null;
  onAuthSuccess: () => void;
}

const Admin2FASetup: React.FC<Props> = ({ tempToken, provisioningUri, onAuthSuccess }) => {
  const [twofaCode, setTwofaCode] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);


  const handle2faSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${BACKEND_URL}/api/admin/login/2fa`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ temp_token: tempToken, twofa_code: twofaCode }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Erro de conexão');
      }
      onAuthSuccess();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-500 to-indigo-600">
      <div className="w-full max-w-sm p-8 space-y-8 bg-white rounded-lg shadow-xl">
        <h2 className="text-3xl font-extrabold text-center text-gray-900">Autenticação 2FA</h2>
        {provisioningUri && (
          <div className="text-center">
            <p className="mb-2 text-sm text-gray-600">Primeiro login com 2FA. Escaneie o QR Code:</p>
            <div className="flex justify-center p-2 bg-gray-100 border rounded">
              <QRCodeCanvas value={provisioningUri} size={180} />
            </div>
          </div>
        )}
        <form className="space-y-6" onSubmit={handle2faSubmit}>
          <input
            type="text"
            placeholder="Código 2FA"
            value={twofaCode}
            onChange={e => setTwofaCode(e.target.value)}
            className="w-full px-4 py-3 text-gray-700 bg-gray-100 border-transparent rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white"
            required
            autoComplete="one-time-code"
          />
          {error && <p className="text-sm text-center text-red-500">{error}</p>}
          <button type="submit" disabled={loading} className="w-full px-4 py-3 font-bold text-white bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            {loading ? 'Validando...' : 'Validar'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Admin2FASetup;
