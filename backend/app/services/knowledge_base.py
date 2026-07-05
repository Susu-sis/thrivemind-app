"""
services/knowledge_base.py — LA ÚNICA FUENTE DE VERDAD DE THRIVEMIND

Todos los diccionarios de conocimiento científico que el sistema consulta
ANTES de hablar con GPT-4o.

Módulos que importan este archivo:
  - context_engine.py     → consulta HRV_THRESHOLDS y CHRONO_NUTRITION_MATRIX
  - nutrition_service.py  → consulta NUTRITION_KNOWLEDGE_BASE y WEATHER_MOOD_BASELINE
  - farming_service.py    → consulta FARMING_KNOWLEDGE_BASE

NOTA: Este archivo contiene la estructura completa con datos representativos.
Los diccionarios completos están documentados en GUIA_THRIVEMIND_v17_v3.md
secciones §5E.1 a §5E.5. Al migrar al Mac, copiar las versiones completas
de la guía para cada diccionario.
"""

# =============================================================================
# DICCIONARIO 1: NUTRITION_KNOWLEDGE_BASE
# Cada clave es un neurotransmisor objetivo con toda su bioquímica.
# =============================================================================

NUTRITION_KNOWLEDGE_BASE = {
    "serotonina": {
        "neurotransmisor": "Serotonina (5-Hidroxitriptamina / 5-HT)",
        "descripcion_mecanismo": (
            "El triptófano dietético cruza la barrera hematoencefálica (BHE) "
            "a través del transportador LAT1. La insulina postprandial capta "
            "los LNAAs competidores (Efecto Wurtman), facilitando el acceso "
            "cerebral del triptófano. Ref: Wurtman & Wurtman (1995)."
        ),
        "precursor_principal": "L-Triptófano",
        "alimentos": [
            {"nombre": "Espirulina (alga seca)", "mg_por_100g": 929,
             "notas_preparacion": "5g en smoothie con plátano maduro para Efecto Wurtman."},
            {"nombre": "Tofu firme", "mg_por_100g": 747,
             "notas_preparacion": "150g con arroz integral o boniato asado."},
            {"nombre": "Semillas de calabaza", "mg_por_100g": 578,
             "notas_preparacion": "28g con fruta de bajo IG (manzana, pera)."},
            {"nombre": "Pavo (pechuga cocida)", "mg_por_100g": 340,
             "notas_preparacion": "Solo con carbohidratos para Efecto Wurtman."},
        ],
        "cofactores": {
            "vitamina_B6": "Cofactor de AADC. Fuentes: plátano, pimiento rojo.",
            "hierro": "Cofactor de TPH2. Fuentes: lentejas, espinacas con vit C.",
            "magnesio": "Cofactor general de >300 enzimas.",
            "zinc": "Modula TPH2. Fuentes: semillas de calabaza.",
        },
        "inhibidores": {
            "alcohol": "Depleciona triptófano vía metabolismo del acetaldehído.",
            "cafeina_excesiva": ">400mg/día activa eje HPA (cortisol).",
            "proteina_sola_sin_carbohidratos": "Eleva todos los LNAAs → triptófano pierde.",
        },
        "ventana_horaria_optima": ["tarde", "noche"],
        "referencia_apa": "Wurtman, R. J., & Wurtman, J. J. (1995). Brain serotonin, carbohydrate-craving, obesity and depression. Obesity Research, 3(S4), 477S-480S.",
    },

    "dopamina": {
        "neurotransmisor": "Dopamina (DA)",
        "descripcion_mecanismo": (
            "La tirosina cruza la BHE y es convertida en L-DOPA por TH "
            "(Tirosina Hidroxilasa). No necesita el truco Wurtman — se "
            "absorbe mejor con proteína. Ref: Fernstrom & Fernstrom (2007)."
        ),
        "precursor_principal": "L-Tirosina",
        "alimentos": [
            {"nombre": "Queso parmesano", "mg_por_100g": 2565,
             "notas_preparacion": "30g rallado en desayuno."},
            {"nombre": "Soja (edamame cocido)", "mg_por_100g": 1497,
             "notas_preparacion": "150g de edamame."},
            {"nombre": "Atún (en agua)", "mg_por_100g": 1207,
             "notas_preparacion": "100g con DHA omega-3."},
        ],
        "cofactores": {
            "hierro": "Cofactor esencial de TH.",
            "vitamina_B6": "Cofactor de AADC.",
            "vitamina_C": "Cofactor de DβH.",
        },
        "inhibidores": {
            "estres_cronico": "El cortisol crónico degrada TH.",
            "azucar_refinada": "Desensibiliza receptores D2.",
        },
        "ventana_horaria_optima": ["manana_temprana", "pico_cognitivo"],
        "referencia_apa": "Fernstrom, J. D., & Fernstrom, M. H. (2007). J Nutrition, 137(6), 1539S-1547S.",
    },

    "gaba": {
        "neurotransmisor": "Ácido γ-Aminobutírico (GABA)",
        "descripcion_mecanismo": (
            "GABA se sintetiza a partir de L-Glutamato por GAD (requiere B6). "
            "L-teanina (té verde) actúa como agonista parcial de GABA-A. "
            "Ref: Abdou et al. (2006)."
        ),
        "precursor_principal": "L-Glutamato",
        "alimentos": [
            {"nombre": "Té verde matcha", "mg_por_100g": 220,
             "notas_preparacion": "2g matcha en agua <80°C."},
            {"nombre": "Kimchi / miso (fermentados)", "mg_por_100g": 150,
             "notas_preparacion": "GABA directo de bacterias lácticas."},
            {"nombre": "Almendras (magnesio)", "mg_por_100g": 268,
             "notas_preparacion": "30g almendras = 80mg Mg."},
        ],
        "cofactores": {
            "vitamina_B6": "Cofactor OBLIGATORIO de GAD.",
            "magnesio": "Bloqueador natural del receptor NMDA.",
        },
        "inhibidores": {
            "alcohol_cronico": "Regula a la baja receptores GABA-A.",
            "cafeina_excesiva": "Reduce tono GABAérgico indirectamente.",
        },
        "ventana_horaria_optima": ["tarde", "noche"],
        "referencia_apa": "Abdou, A. M. et al. (2006). BioFactors, 26(3), 201-208.",
    },

    "acetilcolina": {
        "neurotransmisor": "Acetilcolina (ACh)",
        "descripcion_mecanismo": "Se sintetiza a partir de colina + acetil-CoA por ChAT.",
        "precursor_principal": "Colina",
        "alimentos": [
            {"nombre": "Huevo entero (yema)", "mg_por_100g": 293, "notas_preparacion": "2 huevos = 250mg colina."},
            {"nombre": "Hígado de ternera", "mg_por_100g": 418, "notas_preparacion": "75g cubre 57% AI diaria."},
        ],
        "cofactores": {"vitamina_B5": "Componente del Acetil-CoA.", "vitamina_B12": "Integridad de mielina."},
        "inhibidores": {"anticolinergicos": "Bloquean receptores muscarínicos."},
        "ventana_horaria_optima": ["manana_temprana", "pico_cognitivo"],
        "referencia_apa": "Zeisel, S. H. (2000). Nutrition, 16(7-8), 669-671.",
    },

    "bdnf": {
        "neurotransmisor": "BDNF (Factor Neurotrófico Derivado del Cerebro)",
        "descripcion_mecanismo": "DHA activa genes BDNF y TrkB. Curcumina + piperina potencia 2000%.",
        "precursor_principal": "No aplica (proteína endógena, estimulada por nutrientes).",
        "alimentos": [
            {"nombre": "Salmón/sardinas (DHA)", "mg_por_100g": 2000, "notas_preparacion": "2-3 porciones/semana."},
            {"nombre": "Cúrcuma + pimienta negra", "mg_por_100g": 3400, "notas_preparacion": "1 cta cúrcuma + 1/4 pimienta + aceite."},
            {"nombre": "Arándanos silvestres", "mg_por_100g": 480, "notas_preparacion": "150g/día."},
        ],
        "cofactores": {"ejercicio_aerobico": "El estimulador de BDNF más potente.", "sueño_profundo_N3": "Pico de síntesis BDNF."},
        "inhibidores": {"sedentarismo": "Principal factor de reducción de BDNF."},
        "ventana_horaria_optima": ["manana_temprana", "pico_cognitivo"],
        "referencia_apa": "Gomez-Pinilla, F. (2008). Nature Reviews Neuroscience, 9(7), 568-578.",
    },

    "cortisol_reduccion": {
        "neurotransmisor": "Cortisol — objetivo: reducción adaptógena",
        "descripcion_mecanismo": "El cortisol inhibe BDNF, degrada TH y activa IDO.",
        "precursor_principal": "No aplica — objetivo es reducción.",
        "alimentos": [
            {"nombre": "Ashwagandha KSM-66", "mg_por_100g": None, "notas_preparacion": "300-600mg extracto por la noche."},
            {"nombre": "L-teanina (matcha)", "mg_por_100g": 220, "notas_preparacion": "200mg reduce cortisol 44%."},
        ],
        "cofactores": {"magnesio": "Se agota con estrés.", "vitamina_B5": "Regulación suprarrenal."},
        "inhibidores": {"cafeina_tarde": "Prolonga vida media del cortisol.", "pantallas_noche": "Eleva cortisol por eje HPA."},
        "ventana_horaria_optima": ["tarde", "noche"],
        "referencia_apa": "Chandrasekhar, K. et al. (2012). Indian J Psychological Medicine, 34(3), 255-262.",
    },

    "melatonina": {
        "neurotransmisor": "Melatonina (N-acetil-5-metoxitriptamina)",
        "descripcion_mecanismo": "Se sintetiza en la pineal a partir de serotonina. Inhibida por luz azul.",
        "precursor_principal": "Serotonina (del triptófano)",
        "alimentos": [
            {"nombre": "Cerezas Montmorency", "mg_por_100g": None, "notas_preparacion": "240ml zumo 30-60min antes de dormir."},
            {"nombre": "Nueces", "mg_por_100g": None, "notas_preparacion": "28g en la cena."},
        ],
        "cofactores": {"oscuridad_absoluta": "La luz azul suprime 85% de melatonina.", "magnesio": "Activa SNAT."},
        "inhibidores": {"luz_azul_nocturna": "Principal causa de déficit.", "alcohol": "Fragmenta arquitectura del sueño."},
        "ventana_horaria_optima": ["noche"],
        "referencia_apa": "Howatson, G. et al. (2012). European J Nutrition, 51(8), 909-916.",
    },

    # ── T3-H: Endorfinas (bloque 8) ──
    "endorfinas": {
        "neurotransmisor": "β-Endorfinas (péptidos opioides endógenos)",
        "descripcion_mecanismo": (
            "Se sintetizan en la hipófisis a partir de propiomelanocortina (POMC). "
            "Ejercicio aeróbico >30 min y capsaicina activan su liberación. "
            "Modulan dolor, euforia y refuerzo social. Ref: Boecker et al. (2008)."
        ),
        "precursor_principal": "L-Fenilalanina (precursor indirecto vía POMC)",
        "alimentos": [
            {"nombre": "Chocolate negro ≥85%", "mg_por_100g": None,
             "notas_preparacion": "20-30g. Feniletilamina + anandamida estimulan vías opioides."},
            {"nombre": "Chile/capsaicina", "mg_por_100g": None,
             "notas_preparacion": "Capsaicina activa TRPV1 → liberación endorfínica."},
            {"nombre": "Fresas y frutas rojas", "mg_por_100g": None,
             "notas_preparacion": "150g. Quercetina modula receptores opioides."},
        ],
        "cofactores": {
            "ejercicio_aerobico": "Principal inductor: >30min de intensidad moderada-alta.",
            "risa_social": "Interacción social genuina libera β-endorfinas.",
            "vitamina_D": "Potencia síntesis de POMC.",
        },
        "inhibidores": {
            "sedentarismo_prolongado": "Sin estímulo → downregulation de receptores μ-opioides.",
            "aislamiento_social": "Reduce liberación de opioides endógenos.",
        },
        "ventana_horaria_optima": ["manana_temprana", "pico_cognitivo"],
        "referencia_apa": "Boecker, H. et al. (2008). Cerebral Cortex, 18(11), 2523-2531.",
    },

    # ── T3-I: Oxitocina (bloque 9) ──
    "oxitocina": {
        "neurotransmisor": "Oxitocina (neuropéptido hipotalámico)",
        "descripcion_mecanismo": (
            "Sintetizada en los núcleos paraventricular y supraóptico del hipotálamo. "
            "Liberada por contacto social, lactancia, y confianza interpersonal. "
            "Modula vínculo social, empatía y reducción de cortisol. Ref: Uvnäs-Moberg (1998)."
        ),
        "precursor_principal": "Vitamina C + Magnesio (cofactores de síntesis)",
        "alimentos": [
            {"nombre": "Alimentos ricos en vitamina C (kiwi, pimiento rojo)", "mg_por_100g": None,
             "notas_preparacion": "La vitamina C es cofactor de peptidilglicina α-amidante (PAM)."},
            {"nombre": "Alimentos ricos en magnesio (cacao, almendras)", "mg_por_100g": None,
             "notas_preparacion": "El magnesio facilita la exocitosis de oxitocina."},
            {"nombre": "Probióticos (L. reuteri)", "mg_por_100g": None,
             "notas_preparacion": "L. reuteri DSM 17938 aumenta oxitocina vía eje intestino-cerebro."},
        ],
        "cofactores": {
            "contacto_social": "Abrazos, conversación empática, contacto visual activan liberación.",
            "cuidado_plantas": "El acto de cuidar (regar, podar) activa circuitos de nurturing/oxitocina.",
            "estrógenos": "Potencian expresión del gen OXT (más pronunciado en ciclo lúteo).",
        },
        "inhibidores": {
            "estrés_cronico": "Cortisol sostenido suprime receptores OXTR.",
            "aislamiento": "Reduce estimulación de vías oxytocinérgicas.",
        },
        "ventana_horaria_optima": ["tarde", "noche"],
        "referencia_apa": "Uvnäs-Moberg, K. (1998). Psychoneuroendocrinology, 23(8), 819-835.",
    },
}


