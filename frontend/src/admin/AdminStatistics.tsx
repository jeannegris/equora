import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { defaultIcon } from './leafletIcon';
import 'leaflet/dist/leaflet.css';
import { BACKEND_URL } from '../config';

interface Access {
  ip: string;
  location?: {
    country?: string;
    city?: string;
    latitude?: number;
    longitude?: number;
  };
  timestamp: string;
}

const AdminStatistics: React.FC = () => {
  const [accesses, setAccesses] = useState<Access[]>([]);
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const fetchStats = () => {
    setLoading(true);
    let url = `${BACKEND_URL}/api/admin/stats/access`;
    if (startDate && endDate) {
      url += `?start=${startDate}&end=${endDate}`;
    }
    fetch(url, { credentials: 'include' })
      .then(res => res.json())
      .then(data => setAccesses(data))
      .finally(() => setLoading(false));
  };

  const handleClear = () => {
    if (window.confirm('Tem certeza que deseja limpar todas as estatísticas? Essa ação não pode ser desfeita.')) {
      fetch(`${BACKEND_URL}/api/admin/stats/access`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
      })
        .then(() => fetchStats());
    }
  };

  useEffect(() => {
    // Coletar IP do usuário e enviar sempre que o AdminStatistics montar
    fetch('https://api.ipify.org?format=json')
      .then(res => res.json())
      .then(({ ip }) => {
        fetch(`${BACKEND_URL}/api/admin/stats/access`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ip })
        }).catch(() => {});
      }).catch(() => {});
    fetchStats();
  }, []);

  return (
    <div className="flex flex-col h-full p-6 bg-white border border-gray-200 shadow rounded-2xl">
      <h2 className="mb-4 text-xl font-bold text-blue-600 shrink-0">Estatísticas de Acesso</h2>
      <div className="flex flex-col flex-1 min-h-0 gap-6 lg:flex-row">
        
        {/* Coluna Esquerda */}
        <div className="flex flex-col lg:w-2/5">
          <div className="flex flex-wrap items-center gap-4 mb-4 shrink-0">
            <label className="flex flex-col text-sm">
              Início:
              <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} className="px-2 py-1 mt-1 border rounded" />
            </label>
            <label className="flex flex-col text-sm">
              Fim:
              <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} className="px-2 py-1 mt-1 border rounded" />
            </label>
            <button onClick={fetchStats} className="self-end px-4 py-2 text-white transition bg-blue-600 rounded shadow hover:bg-blue-700">Filtrar</button>
            <button onClick={handleClear} className="self-end px-4 py-2 text-white transition bg-red-600 rounded shadow hover:bg-red-700">Limpar</button>
          </div>

          <div className="flex-1 min-h-0 p-2 overflow-y-auto border rounded">
            {loading ? (
              <div className="text-center text-gray-500">Carregando acessos...</div>
            ) : (
              <ul className="text-sm">
                {accesses.map((a, i) => (
                  <li key={i} className="mb-2">
                    <span className="font-bold">IP:</span> {a.ip}
                    {a.location && (
                      <span className="block text-xs text-gray-600">
                        {a.location.city}, {a.location.country}
                      </span>
                    )}
                    <span className="block text-xs text-gray-500">{new Date(a.timestamp).toLocaleString()}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Coluna Direita */}
        <div className="flex-1 lg:w-3/5">
          {loading ? (
            <div className="flex items-center justify-center w-full h-full text-gray-500">Carregando mapa...</div>
          ) : (
            <div className="w-full h-full overflow-hidden rounded-lg shadow-md">
              <MapContainer center={[0, 0]} zoom={2} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  attribution="&copy; OpenStreetMap contributors"
                />
                {accesses.filter(a => a.location && typeof a.location.latitude === 'number' && typeof a.location.longitude === 'number').map((a, i) => (
                  <Marker key={i} position={[a.location!.latitude!, a.location!.longitude!]} icon={defaultIcon as any}>
                    <Popup>
                      <div>
                        <strong>IP:</strong> {a.ip}<br />
                        <strong>Localização:</strong> {a.location?.city}, {a.location?.country}
                      </div>
                    </Popup>
                  </Marker>
                ))}
              </MapContainer>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminStatistics;
