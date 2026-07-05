'use client';

import { useEffect, useState, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';

interface SearchResult {
  id: string;
  title: string;
  icon: string;
  type: string;
  url: string;
}

export function GlobalSearch() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Record<string, SearchResult[]> | null>(null);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  // Listen for Ctrl+K / Cmd+K
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
      if (e.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  useEffect(() => {
    if (open) setTimeout(() => inputRef.current?.focus(), 50);
  }, [open]);

  const search = useCallback(async (q: string) => {
    if (!q.trim()) { setResults(null); return; }
    setLoading(true);
    try {
      const res = await api.get('/search/global', { params: { q } });
      setResults(res.data);
    } catch { setResults(null); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => search(query), 300);
    return () => clearTimeout(timer);
  }, [query, search]);

  const navigate = (url: string) => {
    router.push(url);
    setOpen(false);
    setQuery('');
  };

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-700/50 hover:bg-slate-700 text-sm text-slate-400 border border-slate-600"
      >
        🔍 Buscar... <kbd className="text-xs bg-slate-600 px-1.5 py-0.5 rounded ml-1">⌘K</kbd>
      </button>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]" onClick={() => setOpen(false)}>
      <div className="absolute inset-0 bg-black/60" />
      <div
        className="relative w-full max-w-lg bg-slate-800 border border-slate-600 rounded-xl shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-4 border-b border-slate-700">
          <input
            ref={inputRef}
            type="text"
            placeholder="Buscar meditaciones, cultivos, recetas..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-transparent text-white placeholder-slate-400 outline-none text-lg"
          />
        </div>

        <div className="max-h-80 overflow-y-auto p-2">
          {loading && <p className="text-center text-slate-400 py-4">Buscando...</p>}

          {results && Object.entries(results).map(([category, items]) => (
            <div key={category} className="mb-3">
              <p className="text-xs font-semibold uppercase text-slate-500 px-2 mb-1">{category}</p>
              {items.map((item) => (
                <button
                  key={item.id}
                  onClick={() => navigate(item.url)}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-700/60 text-left"
                >
                  <span className="text-lg">{item.icon}</span>
                  <span className="text-slate-200 text-sm">{item.title}</span>
                </button>
              ))}
            </div>
          ))}

          {query && !loading && (!results || Object.keys(results).length === 0) && (
            <p className="text-center text-slate-500 py-4">Sin resultados para &ldquo;{query}&rdquo;</p>
          )}

          {!query && !loading && (
            <p className="text-center text-slate-500 py-4 text-sm">Escribe para buscar en todos los módulos</p>
          )}
        </div>

        <div className="p-2 border-t border-slate-700 flex justify-end">
          <span className="text-xs text-slate-500">ESC para cerrar</span>
        </div>
      </div>
    </div>
  );
}
