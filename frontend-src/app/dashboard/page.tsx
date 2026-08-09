'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ScatterChart, Scatter, ZAxis,
} from 'recharts';
import api from '@/lib/api';

interface DashboardData {
  serie_temporal: Array<{
    fecha: string;
    fecha_corta: string;
    estado_emocional: number;
    energia_fisica: number;
    horas_sueno: number;
    conexion_entorno: number;
  }>;
  promedios_pilares: Array<{ pilar: string; valor: number; fullMark: number }>;
  correlacion_sueno_emocional: Array<{ sueno: number; estado_emocional: number }>;
  estadisticas: {
    total_checkins: number;
    promedio_emocional: number;
    tendencia_texto: string;
    correlacion_texto: string;
  };
  mensaje?: string;
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/checkin/dashboard/tendencias?dias=14')
      .then((res) => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center h-full text-slate-400">Cargando dashboard...</div>;
  }

  if (!data || data.mensaje) {
    return (
      <div className="flex items-center justify-center h-full">
        <Card className="max-w-md border-slate-700 bg-slate-800/50">
          <CardContent className="p-8 text-center">
            <span className="text-4xl">📊</span>
            <p className="mt-4 text-slate-400">
              {data?.mensaje || 'Completa tu primer check-in para ver las tendencias.'}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard de Bienestar</h1>

      {/* Stats row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-slate-700 bg-slate-800/50">
          <CardContent className="p-4">
            <p className="text-sm text-slate-400">Check-ins realizados</p>
            <p className="text-2xl font-bold">{data.estadisticas.total_checkins}</p>
          </CardContent>
        </Card>
        <Card className="border-slate-700 bg-slate-800/50">
          <CardContent className="p-4">
            <p className="text-sm text-slate-400">Promedio emocional</p>
            <p className="text-2xl font-bold">{data.estadisticas.promedio_emocional}/10</p>
          </CardContent>
        </Card>
        <Card className="border-slate-700 bg-slate-800/50">
          <CardContent className="p-4">
            <p className="text-sm text-slate-400">Tendencia</p>
            <p className="text-2xl font-bold">{data.estadisticas.tendencia_texto}</p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Line Chart: Evolución temporal */}
        <Card className="border-slate-700 bg-slate-800/50">
          <CardHeader>
            <CardTitle className="text-lg">Evolución emocional</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data.serie_temporal}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="fecha_corta" stroke="#94a3b8" fontSize={12} />
                <YAxis domain={[1, 10]} stroke="#94a3b8" fontSize={12} />
                <Tooltip />
                <Line type="monotone" dataKey="estado_emocional" stroke="#8b5cf6" strokeWidth={2} name="Mente" />
                <Line type="monotone" dataKey="energia_fisica" stroke="#10b981" strokeWidth={2} name="Cuerpo" />
                <Line type="monotone" dataKey="conexion_entorno" stroke="#f59e0b" strokeWidth={2} name="Entorno" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Radar Chart: Promedios por pilar */}
        <Card className="border-slate-700 bg-slate-800/50">
          <CardHeader>
            <CardTitle className="text-lg">Balance de pilares</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={data.promedios_pilares}>
                <PolarGrid stroke="#334155" />
                <PolarAngleAxis dataKey="pilar" stroke="#94a3b8" fontSize={12} />
                <PolarRadiusAxis domain={[0, 10]} stroke="#475569" />
                <Radar dataKey="valor" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Scatter Chart: Correlación sueño-emocional */}
        <Card className="border-slate-700 bg-slate-800/50 lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg">La correlación invisible: Sueño vs Estado Emocional</CardTitle>
            <p className="text-sm text-slate-400">{data.estadisticas.correlacion_texto}</p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="sueno" name="Horas de sueño" stroke="#94a3b8" fontSize={12} />
                <YAxis dataKey="estado_emocional" name="Estado emocional" domain={[1, 10]} stroke="#94a3b8" fontSize={12} />
                <ZAxis range={[80, 80]} />
                <Tooltip />
                <Scatter data={data.correlacion_sueno_emocional} fill="#8b5cf6" />
              </ScatterChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
