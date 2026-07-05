'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import api from '@/lib/api';

interface Meal {
  nombre: string;
  calorias: number;
}

interface MealPlanData {
  plan: Record<string, { desayuno: Meal; almuerzo: Meal; cena: Meal }>;
  shopping_list: Record<string, string[]>;
  calorias_diarias_promedio: number;
}

const MEAL_EMOJIS: Record<string, string> = {
  desayuno: '🌅',
  almuerzo: '☀️',
  cena: '🌙',
};

export default function MealPlannerPage() {
  const [data, setData] = useState<MealPlanData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showShopping, setShowShopping] = useState(false);

  useEffect(() => {
    api.get('/meal-planner/weekly')
      .then((res) => setData(res.data))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-slate-400">Generando plan semanal...</div>;
  }

  if (!data) return null;

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">🍽️ Plan Semanal de Comidas</h1>
          <p className="text-slate-400 mt-1">
            Promedio diario: <span className="text-emerald-400 font-semibold">{data.calorias_diarias_promedio} kcal</span>
          </p>
        </div>
        <button
          onClick={() => setShowShopping((v) => !v)}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm transition-colors"
        >
          {showShopping ? 'Ver Plan' : '🛒 Lista de Compras'}
        </button>
      </div>

      {showShopping ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(data.shopping_list).map(([categoria, items]) => (
            <Card key={categoria} className="bg-slate-800/50 border-slate-700">
              <CardHeader className="pb-2">
                <CardTitle className="text-base">{categoria}</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-1">
                  {items.map((item, i) => (
                    <li key={i} className="text-sm text-slate-300 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {Object.entries(data.plan).map(([dia, meals]) => (
            <Card key={dia} className="bg-slate-800/50 border-slate-700">
              <CardHeader className="pb-2">
                <CardTitle className="text-base capitalize">{dia}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {(['desayuno', 'almuerzo', 'cena'] as const).map((meal) => {
                    const m = meals[meal];
                    return (
                      <div key={meal} className="bg-slate-700/40 rounded-lg p-3">
                        <p className="text-xs text-slate-400 mb-1">
                          {MEAL_EMOJIS[meal]} {meal.charAt(0).toUpperCase() + meal.slice(1)}
                        </p>
                        <p className="text-sm font-medium text-white">{m.nombre}</p>
                        <Badge className="mt-1 bg-slate-600/50 text-slate-300 text-xs">
                          {m.calorias} kcal
                        </Badge>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