# =============================================================================
# DICCIONARIO 2: WEATHER_MOOD_BASELINE
# Mapea condiciones climáticas a impacto neurobiológico + compensación nutricional.
# =============================================================================

WEATHER_MOOD_BASELINE = {
    "soleado": {
        "descripcion_mecanismo": "Luz >2500 lux activa melanopsina → serotonina. Estado positivo.",
        "nutricion_compensatoria": [
            {"alimento": "Agua (hidratación)", "dosis": "500ml adicionales si >25°C",
             "razon": "Deshidratación leve reduce rendimiento cognitivo 15%."},
            {"alimento": "Antioxidantes (berries, té verde)", "dosis": "150g berries",
             "razon": "Protege del estrés oxidativo foto-inducido."},
        ],
    },
    "nublado_leve": {
        "descripcion_mecanismo": "1000-5000 lux. TPH2 ralentiza. Energía algo baja.",
        "nutricion_compensatoria": [
            {"alimento": "Avena integral + plátano", "dosis": "80g avena + 1 plátano",
             "razon": "Triptófano + B6 + Efecto Wurtman."},
        ],
    },
    "nublado_prolongado": {
        "descripcion_mecanismo": "Activa IDO → quinurenina. Riesgo neuroinflamación.",
        "nutricion_compensatoria": [
            {"alimento": "EPA/DHA omega-3", "dosis": "2-3g/día",
             "razon": "EPA inhibe IDO. Anti-inflamatorio más potente."},
            {"alimento": "Vitamina D3 + K2", "dosis": "2000-4000 IU D3",
             "razon": "VDR suprime transcripción del gen IDO."},
        ],
    },
    "invierno_riguroso": {
        "descripcion_mecanismo": "Frío activa HPA → cortisol → menos dopamina.",
        "nutricion_compensatoria": [
            {"alimento": "Chocolate negro ≥85%", "dosis": "30-40g/día",
             "razon": "Teobromina + feniletilamina elevan dopamina."},
        ],
    },
    "ola_calor": {
        "descripcion_mecanismo": "Vasodilatación periférica reduce flujo cerebral.",
        "nutricion_compensatoria": [
            {"alimento": "Sandía (L-citrulina)", "dosis": "300g",
             "razon": "L-citrulina → NO → vasodilatación cerebral."},
        ],
    },
    "lluvia": {
        "descripcion_mecanismo": "Petricor activa sistema límbico. Luz reducida.",
        "nutricion_compensatoria": [
            {"alimento": "Chocolate caliente 85%", "dosis": "30g cacao en leche vegetal",
             "razon": "Confort + efecto dopaminérgico."},
        ],
    },
    "alta_humedad": {
        "descripcion_mecanismo": "Histamina cruza BHE. Irritabilidad.",
        "nutricion_compensatoria": [
            {"alimento": "Vitamina C (pimiento rojo, kiwi)", "dosis": "500-1000mg",
             "razon": "Cofactor DAO + antihistamínico directo."},
        ],
    },
    "viento_fohn": {
        "descripcion_mecanismo": "Iones positivos activan MAO-B. Irritabilidad.",
        "nutricion_compensatoria": [
            {"alimento": "EGCG (té verde)", "dosis": "3-4 tazas",
             "razon": "EGCG inhibe MAO-B selectivamente."},
        ],
    },
}


