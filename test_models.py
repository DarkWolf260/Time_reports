# test_models.py
"""
Pruebas unitarias para los modelos y lógica de negocio.
Para ejecutar: python -m pytest test_models.py -v
"""
import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from models import Operador, OperadorManager, ReportGenerator, AppState

class TestOperador(unittest.TestCase):
    """Pruebas para la clase Operador."""
    
    def setUp(self):
        self.operador = Operador(
            nombre="Juan Pérez",
            cargo="Analista CEMUPRAD",
            jerarquia="OPC I",
            cedula="12345678"
        )
    
    def test_str_representation(self):
        """Prueba la representación string del operador."""
        expected = "Analista CEMUPRAD OPC I Juan Pérez 12345678"
        self.assertEqual(str(self.operador), expected)
    
    def test_to_dict(self):
        """Prueba la conversión a diccionario."""
        expected = {
            "nombre": "Juan Pérez",
            "cargo": "Analista CEMUPRAD",
            "jerarquia": "OPC I",
            "cedula": "12345678"
        }
        self.assertEqual(self.operador.to_dict(), expected)
    
    def test_from_dict(self):
        """Prueba la creación desde diccionario."""
        data = {
            "nombre": "María García",
            "cargo": "Coordinador CEMUPRAD",
            "jerarquia": "OSPC II",
            "cedula": "87654321"
        }
        operador = Operador.from_dict(data)
        self.assertEqual(operador.nombre, "María García")
        self.assertEqual(operador.cargo, "Coordinador CEMUPRAD")
        self.assertEqual(operador.jerarquia, "OSPC II")
        self.assertEqual(operador.cedula, "87654321")

