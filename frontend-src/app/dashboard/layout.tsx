'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import api from '@/lib/api';

const ALL_NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', emoji: '📊', always: true },
  { href: '/dashboard/checkin', label: 'Check-in', emoji: '✍️', always: true },
  { href: '/dashboard/mente', label: 'Mente', emoji: '🧠', pilar: 'mente' },
  { href: '/dashboard/cuerpo', label: 'Cuerpo', emoji: '💚', pilar: 'cuerpo' },
  { href: '/dashboard/entorno', label: 'Entorno', emoji: '🌱', pilar: 'entorno' },
  { href: '/dashboard/configuracion', label: 'Configuración', emoji: '⚙️', always: true },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [pilares, setPilares] = useState({ mente: true, cuerpo: true, entorno: true });

  useEffect(() => {
    api.get('/preferences/').then((res) => {
      setPilares({
        mente: res.data.mente_activo,
        cuerpo: res.data.cuerpo_activo,
        entorno: res.data.entorno_activo,
      });
    }).catch(() => {
      // If preferences not loaded, show all pilars
    });
  }, []);

  const navItems = ALL_NAV_ITEMS.filter(
    (item) => item.always || (item.pilar && pilares[item.pilar as keyof typeof pilares])
  );

  return (
    <div className="flex h-screen bg-slate-900">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-700 bg-slate-800/50 flex flex-col">
        <div className="p-6 border-b border-slate-700">
          <h1 className="text-xl font-bold">🧠 ThriveMind</h1>
          <p className="text-xs text-slate-400 mt-1">{user?.nombre || 'Usuario'}</p>
        </div>
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                  isActive
                    ? 'bg-violet-600/20 text-violet-300'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
                }`}
              >
                <span>{item.emoji}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
        <div className="p-4 border-t border-slate-700">
          <Button variant="ghost" className="w-full text-slate-400" onClick={logout}>
            Cerrar Sesión
          </Button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto p-6">{children}</main>
    </div>
  );
}
