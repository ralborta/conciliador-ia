import { NextRequest, NextResponse } from 'next/server';
import { put } from '@vercel/blob';

const EXTRACTOR_URL = process.env.EXTRACTOR_URL;
const SERVICE_AUTH_SECRET = process.env.SERVICE_AUTH_SECRET;
const BLOB_READ_WRITE_TOKEN = process.env.BLOB_READ_WRITE_TOKEN;

export async function POST(request: NextRequest) {
  try {
    // Validar variables de entorno
    if (!EXTRACTOR_URL || !SERVICE_AUTH_SECRET || !BLOB_READ_WRITE_TOKEN) {
      return NextResponse.json(
        { error: 'Missing required environment variables' },
        { status: 500 }
      );
    }

    console.log("UPLOAD start");
    
    const formData = await request.formData();
    const file = formData.get('file') as File;
    const bankHint = formData.get('bank_hint') as string;

    if (!file) {
      return NextResponse.json(
        { error: 'No se proporcionó archivo' },
        { status: 400 }
      );
    }

    // Validar que sea PDF
    if (file.type !== 'application/pdf') {
      return NextResponse.json(
        { error: 'Solo se permiten archivos PDF' },
        { status: 400 }
      );
    }

    // Subir a Vercel Blob
    const key = `extractos/${Date.now()}-${file.name}`;
    const { url } = await put(key, file, { 
      access: "public", 
      addRandomSuffix: false,
      token: BLOB_READ_WRITE_TOKEN
    });
    console.log("BLOB URL:", url);

    // Llamar al microservicio
    const body = {
      pdf_url: url,
      bank_hint: bankHint || null,
      metadata: {
        filename: file.name,
        size: file.size,
        uploaded_at: new Date().toISOString(),
      },
    };

    console.log("Calling microservice with body:", body);

    const r = await fetch(`${EXTRACTOR_URL}/extract`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json", 
        "X-Service-Auth": SERVICE_AUTH_SECRET!
      },
      body: JSON.stringify(body),
    });
    
    console.log("MICRO STATUS:", r.status);
    
    if (!r.ok) {
      const errText = await r.text();
      console.error("MICRO ERROR:", errText);
      return new Response(errText, { status: 502 });
    }

    const extractorResult = await r.json();
    console.log("MICRO RESPONSE:", extractorResult);

    // Transformar respuesta del microservicio al formato esperado por el frontend
    const transformedResult = {
      header: {
        bank_name: extractorResult.banco || 'Banco no identificado',
        period_start: extractorResult.periodo_inicio,
        period_end: extractorResult.periodo_fin,
        currency: 'ARS',
        account_number: extractorResult.numero_cuenta,
      },
      metrics: {
        rows: extractorResult.total_movimientos || 0,
        precision: extractorResult.precision_estimada || 0,
        method: extractorResult.metodo || 'unknown',
        parsed_pct: extractorResult.precision_estimada || 0,
      },
      transactions: (extractorResult.movimientos || []).map((mov: any) => ({
        fecha_operacion: mov.fecha,
        fecha_valor: mov.fecha,
        descripcion: mov.descripcion,
        debit_amount: mov.tipo === 'egreso' ? mov.importe : null,
        credit_amount: mov.tipo === 'ingreso' ? mov.importe : null,
        amount_signed: mov.tipo === 'egreso' ? -mov.importe : mov.importe,
        balance_after: null, // No disponible en el microservicio actual
        moneda: 'ARS',
        bank_ref: mov.referencia || null,
        canal: 'extractor_ia',
        page: mov.pagina || 1,
      })),
      debug: {
        blob_url: url,
        processing_time: extractorResult.tiempo_procesamiento,
        raw_response: extractorResult,
      },
    };

    return NextResponse.json({
      success: true,
      extractor: transformedResult,
      blob_url: url,
    });

  } catch (error) {
    console.error('Error en upload-and-extract:', error);
    return NextResponse.json(
      { 
        error: error instanceof Error ? error.message : 'Error interno del servidor',
        details: error instanceof Error ? error.stack : undefined,
      },
      { status: 500 }
    );
  }
}
