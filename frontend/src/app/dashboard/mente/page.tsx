'use client';

import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';

// ── Breathing module types ───────────────────────────────────────────────────

type TechniqueKey = 'coherencia' | 'box';

interface BreathPhase {
  label: string;
  duration: number; // seconds
  scale: number;    // circle scale 0.7–1.5
  color: string;    // tailwind ring color class
}

const TECHNIQUES: Record<TechniqueKey, { title: string; subtitle: string; phases: BreathPhase[] }> = {
  coherencia: {
    title: '💚 Coherencia Cardíaca',
    subtitle: '5 s inhala · 5 s exhala · ciclo de 10 s',
    phases: [
      { label: 'Inhala...', duration: 5, scale: 1.45, color: 'ring-green-400' },
      { label: 'Exhala...', duration: 5, scale: 0.75, color: 'ring-blue-400' },
    ],
  },
  box: {
    title: '⬜ Box Breathing',
    subtitle: '4 s inhala · 4 s mantén · 4 s exhala · 4 s mantén',
    phases: [
      { label: 'Inhala...', duration: 4, scale: 1.45, color: 'ring-green-400' },
      { label: 'Mantén',    duration: 4, scale: 1.45, color: 'ring-yellow-400' },
      { label: 'Exhala...', duration: 4, scale: 0.75, color: 'ring-blue-400' },
      { label: 'Mantén',    duration: 4, scale: 0.75, color: 'ring-slate-400' },
    ],
  },
};

// Maps each objetivo to a complementary HUE profile (§3.3.1 orquestación lumínica)
const HUE_POR_OBJETIVO: Record<string, { perfil: string; kelvin: number; brillo: number }> = {
  calma:    { perfil: 'Meditación Calma',    kelvin: 2700, brillo: 40 },
  enfoque:  { perfil: 'Trabajo Productivo',  kelvin: 5000, brillo: 80 },
  gratitud: { perfil: 'Naturaleza Indoor',   kelvin: 4500, brillo: 65 },
  energia:  { perfil: 'Trabajo Productivo',  kelvin: 5000, brillo: 80 },
  sueno:    { perfil: 'Lectura Nocturna',    kelvin: 2500, brillo: 30 },
  ansiedad: { perfil: 'Relajación Profunda', kelvin: 2200, brillo: 20 },
};

// Derives suggested objetivo from current hour (Tabla 3.4 contextual adaptation)
function getSugerenciaContextual() {
  const h = new Date().getHours();
  if (h >= 6  && h < 9)  return { objetivo: 'enfoque',  etiqueta: '🎯 Enfoque',  franja: 'Amanecer · sesión de activación' };
  if (h >= 9  && h < 12) return { objetivo: 'energia',  etiqueta: '⚡ Energía',  franja: 'Mañana · boost mental' };
  if (h >= 12 && h < 16) return { objetivo: 'calma',    etiqueta: '🌊 Calma',    franja: 'Mediodía · reset de 5 min' };
  if (h >= 16 && h < 19) return { objetivo: 'gratitud', etiqueta: '🙏 Gratitud', franja: 'Tarde · momento de reflexión' };
  if (h >= 19 && h < 22) return { objetivo: 'calma',    etiqueta: '🌊 Calma',    franja: 'Noche · transición y desconexión' };
  return                         { objetivo: 'sueno',    etiqueta: '🌙 Sueño',    franja: 'Noche tardía · preparar el sueño' };
}

