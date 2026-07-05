-- ============================================================================
-- ThriveMind — Schema Completo de Base de Datos
-- Ejecutar en: Supabase → SQL Editor → New Query
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";  -- pgvector para RAG

-- ── Tabla de perfiles de usuario ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS profiles (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email         VARCHAR(320) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nombre        TEXT NOT NULL,
    apellido      TEXT,
    avatar_url    TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at    TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- ── Check-ins diarios (los 3 pilares) ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS checkins (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id           UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    estado_emocional  INTEGER NOT NULL CHECK (estado_emocional BETWEEN 1 AND 10),
    emocion_principal TEXT,
    energia_fisica    INTEGER NOT NULL CHECK (energia_fisica BETWEEN 1 AND 10),
    horas_sueno       DECIMAL(3,1),
    conexion_entorno  INTEGER NOT NULL CHECK (conexion_entorno BETWEEN 1 AND 10),
    nota              TEXT,
    tipo_checkin      VARCHAR(20) DEFAULT 'diario' NOT NULL
                      CHECK (tipo_checkin IN (
                          'diario', 'pre_entrenamiento', 'post_entrenamiento',
                          'pre_meditacion', 'post_meditacion',
                          'pre_comida', 'post_comida',
                          'post_cosecha'
                      )),
    hrv_estimado      DECIMAL(6,2),
    referencia_id     UUID,
    hambre            INTEGER,
    saciedad          INTEGER,
    created_at        TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_checkins_user_date
    ON checkins(user_id, created_at DESC);

-- ── Preferencias de usuario (pilares modulares) ──────────────────────────────
CREATE TABLE IF NOT EXISTS user_preferences (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id           UUID UNIQUE NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    mente_activo      BOOLEAN DEFAULT true NOT NULL,
    mente_intensidad  INTEGER DEFAULT 1 NOT NULL CHECK (mente_intensidad BETWEEN 1 AND 3),
    cuerpo_activo     BOOLEAN DEFAULT true NOT NULL,
    cuerpo_intensidad INTEGER DEFAULT 1 NOT NULL CHECK (cuerpo_intensidad BETWEEN 1 AND 3),
    entorno_activo    BOOLEAN DEFAULT true NOT NULL,
    entorno_intensidad INTEGER DEFAULT 1 NOT NULL CHECK (entorno_intensidad BETWEEN 1 AND 3),
    objetivo_principal TEXT DEFAULT 'equilibrio' NOT NULL,
    frecuencia_checkin TEXT DEFAULT 'diario' NOT NULL,
    created_at        TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at        TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- ── Sesiones de meditación generadas por IA ──────────────────────────────────
CREATE TABLE IF NOT EXISTS meditation_sessions (
    id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id          UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    checkin_id       UUID REFERENCES checkins(id),
    intencion        TEXT NOT NULL,
    duracion_min     INTEGER NOT NULL DEFAULT 10,
    objetivo         TEXT NOT NULL,
    tecnica          TEXT,
    guion_meditacion TEXT NOT NULL,
    audio_url        TEXT,
    completada       BOOLEAN DEFAULT FALSE,
    valoracion       INTEGER CHECK (valoracion BETWEEN 1 AND 5),
    referencias_rag  JSONB DEFAULT '[]'::jsonb,
    created_at       TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- ── Análisis nutricionales con GPT-4o Vision ─────────────────────────────────
CREATE TABLE IF NOT EXISTS nutrition_analyses (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    imagen_url      TEXT,
    descripcion     TEXT,
    nombre_plato    TEXT,
    calorias_est    INTEGER,
    proteinas_g     DECIMAL(6,1),
    carbohidratos_g DECIMAL(6,1),
    grasas_g        DECIMAL(6,1),
    fibra_g         DECIMAL(6,1),
    analisis_texto  TEXT NOT NULL,
    recomendaciones TEXT,
    referencias_rag JSONB DEFAULT '[]'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- ── Cultivos de micro-farming ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cultivos_activos (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id           UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    nombre_planta     TEXT NOT NULL,
    tipo              TEXT NOT NULL,
    estado            TEXT NOT NULL DEFAULT 'semilla',
    fecha_siembra     DATE NOT NULL,
    fecha_cosecha_est DATE,
    notas             TEXT,
    imagen_url        TEXT,
    activo            BOOLEAN DEFAULT true NOT NULL,
    created_at        TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at        TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- ── Historial del asistente de farming ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS farming_chat_messages (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id     UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    crop_id     UUID REFERENCES cultivos_activos(id) ON DELETE SET NULL,
    role        TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- ── RAG: Papers científicos con embeddings ───────────────────────────────────
CREATE TABLE IF NOT EXISTS papers (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title           TEXT NOT NULL,
    authors         TEXT NOT NULL,
    year            INTEGER NOT NULL,
    journal         TEXT,
    doi             TEXT,
    pillar          TEXT NOT NULL,
    evidence_type   TEXT,
    embedding_text  TEXT NOT NULL,
    embedding       vector(1536),
    metadata        JSONB DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_papers_embedding
    ON papers USING ivfflat (embedding vector_cosine_ops) WITH (lists = 5);

-- ── Función RPC para buscar papers similares ─────────────────────────────────
CREATE OR REPLACE FUNCTION match_papers(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.72,
    match_count int DEFAULT 3
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    authors TEXT,
    year INTEGER,
    journal TEXT,
    doi TEXT,
    pillar TEXT,
    evidence_type TEXT,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        p.title,
        p.authors,
        p.year,
        p.journal,
        p.doi,
        p.pillar,
        p.evidence_type,
        1 - (p.embedding <=> query_embedding) AS similarity
    FROM papers p
    WHERE 1 - (p.embedding <=> query_embedding) > match_threshold
    ORDER BY p.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ── Row Level Security (RGPD compliance) ─────────────────────────────────────
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE checkins ENABLE ROW LEVEL SECURITY;
ALTER TABLE meditation_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE nutrition_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE cultivos_activos ENABLE ROW LEVEL SECURITY;
ALTER TABLE farming_chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- ── RLS Policies (cada usuario solo ve sus propios datos) ────────────────────
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can view own checkins" ON checkins
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own meditations" ON meditation_sessions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own nutrition" ON nutrition_analyses
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own crops" ON cultivos_activos
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own farming chat" ON farming_chat_messages
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own preferences" ON user_preferences
    FOR ALL USING (auth.uid() = user_id);

-- Papers are readable by all authenticated users
CREATE POLICY "Authenticated users can read papers" ON papers
    FOR SELECT USING (true);
