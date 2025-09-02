export const runtime = "nodejs";         // fuerza runtime de Node en Vercel
export const dynamic = "force-dynamic";  // evita cache

export async function POST(req: Request) {
  try {
    const form = await req.formData();

    // normalizamos nombre de archivo: admite "file" o "archivo"
    if (!form.get("file") && form.get("archivo")) {
      form.set("file", form.get("archivo") as File);
    }

    // ⚠️ Usa SIEMPRE el path correcto que funciona
    const upstream = await fetch(
      "https://conciliador-ia-production.up.railway.app/api/v1/importar-clientes",
      { method: "POST", body: form, cache: "no-store" } // NO pongas Content-Type manual
    );

    // Propagamos body y status tal cual para depurar fácil
    const text = await upstream.text();
    return new Response(text, { status: upstream.status });
  } catch (e: any) {
    return new Response(
      JSON.stringify({ error: e?.message || "proxy_failed" }),
      { status: 500, headers: { "content-type": "application/json" } }
    );
  }
}
