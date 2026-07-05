'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';

export default function MentePage() {
  const [intencion, setIntencion] = useState('');
  const [objetivo, setObjetivo] = useState('calma');
  const [loading, setLoading] = useState(false);
  const [meditacion, setMeditacion] = useState<{ guion: string; tecnica: string } | null>(null);

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
      toast.success('Meditación generada con éxito');
    } catch {
      toast.error('Error al generar la meditación');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold">🧠 Pilar Mente</h1>
      <p className="text-slate-400">Genera una sesión de meditación personalizada basada en tu estado actual.</p>

      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>Nueva Meditación</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
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
    </div>
  );
}
