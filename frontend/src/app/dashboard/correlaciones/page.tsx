'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import api from '@/lib/api';

interface MatrixCell {
  row: string;
  col: string;
  r: number | null;
  p: number | null;
}

interface MatrixData {
  labels: string[];
  cells: MatrixCell[];
  n_checkins: number;
  insufficient_data?: boolean;
}

export default function CorrelacionesPage() {
  const [data, setData] = useState<MatrixData | null>(null);
  const [loading, setLoading] = useState(true);
  const [dias, setDias] = useState(30);

  useEffect(() => {
    setLoading(true);
    api.get(`/insights/matrix?dias=${dias}`)
      .then((res) => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [dias]);

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-slate-400">Construyendo matriz...</div>;
  }

  if (!data || data.insufficient_data) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">🔗 Matriz de Interdependencias</h1>
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-8 text-center text-slate-400">
            <p>Necesitas al menos 5 check-ins. Actualmente: {data?.n_checkins ?? 0}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const cellColor = (r: number | null): string => {
    if (r === null) return 'bg-slate-700/40';
    if (r === 1.0) return 'bg-violet-600/30';
    if (r >= 0.6) return 'bg-green-600/40';
    if (r >= 0.3) return 'bg-green-600/20';
    if (r >= 0) return 'bg-slate-700/40';
    if (r >= -0.3) return 'bg-red-600/10';
    if (r >= -0.6) return 'bg-red-600/20';
    return 'bg-red-600/40';
  };

  const textColor = (r: number | null): string => {
    if (r === null) return 'text-slate-500';
    if (r === 1.0) return 'text-violet-300';
    if (r >= 0.3) return 'text-green-300';
    if (r >= -0.3) return 'text-slate-300';
    return 'text-red-300';
  };

  // Build a 2D structure from the flat cells array
  const labels = data.labels;
  const cellMap = new Map<string, MatrixCell>();
  data.cells.forEach((c) => cellMap.set(`${c.row}_${c.col}`, c));

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">🔗 Matriz de Interdependencias</h1>
          <p className="text-slate-400 mt-1">Correlaciones de Pearson entre todas las dimensiones de bienestar</p>
        </div>
        <div className="flex gap-2">
          {[14, 30, 60, 90].map((d) => (
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

      {/* Heatmap grid */}
      <Card className="bg-slate-800/50 border-slate-700 overflow-hidden">
        <CardHeader>
          <CardTitle>Mapa de Calor</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr>
                  <th className="p-3 text-left text-slate-400 text-sm"></th>
                  {labels.map((l) => (
                    <th key={l} className="p-3 text-center text-slate-300 text-sm font-medium">{l}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {labels.map((row) => (
                  <tr key={row}>
                    <td className="p-3 text-slate-300 text-sm font-medium">{row}</td>
                    {labels.map((col) => {
                      const cell = cellMap.get(`${row}_${col}`);
                      const r = cell?.r ?? null;
                      return (
                        <td key={col} className={`p-3 text-center ${cellColor(r)} border border-slate-700/50`}>
                          <span className={`text-lg font-bold ${textColor(r)}`}>
                            {r !== null ? r.toFixed(2) : '–'}
                          </span>
                          {cell?.p !== null && cell?.p !== undefined && r !== 1.0 && (
                            <div className="text-xs text-slate-500 mt-0.5">p={cell.p.toFixed(3)}</div>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Legend */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardContent className="p-4">
          <h3 className="text-sm font-medium text-slate-300 mb-3">Interpretación</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-green-600/40"></div>
              <span className="text-slate-300">Correlación fuerte (+)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-green-600/20"></div>
              <span className="text-slate-300">Correlación moderada (+)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-red-600/20"></div>
              <span className="text-slate-300">Correlación moderada (-)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-red-600/40"></div>
              <span className="text-slate-300">Correlación fuerte (-)</span>
            </div>
          </div>
          <p className="text-xs text-slate-500 mt-3">
            r cercano a +1 = ambas variables suben juntas. r cercano a -1 = una sube cuando la otra baja.
            p &lt; 0.05 indica significancia estadística. Basado en {data.n_checkins} check-ins.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
