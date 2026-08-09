'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, Upload } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';

// Maps current hour to Tabla 3.6 (T7) circadian nutrition window
function getCircadianWindow() {
  const h = new Date().getHours() + new Date().getMinutes() / 60;
  if (h >= 6.5  && h < 8.5)  return { label: 'Activación matutina',    descripcion: 'Arranca el día con energía y foco mental',                  emoji: '🌅', ejemplo: 'Huevo + aguacate'     };
  if (h >= 8.5  && h < 11)   return { label: 'Pico cognitivo',          descripcion: 'Tu mejor momento para concentrarte — aliméntate bien ahora', emoji: '🧠', ejemplo: 'Sardinas + nueces'    };
  if (h >= 11   && h < 15)   return { label: 'Mediodía',                descripcion: 'Tu cuerpo busca equilibrio — hora de una comida completa',   emoji: '☀️', ejemplo: 'Pavo/tofu + arroz'    };
  if (h >= 15   && h < 17.5) return { label: 'Tarde activa',            descripcion: 'Pequeño bajón de tarde — un snack ahora te reactiva',        emoji: '⚡', ejemplo: 'Almendras + proteína' };
  if (h >= 19.5 && h < 21.5) return { label: 'Cena ligera',             descripcion: 'Tu cuerpo empieza a prepararse para descansar',              emoji: '🌆', ejemplo: 'Avena + plátano'      };
  return                             { label: 'Antes de dormir',         descripcion: 'Hora de calmar el cuerpo — evita cenar pesado',              emoji: '🌙', ejemplo: 'Kéfir + cacao puro'   };
}

const FITNESS_GOALS = [
  { value: 'bajar_peso', label: '⬇️ Bajar peso' },
  { value: 'tonificar',  label: '💪 Tonificar'  },
  { value: 'mantener',   label: '⚖️ Mantener'   },
];

// Client-side snack suggestions anchored to T3 block (Tabla 3.6 + §3.3.2)
function getSnacksForWindow(): string[] {
  const h = new Date().getHours() + new Date().getMinutes() / 60;
  if (h >= 6.5  && h < 8.5)  return ['🥚 Huevo + aguacate',         '🥣 Yogur griego + nueces',   '🥤 Batido de proteína'];
  if (h >= 8.5  && h < 11)   return ['🌰 Nueces del Brasil',         '�ae6️ Arándanos + almendras',    '🐟 Salmón ahumado'];
  if (h >= 11   && h < 15)   return ['🍏 Manzana + cacahuete',       '🥝 Hummus + zanahoria',         '🧀 Queso cottage'];
  if (h >= 15   && h < 17.5) return ['🍫 Almendras + choco 85 %', '🍌 Plátano + mantequilla',     '🪫 Dátiles + nueces'];
  if (h >= 19.5 && h < 21.5) return ['🥛 Kéfir + plátano',           '🌿 Manzanilla + miel',           '🌾 Avena con canela'];
  return                             ['🥛 Kéfir natural',              '🍫 Cacao puro + nueces',         '🌿 Infusión de valeriana'];
}

