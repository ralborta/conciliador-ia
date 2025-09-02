import os
import uvicorn
from main import app  # Import directo, no conciliador_ia.main

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"🚀 Starting FastAPI server on port {port}")
    print(f"📡 Environment PORT: {os.environ.get('PORT', '8000')}")
    print(f"🌐 Host: 0.0.0.0")
    print(f"🔍 Health check available at: http://0.0.0.0:{port}/health")
    print(f"🔍 Health check v1 available at: http://0.0.0.0:{port}/api/v1/health")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