# =============================================================================
# DICCIONARIO 3: FARMING_KNOWLEDGE_BASE
# Cada planta como intervención clínica documentada.
# =============================================================================

FARMING_KNOWLEDGE_BASE = {
    "lavanda": {
        "nombre_comun": "Lavanda (Lavandula angustifolia)",
        "compuesto_activo": "Linalool (25-45%) + Acetato de linalilo (25-46%)",
        "mecanismo_neurologico": "Linalool se une a GABA-A α1β2γ2 (sitio BZD). Efecto ansiolítico en <2min.",
        "receptor_diana": "GABA-A α1β2γ2",
        "efecto_terapeutico": "Reducción de ansiedad, mejora calidad del sueño.",
        "equivalencia_farmacologica": "Equivalente a Diazepam SIN tolerancia ni dependencia.",
        "modo_uso": ["olfativo — 5 min con respiración lenta", "tisana — 4g en 200ml 90°C, 10 min"],
        "tiempo_accion_minutos": 2,
        "estado_emocional_diana": ["ansiedad", "estrés_agudo", "insomnio"],
        "evidencia_nivel": "RCT doble ciego (Kasper et al. 2014, n=539)",
    },
    "menta_piperita": {
        "nombre_comun": "Menta piperita (Mentha × piperita)",
        "compuesto_activo": "1,8-Cineol + Mentol + Mentona",
        "mecanismo_neurologico": "1,8-Cineol inhibe AChE. Mentol activa TRPM8.",
        "receptor_diana": "AChE (inhibidor) + TRPM8",
        "efecto_terapeutico": "+15-24% velocidad de procesamiento cognitivo.",
        "equivalencia_farmacologica": "Mecanismo similar a Donepezilo pero 100x más suave.",
        "modo_uso": ["olfativo — 3-5 hojas 3 min", "infusión — 4g hojas en 200ml 85°C"],
        "tiempo_accion_minutos": 5,
        "estado_emocional_diana": ["fatiga_cognitiva", "foco_bajo", "somnolencia_diurna"],
        "evidencia_nivel": "RCT crossover (Kennedy et al. 2011, n=144)",
    },
    "romero": {
        "nombre_comun": "Romero (Salvia rosmarinus)",
        "compuesto_activo": "1,8-Cineol + Ácido Rosmarínico + Ácido Carnósico",
        "mecanismo_neurologico": "Triple: AChE inhibidor + Nrf2 activador + BDNF inductor.",
        "receptor_diana": "AChE + Nrf2 + RXRβ",
        "efecto_terapeutico": "Mejora cognitiva + neuroprotección + neuroplasticidad.",
        "modo_uso": ["olfativo — ramita fresca 5 min", "infusión — 3g en 200ml 90°C"],
        "tiempo_accion_minutos": 5,
        "estado_emocional_diana": ["fatiga_cognitiva", "foco_bajo", "recuperacion_estres_cronico"],
        "evidencia_nivel": "Estudio prospectivo (Moss et al. 2012)",
    },
    "albahaca": {
        "nombre_comun": "Albahaca santa (Ocimum tenuiflorum / tulsi)",
        "compuesto_activo": "Eugenol + Ácido Ursólico + Ocimumósidos",
        "mecanismo_neurologico": "Eugenol inhibe COX-2 y reduce cortisol vía eje HPA.",
        "receptor_diana": "COX-2 + eje HPA",
        "efecto_terapeutico": "Adaptógeno — reduce cortisol sin sedación.",
        "modo_uso": ["infusión — hojas frescas en agua caliente", "olfativo — aplastar hojas"],
        "tiempo_accion_minutos": 15,
        "estado_emocional_diana": ["estres_cronico", "fatiga_suprarrenal"],
        "evidencia_nivel": "RCT (Saxena et al. 2012, n=150)",
    },
    "girasol_microgreen": {
        "nombre_comun": "Microgreen de girasol (Helianthus annuus, brotes 7-12 días)",
        "compuesto_activo": "L-Triptófano 340mg/100g + Tirosina 290mg/100g + Clorofila",
        "mecanismo_neurologico": "Fuente simultánea de precursores serotonina + dopamina.",
        "receptor_diana": "TPH2 (triptófano) + TH (tirosina)",
        "efecto_terapeutico": "Equilibra serotonina y dopamina simultáneamente.",
        "modo_uso": ["comestible — 30-50g en ensalada o smoothie"],
        "tiempo_accion_minutos": 60,
        "estado_emocional_diana": ["tristeza", "desequilibrio_general"],
        "evidencia_nivel": "Análisis bromatológico + mecanismo bioquímico",
    },
}


