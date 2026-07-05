// supabase/functions/notificaciones-diarias/index.ts
// Edge Function: Notificaciones Diarias de ThriveMind
// Se ejecuta cada noche a las 20:00 UTC via cron de Supabase.

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

interface Usuario { id: string; email: string; nombre: string; }
interface CheckinReciente { estado_emocional: number; energia_fisica: number; horas_sueno: number; hrv_estimado: number | null; created_at: string; }
interface CultivoActivo { id: string; nombre_planta: string; proximo_riego: string; fecha_cosecha_est: string | null; }

interface ContextoNotificacion {
  usuario: Usuario;
  checkins_recientes: CheckinReciente[];
  cultivos: CultivoActivo[];
  triggers_activos: string[];
}

Deno.serve(async (_req: Request) => {
  try {
    const supabase = createClient(
      Deno.env.get("SUPABASE_URL")!,
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
    );

    const hoy = new Date();
    const manana = new Date(hoy);
    manana.setDate(manana.getDate() + 1);
    const mananaISO = manana.toISOString().split("T")[0];

    const { data: usuarios, error: errorUsuarios } = await supabase
      .from("profiles")
      .select("id, email, nombre")
      .not("email", "is", null);

    if (errorUsuarios || !usuarios) {
      return new Response(JSON.stringify({ error: "Error obteniendo usuarios" }), { status: 500 });
    }

    let emailsEnviados = 0;
    let emailsOmitidos = 0;

    for (const usuario of usuarios) {
      const { data: checkins } = await supabase
        .from("checkins")
        .select("estado_emocional, energia_fisica, horas_sueno, hrv_estimado, created_at")
        .eq("user_id", usuario.id)
        .order("created_at", { ascending: false })
        .limit(3);

      const { data: cultivos } = await supabase
        .from("cultivos_activos")
        .select("id, nombre_planta, proximo_riego, fecha_cosecha_est")
        .eq("user_id", usuario.id)
        .eq("activo", true);

      const triggers: string[] = [];

      // Trigger: riego mañana
      const plantasRiego = (cultivos || []).filter((c: CultivoActivo) =>
        c.proximo_riego && c.proximo_riego.startsWith(mananaISO)
      );
      if (plantasRiego.length > 0) {
        triggers.push(`riego:${plantasRiego.map((p: CultivoActivo) => p.nombre_planta).join(",")}`);
      }

      // Trigger: HRV bajo
      const checkinsConHRV = (checkins || []).filter((c: CheckinReciente) => c.hrv_estimado !== null);
      if (checkinsConHRV.length >= 3) {
        const hrvPromedio = checkinsConHRV.reduce((sum: number, c: CheckinReciente) => sum + (c.hrv_estimado || 0), 0) / checkinsConHRV.length;
        if (hrvPromedio < 55) {
          triggers.push(`hrv_bajo:${Math.round(hrvPromedio)}`);
        }
      }

      // Trigger: cosecha lista
      const plantasCosecha = (cultivos || []).filter((c: CultivoActivo) => {
        if (!c.fecha_cosecha_est) return false;
        const dias = Math.floor((new Date(c.fecha_cosecha_est).getTime() - Date.now()) / 86_400_000);
        return dias <= 2;
      });
      if (plantasCosecha.length > 0) {
        triggers.push(`cosecha:${plantasCosecha.map((p: CultivoActivo) => p.nombre_planta).join(",")}`);
      }

      if (triggers.length === 0) { emailsOmitidos++; continue; }

      // Check duplicate
      const { data: notifHoy } = await supabase
        .from("notificaciones_enviadas")
        .select("id")
        .eq("user_id", usuario.id)
        .gte("created_at", hoy.toISOString().split("T")[0])
        .limit(1);

      if (notifHoy && notifHoy.length > 0) { emailsOmitidos++; continue; }

      const ctx: ContextoNotificacion = {
        usuario, checkins_recientes: checkins || [], cultivos: cultivos || [], triggers_activos: triggers,
      };

      const contenidoEmail = await generarContenidoEmail(ctx);
      const enviado = await enviarEmail(usuario.email, contenidoEmail.asunto, contenidoEmail.cuerpoHTML);

      if (enviado) {
        await supabase.from("notificaciones_enviadas").insert({
          user_id: usuario.id,
          tipo: triggers[0].split(":")[0],
          triggers: triggers,
          asunto: contenidoEmail.asunto,
        });
        emailsEnviados++;
      }
    }

    return new Response(JSON.stringify({
      fecha: hoy.toISOString(),
      usuarios_procesados: usuarios.length,
      emails_enviados: emailsEnviados,
      emails_omitidos: emailsOmitidos,
    }), { status: 200 });

  } catch (error) {
    return new Response(JSON.stringify({ error: String(error) }), { status: 500 });
  }
});

