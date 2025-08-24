#!/usr/bin/env python3
"""
Suite de Tests Completa para Conciliador IA
Incluye tests unitarios, de integración y de rendimiento
"""

import sys
import os
import pytest
import unittest
import time
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import pandas as pd
import json

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.extractor import PDFExtractor
from services.matchmaker import ConciliacionService
from agents.conciliador import ConciliadorAgent
from utils.file_helpers import FileManager
from utils.validation_helpers import DataValidator


class TestPDFExtractor(unittest.TestCase):
    """Tests para el extractor de PDF"""
    
    def setUp(self):
        self.extractor = PDFExtractor()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_pdf_extraction_basic(self):
        """Test básico de extracción de PDF"""
        # Crear un PDF de prueba simulado
        test_data = """
        FECHA       CONCEPTO                    DEBITO      CREDITO     SALDO
        01/12/2024  PAGO CLIENTE ABC           -           1500.00     15000.00
        02/12/2024  TRANSFERENCIA XYZ          500.00      -           14500.00
        """
        
        with patch.object(self.extractor, '_extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = test_data
            
            # Simular archivo PDF
            pdf_path = os.path.join(self.test_dir, 'test.pdf')
            Path(pdf_path).touch()
            
            df = self.extractor.extract_from_pdf(pdf_path)
            
            self.assertIsInstance(df, pd.DataFrame)
            self.assertGreater(len(df), 0)
            self.assertIn('fecha', df.columns)
            self.assertIn('concepto', df.columns)
            
    def test_pdf_extraction_empty_file(self):
        """Test manejo de archivo PDF vacío"""
        with patch.object(self.extractor, '_extract_text_from_pdf') as mock_extract:
            mock_extract.return_value = ""
            
            pdf_path = os.path.join(self.test_dir, 'empty.pdf')
            Path(pdf_path).touch()
            
            df = self.extractor.extract_from_pdf(pdf_path)
            self.assertTrue(df.empty)
    
    def test_pdf_extraction_invalid_file(self):
        """Test manejo de archivo PDF inválido"""
        invalid_path = os.path.join(self.test_dir, 'nonexistent.pdf')
        
        with self.assertRaises(Exception):
            self.extractor.extract_from_pdf(invalid_path)
    
    def test_amount_parsing(self):
        """Test parsing de montos con diferentes formatos"""
        test_cases = [
            ("1,500.00", 1500.00),
            ("1.500,00", 1500.00),
            ("$1,500.00", 1500.00),
            ("1500", 1500.00),
            ("-500.00", -500.00),
            ("", 0.0)
        ]
        
        for amount_str, expected in test_cases:
            with self.subTest(amount=amount_str):
                result = self.extractor._parse_amount(amount_str)
                self.assertEqual(result, expected)


class TestConciliacionService(unittest.TestCase):
    """Tests para el servicio de conciliación"""
    
    def setUp(self):
        self.service = ConciliacionService()
        self.mock_agent = Mock(spec=ConciliadorAgent)
        self.service.agent = self.mock_agent
        
    def test_conciliar_movimientos_success(self):
        """Test de conciliación exitosa"""
        # Datos de prueba
        movimientos = pd.DataFrame([
            {'fecha': '2024-01-15', 'concepto': 'PAGO CLIENTE ABC', 'monto': 1500.00, 'tipo': 'credito'},
            {'fecha': '2024-01-16', 'concepto': 'TRANSFERENCIA XYZ', 'monto': -500.00, 'tipo': 'debito'}
        ])
        
        comprobantes = pd.DataFrame([
            {'fecha': '2024-01-15', 'cliente': 'Cliente ABC', 'monto': 1500.00, 'concepto': 'Pago factura'},
            {'fecha': '2024-01-16', 'cliente': 'Cliente XYZ', 'monto': 500.00, 'concepto': 'Servicio'}
        ])
        
        # Mock de respuesta del agente
        mock_response = {
            'items': [
                {
                    'fecha_movimiento': '2024-01-15',
                    'concepto_movimiento': 'PAGO CLIENTE ABC',
                    'monto_movimiento': 1500.00,
                    'estado': 'conciliado',
                    'confianza': 0.95
                }
            ],
            'total_movimientos': 2,
            'movimientos_conciliados': 1
        }
        
        self.mock_agent.conciliar.return_value = mock_response
        
        result = self.service.conciliar_movimientos(movimientos, comprobantes, "test_empresa")
        
        self.assertIsInstance(result, dict)
        self.assertIn('items', result)
        self.assertIn('total_movimientos', result)
        self.assertEqual(result['total_movimientos'], 2)
    
    def test_conciliar_empty_data(self):
        """Test con datos vacíos"""
        empty_df = pd.DataFrame()
        
        result = self.service.conciliar_movimientos(empty_df, empty_df, "test_empresa")
        
        self.assertEqual(result['total_movimientos'], 0)
        self.assertEqual(result['movimientos_conciliados'], 0)
    
    def test_performance_large_dataset(self):
        """Test de rendimiento con dataset grande"""
        # Crear dataset grande
        large_movimientos = pd.DataFrame([
            {'fecha': f'2024-01-{i:02d}', 'concepto': f'MOVIMIENTO {i}', 'monto': i * 100, 'tipo': 'credito'}
            for i in range(1, 1001)  # 1000 movimientos
        ])
        
        large_comprobantes = pd.DataFrame([
            {'fecha': f'2024-01-{i:02d}', 'cliente': f'Cliente {i}', 'monto': i * 100, 'concepto': f'Comprobante {i}'}
            for i in range(1, 1001)  # 1000 comprobantes
        ])
        
        start_time = time.time()
        
        # Mock para evitar llamadas reales a OpenAI
        self.mock_agent.conciliar.return_value = {
            'items': [],
            'total_movimientos': 1000,
            'movimientos_conciliados': 800
        }
        
        result = self.service.conciliar_movimientos(large_movimientos, large_comprobantes, "test_empresa")
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Debería procesar en menos de 5 segundos (sin IA real)
        self.assertLess(processing_time, 5.0)
        self.assertEqual(result['total_movimientos'], 1000)


class TestDataValidator(unittest.TestCase):
    """Tests para validación de datos"""
    
    def setUp(self):
        self.validator = DataValidator()
    
    def test_validate_movimientos_df(self):
        """Test validación de DataFrame de movimientos"""
        # DataFrame válido
        valid_df = pd.DataFrame([
            {'fecha': '2024-01-15', 'concepto': 'TEST', 'monto': 100.0, 'tipo': 'credito'}
        ])
        
        result = self.validator.validate_movimientos_df(valid_df)
        self.assertTrue(result['is_valid'])
        
        # DataFrame inválido - columnas faltantes
        invalid_df = pd.DataFrame([
            {'fecha': '2024-01-15', 'concepto': 'TEST'}  # Falta monto
        ])
        
        result = self.validator.validate_movimientos_df(invalid_df)
        self.assertFalse(result['is_valid'])
        self.assertIn('errores', result)
    
    def test_validate_comprobantes_df(self):
        """Test validación de DataFrame de comprobantes"""
        # DataFrame válido
        valid_df = pd.DataFrame([
            {'fecha': '2024-01-15', 'cliente': 'Cliente Test', 'monto': 100.0, 'concepto': 'Servicio'}
        ])
        
        result = self.validator.validate_comprobantes_df(valid_df)
        self.assertTrue(result['is_valid'])
        
        # DataFrame inválido - fechas incorrectas
        invalid_df = pd.DataFrame([
            {'fecha': 'fecha_invalida', 'cliente': 'Cliente Test', 'monto': 100.0, 'concepto': 'Servicio'}
        ])
        
        result = self.validator.validate_comprobantes_df(invalid_df)
        self.assertFalse(result['is_valid'])


class TestFileManager(unittest.TestCase):
    """Tests para manejo de archivos"""
    
    def setUp(self):
        self.file_manager = FileManager()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_save_uploaded_file(self):
        """Test guardar archivo subido"""
        # Simular archivo
        content = b"contenido de prueba"
        filename = "test.pdf"
        
        saved_path = self.file_manager.save_uploaded_file(content, filename, self.test_dir)
        
        self.assertTrue(os.path.exists(saved_path))
        with open(saved_path, 'rb') as f:
            self.assertEqual(f.read(), content)
    
    def test_validate_file_size(self):
        """Test validación de tamaño de archivo"""
        # Archivo pequeño - válido
        small_content = b"x" * 1000  # 1KB
        self.assertTrue(self.file_manager.validate_file_size(small_content, max_size=10000))
        
        # Archivo grande - inválido
        large_content = b"x" * 20000  # 20KB
        self.assertFalse(self.file_manager.validate_file_size(large_content, max_size=10000))
    
    def test_cleanup_old_files(self):
        """Test limpieza de archivos antiguos"""
        # Crear archivos de prueba
        old_file = os.path.join(self.test_dir, "old_file.pdf")
        new_file = os.path.join(self.test_dir, "new_file.pdf")
        
        Path(old_file).touch()
        Path(new_file).touch()
        
        # Modificar tiempo de modificación del archivo antiguo
        old_time = time.time() - 86400 * 8  # 8 días atrás
        os.utime(old_file, (old_time, old_time))
        
        deleted_count = self.file_manager.cleanup_old_files(self.test_dir, days=7)
        
        self.assertEqual(deleted_count, 1)
        self.assertFalse(os.path.exists(old_file))
        self.assertTrue(os.path.exists(new_file))


class TestIntegrationConciliacion(unittest.TestCase):
    """Tests de integración completos"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('agents.conciliador.ConciliadorAgent.conciliar')
    def test_full_conciliation_flow(self, mock_conciliar):
        """Test del flujo completo de conciliación"""
        # Mock de respuesta de IA
        mock_conciliar.return_value = {
            'items': [
                {
                    'fecha_movimiento': '2024-01-15T10:30:00',
                    'concepto_movimiento': 'PAGO CLIENTE ABC',
                    'monto_movimiento': 1500.00,
                    'estado': 'conciliado',
                    'confianza': 0.95
                }
            ],
            'total_movimientos': 1,
            'movimientos_conciliados': 1,
            'movimientos_pendientes': 0
        }
        
        # Crear archivos de prueba
        csv_content = """fecha,cliente,monto,concepto
2024-01-15,Cliente ABC,1500.00,Pago factura"""
        
        csv_path = os.path.join(self.test_dir, 'comprobantes.csv')
        with open(csv_path, 'w') as f:
            f.write(csv_content)
        
        # Simular extracción de PDF
        movimientos_data = pd.DataFrame([
            {'fecha': '2024-01-15', 'concepto': 'PAGO CLIENTE ABC', 'monto': 1500.00, 'tipo': 'credito'}
        ])
        
        # Cargar comprobantes
        comprobantes_data = pd.read_csv(csv_path)
        
        # Instanciar servicio
        service = ConciliacionService()
        
        # Ejecutar conciliación
        result = service.conciliar_movimientos(movimientos_data, comprobantes_data, "empresa_test")
        
        # Verificaciones
        self.assertIsInstance(result, dict)
        self.assertEqual(result['total_movimientos'], 1)
        self.assertEqual(result['movimientos_conciliados'], 1)
        self.assertIn('items', result)


def run_performance_tests():
    """Ejecutar tests de rendimiento específicos"""
    print("\n" + "="*60)
    print("🚀 EJECUTANDO TESTS DE RENDIMIENTO")
    print("="*60)
    
    # Test 1: Procesamiento de archivos grandes
    print("\n📊 Test 1: Procesamiento de DataFrames grandes")
    start_time = time.time()
    
    # Crear dataset grande
    large_df = pd.DataFrame({
        'fecha': pd.date_range('2024-01-01', periods=10000, freq='H'),
        'concepto': [f'Movimiento {i}' for i in range(10000)],
        'monto': [i * 10.5 for i in range(10000)],
        'tipo': ['credito' if i % 2 == 0 else 'debito' for i in range(10000)]
    })
    
    # Operaciones típicas
    filtered_df = large_df[large_df['monto'] > 1000]
    grouped_df = large_df.groupby('tipo')['monto'].sum()
    
    end_time = time.time()
    print(f"✅ Procesado {len(large_df)} registros en {end_time - start_time:.2f} segundos")
    
    # Test 2: Validación masiva
    print("\n🔍 Test 2: Validación masiva de datos")
    start_time = time.time()
    
    validator = DataValidator()
    for i in range(1000):
        test_df = pd.DataFrame([
            {'fecha': '2024-01-15', 'concepto': f'TEST {i}', 'monto': 100.0, 'tipo': 'credito'}
        ])
        validator.validate_movimientos_df(test_df)
    
    end_time = time.time()
    print(f"✅ Validadas 1000 estructuras en {end_time - start_time:.2f} segundos")


def run_all_tests():
    """Ejecutar toda la suite de tests"""
    print("🧪 INICIANDO SUITE COMPLETA DE TESTS")
    print("="*60)
    
    # Configurar el runner de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Cargar todos los tests
    test_classes = [
        TestPDFExtractor,
        TestConciliacionService,
        TestDataValidator,
        TestFileManager,
        TestIntegrationConciliacion
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Ejecutar tests de rendimiento
    run_performance_tests()
    
    # Resumen final
    print("\n" + "="*60)
    print("📊 RESUMEN DE TESTS")
    print("="*60)
    print(f"✅ Tests ejecutados: {result.testsRun}")
    print(f"❌ Fallos: {len(result.failures)}")
    print(f"🚫 Errores: {len(result.errors)}")
    print(f"⏭️  Saltados: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ FALLOS:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n🚫 ERRORES:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\n🎯 Tasa de éxito: {success_rate:.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Suite de Tests Conciliador IA')
    parser.add_argument('--performance', action='store_true', help='Solo ejecutar tests de rendimiento')
    parser.add_argument('--unit', action='store_true', help='Solo ejecutar tests unitarios')
    parser.add_argument('--integration', action='store_true', help='Solo ejecutar tests de integración')
    
    args = parser.parse_args()
    
    if args.performance:
        run_performance_tests()
    elif args.unit:
        # Ejecutar solo tests unitarios
        unittest.main(argv=[''], test_module=None, verbosity=2, exit=False)
    elif args.integration:
        # Ejecutar solo tests de integración
        suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegrationConciliacion)
        unittest.TextTestRunner(verbosity=2).run(suite)
    else:
        # Ejecutar todos los tests
        success = run_all_tests()
        sys.exit(0 if success else 1)