# =============================================================================
# DICCIONARIO 4: HRV_THRESHOLDS
# Constantes clínicas para interpretar HRV (Task Force ESC/NASPE 1996).
# =============================================================================

HRV_THRESHOLDS = {
    "E1_CRITICAL": {
        "rmssd_max": 20, "sdnn_max": 15, "lf_hf_min": 4.0, "pnn50_max": 3,
        "label": "Activación Simpática Severa",
        "descripcion": "Fight-or-flight activo. Córtex prefrontal parcialmente desconectado.",
        "protocolo_inmediato": "Respiración 4-7-8 × 4 ciclos. Oler lavanda. Agua fría en cara.",
    },
    "E2_STRESSED": {
        "rmssd_min": 20, "rmssd_max": 39, "sdnn_min": 15, "sdnn_max": 29,
        "lf_hf_min": 2.5, "lf_hf_max": 4.0, "pnn50_min": 3, "pnn50_max": 8,
        "label": "Estrés Elevado",
        "descripcion": "Simpático activo. Capacidad cognitiva reducida ~20-30%.",
        "protocolo_inmediato": "L-teanina 200mg + respiración coherente 5 min.",
    },
    "E3_MIXED": {
        "rmssd_min": 40, "rmssd_max": 54, "sdnn_min": 30, "sdnn_max": 44,
        "lf_hf_min": 1.5, "lf_hf_max": 2.5, "pnn50_min": 8, "pnn50_max": 15,
        "label": "Estado Mixto / Recuperación",
        "descripcion": "Balance intermedio. Funcional pero no óptimo.",
        "protocolo_inmediato": "Mantener: hidratación, snack equilibrado.",
    },
    "E4_OPTIMAL": {
        "rmssd_min": 55, "rmssd_max": 74, "sdnn_min": 45, "sdnn_max": 69,
        "lf_hf_min": 0.8, "lf_hf_max": 1.5, "pnn50_min": 15, "pnn50_max": 30,
        "label": "Estado Óptimo / Coherencia Autonómica",
        "descripcion": "Balance ideal. Máximo rendimiento cognitivo. Estado de flow accesible.",
        "protocolo_inmediato": "Mantener rutinas. Momento para deep work.",
    },
    "E5_HIGH": {
        "rmssd_min": 75, "sdnn_min": 70, "lf_hf_max": 0.8, "pnn50_min": 30,
        "label": "HRV Muy Alto / Verificar Contexto",
        "descripcion": "Puede ser excelente fitness o artefacto de medición.",
        "protocolo_inmediato": "Si atleta: excelente. Si inesperado: verificar medición.",
    },
}


