"""
Optimizador de rendimiento para el sistema de conciliación
Incluye cache, procesamiento asíncrono y optimizaciones para archivos grandes
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Callable
import logging
import time
import hashlib
import pickle
import os
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing
from dataclasses import dataclass
from functools import wraps, lru_cache
import sqlite3
import json

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Entrada de cache con metadata"""
    key: str
    data: Any
    timestamp: float
    size_bytes: int
    access_count: int = 0
    last_access: float = 0


class PerformanceCache:
    """Sistema de cache inteligente con persistencia y limpieza automática"""
    
    def __init__(self, cache_dir: str = "data/cache", max_size_mb: int = 500):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.db_path = self.cache_dir / "cache_metadata.db"
        self._init_database()
        self._load_cache_metadata()
    
    def _init_database(self):
        """Inicializa la base de datos de metadata del cache"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    filename TEXT,
                    timestamp REAL,
                    size_bytes INTEGER,
                    access_count INTEGER,
                    last_access REAL,
                    metadata TEXT
                )
            """)
    
    def _load_cache_metadata(self):
        """Carga metadata del cache desde la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT * FROM cache_entries")
                for row in cursor.fetchall():
                    key, filename, timestamp, size_bytes, access_count, last_access, metadata = row
                    
                    file_path = self.cache_dir / filename
                    if file_path.exists():
                        try:
                            with open(file_path, 'rb') as f:
                                data = pickle.load(f)
                            
                            self.memory_cache[key] = CacheEntry(
                                key=key,
                                data=data,
                                timestamp=timestamp,
                                size_bytes=size_bytes,
                                access_count=access_count,
                                last_access=last_access
                            )
                        except Exception as e:
                            logger.warning(f"Error cargando entrada de cache {filename}: {e}")
                            # Limpiar entrada corrupta
                            conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                            if file_path.exists():
                                file_path.unlink()
        except Exception as e:
            logger.error(f"Error cargando metadata de cache: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del cache"""
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            entry.access_count += 1
            entry.last_access = time.time()
            self._update_metadata(entry)
            logger.debug(f"Cache HIT: {key}")
            return entry.data
        
        logger.debug(f"Cache MISS: {key}")
        return None
    
    def set(self, key: str, data: Any, force: bool = False) -> bool:
        """Almacena un valor en el cache"""
        try:
            # Calcular tamaño
            serialized = pickle.dumps(data)
            size_bytes = len(serialized)
            
            # Verificar límites
            if not force and size_bytes > self.max_size_bytes * 0.1:  # No más del 10% del cache total
                logger.warning(f"Objeto demasiado grande para cache: {size_bytes / (1024*1024):.1f}MB")
                return False
            
            # Limpiar espacio si es necesario
            self._ensure_space(size_bytes)
            
            # Crear entrada
            timestamp = time.time()
            filename = f"cache_{hashlib.md5(key.encode()).hexdigest()}.pkl"
            file_path = self.cache_dir / filename
            
            # Guardar a disco
            with open(file_path, 'wb') as f:
                f.write(serialized)
            
            # Crear entrada en memoria
            entry = CacheEntry(
                key=key,
                data=data,
                timestamp=timestamp,
                size_bytes=size_bytes,
                access_count=1,
                last_access=timestamp
            )
            
            self.memory_cache[key] = entry
            self._save_metadata(entry, filename)
            
            logger.debug(f"Cache SET: {key} ({size_bytes / 1024:.1f}KB)")
            return True
            
        except Exception as e:
            logger.error(f"Error guardando en cache {key}: {e}")
            return False
    
    def _ensure_space(self, needed_bytes: int):
        """Libera espacio en el cache si es necesario"""
        current_size = sum(entry.size_bytes for entry in self.memory_cache.values())
        
        if current_size + needed_bytes <= self.max_size_bytes:
            return
        
        # Ordenar por algoritmo LRU (menos recientemente usado)
        entries_by_lru = sorted(
            self.memory_cache.values(),
            key=lambda x: x.last_access
        )
        
        bytes_to_free = current_size + needed_bytes - self.max_size_bytes
        freed_bytes = 0
        
        for entry in entries_by_lru:
            if freed_bytes >= bytes_to_free:
                break
            
            self.remove(entry.key)
            freed_bytes += entry.size_bytes
        
        logger.info(f"Liberados {freed_bytes / (1024*1024):.1f}MB de cache")
    
    def remove(self, key: str) -> bool:
        """Elimina una entrada del cache"""
        if key in self.memory_cache:
            try:
                # Eliminar archivo
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("SELECT filename FROM cache_entries WHERE key = ?", (key,))
                    row = cursor.fetchone()
                    if row:
                        filename = row[0]
                        file_path = self.cache_dir / filename
                        if file_path.exists():
                            file_path.unlink()
                
                # Eliminar de base de datos
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                
                # Eliminar de memoria
                del self.memory_cache[key]
                
                logger.debug(f"Cache REMOVE: {key}")
                return True
                
            except Exception as e:
                logger.error(f"Error eliminando entrada de cache {key}: {e}")
                return False
        
        return False
    
    def _save_metadata(self, entry: CacheEntry, filename: str):
        """Guarda metadata de entrada en la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO cache_entries 
                    (key, filename, timestamp, size_bytes, access_count, last_access, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.key, filename, entry.timestamp, entry.size_bytes,
                    entry.access_count, entry.last_access, "{}"
                ))
        except Exception as e:
            logger.error(f"Error guardando metadata de cache: {e}")
    
    def _update_metadata(self, entry: CacheEntry):
        """Actualiza metadata de acceso"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE cache_entries 
                    SET access_count = ?, last_access = ?
                    WHERE key = ?
                """, (entry.access_count, entry.last_access, entry.key))
        except Exception as e:
            logger.debug(f"Error actualizando metadata: {e}")
    
    def clear(self):
        """Limpia todo el cache"""
        try:
            # Eliminar archivos
            for file_path in self.cache_dir.glob("cache_*.pkl"):
                file_path.unlink()
            
            # Limpiar base de datos
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache_entries")
            
            # Limpiar memoria
            self.memory_cache.clear()
            
            logger.info("Cache completamente limpiado")
            
        except Exception as e:
            logger.error(f"Error limpiando cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        total_size = sum(entry.size_bytes for entry in self.memory_cache.values())
        total_entries = len(self.memory_cache)
        total_accesses = sum(entry.access_count for entry in self.memory_cache.values())
        
        return {
            "total_entries": total_entries,
            "total_size_mb": total_size / (1024 * 1024),
            "max_size_mb": self.max_size_bytes / (1024 * 1024),
            "usage_percentage": (total_size / self.max_size_bytes) * 100,
            "total_accesses": total_accesses,
            "average_entry_size_kb": (total_size / total_entries / 1024) if total_entries > 0 else 0
        }


class AsyncProcessor:
    """Procesador asíncrono para operaciones pesadas"""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.thread_executor = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_executor = ProcessPoolExecutor(max_workers=min(4, os.cpu_count() or 1))
    
    async def process_dataframe_chunks(self, df: pd.DataFrame, chunk_size: int, 
                                     process_func: Callable, **kwargs) -> pd.DataFrame:
        """Procesa un DataFrame grande en chunks de forma asíncrona"""
        if len(df) <= chunk_size:
            return process_func(df, **kwargs)
        
        chunks = [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
        logger.info(f"Procesando DataFrame en {len(chunks)} chunks de {chunk_size} registros")
        
        loop = asyncio.get_event_loop()
        
        # Procesar chunks en paralelo
        tasks = [
            loop.run_in_executor(self.thread_executor, process_func, chunk, **kwargs)
            for chunk in chunks
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Combinar resultados
        return pd.concat(results, ignore_index=True)
    
    async def process_files_parallel(self, file_paths: List[str], 
                                   process_func: Callable, **kwargs) -> List[Any]:
        """Procesa múltiples archivos en paralelo"""
        logger.info(f"Procesando {len(file_paths)} archivos en paralelo")
        
        loop = asyncio.get_event_loop()
        
        tasks = [
            loop.run_in_executor(self.process_executor, process_func, file_path, **kwargs)
            for file_path in file_paths
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar errores
        successful_results = []
        errors = []
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                errors.append(f"Error procesando {file_paths[i]}: {result}")
            else:
                successful_results.append(result)
        
        if errors:
            logger.warning(f"Errores en procesamiento paralelo: {errors}")
        
        return successful_results
    
    def shutdown(self):
        """Cierra los ejecutores"""
        self.thread_executor.shutdown(wait=True)
        self.process_executor.shutdown(wait=True)


class DataFrameOptimizer:
    """Optimizador específico para operaciones con DataFrames grandes"""
    
    @staticmethod
    def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
        """Optimiza tipos de datos para reducir uso de memoria"""
        original_memory = df.memory_usage(deep=True).sum()
        
        for col in df.select_dtypes(include=['object']).columns:
            # Intentar convertir strings a categorías si hay pocas únicas
            if df[col].nunique() < len(df) * 0.5:
                df[col] = df[col].astype('category')
        
        # Optimizar enteros
        for col in df.select_dtypes(include=['int64']).columns:
            col_min = df[col].min()
            col_max = df[col].max()
            
            if col_min >= 0:
                if col_max < 255:
                    df[col] = df[col].astype('uint8')
                elif col_max < 65535:
                    df[col] = df[col].astype('uint16')
                elif col_max < 4294967295:
                    df[col] = df[col].astype('uint32')
            else:
                if col_min > -128 and col_max < 127:
                    df[col] = df[col].astype('int8')
                elif col_min > -32768 and col_max < 32767:
                    df[col] = df[col].astype('int16')
                elif col_min > -2147483648 and col_max < 2147483647:
                    df[col] = df[col].astype('int32')
        
        # Optimizar floats
        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')
        
        optimized_memory = df.memory_usage(deep=True).sum()
        reduction = (original_memory - optimized_memory) / original_memory * 100
        
        logger.info(f"Optimización de memoria: {reduction:.1f}% reducción "
                   f"({original_memory / 1024**2:.1f}MB → {optimized_memory / 1024**2:.1f}MB)")
        
        return df
    
    @staticmethod
    def chunk_operations(df: pd.DataFrame, operation: Callable, chunk_size: int = 10000) -> pd.DataFrame:
        """Ejecuta operaciones en chunks para DataFrames grandes"""
        if len(df) <= chunk_size:
            return operation(df)
        
        results = []
        total_chunks = (len(df) + chunk_size - 1) // chunk_size
        
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i + chunk_size]
            chunk_result = operation(chunk)
            results.append(chunk_result)
            
            if i // chunk_size % 10 == 0:  # Log cada 10 chunks
                logger.info(f"Procesados {min(i + chunk_size, len(df))} / {len(df)} registros")
        
        return pd.concat(results, ignore_index=True)
    
    @staticmethod
    def efficient_merge(left: pd.DataFrame, right: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """Merge optimizado para DataFrames grandes"""
        # Optimizar tipos antes del merge
        left = DataFrameOptimizer.optimize_dtypes(left)
        right = DataFrameOptimizer.optimize_dtypes(right)
        
        # Usar índices si es beneficioso
        on_cols = kwargs.get('on', [])
        if on_cols:
            if len(left) > 100000 or len(right) > 100000:
                logger.info("Usando merge optimizado con índices para DataFrames grandes")
                left_indexed = left.set_index(on_cols)
                right_indexed = right.set_index(on_cols)
                result = left_indexed.merge(right_indexed, left_index=True, right_index=True, **{k:v for k,v in kwargs.items() if k != 'on'})
                return result.reset_index()
        
        return left.merge(right, **kwargs)


def cached_operation(cache_key_func: Callable = None, ttl_seconds: int = 3600):
    """
    Decorador para cachear operaciones costosas
    
    Args:
        cache_key_func: Función para generar clave de cache
        ttl_seconds: Tiempo de vida del cache en segundos
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave de cache
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                # Clave por defecto basada en función y argumentos
                args_str = str(args) + str(sorted(kwargs.items()))
                cache_key = f"{func.__name__}_{hashlib.md5(args_str.encode()).hexdigest()}"
            
            # Intentar obtener del cache
            if hasattr(wrapper, '_cache'):
                cached_result = wrapper._cache.get(cache_key)
                if cached_result is not None:
                    cache_time, result = cached_result
                    if time.time() - cache_time < ttl_seconds:
                        logger.debug(f"Cache hit para {func.__name__}")
                        return result
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            
            if not hasattr(wrapper, '_cache'):
                wrapper._cache = PerformanceCache()
            
            wrapper._cache.set(cache_key, (time.time(), result))
            logger.debug(f"Resultado cacheado para {func.__name__}")
            
            return result
        
        return wrapper
    return decorator


