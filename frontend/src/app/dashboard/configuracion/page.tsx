'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import api from '@/lib/api';

interface Preferences {
  mente_activo: boolean;
  mente_intensidad: number;
  cuerpo_activo: boolean;
  cuerpo_intensidad: number;
  entorno_activo: boolean;
  entorno_intensidad: number;
  objetivo_principal: string;
  frecuencia_checkin: string;
  alergias: string[];
  preferencia_dieta: string;
  presupuesto_semanal: string;
  objetivo_fitness: string;
  // Perfil biométrico básico (Nivel 1 TMB)
  peso_kg?: number;
  altura_cm?: number;
  edad?: number;
  sexo_biologico?: string;
  nivel_actividad?: string;
}

const OBJETIVOS = [
  { value: 'equilibrio', label: '⚖️ Equilibrio general' },
  { value: 'reducir_estres', label: '🧘 Reducir estrés' },
  { value: 'mejorar_sueno', label: '😴 Mejorar sueño' },
  { value: 'aumentar_energia', label: '⚡ Aumentar energía' },
  { value: 'conexion_naturaleza', label: '🌿 Conexión con naturaleza' },
  { value: 'rendimiento_cognitivo', label: '🧠 Rendimiento cognitivo' },
];

const FRECUENCIAS = [
  { value: 'diario',        label: 'Diario' },
  { value: 'cada_dos_dias', label: 'Cada 2 días' },
  { value: 'semanal',       label: 'Semanal' },
];

const DIETAS = [
  { value: 'omnivora',        label: '🍖 Omnívora' },
  { value: 'vegetariana',     label: '🥗 Vegetariana' },
  { value: 'vegana',          label: '🌱 Vegana' },
  { value: 'pescatariana',    label: '🐟 Pescatariana' },
  { value: 'sin_restriccion', label: '🔓 Sin restricciones' },
];

const ALERGIAS_PRESET = [
  { value: 'gluten',       label: 'Gluten' },
  { value: 'lactosa',      label: 'Lactosa' },
  { value: 'frutos_secos', label: 'Frutos secos' },
  { value: 'mariscos',     label: 'Marisco' },
  { value: 'huevo',        label: 'Huevo' },
  { value: 'soja',         label: 'Soja' },
];

const PRESUPUESTOS = [
  { value: 'bajo',  label: '< 60 €' },
  { value: 'medio', label: '60–120 €' },
  { value: 'alto',  label: '> 120 €' },
];

const ACTIVIDAD = [
  { value: 'sedentario', label: '🧘 Sedentario', factor: 1.2 },
  { value: 'moderado',   label: '🚶 Moderado',   factor: 1.375 },
  { value: 'activo',     label: '🏃 Activo',     factor: 1.55 },
  { value: 'muy_activo', label: '🏋️ Muy activo', factor: 1.725 },
];

const OBJETIVO_FITNESS = [
  { value: 'perder_peso',   label: '📉 Perder peso',   ajuste: -500 },
  { value: 'mantener',      label: '⚖️ Mantener',       ajuste: 0 },
  { value: 'tonificar',     label: '💪 Tonificar',      ajuste: 200 },
  { value: 'ganar_musculo', label: '🏋️ Ganar músculo', ajuste: 300 },
];

/** Mifflin-St Jeor × factor actividad ± ajuste objetivo — puramente client-side */
function calcTDEE(p: Preferences): number | null {
  if (!p.peso_kg || !p.altura_cm || !p.edad || !p.sexo_biologico) return null;
  const tmb = p.sexo_biologico === 'hombre'
    ? 10 * p.peso_kg + 6.25 * p.altura_cm - 5 * p.edad + 5
    : 10 * p.peso_kg + 6.25 * p.altura_cm - 5 * p.edad - 161;
  const factores: Record<string, number> = { sedentario: 1.2, moderado: 1.375, activo: 1.55, muy_activo: 1.725 };
  const factor = factores[p.nivel_actividad ?? 'moderado'] ?? 1.375;
  const ajustes: Record<string, number> = { perder_peso: -500, mantener: 0, tonificar: 200, ganar_musculo: 300 };
  const ajuste = ajustes[p.objetivo_fitness ?? 'mantener'] ?? 0;
  return Math.round(tmb * factor + ajuste);
}

