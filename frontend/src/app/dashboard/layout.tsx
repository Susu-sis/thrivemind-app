'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { GlobalSearch } from '@/components/GlobalSearch';
import api from '@/lib/api';

type SubItem = { href: string; label: string; emoji: string };
type NavItem  = { href: string; label: string; emoji: string; pilar?: string; sub?: SubItem[] };
type NavGroup = { label: string | null; items: NavItem[] };

const NAV_GROUPS: NavGroup[] = [
  {
    label: null,
    items: [
      { href: '/dashboard', label: 'Dashboard', emoji: '📊' },
    ],
  },
  {
    label: 'Pilares',
    items: [
      {
        href: '/dashboard/mente',  label: 'Mente',   emoji: '🧠', pilar: 'mente',
        sub: [{ href: '/dashboard/perfiles-hue', label: 'Perfiles HUE', emoji: '💡' }],
      },
      {
        href: '/dashboard/cuerpo', label: 'Cuerpo',  emoji: '💚', pilar: 'cuerpo',
        sub: [
          { href: '/dashboard/checkin',      label: 'Check-in diario', emoji: '✍️' },
          { href: '/dashboard/meal-planner', label: 'Plan Comidas',    emoji: '🍽️' },
        ],
      },
      { href: '/dashboard/entorno', label: 'Entorno', emoji: '🌱', pilar: 'entorno' },
    ],
  },
  {
    label: 'Herramientas',
    items: [
      { href: '/dashboard/insights',      label: 'Recomendaciones', emoji: '💡' },
      { href: '/dashboard/convergencia',  label: 'Convergencia',    emoji: '📈' },
      { href: '/dashboard/correlaciones', label: 'Correlaciones',   emoji: '🔗' },
      { href: '/dashboard/historial',     label: 'Historial',       emoji: '📜' },
      { href: '/dashboard/sentimiento',   label: 'Sentimiento',     emoji: '💬' },
      { href: '/dashboard/gamificacion',  label: 'Gamificación',    emoji: '🏆' },
    ],
  },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, loading, logout } = useAuth();
  const [pilares, setPilares] = useState({ mente: true, cuerpo: true, entorno: true });

  useEffect(() => {
    if (!loading && !user) {
      const token = typeof window !== 'undefined' ? localStorage.getItem('thrivemind_token') : null;
      if (!token) {
        window.location.href = '/login';
      }
    }
  }, [user, loading]);

  useEffect(() => {
    const handleAuthExpired = () => { window.location.href = '/login'; };
    window.addEventListener('auth:expired', handleAuthExpired);
    return () => window.removeEventListener('auth:expired', handleAuthExpired);
  }, []);

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



  return (
    <div className="flex h-screen bg-slate-900">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-700 bg-slate-800/50 flex flex-col">
        <div className="p-6 border-b border-slate-700">
          <h1 className="text-xl font-bold">🧠 ThriveMind</h1>
          <p className="text-xs text-slate-400 mt-1">{user?.nombre || 'Usuario'}</p>
          <div className="mt-3">
            <GlobalSearch />
          </div>
        </div>
        <nav className="flex-1 p-4 space-y-4 overflow-y-auto">
          {NAV_GROUPS.map((group, gi) => (
            <div key={gi}>
              {group.label && (
                <p className="px-3 mb-1 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                  {group.label}
                </p>
              )}
              <div className="space-y-0.5">
                {group.items
                  .filter((item) => !item.pilar || pilares[item.pilar as keyof typeof pilares])
                  .map((item) => {
                    const isActive = pathname === item.href;
                    const isPilar  = !!item.pilar;
                    return (
                      <div key={item.href}>
                        <Link
                          href={item.href}
                          className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                            isActive
                              ? 'bg-violet-600/20 text-violet-300'
                              : isPilar
                                ? 'text-slate-200 font-medium hover:text-white hover:bg-slate-700/50'
                                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
                          }`}
                        >
                          <span>{item.emoji}</span>
                          <span>{item.label}</span>
                        </Link>
                        {item.sub?.map((sub) => {
                          const subActive = pathname === sub.href;
                          return (
                            <Link
                              key={sub.href}
                              href={sub.href}
                              className={`flex items-center gap-2 pl-8 pr-3 py-1.5 rounded-lg text-xs transition-colors ${
                                subActive
                                  ? 'bg-violet-600/15 text-violet-300'
                                  : 'text-slate-500 hover:text-slate-300 hover:bg-slate-700/30'
                              }`}
                            >
                              <span>{sub.emoji}</span>
                              <span>{sub.label}</span>
                            </Link>
                          );
                        })}
                      </div>
                    );
                  })}
              </div>
            </div>
          ))}
          <div className="pt-2 border-t border-slate-700/50">
            <Link
              href="/dashboard/configuracion"
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                pathname === '/dashboard/configuracion'
                  ? 'bg-violet-600/20 text-violet-300'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
              }`}
            >
              <span>⚙️</span>
              <span>Configuración</span>
            </Link>
          </div>
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
