'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import api from '@/lib/api';

interface HolisticData {
  context_label: string;
  hora: number;
  urgency?: string;
  estado?: { emocional: number; energia: number; sueno: number; emocion: string };
  pillar_mente?: {
    meditacion: { titulo: string; objetivo: string; duracion_min: number };
    hue: { perfil: string; kelvin: number; brillo_pct: number; descripcion: string };
  };
  pillar_cuerpo?: {
    nutricion: { grupo_alimenticio: string; ejemplo_comida: string; razon: string };
  };
  pillar_entorno?: {
    planta_accion: string;
    clima: { descripcion: string; temperatura: number };
  };
}

interface Recommendation {
  type: string;
  icon: string;
  title: string;
  reason: string;
  action_label: string;
  action_href: string;
}

export default function InsightsPage() {
  const [holistic, setHolistic] = useState<HolisticData | null>(null);
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [evidencia, setEvidencia] = useState<{titulo: string; autores: string; año: number; pilar: string}[]>([]);

  const cargarInsights = () => {
    setLoading(true);
    Promise.all([
      api.get('/insights/holistic').catch(() => null),
      api.get('/insights/recommendations').catch(() => null),
      api.get('/insights/evidencia?tema=bienestar+mindfulness+nutricion').catch(() => null),
    ]).then(([hRes, rRes, eRes]) => {
      if (hRes?.data) setHolistic(hRes.data);
      if (rRes?.data?.recommendations) setRecs(rRes.data.recommendations);
      if (eRes?.data?.papers) setEvidencia(eRes.data.papers);
    }).finally(() => setLoading(false));
  };

  useEffect(() => { cargarInsights(); }, []);

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-slate-400">Cargando recomendaciones...</div>;
  }

  const urgencyColor = (u?: string) => {
    if (u === 'alta') return 'bg-red-600/20 text-red-300';
    if (u === 'media') return 'bg-yellow-600/20 text-yellow-300';
    return 'bg-green-600/20 text-green-300';
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">💡 Recomendaciones Holísticas</h1>
          <p className="text-slate-400 mt-1">Acciones personalizadas basadas en tu estado actual</p>
        </div>
        <button onClick={cargarInsights}
          className="px-4 py-2 bg-slate-600 hover:bg-slate-500 text-white rounded-lg text-sm transition-colors">
          🔄 Actualizar
        </button>
      </div>

      {/* Holistic 3-pillar card */}
      {holistic && (
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <Badge className={urgencyColor(holistic.urgency)}>
              {holistic.urgency === 'alta' ? '⚠️ Urgencia Alta' : holistic.urgency === 'media' ? '⚡ Urgencia Media' : '✅ Estado OK'}
            </Badge>
            <span className="text-sm text-slate-400">Contexto: {holistic.context_label}</span>
            {holistic.estado && (
              <span className="text-xs text-slate-500">
                Ánimo {holistic.estado.emocional}/10 · Energía {holistic.estado.energia}/10
              </span>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Mente */}
            {holistic.pillar_mente && (
              <Card className="border border-violet-500/30 bg-slate-800/50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center gap-2">🧠 Mente</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="font-semibold text-white">{holistic.pillar_mente.meditacion.titulo}</p>
                  <p className="text-sm text-slate-300">
                    {holistic.pillar_mente.meditacion.objetivo} · {holistic.pillar_mente.meditacion.duracion_min} min
                  </p>
                  <div className="text-xs text-slate-400 mt-2">
                    🎨 HUE: {holistic.pillar_mente.hue.perfil} ({holistic.pillar_mente.hue.kelvin}K, brillo {holistic.pillar_mente.hue.brillo_pct}%)
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Cuerpo */}
            {holistic.pillar_cuerpo && (
              <Card className="border border-emerald-500/30 bg-slate-800/50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center gap-2">💚 Cuerpo</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="font-semibold text-white">{holistic.pillar_cuerpo.nutricion.ejemplo_comida}</p>
                  <p className="text-sm text-slate-300">{holistic.pillar_cuerpo.nutricion.grupo_alimenticio}</p>
                  <p className="text-xs text-slate-400 mt-1">{holistic.pillar_cuerpo.nutricion.razon}</p>
                </CardContent>
              </Card>
            )}

            {/* Entorno */}
            {holistic.pillar_entorno && (
              <Card className="border border-amber-500/30 bg-slate-800/50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center gap-2">🌱 Entorno</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <p className="font-semibold text-white">{holistic.pillar_entorno.planta_accion}</p>
                  <p className="text-sm text-slate-300">
                    🌡️ {holistic.pillar_entorno.clima.temperatura}°C — {holistic.pillar_entorno.clima.descripcion}
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}

      {/* Personalized recommendations */}
      {recs.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">🎯 Recomendaciones Personalizadas</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recs.map((rec, i) => (
              <Card key={i} className="bg-slate-800/50 border-slate-700 hover:border-slate-500 transition-colors">
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{rec.icon}</span>
                    <div className="flex-1">
                      <h3 className="font-semibold text-white">{rec.title}</h3>
                      <p className="text-sm text-slate-300 mt-1">{rec.reason}</p>
                      <div className="mt-3">
                        <Badge className="bg-violet-600/20 text-violet-300">{rec.action_label}</Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {!holistic && recs.length === 0 && (
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-8 text-center text-slate-400">
            <p className="text-lg">Realiza tu primer check-in para recibir recomendaciones personalizadas.</p>
          </CardContent>
        </Card>
      )}

      {/* RAG Scientific Evidence — compact footnote */}
      {evidencia.length > 0 && (
        <div className="border-t border-slate-700 pt-4 mt-4">
          <p className="text-xs text-slate-500 font-medium mb-2">📚 Evidencia científica que fundamenta estas recomendaciones (RAG corpus)</p>
          <ul className="space-y-1">
            {evidencia.map((p, i) => (
              <li key={i} className="text-xs text-slate-500">
                [{i + 1}] {p.autores} ({p.año}). <span className="italic">{p.titulo}</span>.{p.doi && <span className="text-slate-600"> DOI: {p.doi}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
