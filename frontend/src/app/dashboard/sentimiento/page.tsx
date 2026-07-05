'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import api from '@/lib/api';

interface KeywordEntry {
  word: string;
  count: number;
}

interface TopEmotion {
  emotion: string;
  score: number;
  pct: number;
}

interface SentimentData {
  emotion_distribution: Record<string, number>;
  keyword_cloud: KeywordEntry[];
  top_emotions: TopEmotion[];
  insight: string;
  total_notes_analyzed: number;
}

const EMOTION_COLORS: Record<string, string> = {
  'alegría': '#facc15',
  calma: '#6ee7b7',
  gratitud: '#c084fc',
  'motivación': '#f97316',
  ansiedad: '#ef4444',
  tristeza: '#60a5fa',
  'frustración': '#dc2626',
  cansancio: '#94a3b8',
  'energía': '#34d399',
  esperanza: '#a78bfa',
};

export default function SentimientoPage() {
  const [data, setData] = useState<SentimentData | null>(null);
  const [loading, setLoading] = useState(true);
  const [dias, setDias] = useState(7);

  useEffect(() => {
    setLoading(true);
    api.get(`/insights/sentiment?dias=${dias}`)
      .then((res) => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [dias]);

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-slate-400">Analizando sentimiento...</div>;
  }

  if (!data || data.total_notes_analyzed === 0) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">💬 Análisis de Sentimiento</h1>
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-8 text-center text-slate-400">
            <p>No hay notas personales en tus check-ins recientes. Agrega notas para ver el análisis.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const chartData = Object.entries(data.emotion_distribution)
    .map(([emocion, porcentaje]) => ({ emocion, conteo: Math.round(porcentaje), porcentaje }))
    .sort((a, b) => b.conteo - a.conteo);

  // Build a word-cloud-like display from keyword_cloud array
  const keywords = data.keyword_cloud.slice(0, 20);
  const maxCount = keywords.length > 0 ? keywords[0].count : 1;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">💬 Análisis de Sentimiento</h1>
          <p className="text-slate-400 mt-1">Emociones detectadas en tus notas de check-in</p>
        </div>
        <div className="flex gap-2">
          {[7, 14, 30].map((d) => (
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

      {/* Top emotions */}
      <div className="flex gap-2 flex-wrap">
        {data.top_emotions.map((em) => (
          <Badge
            key={em.emotion}
            className="text-sm px-3 py-1"
            style={{ backgroundColor: (EMOTION_COLORS[em.emotion] || '#8b5cf6') + '33', color: EMOTION_COLORS[em.emotion] || '#c4b5fd' }}
          >
            {em.emotion} ({em.pct}%)
          </Badge>
        ))}
      </div>

      {/* Emotion Distribution Bar Chart */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle>Distribución de Emociones</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                <XAxis type="number" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <YAxis
                  dataKey="emocion"
                  type="category"
                  stroke="#94a3b8"
                  tick={{ fontSize: 12 }}
                  width={90}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: 8 }}
                  formatter={(value: number, _: string, props: any) => [`${value} (${props.payload.porcentaje}%)`, 'Menciones']}
                />
                <Bar dataKey="conteo" radius={[0, 4, 4, 0]}>
                  {chartData.map((entry) => (
                    <Cell key={entry.emocion} fill={EMOTION_COLORS[entry.emocion] || '#8b5cf6'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Keyword Cloud */}
      {keywords.length > 0 && (
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle>Nube de Palabras Clave</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3 items-center justify-center py-4">
              {keywords.map((kw) => {
                const scale = 0.8 + (kw.count / maxCount) * 1.2;
                const opacity = 0.5 + (kw.count / maxCount) * 0.5;
                return (
                  <span
                    key={kw.word}
                    className="text-violet-300 hover:text-violet-100 transition-colors cursor-default"
                    style={{ fontSize: `${scale}rem`, opacity }}
                  >
                    {kw.word}
                  </span>
                );
              })}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Insight */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle>🔍 Insight</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-300">{data.insight}</p>
          <p className="text-xs text-slate-500 mt-3">Basado en {data.total_notes_analyzed} notas de los últimos {dias} días</p>
        </CardContent>
      </Card>
    </div>
  );
}