async function generarContenidoEmail(ctx: ContextoNotificacion): Promise<{ asunto: string; cuerpoHTML: string }> {
  const openaiKey = Deno.env.get("OPENAI_API_KEY");

  const triggersTexto = ctx.triggers_activos.map((t: string) => {
    const [tipo, valor] = t.split(":");
    switch (tipo) {
      case "riego": return `- Plantas que necesitan riego mañana: ${valor}`;
      case "hrv_bajo": return `- HRV promedio últimos 3 días: ${valor} ms (bajo)`;
      case "cosecha": return `- Plantas listas para cosechar: ${valor}`;
      default: return `- ${t}`;
    }
  }).join("\n");

  const ultimoCheckin = ctx.checkins_recientes[0];
  const estadoUsuario = ultimoCheckin
    ? `Estado emocional: ${ultimoCheckin.estado_emocional}/10, Energía: ${ultimoCheckin.energia_fisica}/10, Sueño: ${ultimoCheckin.horas_sueno}h`
    : "Sin check-in reciente";

  const prompt = `Eres el asistente de bienestar de ThriveMind. Genera un email breve, cálido y motivador para ${ctx.usuario.nombre || "el usuario"}.

SITUACIÓN DEL USUARIO HOY:
${estadoUsuario}

RAZONES PARA CONTACTAR HOY:
${triggersTexto}

INSTRUCCIONES:
- Asunto: específico, personal, motivador (max 60 chars)
- Cuerpo: 3-4 frases max, breve y accionable
- Tono: cálido, como un amigo que se preocupa
- 1 acción concreta que pueda hacer hoy
- NO lenguaje corporativo
- Responde JSON: {"asunto": "...", "cuerpo": "..."}`;

  try {
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: { "Authorization": `Bearer ${openaiKey}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [{ role: "user", content: prompt }],
        response_format: { type: "json_object" },
        max_tokens: 300,
        temperature: 0.7,
      }),
    });

    const data = await response.json();
    const contenido = JSON.parse(data.choices[0].message.content);

    const cuerpoHTML = `
      <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;">
        <div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);padding:20px;border-radius:12px 12px 0 0;">
          <h1 style="color:white;margin:0;font-size:24px;">ThriveMind ✨</h1>
        </div>
        <div style="background:#f9f9f9;padding:24px;border-radius:0 0 12px 12px;">
          <p style="color:#333;font-size:16px;line-height:1.6;">${contenido.cuerpo.replace(/\n/g, "<br>")}</p>
          <a href="https://thrivemind.app" style="background:#667eea;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold;display:inline-block;">Abrir ThriveMind →</a>
        </div>
      </div>`;

    return { asunto: contenido.asunto, cuerpoHTML };
  } catch {
    return {
      asunto: "Tu resumen diario de ThriveMind",
      cuerpoHTML: `<p>Hola ${ctx.usuario.nombre || ""},<br>Tienes actividad pendiente en ThriveMind.<br><a href="https://thrivemind.app">Abrir ThriveMind →</a></p>`,
    };
  }
}

async function enviarEmail(destinatario: string, asunto: string, cuerpoHTML: string): Promise<boolean> {
  const resendKey = Deno.env.get("RESEND_API_KEY");
  try {
    const response = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { "Authorization": `Bearer ${resendKey}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        from: "ThriveMind <onboarding@resend.dev>",
        to: [destinatario],
        subject: asunto,
        html: cuerpoHTML,
      }),
    });
    return response.ok;
  } catch {
    return false;
  }
}
