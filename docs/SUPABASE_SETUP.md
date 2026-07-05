# 🗄️ Configuración de Base de Datos — Supabase

> Este documento detalla todos los cambios que debes realizar **manualmente** en tu dashboard de Supabase para que las nuevas funcionalidades de ThriveMind funcionen correctamente.

---

## Tabla de Contenido
1. [Soft Deletes — cultivos_activos](#1-soft-deletes--cultivos_activos)
2. [Gamificación](#2-gamificación)
3. [Perfiles HUE Personalizados](#3-perfiles-hue-personalizados)
4. [Planificación de Comidas](#4-planificación-de-comidas)
5. [Notificaciones Post Check-in](#5-notificaciones-post-check-in)
6. [Refresh Tokens (Opcional)](#6-refresh-tokens-opcional)
7. [Row Level Security (RLS)](#7-row-level-security-rls)
8. [Intervention Logs (MLOps)](#8-intervention-logs-mlops)
9. [Extended User Preferences](#9-extended-user-preferences)

---

## 1. Soft Deletes — `cultivos_activos`

Se añaden columnas para borrado lógico en lugar de eliminación permanente.

```sql
-- Agregar columnas de soft delete
ALTER TABLE cultivos_activos
  ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ DEFAULT NULL,
  ADD COLUMN IF NOT EXISTS deleted_by UUID DEFAULT NULL REFERENCES auth.users(id);

-- Índice para filtrar rápidamente los registros activos
CREATE INDEX IF NOT EXISTS idx_cultivos_deleted_at
  ON cultivos_activos(deleted_at)
  WHERE deleted_at IS NULL;
```

---

## 2. Gamificación

### 2.1 Agregar puntos al perfil del usuario

```sql
ALTER TABLE profiles
  ADD COLUMN IF NOT EXISTS gamification_points INTEGER DEFAULT 0;
```

### 2.2 Tabla de historial de puntos

```sql
CREATE TABLE IF NOT EXISTS gamification_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  action TEXT NOT NULL,          -- e.g. 'checkin_diario', 'meditacion_completada'
  points INTEGER NOT NULL,
  referencia_id TEXT DEFAULT NULL, -- ID del checkin, meditación, etc.
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_gamification_history_user
  ON gamification_history(user_id, created_at DESC);
```

### 2.3 Tabla de hitos desbloqueados

```sql
CREATE TABLE IF NOT EXISTS user_milestones (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  milestone_key TEXT NOT NULL,   -- e.g. 'semilla', 'brote', 'florecimiento'
  unlocked_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(user_id, milestone_key)
);

CREATE INDEX IF NOT EXISTS idx_user_milestones_user
  ON user_milestones(user_id);
```

---

## 3. Perfiles HUE Personalizados

```sql
CREATE TABLE IF NOT EXISTS hue_profiles (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  kelvin INTEGER NOT NULL CHECK (kelvin BETWEEN 2000 AND 6500),
  brightness INTEGER NOT NULL CHECK (brightness BETWEEN 0 AND 100),
  color_hex TEXT DEFAULT '#ffffff',
  description TEXT DEFAULT '',
  is_custom BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_hue_profiles_user
  ON hue_profiles(user_id);
```

---

## 4. Planificación de Comidas

```sql
CREATE TABLE IF NOT EXISTS meal_plans (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  plan JSONB NOT NULL,              -- Array de 7 objetos {dia, desayuno, almuerzo, cena}
  shopping_list JSONB NOT NULL,     -- Array de {categoria, items[]}
  objetivo TEXT DEFAULT 'equilibrio', -- 'equilibrio', 'energia', 'relajacion'
  calorias_diarias_promedio INTEGER DEFAULT 0,
  semana_inicio DATE NOT NULL,
  semana_fin DATE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_meal_plans_user
  ON meal_plans(user_id, semana_inicio DESC);
```

---

## 5. Notificaciones Post Check-in

```sql
CREATE TABLE IF NOT EXISTS notifications (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  tipo TEXT NOT NULL,              -- 'mejora', 'alerta', 'motivacion'
  titulo TEXT NOT NULL,
  mensaje TEXT NOT NULL,
  emoji TEXT DEFAULT '📌',
  delta JSONB DEFAULT NULL,        -- {campo: 'energia', valor: +2}
  read BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_unread
  ON notifications(user_id, read, created_at DESC)
  WHERE read = false;
```

---

## 6. Refresh Tokens (Opcional)

Si quieres almacenar refresh tokens en la base de datos para poder revocarlos (en lugar de solo validar por firma JWT), crea esta tabla:

```sql
CREATE TABLE IF NOT EXISTS refresh_tokens (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  token_hash TEXT NOT NULL,        -- SHA-256 del token (nunca guardar en texto plano)
  expires_at TIMESTAMPTZ NOT NULL,
  revoked BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user
  ON refresh_tokens(user_id)
  WHERE revoked = false;
```

> **Nota:** La implementación actual valida refresh tokens por firma JWT sin consulta a la DB. Esta tabla es para cuando quieras añadir revocación explícita de tokens.

---

## 7. Row Level Security (RLS)

Asegúrate de que **RLS está habilitado** en todas las tablas nuevas y que las políticas permitan que cada usuario solo acceda a sus propios datos.

```sql
-- Habilitar RLS en las nuevas tablas
ALTER TABLE gamification_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE hue_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE meal_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Políticas: cada usuario solo lee/escribe sus propios datos
-- Repite este patrón para cada tabla:

CREATE POLICY "Users can manage their own gamification_history"
  ON gamification_history FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can manage their own user_milestones"
  ON user_milestones FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can manage their own hue_profiles"
  ON hue_profiles FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can manage their own meal_plans"
  ON meal_plans FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can manage their own notifications"
  ON notifications FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

---

## 8. Intervention Logs (MLOps)

Tabla para cerrar el ciclo MLOps: registra cada intervención generada por el sistema
junto con el estado emocional del usuario y su feedback posterior.

```sql
CREATE TABLE IF NOT EXISTS intervention_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
  emotional_state TEXT NOT NULL,
  confidence FLOAT NOT NULL DEFAULT 0,
  intervention_type TEXT NOT NULL,
  intervention_detail JSONB DEFAULT '{}',
  context_snapshot JSONB DEFAULT '{}',
  user_feedback_score INTEGER CHECK (user_feedback_score >= 1 AND user_feedback_score <= 5),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_intervention_logs_user
  ON intervention_logs(user_id, created_at DESC);

ALTER TABLE intervention_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage their own intervention_logs"
  ON intervention_logs FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

---

## 9. Extended User Preferences

Añade campos de personalización nutricional al modelo de preferencias.

```sql
ALTER TABLE user_preferences
  ADD COLUMN IF NOT EXISTS alergias JSONB DEFAULT '[]',
  ADD COLUMN IF NOT EXISTS preferencia_dieta TEXT DEFAULT 'sin_restriccion',
  ADD COLUMN IF NOT EXISTS presupuesto_semanal TEXT DEFAULT 'medio',
  ADD COLUMN IF NOT EXISTS objetivo_fitness TEXT DEFAULT 'mantener';
```

---

## ✅ Orden Recomendado de Ejecución

1. Abre el **SQL Editor** en tu dashboard de Supabase
2. Ejecuta las secciones en orden (1 → 7)
3. Verifica que las tablas aparezcan en **Table Editor**
4. Confirma que RLS está habilitado (columna verde en cada tabla)

> **Tip:** Puedes copiar todo el SQL de este documento y ejecutarlo de una vez. Todos los comandos usan `IF NOT EXISTS` / `IF NOT EXISTS` para ser idempotentes.

---

## 📋 Resumen de Cambios

| Tabla | Acción | Funcionalidad |
|-------|--------|---------------|
| `cultivos_activos` | ALTER (2 columnas + índice) | Soft Deletes |
| `profiles` | ALTER (1 columna) | Gamificación |
| `gamification_history` | CREATE | Historial de puntos |
| `user_milestones` | CREATE | Hitos desbloqueados |
| `hue_profiles` | CREATE | Perfiles HUE personalizados |
| `meal_plans` | CREATE | Planes de comidas semanales |
| `notifications` | CREATE | Notificaciones post check-in |
| `refresh_tokens` | CREATE (opcional) | Revocación de tokens |
| `intervention_logs` | CREATE | Logging MLOps (estado→intervención→feedback) |
| `user_preferences` | ALTER (4 columnas) | Alergias, dieta, presupuesto, fitness |