# =============================================================================
# DICCIONARIO 5: CHRONO_NUTRITION_MATRIX
# Casa la hora del día con los alimentos correctos (crononutrición).
# =============================================================================

CHRONO_NUTRITION_MATRIX = {
    "manana_temprana": {
        "horario": "06:00 - 08:30",
        "neurotransmisor_prioritario": "dopamina",
        "razon_biologica": "CAR (Cortisol Awakening Response) potencia TH → síntesis dopamina.",
        "alimentos_recomendados": [
            {"nombre": "Huevos + queso parmesano", "objetivo_kb": "acetilcolina + dopamina"},
            {"nombre": "Café negro o matcha", "objetivo_kb": "dopamina (indirecto)"},
        ],
        "alimentos_contraindicados": [
            {"alimento": "Triptófano solo", "razon": "Produce somnolencia por serotonina diurna."},
            {"alimento": "Azúcar refinada", "razon": "Pico glucémico → hipoglucemia reactiva."},
        ],
    },
    "pico_cognitivo": {
        "horario": "08:30 - 13:00",
        "neurotransmisor_prioritario": "acetilcolina + dopamina (sostenimiento)",
        "razon_biologica": "Máximo rendimiento cognitivo. Córtex prefrontal y sistema colinérgico activos.",
        "alimentos_recomendados": [
            {"nombre": "Nueces + arándanos", "objetivo_kb": "bdnf + dopamina"},
            {"nombre": "Proteína magra + crucíferas", "objetivo_kb": "acetilcolina + bdnf"},
        ],
        "alimentos_contraindicados": [
            {"alimento": "Comida pesada", "razon": "Insulina → parasimpático → somnolencia."},
        ],
    },
    "tarde": {
        "horario": "15:00 - 19:30",
        "neurotransmisor_prioritario": "serotonina",
        "razon_biologica": "Preparan cascada serotonina → melatonina nocturna.",
        "alimentos_recomendados": [
            {"nombre": "Triptófano + carbohidrato bajo IG", "objetivo_kb": "serotonina"},
            {"nombre": "Plátano + semillas calabaza + avena", "objetivo_kb": "serotonina + B6"},
        ],
        "alimentos_contraindicados": [
            {"alimento": "Cafeína", "razon": "Bloquea transición simpático → parasimpático."},
        ],
    },
    "noche": {
        "horario": "19:30 - 22:00",
        "neurotransmisor_prioritario": "melatonina + GABA",
        "razon_biologica": "Activación pineal. Transición al sueño.",
        "alimentos_recomendados": [
            {"nombre": "Cerezas Montmorency / zumo", "objetivo_kb": "melatonina"},
            {"nombre": "Infusión de manzanilla o lavanda", "objetivo_kb": "gaba"},
            {"nombre": "Magnesio (almendras, chocolate 85%)", "objetivo_kb": "gaba + melatonina"},
        ],
        "alimentos_contraindicados": [
            {"alimento": "Proteína alta", "razon": "LNAAs compiten con triptófano residual."},
            {"alimento": "Pantallas/luz azul", "razon": "Suprime melatonina 85%."},
        ],
    },
}


