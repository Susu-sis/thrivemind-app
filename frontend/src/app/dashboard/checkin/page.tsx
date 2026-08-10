'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
import api from '@/lib/api';

const EMOCIONES = [
  'alegría', 'calma', 'gratitud', 'energía', 'esperanza',
  'neutral', 'cansancio', 'estrés', 'ansiedad', 'tristeza', 'agobio',
];

const STATE_STYLES: Record<string, { border: string; bg: string; text: string; emoji: string }> = {
  estres_agudo:       { border: 'border-red-500/50',    bg: 'bg-red-500/10',    text: 'text-red-400',    emoji: '🔴' },
  fatiga_cronica:     { border: 'border-purple-500/50', bg: 'bg-purple-500/10', text: 'text-purple-400', emoji: '🟣' },
  recuperacion_activa:{ border: 'border-green-500/50',  bg: 'bg-green-500/10',  text: 'text-green-400',  emoji: '🟢' },
  equilibrio:         { border: 'border-blue-500/50',   bg: 'bg-blue-500/10',   text: 'text-blue-400',   emoji: '🔵' },
  activacion:         { border: 'border-orange-500/50', bg: 'bg-orange-500/10', text: 'text-orange-400', emoji: '🟠' },
};

const INTERVENTION_HINTS: Record<string, string> = {
  estres_agudo:        'Respiración 4-7-8 · Perfil HUE Relajación Profunda 2200K',
  fatiga_cronica:      'Descanso prioritario · Nutrición T3-E (magnesio) · Luz ámbar 1900K',
  recuperacion_activa: 'Coherencia Cardíaca 0.1 Hz · Nutrición T3-B (triptófano)',
  equilibrio:          'Estado ideal para meditación y trabajo cognitivo profundo',
  activacion:          'Perfil HUE Trabajo Productivo 5000K · Aprovecha el estado de flow',
};

interface ClassifyResult {
  state: string;
  confidence: number;
  method: string;
  description: { label: string; descripcion: string };
  n_checkins_available: number;
  reason: string;
}