export default function CuerpoPage() {
  const [circadianWindow, setCircadianWindow] = useState<ReturnType<typeof getCircadianWindow> | null>(null);
  const [snacks, setSnacks] = useState<string[]>([]);
  const [fitnessGoal, setFitnessGoal] = useState('mantener');
  const [checkinValues, setCheckinValues] = useState({
    estado_emocional: 5, energia_fisica: 5, horas_sueno: 7, emocion_principal: 'neutral',
  });
  const [loading, setLoading] = useState(false);

  // Compute time-dependent values client-side only (avoids SSR hydration mismatch)
  useEffect(() => {
    setCircadianWindow(getCircadianWindow());
    setSnacks(getSnacksForWindow());
  }, []);

  // Personalize recommendation with last real check-in values
  useEffect(() => {
    api.get('/checkins/dashboard/tendencias?dias=30')
      .then((res) => {
        const serie = res.data?.serie_temporal;
        if (serie?.length > 0) {
          const ultimo = serie[serie.length - 1];
          setCheckinValues({
            estado_emocional:  ultimo.estado_emocional  ?? 5,
            energia_fisica:    ultimo.energia_fisica    ?? 5,
            horas_sueno:       ultimo.horas_sueno       ?? 7,
            emocion_principal: ultimo.emocion_principal || 'neutral',
          });
        }
      })
      .catch(() => {});
  }, []);
  const [analisis, setAnalisis] = useState<Record<string, unknown> | null>(null);
  const [recLoading, setRecLoading] = useState(false);
  const [recomendacion, setRecomendacion] = useState<Record<string, unknown> | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [despensaAnalisis, setDespensaAnalisis] = useState<Record<string, unknown> | null>(null);
  const [despensaLoading, setDespensaLoading] = useState(false);
  const despensaInputRef = useRef<HTMLInputElement>(null);
  const [preComidaScore, setPreComidaScore] = useState<number | null>(null);
  const [preComidaSaved, setPreComidaSaved] = useState(false);
  const [postComidaSaved, setPostComidaSaved] = useState(false);

  const pedirRecomendacion = async () => {
    setRecLoading(true);
    try {
      const res = await api.post(
        `/cuerpo/nutricion/recomendacion?estado_emocional=${checkinValues.estado_emocional}&emocion_principal=${checkinValues.emocion_principal}&energia_fisica=${checkinValues.energia_fisica}&horas_sueno=${checkinValues.horas_sueno}&objetivo=${fitnessGoal}`,
      );
      setRecomendacion(res.data);
      toast.success('Recomendación generada');
    } catch {
      toast.error('Error al generar recomendación');
    } finally {
      setRecLoading(false);
    }
  };

  const savePreComida = (score: number) => {
    setPreComidaScore(score);
    api.post('/checkins', { estado_emocional: score, energia_fisica: 5, horas_sueno: 7, emocion_principal: 'pre_comida' }).catch(() => {});
    setPreComidaSaved(true);
  };

  const savePostComida = (score: number) => {
    api.post('/checkins', { estado_emocional: score, energia_fisica: 5, horas_sueno: 7, emocion_principal: 'post_comida' }).catch(() => {});
    setPostComidaSaved(true);
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
      api.post('/gamification/award?action=receta_analizada').catch(() => {});
      toast.success('Plato analizado con éxito');
    } catch {
      toast.error('Error al analizar la imagen');
    } finally {
      setLoading(false);
    }
  };

  const handleDespensaUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    setDespensaLoading(true);
    try {
      const res = await api.post('/cuerpo/despensa/analizar', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setDespensaAnalisis(res.data);
      toast.success('Despensa analizada');
    } catch {
      toast.error('Error al analizar la despensa');
    } finally {
      setDespensaLoading(false);
      if (despensaInputRef.current) despensaInputRef.current.value = '';
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">💚 Pilar Cuerpo</h1>
      <p className="text-slate-400">Analiza un plato con IA o recibe recomendaciones nutricionales personalizadas.</p>

      {/* Inputs biométricos — wearables (§3.3.2 Capa de Personalización Fase 2) */}
      <div className="rounded-lg border border-dashed border-slate-600 bg-slate-800/20 px-4 py-3">
        <div className="flex items-start gap-3">
          <span className="text-xl mt-0.5">📡</span>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <p className="text-sm font-medium text-slate-300">Inputs biométricos · Wearables</p>
              <span className="text-[10px] bg-violet-800/40 border border-violet-600/40 text-violet-300 px-1.5 py-0.5 rounded">Fase 2</span>
            </div>
          </div>
        </div>
      </div>

      {/* Circadian nutrition banner — Tabla 3.6 T7 window: WHEN to eat and what category */}
      {circadianWindow && (
        <div className="flex flex-wrap items-center gap-3 rounded-lg border border-emerald-700/40 bg-emerald-900/20 px-4 py-2.5 text-sm">
          <span className="text-emerald-300 font-medium">{circadianWindow.emoji} {circadianWindow.label}</span>
          <span className="text-slate-500">·</span>
          <span className="text-slate-400">{circadianWindow.descripcion}</span>
          <span className="text-slate-500">·</span>
          <span className="text-slate-500 text-xs">Ahora:</span>
          <span className="text-emerald-200 italic text-xs">{circadianWindow.ejemplo}</span>
        </div>
      )}

      {/* Snacks funcionales — client-side, T3 block aware (§3.3.2 RF-007) */}
      {snacks.length > 0 && (
        <div className="rounded-lg border border-slate-700 bg-slate-800/30 px-4 py-3">
          <p className="text-sm font-medium text-slate-300 mb-2">🍎 Snacks funcionales para ahora</p>
          <div className="flex flex-wrap gap-2">
            {snacks.map((s, i) => (
              <span key={i} className="text-xs bg-slate-700/60 border border-slate-600 text-slate-300 rounded-full px-3 py-1.5">
                {s}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recomendación nutricional sin imagen */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>Recomendación Nutricional IA</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-slate-400">¿El plato de hoy no encaja con cómo te sientes? Ajústalo en base a tu estado actual.</p>
          <a href="/dashboard/recomendaciones" className="inline-block text-xs text-emerald-400 hover:text-emerald-300 underline-offset-2 hover:underline">Ver acciones personalizadas para hoy →</a>
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
          <div className="flex items-center gap-2">
            <CardTitle>Analizar un Plato</CardTitle>
            <span className="text-xs font-normal text-slate-400 border border-slate-600 rounded px-1.5 py-0.5">Comida Social</span>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Pre-comida contextual check-in (§3.4.1) */}
          <div className="rounded-lg border border-slate-700/50 bg-slate-800/20 px-3 py-2.5">
            <p className="text-xs text-slate-400 mb-2">¿Cómo estás <span className="font-medium text-slate-300">antes</span> de comer? <span className="text-slate-600">· Diario Inteligente</span></p>
            {!preComidaSaved ? (
              <div className="flex gap-2">
                {['😔', '😕', '😐', '🙂', '😊'].map((emoji, i) => (
                  <button key={i} onClick={() => savePreComida(i * 2 + 2)}
                    className={`text-xl rounded-lg px-2 py-1 transition-all hover:scale-110 hover:bg-slate-700/50 ${
                      preComidaScore === i * 2 + 2 ? 'bg-emerald-600/20 border border-emerald-600/40' : ''
                    }`}>
                    {emoji}
                  </button>
                ))}
              </div>
            ) : (
              <p className="text-xs text-emerald-400">✓ Estado pre-comida guardado</p>
            )}
          </div>
          <p className="text-sm text-slate-400">Sube una foto de tu comida y GPT-4o la analizará nutricionalmente.</p>
          <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleUpload} />
          <Button className="w-full" variant="outline" onClick={() => fileInputRef.current?.click()} disabled={loading}>
            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Upload className="w-4 h-4 mr-2" />}
            {loading ? 'Analizando...' : 'Subir Imagen del Plato'}
          </Button>
        </CardContent>
      </Card>

      {/* Resultado del análisis + post-comida check-in */}
      {analisis && (
        <>
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
          {/* Post-comida contextual check-in (§3.4.1) */}
          <div className="rounded-lg border border-emerald-700/30 bg-emerald-900/10 px-4 py-3 space-y-2">
            <p className="text-sm text-slate-300">🍽️ ¿Cómo te sientes <span className="font-medium text-emerald-300">después</span> de comer? <span className="text-slate-600 text-xs">· Diario Inteligente</span></p>
            {!postComidaSaved ? (
              <div className="flex gap-2">
                {['😔', '😕', '😐', '🙂', '😊'].map((emoji, i) => (
                  <button key={i} onClick={() => savePostComida(i * 2 + 2)}
                    className="text-xl rounded-lg px-2 py-1 hover:bg-emerald-700/30 hover:scale-110 transition-all">
                    {emoji}
                  </button>
                ))}
              </div>
            ) : (
              <p className="text-xs text-emerald-400">✓ Registro guardado en tu Diario</p>
            )}
          </div>
        </>
      )}

      {/* Análisis de despensa — RF-006 */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>📦 Analizar mi Despensa</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-slate-400">Sube una foto de tu despensa y la IA identifica ingredientes disponibles para optimizar tus recetas semanales.</p>
          <input ref={despensaInputRef} type="file" accept="image/*" className="hidden" onChange={handleDespensaUpload} />
          <Button className="w-full" variant="outline" onClick={() => despensaInputRef.current?.click()} disabled={despensaLoading}>
            {despensaLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Upload className="w-4 h-4 mr-2" />}
            {despensaLoading ? 'Analizando...' : 'Fotografiar Despensa'}
          </Button>
          {despensaAnalisis && (
            <div className="mt-4 p-3 rounded-lg bg-emerald-900/20 border border-emerald-700/30 text-sm text-slate-200 whitespace-pre-wrap">
              {despensaAnalisis.analisis_texto as string}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
