'use client';

import { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, Upload } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';

// Maps current hour to Tabla 3.6 (T7) circadian nutrition window
function getCircadianWindow() {
  const h = new Date().getHours() + new Date().getMinutes() / 60;
  if (h >= 6.5  && h < 8.5)  return { codigo: 'F2', label: 'Activación matutina',    precursor: 'L-Tirosina (T3-B)',   objetivo: '↑ Dopamina · foco',        emoji: '🌅' };
  if (h >= 8.5  && h < 11)   return { codigo: 'F3', label: 'Pico cognitivo',          precursor: 'Colina + Omega-3',    objetivo: '↑ Acetilcolina · memoria', emoji: '🧠' };
  if (h >= 11   && h < 15)   return { codigo: 'F4', label: 'Mediodía',                precursor: 'Triptófano + CH',     objetivo: '↑ Serotonina tarde',       emoji: '☀️'   };
  if (h >= 15   && h < 17.5) return { codigo: 'F5', label: 'Reactivación vespertina', precursor: 'L-Tirosina + Mg',     objetivo: '2.º pico dopaminérgico',  emoji: '⚡'    };
  if (h >= 19.5 && h < 21.5) return { codigo: 'F7', label: 'Transición crepuscular',  precursor: 'Triptófano nocturno', objetivo: 'Precarga melatonina',       emoji: '🌆' };
  return                             { codigo: 'F8', label: 'Preparación sueño',       precursor: 'Probióticos + GABA',  objetivo: '↓ Activación amigdalina',  emoji: '🌙' };
}

const FITNESS_GOALS = [
  { value: 'bajar_peso', label: '⬇️ Bajar peso' },
  { value: 'tonificar',  label: '💪 Tonificar'  },
  { value: 'mantener',   label: '⚖️ Mantener'   },
];

export default function CuerpoPage() {
  const circadianWindow = getCircadianWindow();
  const [fitnessGoal, setFitnessGoal] = useState('mantener');
  const [loading, setLoading] = useState(false);
  const [analisis, setAnalisis] = useState<Record<string, unknown> | null>(null);
  const [recLoading, setRecLoading] = useState(false);
  const [recomendacion, setRecomendacion] = useState<Record<string, unknown> | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const pedirRecomendacion = async () => {
    setRecLoading(true);
    try {
      const res = await api.post(`/cuerpo/nutricion/recomendacion?estado_emocional=5&emocion_principal=neutral&energia_fisica=5&horas_sueno=7&objetivo=${fitnessGoal}`);
      setRecomendacion(res.data);
      toast.success('Recomendación generada');
    } catch {
      toast.error('Error al generar recomendación');
    } finally {
      setRecLoading(false);
    }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    try {
      const res = await api.post('/cuerpo/nutricion/analizar-imagen', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setAnalisis(res.data);
      toast.success('Plato analizado con éxito');
    } catch {
      toast.error('Error al analizar la imagen');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">💚 Pilar Cuerpo</h1>
      <p className="text-slate-400">Analiza un plato con IA o recibe recomendaciones nutricionales personalizadas.</p>

      {/* Circadian nutrition banner — Tabla 3.6 T7 window */}
      <div className="flex flex-wrap items-center gap-3 rounded-lg border border-emerald-700/40 bg-emerald-900/20 px-4 py-2.5 text-sm">
        <span className="text-emerald-300 font-medium">{circadianWindow.emoji} {circadianWindow.codigo} · {circadianWindow.label}</span>
        <span className="text-slate-500">·</span>
        <span className="text-slate-400">Precursor óptimo ahora:</span>
        <span className="text-emerald-300 font-semibold">{circadianWindow.precursor}</span>
        <span className="text-slate-500">·</span>
        <span className="text-slate-400">{circadianWindow.objetivo}</span>
      </div>

      {/* Recomendación nutricional sin imagen */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>Recomendación Nutricional IA</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-slate-400">Recibe un consejo nutricional personalizado basado en tu estado actual, sin necesidad de imagen.</p>
          <div className="flex gap-2">
            {FITNESS_GOALS.map((g) => (
              <button
                key={g.value}
                onClick={() => setFitnessGoal(g.value)}
                className={`flex-1 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  fitnessGoal === g.value
                    ? 'bg-emerald-600/30 border border-emerald-500 text-emerald-200'
                    : 'bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {g.label}
              </button>
            ))}
          </div>
          <Button className="w-full" onClick={pedirRecomendacion} disabled={recLoading}>
            {recLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
            {recLoading ? 'Generando...' : '🥦 Obtener Recomendación'}
          </Button>
          {recomendacion && (
            <div className="mt-4 p-3 rounded-lg bg-emerald-900/20 border border-emerald-700/30 text-sm text-slate-200 whitespace-pre-wrap">
              {recomendacion.recomendacion as string}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Link to weekly meal planner */}
      <a
        href="/dashboard/meal-planner"
        className="flex items-center justify-between rounded-lg border border-slate-600 bg-slate-800/30 px-4 py-3 text-sm hover:bg-slate-700/40 transition-colors group"
      >
        <span className="text-slate-300">🍽️ Planificación semanal · 7 días × 3 comidas</span>
        <span className="text-emerald-400 group-hover:text-emerald-300 font-medium whitespace-nowrap">Ver Plan Semanal (Cocina en casa) →</span>
      </a>

      {/* Análisis de imagen — Modo 4 Comida Social */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>
            Analizar un Plato
            <span className="ml-2 text-xs font-normal text-slate-400 border border-slate-600 rounded px-1.5 py-0.5">Modo 4 — Comida Social</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-slate-400">Sube una foto de tu comida y GPT-4o la analizará nutricionalmente.</p>
          <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleUpload} />
          <Button className="w-full" variant="outline" onClick={() => fileInputRef.current?.click()} disabled={loading}>
            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Upload className="w-4 h-4 mr-2" />}
            {loading ? 'Analizando...' : 'Subir Imagen del Plato'}
          </Button>
        </CardContent>
      </Card>

      {/* Resultado del análisis */}
      {analisis && (
        <Card className="border-emerald-700/50 bg-slate-800/50">
          <CardHeader>
            <CardTitle>{(analisis.nombre_plato as string) || 'Análisis Nutricional'}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold">{analisis.calorias_est as number ?? '—'}</p>
                <p className="text-xs text-slate-400">kcal</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">{analisis.proteinas_g as number ?? '—'}g</p>
                <p className="text-xs text-slate-400">Proteínas</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">{analisis.carbohidratos_g as number ?? '—'}g</p>
                <p className="text-xs text-slate-400">Carbohidratos</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold">{analisis.grasas_g as number ?? '—'}g</p>
                <p className="text-xs text-slate-400">Grasas</p>
              </div>
            </div>
            <div className="prose prose-invert max-w-none text-slate-300 text-sm whitespace-pre-wrap">
              {analisis.analisis_texto as string}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