function BreathingExercise({ suggestedTechnique = null }: { suggestedTechnique?: TechniqueKey | null }) {
  const [technique, setTechnique] = useState<TechniqueKey>('coherencia');
  const [running, setRunning] = useState(false);
  const [phaseIdx, setPhaseIdx] = useState(0);
  const [countdown, setCountdown] = useState(0);
  const [rounds, setRounds] = useState(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const phases = TECHNIQUES[technique].phases;
  const currentPhase = running ? phases[phaseIdx] : phases[0];

  const stop = () => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    setRunning(false);
    setPhaseIdx(0);
    setCountdown(phases[0].duration);
    setRounds(0);
  };

  const start = () => {
    setPhaseIdx(0);
    setCountdown(phases[0].duration);
    setRounds(0);
    setRunning(true);
  };

  // Reset countdown when technique changes
  useEffect(() => {
    stop();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [technique]);

  // Auto-select technique when meditation result suggests one
  useEffect(() => {
    if (suggestedTechnique) setTechnique(suggestedTechnique);
  }, [suggestedTechnique]);

  // Drive the timer
  useEffect(() => {
    if (!running) return;
    intervalRef.current = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          // advance phase
          setPhaseIdx((pi) => {
            const next = (pi + 1) % phases.length;
            if (next === 0) setRounds((r) => r + 1);
            return next;
          });
          // next phase duration will be set in the next tick via phaseIdx
          return -1; // sentinel
        }
        return prev - 1;
      });
    }, 1000);
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [running, phases]);

  // Sync countdown when phase changes
  useEffect(() => {
    if (running) setCountdown(phases[phaseIdx].duration);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [phaseIdx]);

  const scale = running ? currentPhase.scale : 1;
  const ringColor = running ? currentPhase.color : 'ring-slate-600';
  const phaseLabel = running ? currentPhase.label : 'Listo para empezar';

  return (
    <Card className="border-slate-700 bg-slate-800/50">
      <CardHeader>
        <CardTitle className="text-lg">Ejercicio de Respiración</CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        {/* Technique selector */}
        <div className="flex gap-2">
          {(Object.keys(TECHNIQUES) as TechniqueKey[]).map((key) => (
            <button
              key={key}
              onClick={() => setTechnique(key)}
              className={`px-3 py-1.5 rounded text-sm transition-colors ${
                technique === key
                  ? 'bg-violet-600 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {TECHNIQUES[key].title}
            </button>
          ))}
        </div>
        <p className="text-xs text-slate-400">{TECHNIQUES[technique].subtitle}</p>

        {/* Animated circle */}
        <div className="flex flex-col items-center gap-4 py-4">
          <div
            className={`w-28 h-28 rounded-full ring-4 ${ringColor} bg-slate-700/60 flex items-center justify-center transition-all`}
            style={{ transform: `scale(${scale})`, transition: 'transform 0.9s ease-in-out' }}
          >
            <span className="text-2xl font-light text-slate-200 select-none">
              {running ? countdown : ''}
            </span>
          </div>
          <p className="text-slate-300 text-lg font-medium tracking-wide">{phaseLabel}</p>
          {running && rounds > 0 && (
            <p className="text-xs text-slate-500">{rounds} {rounds === 1 ? 'ciclo completado' : 'ciclos completados'}</p>
          )}
        </div>

        {/* Controls */}
        <div className="flex justify-center gap-3">
          {!running ? (
            <Button onClick={start} className="bg-violet-600 hover:bg-violet-500 px-6">
              ▶ Comenzar
            </Button>
          ) : (
            <Button onClick={stop} variant="outline" className="border-slate-600 px-6">
              ■ Detener
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
const CLIMA_EMOJI: Record<string, string> = {
  sol: '☀️', despejado: '🌤️', nublado: '☁️', lluvia: '🌧️',
  tormenta: '⛈️', niebla: '🌫️', nieve: '❄️',
};

// Maps backend técnica string to a TechniqueKey for the breathing exercise
function mapTecnicaToKey(tecnica: string): TechniqueKey | null {
  const t = tecnica.toLowerCase();
  if (t.includes('coherencia') || t.includes('card')) return 'coherencia';
  if (t.includes('box') || t.includes('caja') || t.includes('cuadrada')) return 'box';
  return null;
}
// ── Main page ────────────────────────────────────────────────────────────────

export default function MentePage() {
  const [sugerencia, setSugerencia] = useState<ReturnType<typeof getSugerenciaContextual> | null>(null);
  const [intencion, setIntencion] = useState('');
  const [objetivo, setObjetivo] = useState('calma');
  const [loading, setLoading] = useState(false);
  const [meditacion, setMeditacion] = useState<{ guion: string; tecnica: string } | null>(null);
  const [clima, setClima] = useState<{ temperatura: number; clasificacion: string } | null>(null);
  const [feedbackScore, setFeedbackScore] = useState<number | null>(null);
  const [feedbackSaved, setFeedbackSaved] = useState(false);
  const [preMedScore, setPreMedScore] = useState<number | null>(null);
  const [preMedSaved, setPreMedSaved] = useState(false);

  useEffect(() => {
    const s = getSugerenciaContextual();
    setSugerencia(s);
    setObjetivo(s.objetivo);
    api.get('/entorno/clima').then((res) => setClima(res.data)).catch(() => {});
  }, []);

  const objetivos = [
    { value: 'calma', label: '🌊 Calma' },
    { value: 'enfoque', label: '🎯 Enfoque' },
    { value: 'gratitud', label: '🙏 Gratitud' },
    { value: 'energia', label: '⚡ Energía' },
    { value: 'sueno', label: '🌙 Sueño' },
    { value: 'ansiedad', label: '💨 Ansiedad' },
  ];

  const handleGenerar = async () => {
    if (!intencion) {
      toast.error('Escribe una intención para tu meditación');
      return;
    }
    setLoading(true);
    try {
      const res = await api.post('/mente/generar', {
        intencion,
        objetivo,
        duracion_min: 10,
        generar_audio: false,
      });
      setMeditacion(res.data);
      setFeedbackScore(null);
      setFeedbackSaved(false);
      // Award gamification points (fire-and-forget)
      api.post('/gamification/award?action=meditacion_completada').catch(() => {});
      toast.success('Meditación generada con éxito');
    } catch {
      toast.error('Error al generar la meditación');
    } finally {
      setLoading(false);
    }
  };

  const submitFeedback = async (score: number) => {
    setFeedbackScore(score);
    try {
      await api.post('/checkins', {
        estado_emocional: score,
        energia_fisica: 5,
        horas_sueno: 7,
        emocion_principal: 'post_meditacion',
      });
    } catch {
      // silent — feedback is best-effort
    } finally {
      setFeedbackSaved(true);
    }
  };

  const savePreMed = async (score: number) => {
    setPreMedScore(score);
    api.post('/checkins', { estado_emocional: score, energia_fisica: 5, horas_sueno: 7, emocion_principal: 'pre_meditacion' }).catch(() => {});
    setPreMedSaved(true);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">🧠 Pilar Mente</h1>
      <p className="text-slate-400">Genera una sesión de meditación personalizada basada en tu estado actual.</p>

      {/* Contextual banner: clima + franja + sugerencia + perfil HUE ambiental (Tabla 3.3 + Tabla 3.4) */}
      {sugerencia && (
        <div className="rounded-lg border border-blue-700/40 bg-blue-900/20 px-4 py-3 text-sm space-y-2">
          <div className="flex flex-wrap items-center gap-3">
            {clima && (
              <>
                <span className="text-slate-300 font-medium">
                  {CLIMA_EMOJI[clima.clasificacion] ?? '🌡️'} {Math.round(clima.temperatura)}°C
                </span>
                <span className="text-slate-600">·</span>
              </>
            )}
            <span className="text-blue-300 font-medium">{sugerencia.franja}</span>
            <span className="text-slate-500">·</span>
            <span className="text-slate-400">ThriveMind sugiere:</span>
            <span className="text-blue-300 font-semibold">{sugerencia.etiqueta}</span>
          </div>
          {HUE_POR_OBJETIVO[sugerencia.objetivo] && (
            <div className="flex items-center gap-2 pt-1 border-t border-blue-800/40">
              <span className="text-amber-400">💡</span>
              <span className="text-xs text-amber-300">
                Luz · {HUE_POR_OBJETIVO[sugerencia.objetivo].perfil} · {HUE_POR_OBJETIVO[sugerencia.objetivo].kelvin}K · {HUE_POR_OBJETIVO[sugerencia.objetivo].brillo}% intensidad
              </span>
              <a href="/dashboard/perfiles-hue" className="ml-auto text-xs text-amber-400/70 hover:text-amber-300 hover:underline whitespace-nowrap">
                Abrir HUE →
              </a>
            </div>
          )}
        </div>
      )}

      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>Nueva Meditación</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Pre-meditation contextual check-in (§3.4.1) */}
          <div className="rounded-lg border border-slate-700/50 bg-slate-800/20 px-3 py-2.5">
            <p className="text-xs text-slate-400 mb-2">¿Cómo estás <span className="font-medium text-slate-300">antes</span> de meditar? <span className="text-slate-600">· Diario Inteligente</span></p>
            {!preMedSaved ? (
              <div className="flex gap-2">
                {['😔', '😕', '😐', '🙂', '😊'].map((emoji, i) => (
                  <button key={i} onClick={() => savePreMed(i * 2 + 2)}
                    className={`text-xl rounded-lg px-2 py-1 transition-all hover:scale-110 hover:bg-slate-700/50 ${
                      preMedScore === i * 2 + 2 ? 'bg-violet-600/30 border border-violet-500' : ''
                    }`}>
                    {emoji}
                  </button>
                ))}
              </div>
            ) : (
              <p className="text-xs text-emerald-400">✓ Estado pre-meditación guardado</p>
            )}
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">¿Cuál es tu intención?</label>
            <Input placeholder="Ej: quiero soltar el estrés del trabajo" value={intencion}
              onChange={(e) => setIntencion(e.target.value)}
              className="bg-slate-700 border-slate-600" />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Objetivo</label>
            <div className="flex flex-wrap gap-2">
              {objetivos.map((obj) => (
                <Button key={obj.value} variant={objetivo === obj.value ? 'default' : 'outline'}
                  size="sm" onClick={() => setObjetivo(obj.value)}>
                  {obj.label}
                </Button>
              ))}
            </div>
          </div>
          <Button className="w-full" onClick={handleGenerar} disabled={loading}>
            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
            Generar Meditación
          </Button>
        </CardContent>
      </Card>

      {meditacion && (
        <Card className="border-violet-700/50 bg-slate-800/50">
          <CardHeader>
            <CardTitle>Tu meditación — {meditacion.tecnica}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose prose-invert max-w-none whitespace-pre-wrap text-slate-300">
              {meditacion.guion}
            </div>
          </CardContent>
        </Card>
      )}

      {/* HUE luminary suggestion tied to the meditation objective (§3.3.1 orquestación ambiental) */}
      {meditacion && HUE_POR_OBJETIVO[objetivo] && (
        <div className="flex items-center gap-3 rounded-lg border border-amber-700/40 bg-amber-900/10 px-4 py-3">
          <span className="text-amber-400 text-xl">💡</span>
          <div className="flex-1">
            <p className="text-sm font-medium text-amber-300">Escena lumínica para esta sesión</p>
            <p className="text-xs text-slate-400 mt-0.5">
              {HUE_POR_OBJETIVO[objetivo].perfil} · {HUE_POR_OBJETIVO[objetivo].kelvin}K · {HUE_POR_OBJETIVO[objetivo].brillo}% intensidad
            </p>
          </div>
          <a href="/dashboard/perfiles-hue" className="text-xs text-amber-400 hover:text-amber-300 hover:underline whitespace-nowrap">
            Configurar HUE →
          </a>
        </div>
      )}

      {/* Post-session feedback — RF-009 user_feedback_score */}
      {meditacion && !feedbackSaved && (
        <div className="rounded-lg border border-slate-700 bg-slate-800/30 px-4 py-4">
          <p className="text-sm font-medium text-slate-300 mb-3">¿Cómo te sientes después de la meditación?</p>
          <div className="flex gap-3 justify-center">
            {['😞', '😕', '😐', '🙂', '😊'].map((emoji, i) => (
              <button
                key={i}
                onClick={() => submitFeedback(i + 1)}
                className={`text-2xl rounded-lg px-3 py-2 transition-all hover:scale-110 ${
                  feedbackScore === i + 1
                    ? 'bg-violet-600/30 border border-violet-500'
                    : 'hover:bg-slate-700/50'
                }`}
              >
                {emoji}
              </button>
            ))}
          </div>
        </div>
      )}
      {meditacion && feedbackSaved && (
        <p className="text-center text-sm text-emerald-400">✓ Gracias por tu feedback</p>
      )}

      <BreathingExercise suggestedTechnique={meditacion ? mapTecnicaToKey(meditacion.tecnica) : null} />

      {/* Modulación de Música Sonora — Endel API (§3.3.1 Fase 2) */}
      <div className="rounded-lg border border-dashed border-slate-600 bg-slate-800/20 px-4 py-4">
        <div className="flex items-start gap-3">
          <span className="text-2xl mt-0.5">🎵</span>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <p className="text-sm font-medium text-slate-300">Modulación de Música Sonora</p>
              <span className="text-[10px] bg-violet-800/40 border border-violet-600/40 text-violet-300 px-1.5 py-0.5 rounded">Fase 2</span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Endel API · Flujo sonoro generado en tiempo real, sincronizado con HRV, hora del día y clima. Induce ondas alpha para relajación o theta para meditación profunda según el objetivo de la sesión.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