# =============================================================================
# DICCIONARIO 6: T7×T8 OVERRIDE MATRIX
# Cruza ventana circadiana (T7) × estado autonómico (T8).
# Determina override de iluminación/nutrición cuando existe conflicto.
# Ref: Cajochen et al. (2011), Porges (2011)
# =============================================================================

CIRCADIAN_AUTONOMIC_MATRIX = {
    # Clave: (ventana_circadiana, estado_hrv) → override de acción
    ("manana_temprana", "E1_CRITICAL"): {
        "override": True,
        "luz": {"perfil": "relajacion_profunda", "kelvin": 2200, "brillo": 40},
        "nutricion": "magnesio + L-teanina (NO cafeína hasta estabilizar)",
        "meditacion": "respiracion_4_7_8",
        "razon": "E1 prevalece: fight-or-flight activo anula activación matutina.",
    },
    ("manana_temprana", "E2_STRESSED"): {
        "override": True,
        "luz": {"perfil": "amanecer_golden", "kelvin": 3000, "brillo": 50},
        "nutricion": "tirosina moderada + magnesio (activación suave, no agresiva)",
        "meditacion": "coherencia_cardiaca_5min",
        "razon": "E2 temprano: activación suave, sin forzar simpático ya elevado.",
    },
    ("pico_cognitivo", "E1_CRITICAL"): {
        "override": True,
        "luz": {"perfil": "relajacion_profunda", "kelvin": 2500, "brillo": 35},
        "nutricion": "GABA + magnesio (prioridad: reducir cortisol antes de cognitivo)",
        "meditacion": "respiracion_4_7_8",
        "razon": "E1 siempre fuerza relajación independientemente de hora.",
    },
    ("tarde", "E1_CRITICAL"): {
        "override": True,
        "luz": {"perfil": "tormenta_refugio", "kelvin": 2200, "brillo": 35},
        "nutricion": "triptófano + magnesio (cascada calma urgente)",
        "meditacion": "body_scan_relajante",
        "razon": "E1_collapse siempre activa relaxation_amber (regla absoluta).",
    },
    ("noche", "E5_HIGH"): {
        "override": False,
        "luz": None,
        "nutricion": None,
        "meditacion": None,
        "razon": "Noche + E5: flujo ideal, no se interrumpe.",
    },
}


