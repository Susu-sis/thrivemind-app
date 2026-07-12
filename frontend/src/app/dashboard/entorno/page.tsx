'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';

interface Cultivo {
  id: string;
  nombre_planta: string;
  tipo: string;
  estado: string;
  fecha_siembra: string;
  fecha_cosecha_est: string | null;
  activo: boolean;
}

export default function EntornoPage() {
  const [cultivos, setCultivos] = useState<Cultivo[]>([]);
  const [loading, setLoading] = useState(true);
  const [clima, setClima] = useState<Record<string, unknown> | null>(null);
  const [consejo, setConsejo] = useState<string | null>(null);
  const [consejoLoading, setConsejoLoading] = useState(false);
  const [consulta, setConsulta] = useState('');

  useEffect(() => {
    Promise.all([
      api.get('/entorno/cultivos').then((r) => setCultivos(r.data)),
      api.get('/entorno/clima').then((r) => setClima(r.data)).catch(() => null),
    ]).finally(() => setLoading(false));
  }, []);

  const pedirConsejo = async () => {
    if (!consulta.trim()) { toast.error('Escribe una consulta primero'); return; }
    setConsejoLoading(true);
    try {
      const res = await api.post(`/entorno/consejo?consulta=${encodeURIComponent(consulta)}`);
      setConsejo(res.data.respuesta || JSON.stringify(res.data));
      toast.success('Consejo generado');
    } catch {
      toast.error('Error al obtener consejo');
    } finally {
      setConsejoLoading(false);
    }
  };

  const agregarCultivo = async (planta: string, tipo: string) => {
    try {
      const res = await api.post(`/entorno/cultivos?nombre_planta=${encodeURIComponent(planta)}&tipo=${encodeURIComponent(tipo)}`);
      setCultivos([...cultivos, res.data]);
      toast.success(`${planta} añadida a tus cultivos`);
    } catch {
      toast.error('Error al añadir el cultivo');
    }
  };

  const eliminarCultivo = async (id: string, nombre: string) => {
    try {
      await api.delete(`/entorno/cultivos/${id}`);
      setCultivos(cultivos.filter((c) => c.id !== id));
      toast.success(`${nombre} eliminado`);
    } catch {
      toast.error('Error al eliminar el cultivo');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-full text-slate-400"><Loader2 className="animate-spin" /></div>;
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">🌱 Pilar Entorno</h1>
      <p className="text-slate-400">Micro-farming urbano y conexión con la naturaleza.</p>

      {/* Clima actual */}
      {clima && (
        <Card className="border-slate-700 bg-slate-800/50">
          <CardContent className="p-4 flex items-center gap-4">
            <span className="text-3xl">🌤️</span>
            <div>
              <p className="font-medium">{clima.descripcion as string}</p>
              <p className="text-sm text-slate-400">{clima.temperatura as number}°C — {clima.ciudad as string}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Cultivos activos */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>Tus Cultivos</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {cultivos.length === 0 ? (
            <p className="text-slate-400 text-sm">Aún no tienes cultivos. ¡Empieza con una planta!</p>
          ) : (
            cultivos.map((c) => (
              <div key={c.id} className="flex items-center justify-between p-3 rounded-lg bg-slate-700/50">
                <div>
                  <p className="font-medium">{c.nombre_planta}</p>
                  <p className="text-xs text-slate-400">
                    Sembrada: {c.fecha_siembra}
                    {c.fecha_cosecha_est && ` — Cosecha est.: ${c.fecha_cosecha_est}`}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="outline">{c.estado}</Badge>
                  <button onClick={() => eliminarCultivo(c.id, c.nombre_planta)}
                    className="text-red-400 hover:text-red-300 text-xs px-2 py-1 rounded hover:bg-red-900/30 transition-colors">
                    ✕
                  </button>
                </div>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      {/* Consejo IA */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>🌿 Consejo de Cultivo con IA</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-slate-400">Pregunta sobre tus plantas, clima o temporada y obtén consejo personalizado.</p>
          <input
            value={consulta}
            onChange={(e) => setConsulta(e.target.value)}
            placeholder="Ej: ¿Qué debo plantar en verano? ¿Cómo cuido mi menta?"
            className="w-full px-3 py-2 rounded-lg bg-slate-700 border border-slate-600 text-sm text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-emerald-500"
          />
          <Button className="w-full" onClick={pedirConsejo} disabled={consejoLoading}>
            {consejoLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
            {consejoLoading ? 'Consultando IA...' : '🤖 Obtener Consejo'}
          </Button>
          {consejo && (
            <div className="mt-3 p-3 rounded-lg bg-emerald-900/20 border border-emerald-700/30 text-sm text-slate-200 whitespace-pre-wrap">
              {consejo}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Plantas sugeridas */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>Plantas Recomendadas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3">
            {[
              { nombre: 'Menta', tipo: 'hierba' },
              { nombre: 'Lavanda', tipo: 'flor' },
              { nombre: 'Albahaca', tipo: 'hierba' },
              { nombre: 'Manzanilla', tipo: 'flor' },
              { nombre: 'Romero', tipo: 'hierba' },
            ].map((p) => (
              <Button key={p.nombre} variant="outline" className="justify-start"
                onClick={() => agregarCultivo(p.nombre, p.tipo)}>
                🌿 {p.nombre}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
