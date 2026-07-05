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

export default function CheckinPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
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
      await api.post('/checkin/', form);
      toast.success('Check-in guardado correctamente');
      router.push('/dashboard');
    } catch {
      toast.error('Error al guardar el check-in');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">Check-in de Bienestar</h1>

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
        {loading ? 'Guardando...' : '✓ Guardar Check-in'}
      </Button>
    </div>
  );
}
