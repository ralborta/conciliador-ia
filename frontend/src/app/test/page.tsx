export default function TestPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          ¡Funciona! 🎉
        </h1>
        <p className="text-lg text-gray-600">
          La aplicación está desplegada correctamente en Vercel
        </p>
        <a 
          href="/" 
          className="mt-4 inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Ir a la aplicación principal
        </a>
      </div>
    </div>
  );
} 