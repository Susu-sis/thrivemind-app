'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import api from '@/lib/api';

interface ContextEntry {
  id: string;
  context_key: string;
  context_label: string;
  hue_profile: string;
  mood_before: number;
  energy_before: number;
  mood_after: number;
  energy_after: number;
  meditation_completed: boolean;
  created_at: string;
}

export default function HistorialPage() {
  const [history, setHistory] = useState<ContextEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/insights/context-history?limit=20')
      .then((res) => setHistory(res.data.history || []))
      .catch(() => setHistory([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-slate-400">Cargando historial...</div>;
  }

  const delta = (before: number, after: number) => {
    const diff = after - before;
    if (diff > 0) return <span className="text-green-400">+{diff}</span>;
    if (diff < 0) return <span className="text-red-400">{diff}</span>;
    return <span className="text-slate-400">0</span>;
  };

  const formatDate = (iso: string) => {
    const d = new Date(iso);
    return d.toLocaleDateString('es-ES', { weekday: 'short', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">📜 Historial de Contextos</h1>
        <p className="text-slate-400 mt-1">Registro de recomendaciones aplicadas y su impacto en tu bienestar</p>
      </div>

      {history.length === 0 ? (
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-8 text-center text-slate-400">
            <p>Aún no hay contextos registrados. Usa las recomendaciones holísticas para comenzar.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {history.map((entry) => (
            <Card key={entry.id} className="bg-slate-800/50 border-slate-700">
              <CardContent className="p-4">
                <div className="flex flex-col md:flex-row md:items-center gap-4">
                  {/* Context info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-white">{entry.context_label}</h3>
                      {entry.meditation_completed && (
                        <Badge className="bg-violet-600/20 text-violet-300 text-xs">🧘 Meditación</Badge>
                      )}
                    </div>
                    <p className="text-xs text-slate-500 mt-1">{formatDate(entry.created_at)}</p>
                    <div className="text-sm text-slate-400 mt-1">
                      Perfil HUE: <span className="text-slate-300">{entry.hue_profile.replace(/_/g, ' ')}</span>
                    </div>
                  </div>

                  {/* Before / After */}
                  <div className="flex gap-6">
                    <div className="text-center">
                      <p className="text-xs text-slate-500 uppercase tracking-wide">Ánimo</p>
                      <div className="flex items-center gap-1 mt-1">
                        <span className="text-slate-400">{entry.mood_before}</span>
                        <span className="text-slate-600">→</span>
                        <span className="text-white font-semibold">{entry.mood_after}</span>
                        <span className="text-sm ml-1">({delta(entry.mood_before, entry.mood_after)})</span>
                      </div>
                    </div>
                    <div className="text-center">
                      <p className="text-xs text-slate-500 uppercase tracking-wide">Energía</p>
                      <div className="flex items-center gap-1 mt-1">
                        <span className="text-slate-400">{entry.energy_before}</span>
                        <span className="text-slate-600">→</span>
                        <span className="text-white font-semibold">{entry.energy_after}</span>
                        <span className="text-sm ml-1">({delta(entry.energy_before, entry.energy_after)})</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