class TestOperadorManager(unittest.TestCase):
    """Pruebas para la clase OperadorManager."""
    
    def setUp(self):
        """Configuración para cada prueba."""
        # Crear archivo temporal para las pruebas
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        
        # Mockear el archivo de operadores
        self.original_file = OperadorManager.__dict__.get('OPERADORES_FILE')
        with patch('models.OPERADORES_FILE', self.temp_file.name):
            self.manager = OperadorManager()
    
    def tearDown(self):
        """Limpieza después de cada prueba."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    @patch('models.OPERADORES_FILE')
    def test_cargar_operadores_archivo_no_existe(self, mock_file):
        """Prueba carga cuando el archivo no existe."""
        mock_file.return_value = "archivo_inexistente.json"
        with patch('os.path.exists', return_value=False):
            manager = OperadorManager()
            self.assertEqual(len(manager.obtener_operadores()), 0)
    
    @patch('models.OPERADORES_FILE')
    def test_agregar_operador_valido(self, mock_file):
        """Prueba agregar un operador válido."""
        mock_file.return_value = self.temp_file.name
        
        with patch('models.OPERADORES_FILE', self.temp_file.name):
            manager = OperadorManager()
            resultado = manager.agregar_operador("Juan Pérez", "Analista CEMUPRAD", "OPC I", "12345678")
            
            self.assertTrue(resultado)
            self.assertEqual(manager.cantidad, 1)
            
            operador = manager.buscar_por_nombre("Juan Pérez")
            self.assertIsNotNone(operador)
            self.assertEqual(operador.cedula, "12345678")
    
    @patch('models.OPERADORES_FILE')
    def test_agregar_operador_datos_invalidos(self, mock_file):
        """Prueba agregar operador con datos inválidos."""
        mock_file.return_value = self.temp_file.name
        
        with patch('models.OPERADORES_FILE', self.temp_file.name):
            manager = OperadorManager()
            
            # Nombre vacío
            resultado = manager.agregar_operador("", "Analista CEMUPRAD", "OPC I", "12345678")
            self.assertFalse(resultado)
            
            # Cédula vacía
            resultado = manager.agregar_operador("Juan Pérez", "Analista CEMUPRAD", "OPC I", "")
            self.assertFalse(resultado)
    
    @patch('models.OPERADORES_FILE')
    def test_eliminar_operador(self, mock_file):
        """Prueba eliminar un operador."""
        mock_file.return_value = self.temp_file.name
        
        with patch('models.OPERADORES_FILE', self.temp_file.name):
            manager = OperadorManager()
            manager.agregar_operador("Juan Pérez", "Analista CEMUPRAD", "OPC I", "12345678")
            
            resultado = manager.eliminar_operador("Juan Pérez")
            self.assertTrue(resultado)
            self.assertEqual(manager.cantidad, 0)
            
            # Intentar eliminar operador inexistente
            resultado = manager.eliminar_operador("No Existe")
            self.assertFalse(resultado)
    
    @patch('models.OPERADORES_FILE')
    def test_buscar_operadores(self, mock_file):
        """Prueba búsqueda de operadores."""
        mock_file.return_value = self.temp_file.name
        
        with patch('models.OPERADORES_FILE', self.temp_file.name):
            manager = OperadorManager()
            manager.agregar_operador("Juan Pérez", "Analista CEMUPRAD", "OPC I", "12345678")
            manager.agregar_operador("María García", "Coordinador CEMUPRAD", "OSPC II", "87654321")
            
            # Buscar por nombre
            operador = manager.buscar_por_nombre("Juan Pérez")
            self.assertIsNotNone(operador)
            self.assertEqual(operador.cedula, "12345678")
            
            # Buscar por cédula
            operador = manager.buscar_por_cedula("87654321")
            self.assertIsNotNone(operador)
            self.assertEqual(operador.nombre, "María García")
            
            # Buscar inexistente
            operador = manager.buscar_por_nombre("No Existe")
            self.assertIsNone(operador)

class TestReportGenerator(unittest.TestCase):
    """Pruebas para la clase ReportGenerator."""
    
    def setUp(self):
        self.operador = Operador(
            nombre="Juan Pérez",
            cargo="Analista CEMUPRAD", 
            jerarquia="OPC I",
            cedula="12345678"
        )
    
    @patch('models.datetime')
    def test_generar_reporte_con_operador(self, mock_datetime):
        """Prueba generación de reporte con operador."""
        # Mockear fecha y hora
        mock_date = MagicMock()
        mock_date.today().strftime.return_value = "08/09/2025"
        mock_datetime.date = mock_date
        
        mock_time = MagicMock()
        mock_time.now().strftime.return_value = "14:30"
        mock_datetime.datetime = mock_time
        
        reporte = ReportGenerator.generar_reporte(0, self.operador)
        
        # Verificar contenido del reporte
        self.assertIn("PROTECCIÓN CIVIL MUNICIPIO GUANTA", reporte)
        self.assertIn("08/09/2025", reporte)
        self.assertIn("14:30 HLV", reporte)
        self.assertIn("Juan Pérez", reporte)
        self.assertIn("☀", reporte)  # Emoji para cielo despejado
        self.assertIn("Cielo despejado", reporte)
    
    def test_generar_reporte_sin_operador(self):
        """Prueba generación de reporte sin operador."""
        reporte = ReportGenerator.generar_reporte(0, None)
        self.assertIn("(Sin operador)", reporte)
    
    def test_generar_reporte_indice_invalido(self):
        """Prueba generación con índice de tiempo inválido."""
        # Índice negativo
        reporte = ReportGenerator.generar_reporte(-1, self.operador)
        self.assertIn("Cielo despejado", reporte)  # Debe usar índice 0
        
        # Índice muy alto
        reporte = ReportGenerator.generar_reporte(999, self.operador)
        self.assertIn("Cielo despejado", reporte)  # Debe usar índice 0
    
    def test_markdown_a_textspan(self):
        """Prueba conversión de markdown a TextSpan."""
        texto = "*Texto en negrita* y texto normal"
        spans = ReportGenerator.markdown_a_textspan(texto)
        
        self.assertEqual(len(spans), 2)
        # Verificar que el primer span contiene el texto en negrita
        self.assertEqual(spans[0].text, "Texto en negrita")
        # Verificar que el segundo span contiene el texto normal
        self.assertEqual(spans[1].text, " y texto normal")

class TestAppState(unittest.TestCase):
    """Pruebas para la clase AppState."""
    
    def setUp(self):
        with patch('models.OperadorManager') as MockManager:
            self.mock_manager = MockManager.return_value
            self.app_state = AppState()
    
    def test_estado_inicial(self):
        """Prueba el estado inicial de la aplicación."""
        self.assertEqual(self.app_state.indice_tiempo, 0)
        self.assertEqual(self.app_state.indice_operador, 0)
        self.assertFalse(self.app_state.is_dark_theme)
    
    def test_cambiar_tiempo(self):
        """Prueba cambio de índice de tiempo."""
        self.app_state.cambiar_tiempo(5)
        self.assertEqual(self.app_state.indice_tiempo, 5)
        
        # Índice inválido no debe cambiar el estado
        self.app_state.cambiar_tiempo(-1)
        self.assertEqual(self.app_state.indice_tiempo, 5)  # No cambió
        
        self.app_state.cambiar_tiempo(999)
        self.assertEqual(self.app_state.indice_tiempo, 5)  # No cambió
    
    def test_cambiar_operador(self):
        """Prueba cambio de operador."""
        self.mock_manager.obtener_indice_por_nombre.return_value = 2
        
        self.app_state.cambiar_operador("Juan Pérez")
        
        self.mock_manager.obtener_indice_por_nombre.assert_called_with("Juan Pérez")
        self.assertEqual(self.app_state.indice_operador, 2)
    
    def test_cambiar_operador_inexistente(self):
        """Prueba cambio a operador inexistente."""
        self.mock_manager.obtener_indice_por_nombre.return_value = -1
        
        original_indice = self.app_state.indice_operador
        self.app_state.cambiar_operador("No Existe")
        
        # El índice no debe cambiar
        self.assertEqual(self.app_state.indice_operador, original_indice)

if __name__ == '__main__':
    # Configurar logging para las pruebas
    import logging
    logging.basicConfig(level=logging.CRITICAL)
    
    # Ejecutar pruebas
    unittest.main(verbosity=2)