export default function CheckinPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ClassifyResult | null>(null);
  const [form, setForm] = useState({
    estado_emocional: 5,
    energia_fisica: 5,
    horas_sueno: 7,
    conexion_entorno: 5,
    emocion_principal: 'neutral',
    nota: '',
    tipo_checkin: 'diario' as const,
  });

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const res = await api.post('/checkin/', form);
      if (res.data?.clasificacion) {
        setResult(res.data.clasificacion);
      }
      // Award gamification points (fire-and-forget)
      api.post('/gamification/award?action=checkin_diario').catch(() => {});
      toast.success('Check-in guardado correctamente');
    } catch {
      toast.error('Error al guardar el check-in — revisa tu conexión');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold">✍️ Check-in de Bienestar</h1>
        <p className="text-sm text-slate-400 mt-1">Tu entrada diaria al <span className="text-violet-300">Diario Inteligente</span> — alimenta los 3 pilares y genera tu clasificación emocional.</p>
      </div>

      {/* ── Classification result card ── */}
      {result && (() => {
        const style = STATE_STYLES[result.state] ?? STATE_STYLES['equilibrio'];
        const pct = Math.round(result.confidence * 100);
        const hint = INTERVENTION_HINTS[result.state] ?? '';
        const modeLabel = result.method === 'xgboost'
          ? 'L3 · XGBoost'
          : 'L1 · Heurístico multi-señal';
        return (
          <div className="space-y-6">
            <Card className={`border-2 ${style.border} ${style.bg}`}>
              <CardContent className="p-6 space-y-5">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{style.emoji}</span>
                  <span className="text-xs font-medium text-slate-400 uppercase tracking-widest">Estado clasificado por Motor IA</span>
                </div>

                <div>
                  <p className={`text-3xl font-bold ${style.text}`}>
                    {result.description?.label ?? result.state}
                  </p>
                  <p className="text-sm text-slate-300 mt-1">{result.description?.descripcion}</p>
                </div>

                {/* Confidence bar */}
                <div className="space-y-1">
                  <div className="flex justify-between text-xs text-slate-400">
                    <span>Confianza del modelo</span>
                    <span className="font-semibold text-white">{pct}%</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${style.text.replace('text-', 'bg-')}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>

                {/* Badges */}
                <div className="flex flex-wrap gap-2">
                  <Badge className="bg-slate-700 text-slate-200 text-xs">{modeLabel}</Badge>
                  {result.n_checkins_available > 0 && (
                    <Badge className="bg-slate-700 text-slate-200 text-xs">{result.n_checkins_available} check-ins</Badge>
                  )}
                </div>

                {/* Intervention hint */}
                {hint && (
                  <div className="flex items-start gap-2 pt-1 border-t border-slate-700">
                    <span className="text-base mt-0.5">💡</span>
                    <div>
                      <p className="text-xs text-slate-400 font-medium">Protocolo activo</p>
                      <p className="text-sm text-slate-200">{hint}</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            <Button className="w-full" size="lg" onClick={() => router.push('/dashboard')}>
              Ver mi dashboard →
            </Button>
          </div>
        );
      })()}

      {/* ── Check-in form (hidden after classification) ── */}
      {!result && (<>
      {/* Estado emocional */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle className="text-lg">🧠 ¿Cómo te sientes emocionalmente?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between">
            <span className="text-sm text-slate-400">Muy mal</span>
            <span className="text-2xl font-bold">{form.estado_emocional}/10</span>
            <span className="text-sm text-slate-400">Excelente</span>
          </div>
          <Slider value={[form.estado_emocional]} min={1} max={10} step={1}
            onValueChange={([v]) => setForm({ ...form, estado_emocional: v })} />
        </CardContent>
      </Card>

      {/* Energía física */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle className="text-lg">💚 ¿Cómo está tu energía física?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between">
            <span className="text-sm text-slate-400">Sin energía</span>
            <span className="text-2xl font-bold">{form.energia_fisica}/10</span>
            <span className="text-sm text-slate-400">Máxima energía</span>
          </div>
          <Slider value={[form.energia_fisica]} min={1} max={10} step={1}
            onValueChange={([v]) => setForm({ ...form, energia_fisica: v })} />
        </CardContent>
      </Card>

      {/* Horas de sueño */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle className="text-lg">😴 ¿Cuántas horas dormiste?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between">
            <span className="text-sm text-slate-400">3h</span>
            <span className="text-2xl font-bold">{form.horas_sueno}h</span>
            <span className="text-sm text-slate-400">10h</span>
          </div>
          <Slider value={[form.horas_sueno]} min={3} max={10} step={0.5}
            onValueChange={([v]) => setForm({ ...form, horas_sueno: v })} />
        </CardContent>
      </Card>

      {/* Conexión con entorno */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle className="text-lg">🌱 ¿Qué tan conectado te sientes con tu entorno?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between">
            <span className="text-sm text-slate-400">Desconectado</span>
            <span className="text-2xl font-bold">{form.conexion_entorno}/10</span>
            <span className="text-sm text-slate-400">Muy conectado</span>
          </div>
          <Slider value={[form.conexion_entorno]} min={1} max={10} step={1}
            onValueChange={([v]) => setForm({ ...form, conexion_entorno: v })} />
        </CardContent>
      </Card>

      {/* Emoción principal */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle className="text-lg">¿Cuál es tu emoción principal?</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {EMOCIONES.map((emo) => (
              <Badge
                key={emo}
                variant={form.emocion_principal === emo ? 'default' : 'outline'}
                className="cursor-pointer"
                onClick={() => setForm({ ...form, emocion_principal: emo })}
              >
                {emo}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Nota */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle className="text-lg">💭 ¿Algo que quieras añadir? (opcional)</CardTitle>
        </CardHeader>
        <CardContent>
          <Input placeholder="Escribe una nota breve..." value={form.nota}
            onChange={(e) => setForm({ ...form, nota: e.target.value })}
            className="bg-slate-700 border-slate-600" />
        </CardContent>
      </Card>

      <Button className="w-full" size="lg" onClick={handleSubmit} disabled={loading}>
        {loading ? 'Analizando tu estado...' : '✓ Guardar Check-in'}
      </Button>
      </>)}
    </div>
  );
}
