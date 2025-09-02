import os
import sys
import uvicorn
import logging
from main import app

# Configurar logging para Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info("=" * 50)
    logger.info("🚀 INICIANDO CONCILIADOR IA")
    logger.info("=" * 50)
    logger.info(f"📡 Puerto: {port}")
    logger.info(f"🌐 Host: {host}")
    logger.info(f"🔍 Health check: http://{host}:{port}/health")
    logger.info(f"📚 Docs: http://{host}:{port}/docs")
    logger.info("=" * 50)
    
    try:
        # Configuración de uvicorn optimizada para Railway
        config = uvicorn.Config(
            app=app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            use_colors=False,  # Better for Railway logs
            loop="asyncio",
            workers=1  # Railway works better with single worker
        )
        
        server = uvicorn.Server(config)
        logger.info("✅ Servidor configurado, iniciando...")
        server.run()
        
    except Exception as e:
        logger.error(f"❌ Error al iniciar servidor: {e}")
        sys.exit(1)