def get_override(ventana: str, hrv_state: str) -> dict | None:
    """
    Consulta la T7×T8 matrix. Retorna override si existe, None si no hay conflicto.
    """
    key = (ventana, hrv_state)
    entry = CIRCADIAN_AUTONOMIC_MATRIX.get(key)
    if entry and entry.get("override"):
        return entry
    return None


# =============================================================================
# FUNCIÓN: WURTMAN-SCHEER ENFORCEMENT
# Hard constraint: nunca recomendar tirosina bolus nocturno ni triptófano
# puro en mañana temprana.
# Ref: Wurtman & Wurtman (1995), Scheer et al. (2009)
# =============================================================================

WURTMAN_SCHEER_RULES = [
    {
        "regla": "NO_TIROSINA_NOCTURNA",
        "ventanas_prohibidas": ["noche"],
        "neurotransmisor": "dopamina",
        "alimentos_bloqueados": ["tirosina", "fenilalanina"],
        "razon": "Tirosina bolus en F7/F8 activa simpático → inhibe melatonina → insomnio.",
        "referencia": "Wurtman, R. J. & Wurtman, J. J. (1995). Brain serotonin, carbohydrate-craving.",
    },
    {
        "regla": "NO_TRIPTOFANO_PURO_MANANA",
        "ventanas_prohibidas": ["manana_temprana"],
        "neurotransmisor": "serotonina",
        "alimentos_bloqueados": ["triptófano solo", "triptófano puro"],
        "razon": "Triptófano puro en F2 produce somnolencia diurna vía serotonina → melatonina.",
        "referencia": "Scheer, F. A. et al. (2009). PNAS, 106(11), 4453-4458.",
    },
    {
        "regla": "NO_CAFEINA_NOCTURNA",
        "ventanas_prohibidas": ["tarde", "noche"],
        "neurotransmisor": "dopamina",
        "alimentos_bloqueados": ["cafeína", "café", "té negro"],
        "razon": "Cafeína bloquea adenosina A2A → prolonga vida media cortisol → inhibe GABA/melatonina.",
        "referencia": "Drake, C. et al. (2013). J Clin Sleep Medicine, 9(11), 1195-1200.",
    },
    {
        "regla": "NO_AZUCAR_REFINADA_MANANA",
        "ventanas_prohibidas": ["manana_temprana"],
        "neurotransmisor": "dopamina",
        "alimentos_bloqueados": ["azúcar refinada", "cereales azucarados"],
        "razon": "Pico glucémico reactivo → hipoglucemia → cortisol → crash energético matutino.",
        "referencia": "Ludwig, D. S. (2002). JAMA, 287(18), 2414-2423.",
    },
]


def enforce_wurtman_scheer(recomendacion: str, ventana: str) -> dict:
    """
    Verifica una recomendación nutricional contra las reglas Wurtman-Scheer.
    Retorna: {"allowed": True/False, "violations": [...], "safe_text": str}
    """
    violations = []
    texto_lower = recomendacion.lower()

    for rule in WURTMAN_SCHEER_RULES:
        if ventana in rule["ventanas_prohibidas"]:
            for alimento in rule["alimentos_bloqueados"]:
                if alimento.lower() in texto_lower:
                    violations.append({
                        "regla": rule["regla"],
                        "alimento_detectado": alimento,
                        "razon": rule["razon"],
                        "referencia": rule["referencia"],
                    })

    if violations:
        safe_text = (
            f"⚠️ La recomendación original contenía {len(violations)} elemento(s) "
            f"contraindicado(s) para la ventana '{ventana}' según las reglas "
            f"cronobiológicas de Wurtman-Scheer. Se han filtrado."
        )
        return {"allowed": False, "violations": violations, "safe_text": safe_text}

    return {"allowed": True, "violations": [], "safe_text": recomendacion}
