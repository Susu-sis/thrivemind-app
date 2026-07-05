'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import api from '@/lib/api';

interface Milestone {
  key: string;
  name: string;
  emoji: string;
  points_required: number;
}

interface GamificationData {
  total_points: number;
  milestones_unlocked: Milestone[];
  next_milestone: Milestone | null;
  history: Array<{ action: string; points: number; created_at: string }>;
}

const ACTION_LABELS: Record<string, string> = {
  checkin_diario: '✍️ Check-in diario',
  meditacion_completada: '🧘 Meditación',
  receta_analizada: '🍽️ Receta analizada',
  cosecha_registrada: '🌿 Cosecha',
  racha_7_dias: '🔥 Racha 7 días',
  racha_30_dias: '🏆 Racha 30 días',
};

export default function GamificacionPage() {
  const [data, setData] = useState<GamificationData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/gamification/')
      .then((res) => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-slate-400">Cargando progreso...</div>;
  }

  if (!data) return null;

  const nextPts = data.next_milestone ? data.next_milestone.points_required : data.total_points;
  const progress = data.next_milestone
    ? Math.min(100, Math.round((data.total_points / nextPts) * 100))
    : 100;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">🏆 Gamificación</h1>
        <p className="text-slate-400 mt-1">Tu progreso y logros en ThriveMind</p>
      </div>

      {/* Points card */}
      <Card className="bg-gradient-to-r from-amber-900/30 to-orange-900/30 border-amber-500/30">
        <CardContent className="p-6 text-center">
          <p className="text-5xl font-bold text-amber-300">{data.total_points}</p>
          <p className="text-sm text-slate-400 mt-1">puntos totales</p>
          {data.next_milestone && (
            <div className="mt-4">
              <div className="w-full bg-slate-700 rounded-full h-3">
                <div
                  className="bg-amber-400 h-3 rounded-full transition-all"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-xs text-slate-400 mt-2">
                {nextPts - data.total_points} puntos para {data.next_milestone.emoji} {data.next_milestone.name}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Milestones */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle>🎯 Hitos Desbloqueados</CardTitle>
        </CardHeader>
        <CardContent>
          {data.milestones_unlocked.length === 0 ? (
            <p className="text-slate-400 text-sm">Aún no has desbloqueado hitos. ¡Sigue acumulando puntos!</p>
          ) : (
            <div className="flex flex-wrap gap-3">
              {data.milestones_unlocked.map((m) => (
                <div key={m.key} className="flex items-center gap-2 bg-slate-700/50 rounded-lg px-3 py-2">
                  <span className="text-xl">{m.emoji}</span>
                  <div>
                    <p className="text-sm font-semibold text-white">{m.name}</p>
                    <p className="text-xs text-slate-400">{m.points_required} pts</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent history */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle>📜 Actividad Reciente</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {data.history.map((h, i) => (
            <div key={i} className="flex items-center justify-between py-2 border-b border-slate-700/50 last:border-0">
              <span className="text-sm text-slate-300">{ACTION_LABELS[h.action] || h.action}</span>
              <div className="flex items-center gap-3">
                <Badge className="bg-amber-600/20 text-amber-300">+{h.points}</Badge>
                <span className="text-xs text-slate-500">{h.created_at.slice(0, 10)}</span>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
