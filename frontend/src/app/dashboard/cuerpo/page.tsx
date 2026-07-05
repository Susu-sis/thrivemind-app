'use client';

import { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, Upload } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';

export default function CuerpoPage() {
  const [loading, setLoading] = useState(false);
  const [analisis, setAnalisis] = useState<Record<string, unknown> | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

      {/* Análisis de imagen */}
      <Card className="border-slate-700 bg-slate-800/50">
        <CardHeader>
          <CardTitle>Analizar un Plato</CardTitle>
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
