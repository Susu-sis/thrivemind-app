'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';

interface Cultivo {
  id: string;
  nombre_planta: string;
  tipo: string;
  estado: string;
  fecha_siembra: string;
  fecha_cosecha_est: string | null;
  activo: boolean;
}

interface PlantProfile {
  riegoDias: number;
  ildPicoDias: number;
  emoji: string;
  motivo?: string;
}

const PLANT_PROFILES: Record<string, PlantProfile> = {
  Lavanda:    { riegoDias: 3, ildPicoDias: 60, emoji: '💜', motivo: 'Linalool · ansiolítico natural · agonista GABA' },
  Menta:      { riegoDias: 2, ildPicoDias: 14, emoji: '🌿', motivo: 'Mentol · activación y foco' },
  Albahaca:   { riegoDias: 2, ildPicoDias: 14, emoji: '🌱', motivo: 'Eugenol · antiinflamatorio' },
  Manzanilla: { riegoDias: 3, ildPicoDias: 21, emoji: '🌼', motivo: 'Apigenina · efecto calmante' },
  Romero:     { riegoDias: 4, ildPicoDias: 30, emoji: '🌲', motivo: 'Ácido rosmarínico · neuroprotector' },
};

function getProfile(nombre: string): PlantProfile {
  return PLANT_PROFILES[nombre] ?? { riegoDias: 3, ildPicoDias: 21, emoji: '🌿' };
}

function daysSince(dateStr: string): number {
  return Math.floor((Date.now() - new Date(dateStr).getTime()) / 86_400_000);
}

function nextRiegoLabel(siembra: string, riegoDias: number): string {
  const elapsed = daysSince(siembra);
  const cyclesDone = Math.floor(elapsed / riegoDias);
  const next = new Date(siembra);
  next.setDate(next.getDate() + (cyclesDone + 1) * riegoDias);
  const diff = Math.round((next.getTime() - Date.now()) / 86_400_000);
  if (diff <= 0) return 'hoy';
  if (diff === 1) return 'mañana';
  return `en ${diff} días`;
}

