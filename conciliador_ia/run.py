import os
import uvicorn
from main import app  # Import directo, no conciliador_ia.main

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"🚀 Starting FastAPI server on port {port}")
    print(f"📡 Environment PORT: {os.environ.get('PORT', '8000')}")
    print(f"🌐 Host: 0.0.0.0")
    uvicorn.run(app, host="0.0.0.0", port=port)