class PerformanceMonitor:
    """Monitor de rendimiento del sistema"""
    
    def __init__(self):
        self.metrics = {}
        self.start_times = {}
    
    def start_timer(self, operation_name: str):
        """Inicia un timer para una operación"""
        self.start_times[operation_name] = time.time()
    
    def end_timer(self, operation_name: str) -> float:
        """Termina un timer y retorna el tiempo transcurrido"""
        if operation_name in self.start_times:
            elapsed = time.time() - self.start_times[operation_name]
            self.record_metric(f"{operation_name}_time", elapsed)
            del self.start_times[operation_name]
            return elapsed
        return 0.0
    
    def record_metric(self, metric_name: str, value: float):
        """Registra una métrica"""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        self.metrics[metric_name].append({
            'value': value,
            'timestamp': time.time()
        })
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de métricas"""
        summary = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                values_only = [v['value'] for v in values]
                summary[metric_name] = {
                    'count': len(values_only),
                    'avg': np.mean(values_only),
                    'min': np.min(values_only),
                    'max': np.max(values_only),
                    'std': np.std(values_only),
                    'last': values_only[-1]
                }
        
        return summary
    
    def clear_metrics(self):
        """Limpia todas las métricas"""
        self.metrics.clear()
        self.start_times.clear()


# Instancia global del cache
global_cache = PerformanceCache()
global_monitor = PerformanceMonitor()


def performance_test(func: Callable) -> Callable:
    """Decorador para medir automáticamente el rendimiento de funciones"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        operation_name = f"{func.__module__}.{func.__name__}"
        global_monitor.start_timer(operation_name)
        
        try:
            result = func(*args, **kwargs)
            elapsed = global_monitor.end_timer(operation_name)
            logger.info(f"⏱️ {operation_name}: {elapsed:.3f}s")
            return result
        except Exception as e:
            global_monitor.end_timer(operation_name)
            raise
    
    return wrapper