export default function EntornoPage() {
  const [cultivos, setCultivos] = useState<Cultivo[]>([]);
  const [loading, setLoading] = useState(true);
  const [clima, setClima] = useState<Record<string, unknown> | null>(null);
  const [consejo, setConsejo] = useState<string | null>(null);
  const [consejoLoading, setConsejoLoading] = useState(false);
  const [consulta, setConsulta] = useState('');
  const [cosechando, setCosechando] = useState<Set<string>>(new Set());

  useEffect(() => {
    Promise.all([
      api.get('/entorno/cultivos').then((r) => setCultivos(r.data)),
      api.get('/entorno/clima').then((r) => setClima(r.data)).catch(() => null),
    ]).finally(() => setLoading(false));
  }, []);

  const pedirConsejo = async () => {
    if (!consulta.trim()) { toast.error('Escribe una consulta primero'); return; }
    setConsejoLoading(true);
    try {
      const res = await api.post(`/entorno/consejo?consulta=${encodeURIComponent(consulta)}`);
      setConsejo(res.data.respuesta || JSON.stringify(res.data));
      toast.success('Consejo generado');
    } catch {
      toast.error('Error al obtener consejo');
    } finally {
      setConsejoLoading(false);
    }
  };

  const agregarCultivo = async (planta: string, tipo: string) => {
    try {
      const res = await api.post(`/entorno/cultivos?nombre_planta=${encodeURIComponent(planta)}&tipo=${encodeURIComponent(tipo)}`);
      setCultivos((prev) => [...prev, res.data]);
      toast.success(`${planta} añadida a tus cultivos`);
    } catch {
      toast.error('Error al añadir el cultivo');
    }
  };

  const eliminarCultivo = async (id: string, nombre: string) => {
    try {
      await api.delete(`/entorno/cultivos/${id}`);
      setCultivos((prev) => prev.filter((c) => c.id !== id));
      toast.success(`${nombre} eliminado`);
    } catch {
      toast.error('Error al eliminar el cultivo');
    }
  };

  const registrarCosecha = async (id: string, nombre: string) => {
    setCosechando((prev) => new Set(prev).add(id));
    try {
      await api.delete(`/entorno/cultivos/${id}`);
      setCultivos((prev) => prev.filter((c) => c.id !== id));
      toast.success(`✅ ¡${nombre} cosechada! Úsala fresca — ve al Pilar Cuerpo para recetas.`);
    } catch {
      toast.error('Error al registrar la cosecha');
    } finally {
      setCosechando((prev) => { const n = new Set(prev); n.delete(id); return n; });
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-full text-slate-400"><Loader2 className="animate-spin" /></div>;
  }

  const events: { label: string; planta: string; emoji: string; tipo: 'riego' | 'cosecha' }[] = [];
  cultivos.forEach((c) => {
    const p = getProfile(c.nombre_planta);
    events.push({ label: nextRiegoLabel(c.fecha_siembra, p.riegoDias), planta: c.nombre_planta, emoji: p.emoji, tipo: 'riego' });
    if (c.fecha_cosecha_est) {
      const daysUntil = Math.round((new Date(c.fecha_cosecha_est).getTime() - Date.now()) / 86_400_000);
      const cosechaLabel = daysUntil <= 0 ? '¡lista para cosechar!' : daysUntil === 1 ? 'mañana' : `en ${daysUntil} días`;
      events.push({ label: cosechaLabel, planta: c.nombre_planta, emoji: p.emoji, tipo: 'cosecha' });
    }
  });

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">🌱 Pilar Entorno</h1>
      <p className="text-slate-400">Micro-farming urbano y conexión con la naturaleza.</p>

      {/* Notificación proactiva — Edge Function activa en producción (cron 0 20 * * *) */}
      <div className="flex items-start gap-3 rounded-lg border border-amber-700/40 bg-amber-900/10 px-4 py-3">
        <span className="text-lg mt-0.5">🔔</span>
        <div className="flex-1">
          <p className="text-sm font-medium text-amber-300">Recordatorio de esta noche (20:00)</p>
          <p className="text-xs text-slate-400 mt-0.5">
            {cultivos.length > 0
              ? `${cultivos[0].nombre_planta}: riego ${nextRiegoLabel(cultivos[0].fecha_siembra, getProfile(cultivos[0].nombre_planta).riegoDias)} · ThriveMind te avisará por email cuando sea el momento.`
              : 'Añade tu primera planta para activar los recordatorios automáticos de riego y cosecha.'}
          </p>
          <span className="inline-block mt-1 text-[10px] bg-amber-800/30 border border-amber-600/40 text-amber-400 px-1.5 py-0.5 rounded">Edge Function activa ✓</span>
        </div>
      </div>

      {/* Clima actual */}
      {clima && (
        <Card className="border-slate-700 bg-slate-800/50">
          <CardContent className="p-4 flex items-center gap-4">
            <span className="text-3xl">🌤️</span>
            <div>
              <p className="font-medium">{clima.descripcion as string}</p>
              <p className="text-sm text-slate-400">{clima.temperatura as number}°C — {clima.ciudad as string}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Cultivos activos — con ILD y botón de cosecha */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>Tus Cultivos</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {cultivos.length === 0 ? (
            <p className="text-slate-400 text-sm">Aún no tienes cultivos. ¡Empieza con una planta del kit de inicio!</p>
          ) : (
            cultivos.map((c) => {
              const p = getProfile(c.nombre_planta);
              const elapsed = daysSince(c.fecha_siembra);
              const ildLeft = Math.max(0, p.ildPicoDias - elapsed);
              return (
                <div key={c.id} className="rounded-lg bg-slate-700/50 p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{p.emoji} {c.nombre_planta}</p>
                      <p className="text-xs text-slate-400">
                        Sembrada: {c.fecha_siembra}
                        {c.fecha_cosecha_est && ` · Cosecha est.: ${c.fecha_cosecha_est}`}
                      </p>
                    </div>
                    <Badge variant="outline">{c.estado}</Badge>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-violet-300">
                    <span>🧠</span>
                    <span>ILD D+{elapsed}{ildLeft > 0 ? ` · pico dopaminérgico en ${ildLeft} días` : ' · ¡en el pico — buen momento para cosechar!'}</span>
                  </div>
                  <div className="flex gap-2 pt-1">
                    <button
                      onClick={() => registrarCosecha(c.id, c.nombre_planta)}
                      disabled={cosechando.has(c.id)}
                      className="flex-1 text-xs bg-emerald-700/30 border border-emerald-600/40 text-emerald-300 px-2 py-1.5 rounded hover:bg-emerald-700/50 disabled:opacity-50 transition-colors"
                    >
                      {cosechando.has(c.id) ? <Loader2 className="w-3 h-3 animate-spin inline mr-1" /> : null}
                      ✅ Registrar cosecha
                    </button>
                    <button
                      onClick={() => eliminarCultivo(c.id, c.nombre_planta)}
                      className="text-red-400 hover:text-red-300 text-xs px-2 py-1 rounded hover:bg-red-900/30 transition-colors"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </CardContent>
      </Card>

      {/* Calendario riego/cosecha */}
      {events.length > 0 && (
        <Card className="border-slate-700 bg-slate-800/50">
          <CardHeader>
            <CardTitle>📅 Próximos eventos · Riego y Cosecha</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {events.map((e, i) => (
                <div key={i} className="flex items-center gap-3 text-sm">
                  <span className="text-base">{e.tipo === 'riego' ? '💧' : '🌾'}</span>
                  <span className="text-slate-300 font-medium capitalize">{e.tipo}</span>
                  <span className="text-slate-400">{e.emoji} {e.planta}</span>
                  <span className={`ml-auto text-xs font-medium ${e.tipo === 'cosecha' && e.label.includes('lista') ? 'text-emerald-400' : 'text-slate-400'}`}>
                    {e.label}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Consejo IA */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>🌿 Consejo de Cultivo con IA</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-slate-400">Pregunta sobre tus plantas, clima o temporada y obtén consejo personalizado.</p>
          <input
            value={consulta}
            onChange={(e) => setConsulta(e.target.value)}
            placeholder="Ej: ¿Qué debo plantar en verano? ¿Cómo cuido mi menta?"
            className="w-full px-3 py-2 rounded-lg bg-slate-700 border border-slate-600 text-sm text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-emerald-500"
          />
          <Button className="w-full" onClick={pedirConsejo} disabled={consejoLoading}>
            {consejoLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
            {consejoLoading ? 'Consultando IA...' : '🤖 Obtener Consejo'}
          </Button>
          {consejo && (
            <div className="mt-3 p-3 rounded-lg bg-emerald-900/20 border border-emerald-700/30 text-sm text-slate-200 whitespace-pre-wrap">
              {consejo}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Kit de inicio — lavanda prioritaria (§3.3.3 Kasper 2014, linalool/GABA) */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>🌿 Kit de Inicio · Plantas Terapéuticas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <button
              onClick={() => agregarCultivo('Lavanda', 'flor')}
              className="w-full flex items-center gap-3 rounded-lg p-3 bg-violet-900/20 border border-violet-600/30 hover:bg-violet-900/40 text-left transition-colors"
            >
              <span className="text-lg">💜</span>
              <div>
                <p className="text-sm font-medium text-slate-200">
                  Lavanda
                  <span className="text-[10px] bg-violet-700/40 text-violet-300 px-1.5 py-0.5 rounded ml-2">Recomendada</span>
                </p>
                <p className="text-xs text-slate-400 mt-0.5">Linalool · ansiolítico natural · agonista GABA sin dependencia</p>
              </div>
            </button>
            {[
              { nombre: 'Menta',      tipo: 'hierba', emoji: '🌿', motivo: 'Mentol · activación y foco' },
              { nombre: 'Albahaca',   tipo: 'hierba', emoji: '🌱', motivo: 'Eugenol · antiinflamatorio' },
              { nombre: 'Manzanilla', tipo: 'flor',   emoji: '🌼', motivo: 'Apigenina · efecto calmante' },
              { nombre: 'Romero',     tipo: 'hierba', emoji: '🌲', motivo: 'Ácido rosmarínico · neuroprotector' },
            ].map((p) => (
              <button
                key={p.nombre}
                onClick={() => agregarCultivo(p.nombre, p.tipo)}
                className="w-full flex items-center gap-3 rounded-lg p-3 bg-slate-700/30 border border-slate-600/30 hover:bg-slate-700/50 text-left transition-colors"
              >
                <span className="text-lg">{p.emoji}</span>
                <div>
                  <p className="text-sm font-medium text-slate-200">{p.nombre}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{p.motivo}</p>
                </div>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Fase 2 roadmap cards */}
      <div className="space-y-3">
        <div className="rounded-lg border border-dashed border-slate-600 bg-slate-800/20 p-4">
          <div className="flex items-start gap-3">
            <span className="text-xl">🍽️</span>
            <div>
              <div className="flex items-center gap-2">
                <p className="text-sm font-medium text-slate-300">Tus hierbas en tus recetas</p>
                <span className="text-[10px] bg-violet-800/40 border border-violet-600/40 text-violet-300 px-1.5 py-0.5 rounded">Fase 2</span>
              </div>
              <p className="text-xs text-slate-500 mt-1">La IA priorizará automáticamente tus hierbas cosechadas en las sugerencias del Pilar Cuerpo.</p>
            </div>
          </div>
        </div>
        <div className="rounded-lg border border-dashed border-slate-600 bg-slate-800/20 p-4">
          <div className="flex items-start gap-3">
            <span className="text-xl">📋</span>
            <div>
              <div className="flex items-center gap-2">
                <p className="text-sm font-medium text-slate-300">Guía visual paso a paso</p>
                <span className="text-[10px] bg-violet-800/40 border border-violet-600/40 text-violet-300 px-1.5 py-0.5 rounded">Fase 2</span>
              </div>
              <p className="text-xs text-slate-500 mt-1">Instrucciones enriquecidas con imágenes para siembra, cuidado y cosecha de cada planta.</p>
            </div>
          </div>
        </div>
        <div className="rounded-lg border border-dashed border-slate-600 bg-slate-800/20 p-4">
          <div className="flex items-start gap-3">
            <span className="text-xl">🔬</span>
            <div>
              <div className="flex items-center gap-2">
                <p className="text-sm font-medium text-slate-300">Monitor de salud vegetal</p>
                <span className="text-[10px] bg-violet-800/40 border border-violet-600/40 text-violet-300 px-1.5 py-0.5 rounded">Fase 2</span>
              </div>
              <p className="text-xs text-slate-500 mt-1">GPT-4o Vision analizará fotos de tus plantas para detectar enfermedades o carencias.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
