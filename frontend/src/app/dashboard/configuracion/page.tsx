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
  { value: 'diario', label: 'Diario' },
  { value: 'cada_dos_dias', label: 'Cada 2 días' },
  { value: 'semanal', label: 'Semanal' },
];

export default function ConfiguracionPage() {
  const [prefs, setPrefs] = useState<Preferences | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

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
