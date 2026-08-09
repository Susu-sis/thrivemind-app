'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import api from '@/lib/api';

interface HueRecommendation {
  name: string;
  kelvin: number;
  brightness: number;
  reason: string;
}

function getHueRecommendation(emocion: string, energia: number, hora: number): HueRecommendation {
  const negativas = ['estrés', 'ansiedad', 'agobio'];
  const tristes = ['tristeza', 'cansancio'];
  const positivas = ['alegría', 'energía', 'esperanza', 'gratitud'];

  if (negativas.includes(emocion) || energia < 5) {
    return { name: 'Relajación Profunda', kelvin: 2200, brightness: 20, reason: `${emocion} · energía ${energia}/10` };
  }
  if (energia > 7 && hora < 12) {
    return { name: 'Trabajo Productivo', kelvin: 5000, brightness: 80, reason: `energía ${energia}/10 · horario matutino` };
  }
  if (tristes.includes(emocion)) {
    return { name: 'Meditación Calma', kelvin: 2700, brightness: 40, reason: `estado ${emocion}` };
  }
  if (positivas.includes(emocion) && energia > 6) {
    return { name: 'Naturaleza Indoor', kelvin: 4500, brightness: 65, reason: `${emocion} · energía ${energia}/10` };
  }
  if (hora >= 21) {
    return { name: 'Lectura Nocturna', kelvin: 2500, brightness: 30, reason: `horario nocturno` };
  }
  return { name: 'Yoga Ambiente', kelvin: 3000, brightness: 35, reason: 'estado equilibrado' };
}

interface HueProfile {
  id: string;
  name: string;
  kelvin: number;
  brightness: number;
  color_hex: string;
  description: string;
  is_custom: boolean;
}

interface MeditationHue {
  perfil: string;
  kelvin: number;
  brillo: number;
  objetivo: string;
  timestamp: number;
}

