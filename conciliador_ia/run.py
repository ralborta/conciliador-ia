import os
import uvicorn
from conciliador_ia.main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"🚀 Starting FastAPI server on port {port}")
    print(f"📡 Environment PORT: {os.environ.get('PORT', '8000')}")
    uvicorn.run(app, host="0.0.0.0", port=port)
