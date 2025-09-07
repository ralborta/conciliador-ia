import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class PatronManager:
    """Gestor de patrones entrenados para extractos bancarios"""
    
    def __init__(self):
        self.data_dir = Path("data")
        self.patrones_dir = self.data_dir / "patrones_entrenados"
        self.extractos_dir = self.data_dir / "extractos_ejemplo"
        self.bancos_file = self.patrones_dir / "bancos.json"
        
        # Crear directorios si no existen
        self.patrones_dir.mkdir(parents=True, exist_ok=True)
        self.extractos_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializar archivo de bancos si no existe
        if not self.bancos_file.exists():
            self._inicializar_archivo_bancos()
    
    def _inicializar_archivo_bancos(self):
        """Inicializa el archivo de bancos con estructura básica"""
        estructura_inicial = {
            "version": "1.0.0",
            "ultima_actualizacion": datetime.now().isoformat(),
            "bancos_entrenados": {},
            "estadisticas_globales": {
                "total_bancos": 0,
                "total_entrenamientos": 0,
                "precision_promedio": 0.0
            }
        }
        
        with open(self.bancos_file, 'w', encoding='utf-8') as f:
            json.dump(estructura_inicial, f, indent=2, ensure_ascii=False)
        
        logger.info("Archivo de bancos inicializado")
    
    def cargar_bancos(self) -> Dict[str, Any]:
        """Carga todos los bancos entrenados"""
        try:
            with open(self.bancos_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error cargando bancos: {e}")
            return {"bancos_entrenados": {}}
    
    def guardar_bancos(self, datos: Dict[str, Any]):
        """Guarda todos los bancos entrenados"""
        try:
            datos["ultima_actualizacion"] = datetime.now().isoformat()
            with open(self.bancos_file, 'w', encoding='utf-8') as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)
            logger.info("Bancos guardados exitosamente")
        except Exception as e:
            logger.error(f"Error guardando bancos: {e}")
            raise
    
    def obtener_banco(self, banco_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un banco específico por ID"""
        bancos = self.cargar_bancos()
        return bancos.get("bancos_entrenados", {}).get(banco_id)
    
    def guardar_banco(self, banco_id: str, datos: Dict[str, Any]):
        """Guarda o actualiza un banco específico"""
        bancos = self.cargar_bancos()
        
        # Estructura estándar para un banco
        banco_data = {
            "id": banco_id,
            "nombre": datos.get("nombre", banco_id.upper()),
            "patrones": datos.get("patrones", {}),
            "configuracion": datos.get("configuracion", {}),
            "estadisticas": {
                "precision": datos.get("precision", 0.0),
                "total_entrenamientos": datos.get("total_entrenamientos", 0),
                "ultima_actualizacion": datetime.now().isoformat(),
                "casos_exitosos": datos.get("casos_exitosos", 0),
                "casos_fallidos": datos.get("casos_fallidos", 0)
            },
            "ejemplos_entrenamiento": datos.get("ejemplos_entrenamiento", []),
            "activo": datos.get("activo", True)
        }
        
        bancos["bancos_entrenados"][banco_id] = banco_data
        
        # Actualizar estadísticas globales
        self._actualizar_estadisticas_globales(bancos)
        
        self.guardar_bancos(bancos)
        logger.info(f"Banco {banco_id} guardado exitosamente")
    
    def _actualizar_estadisticas_globales(self, bancos: Dict[str, Any]):
        """Actualiza las estadísticas globales"""
        bancos_entrenados = bancos.get("bancos_entrenados", {})
        
        total_bancos = len(bancos_entrenados)
        total_entrenamientos = sum(
            banco.get("estadisticas", {}).get("total_entrenamientos", 0)
            for banco in bancos_entrenados.values()
        )
        
        precisiones = [
            banco.get("estadisticas", {}).get("precision", 0.0)
            for banco in bancos_entrenados.values()
            if banco.get("estadisticas", {}).get("precision", 0.0) > 0
        ]
        
        precision_promedio = sum(precisiones) / len(precisiones) if precisiones else 0.0
        
        bancos["estadisticas_globales"] = {
            "total_bancos": total_bancos,
            "total_entrenamientos": total_entrenamientos,
            "precision_promedio": round(precision_promedio, 3)
        }
    
    def listar_bancos(self) -> List[Dict[str, Any]]:
        """Lista todos los bancos entrenados con información básica"""
        bancos = self.cargar_bancos()
        bancos_entrenados = bancos.get("bancos_entrenados", {})
        
        lista_bancos = []
        for banco_id, banco_data in bancos_entrenados.items():
            lista_bancos.append({
                "id": banco_id,
                "nombre": banco_data.get("nombre", banco_id.upper()),
                "precision": banco_data.get("estadisticas", {}).get("precision", 0.0),
                "total_entrenamientos": banco_data.get("estadisticas", {}).get("total_entrenamientos", 0),
                "ultima_actualizacion": banco_data.get("estadisticas", {}).get("ultima_actualizacion"),
                "activo": banco_data.get("activo", True)
            })
        
        return sorted(lista_bancos, key=lambda x: x["nombre"])
    
    def eliminar_banco(self, banco_id: str) -> bool:
        """Elimina un banco del sistema"""
        try:
            bancos = self.cargar_bancos()
            if banco_id in bancos.get("bancos_entrenados", {}):
                del bancos["bancos_entrenados"][banco_id]
                self._actualizar_estadisticas_globales(bancos)
                self.guardar_bancos(bancos)
                logger.info(f"Banco {banco_id} eliminado exitosamente")
                return True
            return False
        except Exception as e:
            logger.error(f"Error eliminando banco {banco_id}: {e}")
            return False
    
    def actualizar_precision(self, banco_id: str, precision: float, caso_exitoso: bool = True):
        """Actualiza la precisión de un banco después de un entrenamiento"""
        try:
            banco = self.obtener_banco(banco_id)
            if not banco:
                logger.warning(f"Banco {banco_id} no encontrado para actualizar precisión")
                return False
            
            # Actualizar estadísticas
            estadisticas = banco.get("estadisticas", {})
            total_entrenamientos = estadisticas.get("total_entrenamientos", 0)
            casos_exitosos = estadisticas.get("casos_exitosos", 0)
            casos_fallidos = estadisticas.get("casos_fallidos", 0)
            
            if caso_exitoso:
                casos_exitosos += 1
            else:
                casos_fallidos += 1
            
            total_entrenamientos += 1
            
            # Calcular nueva precisión
            nueva_precision = casos_exitosos / total_entrenamientos if total_entrenamientos > 0 else 0.0
            
            # Actualizar datos
            banco["estadisticas"]["precision"] = round(nueva_precision, 3)
            banco["estadisticas"]["total_entrenamientos"] = total_entrenamientos
            banco["estadisticas"]["casos_exitosos"] = casos_exitosos
            banco["estadisticas"]["casos_fallidos"] = casos_fallidos
            banco["estadisticas"]["ultima_actualizacion"] = datetime.now().isoformat()
            
            # Guardar cambios
            self.guardar_banco(banco_id, banco)
            logger.info(f"Precisión del banco {banco_id} actualizada: {nueva_precision}")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando precisión del banco {banco_id}: {e}")
            return False
    
    def obtener_estadisticas_globales(self) -> Dict[str, Any]:
        """Obtiene las estadísticas globales del sistema"""
        bancos = self.cargar_bancos()
        return bancos.get("estadisticas_globales", {})
    
    def buscar_banco_por_nombre(self, nombre: str) -> Optional[str]:
        """Busca un banco por nombre y retorna su ID"""
        bancos = self.cargar_bancos()
        bancos_entrenados = bancos.get("bancos_entrenados", {})
        
        for banco_id, banco_data in bancos_entrenados.items():
            if nombre.lower() in banco_data.get("nombre", "").lower():
                return banco_id
        
        return None
    
    def exportar_patrones(self, banco_id: Optional[str] = None) -> Dict[str, Any]:
        """Exporta patrones para backup o migración"""
        if banco_id:
            banco = self.obtener_banco(banco_id)
            return {banco_id: banco} if banco else {}
        else:
            return self.cargar_bancos()
    
    def importar_patrones(self, datos: Dict[str, Any]) -> bool:
        """Importa patrones desde un backup"""
        try:
            # Validar estructura
            if "bancos_entrenados" not in datos:
                logger.error("Estructura de datos inválida para importar")
                return False
            
            # Hacer backup del archivo actual
            backup_file = self.bancos_file.with_suffix(f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            if self.bancos_file.exists():
                import shutil
                shutil.copy2(self.bancos_file, backup_file)
            
            # Importar nuevos datos
            self.guardar_bancos(datos)
            logger.info("Patrones importados exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error importando patrones: {e}")
            return False