export default function PerfilesHuePage() {
  const [profiles, setProfiles] = useState<HueProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', kelvin: 4000, brightness: 70, color_hex: '#ffd699', description: '' });
  const [recommendation, setRecommendation] = useState<HueRecommendation | null>(null);
  const [meditationHue, setMeditationHue] = useState<MeditationHue | null>(null);

  const load = () => {
    api.get('/hue/profiles')
      .then((res) => {
        const list = Array.isArray(res.data) ? res.data : (res.data.profiles || []);
        setProfiles(list);
      })
      .catch(() => setProfiles([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    load();
    // Read active meditation HUE suggestion (set by Mente page on generation)
    try {
      const stored = localStorage.getItem('hue_meditation_suggestion');
      if (stored) {
        const parsed: MeditationHue = JSON.parse(stored);
        // Valid for 2 hours
        if (Date.now() - parsed.timestamp < 2 * 60 * 60 * 1000) {
          setMeditationHue(parsed);
        } else {
          localStorage.removeItem('hue_meditation_suggestion');
        }
      }
    } catch { /* ignore */ }
    api.get('/checkin/dashboard/tendencias?dias=7')
      .then((res) => {
        const serie = res.data?.serie_temporal;
        if (serie && serie.length > 0) {
          const ultimo = serie[serie.length - 1];
          setRecommendation(getHueRecommendation(
            ultimo.emocion_principal || 'neutral',
            ultimo.energia_fisica ?? 5,
            new Date().getHours(),
          ));
        }
      })
      .catch(() => null);
  }, []);

  const handleCreate = async () => {
    try {
      await api.post('/hue/profiles/custom', form);
      setShowForm(false);
      setForm({ name: '', kelvin: 4000, brightness: 70, color_hex: '#ffd699', description: '' });
      load();
    } catch { /* ignore */ }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/hue/profiles/${id}`);
      load();
    } catch { /* ignore */ }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-slate-400">Cargando perfiles...</div>;
  }

  const predefined = profiles.filter((p) => !p.is_custom);
  const custom = profiles.filter((p) => p.is_custom);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">💡 Perfiles HUE</h1>
          <p className="text-slate-400 mt-1">Gestiona la iluminación ambiental para tu bienestar</p>
        </div>
        <button
          onClick={() => setShowForm((v) => !v)}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm transition-colors"
        >
          {showForm ? 'Cancelar' : '+ Crear Perfil'}
        </button>
      </div>

      {/* Active meditation HUE — overrides base recommendation when a session was just generated */}
      {meditationHue && (
        <div className="flex flex-wrap items-center gap-3 px-5 py-4 rounded-xl bg-violet-500/10 border border-violet-500/40">
          <span className="text-xl">🧘</span>
          <div className="flex-1 min-w-0">
            <span className="text-violet-300 font-medium text-sm">Sesión de meditación activa</span>
            <span className="text-slate-300 text-sm"> → objetivo: </span>
            <span className="text-white font-semibold text-sm capitalize">{meditationHue.objetivo}</span>
            <span className="text-slate-400 text-xs ml-2">{meditationHue.kelvin}K · {meditationHue.brillo}%</span>
            <p className="text-xs text-violet-400 mt-0.5">Perfil: <strong className="text-white">{meditationHue.perfil}</strong></p>
          </div>
          <button
            onClick={() => { localStorage.removeItem('hue_meditation_suggestion'); setMeditationHue(null); }}
            className="text-xs text-slate-500 hover:text-slate-400"
          >
            Cerrar ×
          </button>
        </div>
      )}

      {recommendation && (
        <div className="flex flex-wrap items-center gap-3 px-5 py-4 rounded-xl bg-amber-500/10 border border-amber-500/30">
          <span className="text-xl">💡</span>
          <div className="flex-1 min-w-0">
            <span className="text-amber-300 font-medium text-sm">{meditationHue ? 'Estado basal (check-in)' : 'Para tu estado actual'}</span>
            <span className="text-slate-300 text-sm"> → ThriveMind recomienda: </span>
            <span className="text-white font-semibold text-sm">{recommendation.name}</span>
            <span className="text-slate-400 text-xs ml-2">{recommendation.kelvin}K · {recommendation.brightness}%</span>
          </div>
          <span className="text-xs text-slate-500 italic">{recommendation.reason}</span>
        </div>
      )}

      {showForm && (
        <Card className="bg-slate-800/50 border-indigo-500/30">
          <CardContent className="p-6 space-y-4">
            <div>
              <label className="text-xs text-slate-400">Nombre</label>
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full mt-1 px-3 py-2 bg-slate-700 rounded-lg text-white text-sm border border-slate-600 focus:border-indigo-500 outline-none"
                placeholder="Mi perfil personalizado"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-slate-400">Temperatura (K): {form.kelvin}</label>
                <input
                  type="range"
                  min={2000}
                  max={6500}
                  value={form.kelvin}
                  onChange={(e) => setForm({ ...form, kelvin: +e.target.value })}
                  className="w-full mt-1"
                />
                <div className="flex justify-between text-xs text-slate-500">
                  <span>2000K (cálido)</span>
                  <span>6500K (frío)</span>
                </div>
              </div>
              <div>
                <label className="text-xs text-slate-400">Brillo: {form.brightness}%</label>
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={form.brightness}
                  onChange={(e) => setForm({ ...form, brightness: +e.target.value })}
                  className="w-full mt-1"
                />
              </div>
            </div>
            <div>
              <label className="text-xs text-slate-400">Descripción (opcional)</label>
              <input
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                className="w-full mt-1 px-3 py-2 bg-slate-700 rounded-lg text-white text-sm border border-slate-600 focus:border-indigo-500 outline-none"
                placeholder="Para lectura nocturna..."
              />
            </div>
            <button
              onClick={handleCreate}
              disabled={!form.name.trim()}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-40 text-white rounded-lg text-sm transition-colors"
            >
              Guardar Perfil
            </button>
          </CardContent>
        </Card>
      )}

      {/* Custom profiles */}
      {custom.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold mb-3">Mis Perfiles</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {custom.map((p) => (
              <Card key={p.id} className="bg-slate-800/50 border-indigo-500/30">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 rounded-full" style={{ backgroundColor: p.color_hex }} />
                      <span className="font-medium text-white">{p.name}</span>
                    </div>
                    <button onClick={() => handleDelete(p.id)} className="text-red-400 hover:text-red-300 text-xs">
                      Eliminar
                    </button>
                  </div>
                  <p className="text-xs text-slate-400">{p.description}</p>
                  <div className="flex gap-2 mt-2">
                    <Badge className="bg-slate-600/50 text-slate-300 text-xs">{p.kelvin}K</Badge>
                    <Badge className="bg-slate-600/50 text-slate-300 text-xs">{p.brightness}%</Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Predefined profiles */}
      <div>
        <h2 className="text-lg font-semibold mb-3">Perfiles Predefinidos</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {predefined.map((p) => (
            <Card key={p.id} className="bg-slate-800/50 border-slate-700">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-4 h-4 rounded-full" style={{ backgroundColor: p.color_hex }} />
                  <span className="font-medium text-white">{p.name}</span>
                </div>
                <p className="text-xs text-slate-400">{p.description}</p>
                <div className="flex gap-2 mt-2">
                  <Badge className="bg-slate-600/50 text-slate-300 text-xs">{p.kelvin}K</Badge>
                  <Badge className="bg-slate-600/50 text-slate-300 text-xs">{p.brightness}%</Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