export default function ConfiguracionPage() {
  const [prefs, setPrefs] = useState<Preferences | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [otraAlergia, setOtraAlergia] = useState('');
  const [showOtraInput, setShowOtraInput] = useState(false);

  useEffect(() => {
    api.get('/preferences/').then((res) => setPrefs(res.data)).catch(() => {});
  }, []);

  const handleSave = async () => {
    if (!prefs) return;
    setSaving(true);
    try {
      await api.patch('/preferences/', {
        mente: { activo: prefs.mente_activo, intensidad: prefs.mente_intensidad },
        cuerpo: { activo: prefs.cuerpo_activo, intensidad: prefs.cuerpo_intensidad },
        entorno: { activo: prefs.entorno_activo, intensidad: prefs.entorno_intensidad },
        objetivo_principal: prefs.objetivo_principal,
        frecuencia_checkin: prefs.frecuencia_checkin,
        alergias: prefs.alergias,
        preferencia_dieta: prefs.preferencia_dieta,
        presupuesto_semanal: prefs.presupuesto_semanal,
        objetivo_fitness: prefs.objetivo_fitness,
        peso_kg: prefs.peso_kg ?? null,
        altura_cm: prefs.altura_cm ?? null,
        edad: prefs.edad ?? null,
        sexo_biologico: prefs.sexo_biologico ?? null,
        nivel_actividad: prefs.nivel_actividad ?? null,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {
      // silent
    } finally {
      setSaving(false);
    }
  };

  if (!prefs) {
    return <div className="text-slate-400">Cargando configuración...</div>;
  }

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">⚙️ Configuración</h1>

      {/* Pilares */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>Pilares activos</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <PilarToggle
            label="🧠 Mente"
            activo={prefs.mente_activo}
            intensidad={prefs.mente_intensidad}
            onToggle={(v) => setPrefs({ ...prefs, mente_activo: v })}
            onIntensidad={(v) => setPrefs({ ...prefs, mente_intensidad: v })}
          />
          <PilarToggle
            label="💚 Cuerpo"
            activo={prefs.cuerpo_activo}
            intensidad={prefs.cuerpo_intensidad}
            onToggle={(v) => setPrefs({ ...prefs, cuerpo_activo: v })}
            onIntensidad={(v) => setPrefs({ ...prefs, cuerpo_intensidad: v })}
          />
          <PilarToggle
            label="🌱 Entorno"
            activo={prefs.entorno_activo}
            intensidad={prefs.entorno_intensidad}
            onToggle={(v) => setPrefs({ ...prefs, entorno_activo: v })}
            onIntensidad={(v) => setPrefs({ ...prefs, entorno_intensidad: v })}
          />
        </CardContent>
      </Card>

      {/* Objetivo */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>Objetivo principal</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-2">
            {OBJETIVOS.map((obj) => (
              <button
                key={obj.value}
                onClick={() => setPrefs({ ...prefs, objetivo_principal: obj.value })}
                className={`rounded-lg px-3 py-2 text-sm text-left transition-colors ${
                  prefs.objetivo_principal === obj.value
                    ? 'bg-violet-600/30 border border-violet-500 text-violet-200'
                    : 'bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {obj.label}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Frecuencia */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>Frecuencia de check-in</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            {FRECUENCIAS.map((f) => (
              <button
                key={f.value}
                onClick={() => setPrefs({ ...prefs, frecuencia_checkin: f.value })}
                className={`rounded-lg px-4 py-2 text-sm transition-colors ${
                  prefs.frecuencia_checkin === f.value
                    ? 'bg-violet-600/30 border border-violet-500 text-violet-200'
                    : 'bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Perfil Nutricional */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>Perfil Nutricional</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">

          {/* Dieta */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-300">Tipo de dieta</p>
            <div className="flex flex-wrap gap-2">
              {DIETAS.map((d) => (
                <button
                  key={d.value}
                  onClick={() => setPrefs({ ...prefs, preferencia_dieta: d.value })}
                  className={`rounded-lg px-3 py-1.5 text-sm transition-colors ${
                    prefs.preferencia_dieta === d.value
                      ? 'bg-emerald-600/30 border border-emerald-500 text-emerald-200'
                      : 'bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {d.label}
                </button>
              ))}
            </div>
          </div>

          {/* Alergias */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-300">Alergias e intolerancias</p>
            <div className="flex flex-wrap gap-2">
              {ALERGIAS_PRESET.map((a) => {
                const active = (prefs.alergias ?? []).includes(a.value);
                return (
                  <button
                    key={a.value}
                    onClick={() =>
                      setPrefs({
                        ...prefs,
                        alergias: active
                          ? prefs.alergias.filter((x) => x !== a.value)
                          : [...(prefs.alergias ?? []), a.value],
                      })
                    }
                    className={`rounded-lg px-3 py-1.5 text-sm transition-colors ${
                      active
                        ? 'bg-rose-600/30 border border-rose-500 text-rose-200'
                        : 'bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {a.label}
                  </button>
                );
              })}
              {/* Custom allergies added by user */}
              {(prefs.alergias ?? [])
                .filter((v) => !ALERGIAS_PRESET.some((p) => p.value === v))
                .map((custom) => (
                  <button
                    key={custom}
                    onClick={() =>
                      setPrefs({ ...prefs, alergias: prefs.alergias.filter((x) => x !== custom) })
                    }
                    className="flex items-center gap-1 rounded-lg px-3 py-1.5 text-sm bg-rose-600/30 border border-rose-500 text-rose-200"
                  >
                    {custom.replace(/_/g, ' ')} <span className="text-xs opacity-70">×</span>
                  </button>
                ))}
              {/* Add custom */}
              {showOtraInput ? (
                <div className="flex items-center gap-1">
                  <input
                    autoFocus
                    value={otraAlergia}
                    onChange={(e) => setOtraAlergia(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        const val = otraAlergia.trim().toLowerCase().replace(/\s+/g, '_');
                        if (val && !(prefs.alergias ?? []).includes(val)) {
                          setPrefs({ ...prefs, alergias: [...(prefs.alergias ?? []), val] });
                        }
                        setOtraAlergia('');
                        setShowOtraInput(false);
                      }
                      if (e.key === 'Escape') { setShowOtraInput(false); setOtraAlergia(''); }
                    }}
                    placeholder="ej. kiwi"
                    className="rounded-lg px-3 py-1.5 text-sm w-28 bg-slate-700 border border-slate-500 text-slate-200 outline-none focus:border-emerald-500"
                  />
                  <button
                    onClick={() => {
                      const val = otraAlergia.trim().toLowerCase().replace(/\s+/g, '_');
                      if (val && !(prefs.alergias ?? []).includes(val)) {
                        setPrefs({ ...prefs, alergias: [...(prefs.alergias ?? []), val] });
                      }
                      setOtraAlergia('');
                      setShowOtraInput(false);
                    }}
                    className="rounded-lg px-2.5 py-1.5 text-sm bg-emerald-700/50 border border-emerald-600 text-emerald-200 hover:bg-emerald-700"
                  >
                    ＋
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setShowOtraInput(true)}
                  className="rounded-lg px-3 py-1.5 text-sm border border-dashed border-slate-600 text-slate-500 hover:text-slate-300 hover:border-slate-500"
                >
                  ＋ Otra...
                </button>
              )}
            </div>
          </div>

          {/* Presupuesto */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-300">Presupuesto semanal en alimentación</p>
            <div className="flex gap-2">
              {PRESUPUESTOS.map((p) => (
                <button
                  key={p.value}
                  onClick={() => setPrefs({ ...prefs, presupuesto_semanal: p.value })}
                  className={`flex-1 rounded-lg px-3 py-2 text-sm transition-colors ${
                    prefs.presupuesto_semanal === p.value
                      ? 'bg-emerald-600/30 border border-emerald-500 text-emerald-200'
                      : 'bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

        </CardContent>
      </Card>

      {/* Perfil Biométrico Básico */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>Perfil Biométrico · Nivel 1</CardTitle>
          <p className="text-xs text-slate-400 mt-1">
            Calcula tu objetivo calórico personalizado mediante la fórmula Mifflin-St Jeor.
            Datos usados exclusivamente para este cálculo.
          </p>
        </CardHeader>
        <CardContent className="space-y-5">

          {/* Sexo biológico */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-300">Sexo biológico <span className="text-xs text-slate-500">(para cálculo metabólico)</span></p>
            <div className="flex gap-2">
              {(['hombre', 'mujer'] as const).map((s) => (
                <button key={s}
                  onClick={() => setPrefs({ ...prefs, sexo_biologico: s })}
                  className={`flex-1 rounded-lg px-3 py-2 text-sm capitalize transition-colors ${
                    prefs.sexo_biologico === s
                      ? 'bg-violet-600/30 border border-violet-500 text-violet-200'
                      : 'bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-slate-700'
                  }`}>
                  {s === 'hombre' ? '♂️ Hombre' : '♀️ Mujer'}
                </button>
              ))}
            </div>
          </div>

          {/* Peso / Altura / Edad */}
          <div className="grid grid-cols-3 gap-3">
            {([
              { key: 'peso_kg',   label: 'Peso (kg)',  min: 30,  max: 300, step: 0.5, placeholder: '70' },
              { key: 'altura_cm', label: 'Altura (cm)', min: 100, max: 250, step: 1,   placeholder: '170' },
              { key: 'edad',      label: 'Edad',        min: 10,  max: 120, step: 1,   placeholder: '30' },
            ] as const).map(({ key, label, min, max, step, placeholder }) => (
              <div key={key} className="space-y-1">
                <p className="text-xs font-medium text-slate-400">{label}</p>
                <input
                  type="number" min={min} max={max} step={step}
                  placeholder={placeholder}
                  value={prefs[key] ?? ''}
                  onChange={(e) => setPrefs({ ...prefs, [key]: e.target.value ? Number(e.target.value) : undefined })}
                  className="w-full rounded-lg px-3 py-2 text-sm bg-slate-700 border border-slate-600 text-slate-200 outline-none focus:border-violet-500 [appearance:textfield]"
                />
              </div>
            ))}
          </div>

          {/* Nivel de actividad */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-300">Nivel de actividad física</p>
            <div className="grid grid-cols-2 gap-2">
              {ACTIVIDAD.map((a) => (
                <button key={a.value}
                  onClick={() => setPrefs({ ...prefs, nivel_actividad: a.value })}
                  className={`rounded-lg px-3 py-2 text-sm text-left transition-colors ${
                    prefs.nivel_actividad === a.value
                      ? 'bg-violet-600/30 border border-violet-500 text-violet-200'
                      : 'bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-slate-700'
                  }`}>
                  {a.label}
                </button>
              ))}
            </div>
          </div>

          {/* Objetivo fitness */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-300">Objetivo fitness</p>
            <div className="grid grid-cols-2 gap-2">
              {OBJETIVO_FITNESS.map((o) => (
                <button key={o.value}
                  onClick={() => setPrefs({ ...prefs, objetivo_fitness: o.value })}
                  className={`rounded-lg px-3 py-2 text-sm text-left transition-colors ${
                    prefs.objetivo_fitness === o.value
                      ? 'bg-emerald-600/30 border border-emerald-500 text-emerald-200'
                      : 'bg-slate-700/50 border border-slate-600 text-slate-300 hover:bg-slate-700'
                  }`}>
                  {o.label}
                </button>
              ))}
            </div>
          </div>

          {/* TDEE resultado */}
          {calcTDEE(prefs) !== null && (
            <div className="rounded-lg bg-emerald-900/30 border border-emerald-700/50 p-4">
              <p className="text-xs text-emerald-400 mb-1">Objetivo calórico personalizado (Nivel 1 · TMB Mifflin-St Jeor)</p>
              <p className="text-2xl font-bold text-emerald-300">{calcTDEE(prefs)?.toLocaleString()} kcal<span className="text-sm font-normal text-emerald-400">/día</span></p>
              <p className="text-xs text-slate-400 mt-1">
                Fase 2: wearables + básculas inteligentes vía Terra API.
              </p>
            </div>
          )}

        </CardContent>
      </Card>

      {/* Save */}
      <Button onClick={handleSave} disabled={saving} className="w-full">
        {saving ? 'Guardando...' : saved ? '✓ Guardado' : 'Guardar cambios'}
      </Button>
    </div>
  );
}

function PilarToggle({
  label, activo, intensidad, onToggle, onIntensidad,
}: {
  label: string;
  activo: boolean;
  intensidad: number;
  onToggle: (v: boolean) => void;
  onIntensidad: (v: number) => void;
}) {
  const niveles = ['Básico', 'Intermedio', 'Avanzado'];
  return (
    <div className="flex items-center gap-4 p-3 rounded-lg bg-slate-700/30">
      <button
        onClick={() => onToggle(!activo)}
        className={`w-10 h-6 rounded-full relative transition-colors ${
          activo ? 'bg-violet-600' : 'bg-slate-600'
        }`}
      >
        <span
          className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
            activo ? 'left-5' : 'left-1'
          }`}
        />
      </button>
      <span className="text-sm font-medium flex-1">{label}</span>
      {activo && (
        <div className="flex items-center gap-2">
          <Slider
            value={[intensidad]}
            onValueChange={(v) => onIntensidad(v[0])}
            min={1}
            max={3}
            step={1}
            className="w-24"
          />
          <span className="text-xs text-slate-400 w-20">{niveles[intensidad - 1]}</span>
        </div>
      )}
    </div>
  );
}
