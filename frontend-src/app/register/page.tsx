'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';

export default function RegisterPage() {
  const [nombre, setNombre] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!nombre || !email || !password) {
      setError('Por favor completa todos los campos');
      return;
    }
    if (password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres');
      return;
    }

    setIsLoading(true);
    try {
      await register(email, password, nombre);
      toast.success('¡Cuenta creada! Bienvenido a ThriveMind');
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Error al crear la cuenta';
      setError(msg);
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 px-4">
      <Card className="w-full max-w-md border-slate-700 bg-slate-800/50 backdrop-blur">
        <CardHeader className="space-y-2">
          <div className="flex items-center justify-center mb-4">
            <span className="text-4xl">🌱</span>
          </div>
          <CardTitle className="text-2xl text-center">Crea tu cuenta</CardTitle>
          <CardDescription className="text-center">
            Empieza tu viaje de bienestar holístico
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="nombre" className="text-sm font-medium">Nombre</label>
              <Input id="nombre" type="text" placeholder="Tu nombre" value={nombre}
                onChange={(e) => setNombre(e.target.value)} disabled={isLoading}
                className="bg-slate-700 border-slate-600" />
            </div>
            <div className="space-y-2">
              <label htmlFor="email" className="text-sm font-medium">Email</label>
              <Input id="email" type="email" placeholder="tu@email.com" value={email}
                onChange={(e) => setEmail(e.target.value)} disabled={isLoading}
                className="bg-slate-700 border-slate-600" />
            </div>
            <div className="space-y-2">
              <label htmlFor="password" className="text-sm font-medium">Contraseña</label>
              <Input id="password" type="password" placeholder="Mínimo 6 caracteres" value={password}
                onChange={(e) => setPassword(e.target.value)} disabled={isLoading}
                className="bg-slate-700 border-slate-600" />
            </div>
            {error && <p className="text-sm text-red-400">{error}</p>}
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : null}
              Crear Cuenta
            </Button>
            <p className="text-sm text-center text-slate-400">
              ¿Ya tienes cuenta?{' '}
              <Link href="/login" className="text-violet-400 hover:underline">Inicia sesión</Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
