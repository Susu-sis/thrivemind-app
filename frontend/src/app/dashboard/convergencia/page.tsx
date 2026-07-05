'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts';
import api from '@/lib/api';

interface PillarScores {
  mente: number;
  cuerpo: number;
  entorno: number;
  sueno: number;
}

interface ConvergencePoint {
  fecha: string;
  fecha_corta: string;
  mente: number;
  cuerpo: number;
  entorno: number;
}

interface MatrixEntry {
  r: number;
  p: number;
}

interface ConvergenceData {
  pillar_scores: PillarScores;
  convergence_series: ConvergencePoint[];
  interdependency_matrix: Record<string, MatrixEntry>;
  insights: string[];
  n_checkins: number;
  dias: number;
  insufficient_data?: boolean;
}

export default function ConvergenciaPage() {
  const [data, setData] = useState<ConvergenceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [dias, setDias] = useState(14);

  useEffect(() => {
    setLoading(true);
    api.get(`/insights/convergence?dias=${dias}`)
      .then((res) => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [dias]);

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-slate-400">Analizando convergencia...</div>;
  }

  if (!data || data.insufficient_data) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">📈 Dashboard de Convergencia</h1>
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-8 text-center text-slate-400">
            <p>Necesitas al menos 3 check-ins para ver la convergencia. Actualmente: {data?.n_checkins ?? 0}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const scoreColor = (v: number) => {
    if (v >= 7) return 'text-green-400';
    if (v >= 5) return 'text-yellow-400';
    return 'text-red-400';
  };

  const pillars = [
    { key: 'mente', label: 'Mente', emoji: '🧠', color: '#8b5cf6' },
    { key: 'cuerpo', label: 'Cuerpo', emoji: '💚', color: '#10b981' },
    { key: 'entorno', label: 'Entorno', emoji: '🌱', color: '#f59e0b' },
    { key: 'sueno', label: 'Sueño', emoji: '😴', color: '#6366f1' },
  ];

  const rLabel = (r: number) => {
    const abs = Math.abs(r);
    if (abs >= 0.7) return 'Fuerte';
    if (abs >= 0.4) return 'Moderada';
    if (abs >= 0.2) return 'Débil';
    return 'Ninguna';
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">📈 Dashboard de Convergencia</h1>
          <p className="text-slate-400 mt-1">Cómo interactúan tus 3 pilares del bienestar</p>
        </div>
        <div className="flex gap-2">
          {[7, 14, 30, 60].map((d) => (
            <button
              key={d}
              onClick={() => setDias(d)}
              className={`px-3 py-1 rounded text-sm ${
                dias === d ? 'bg-violet-600 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {d}d
            </button>
          ))}
        </div>
      </div>

      {/* Pillar score cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {pillars.map(({ key, label, emoji }) => {
          const score = data.pillar_scores[key as keyof PillarScores];
          return (
            <Card key={key} className="bg-slate-800/50 border-slate-700">
              <CardContent className="p-4 text-center">
                <span className="text-2xl">{emoji}</span>
                <p className="text-sm text-slate-400 mt-1">{label}</p>
                <p className={`text-3xl font-bold mt-1 ${scoreColor(score)}`}>{score}</p>
                <p className="text-xs text-slate-500">/10</p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Convergence line chart */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle>Evolución de los 3 Pilares</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.convergence_series}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="fecha_corta" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 10]} stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: 8 }}
                  labelStyle={{ color: '#e2e8f0' }}
                />
                <Legend />
                <Line type="monotone" dataKey="mente" stroke="#8b5cf6" strokeWidth={2} name="Mente" dot={false} />
                <Line type="monotone" dataKey="cuerpo" stroke="#10b981" strokeWidth={2} name="Cuerpo" dot={false} />
                <Line type="monotone" dataKey="entorno" stroke="#f59e0b" strokeWidth={2} name="Entorno" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Cross-correlation summary */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle>Correlaciones entre Pilares</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(data.interdependency_matrix).map(([pair, entry]) => {
              const [a, b] = pair.split('_');
              const r = entry.r;
              const bg = r > 0.4 ? 'bg-green-600/10 border-green-500/20' : r > 0 ? 'bg-slate-700/50 border-slate-600/20' : 'bg-red-600/10 border-red-500/20';
              return (
                <div key={pair} className={`rounded-lg p-4 border ${bg}`}>
                  <p className="text-sm text-slate-300 capitalize">{a} ↔ {b}</p>
                  <p className="text-2xl font-bold mt-1">{r.toFixed(3)}</p>
                  <Badge className="mt-1 text-xs">{rLabel(r)}</Badge>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Insights */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle>🔍 Insights</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {data.insights.map((insight, i) => (
            <div key={i} className="flex items-start gap-2">
              <span className="text-violet-400 mt-0.5">•</span>
              <p className="text-slate-300">{insight}</p>
            </div>
          ))}
          <p className="text-xs text-slate-500 mt-3">Basado en {data.n_checkins} check-ins de {data.dias} días</p>
        </CardContent>
      </Card>
    </div>
  );
}
