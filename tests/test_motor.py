"""
Tests unitarios para el motor de evaluación del Simulador WISC-V.
Cubre evaluación de dígitos, dibujos (2/1/0), baremos y discontinuación.
"""

import unittest
from src.motor import MotorEvaluacion


class TestEvalDigitos(unittest.TestCase):
    """Tests para evaluar_digitos()."""

    def test_directo_correcto(self):
        self.assertTrue(
            MotorEvaluacion.evaluar_digitos("1 2 3", [1, 2, 3], "directo")
        )

    def test_directo_incorrecto(self):
        self.assertFalse(
            MotorEvaluacion.evaluar_digitos("132", [1, 2, 3], "directo")
        )

    def test_inverso_correcto(self):
        self.assertTrue(
            MotorEvaluacion.evaluar_digitos("321", [1, 2, 3], "inverso")
        )

    def test_inverso_incorrecto(self):
        self.assertFalse(
            MotorEvaluacion.evaluar_digitos("123", [1, 2, 3], "inverso")
        )

    def test_secuenciacion_correcto(self):
        self.assertTrue(
            MotorEvaluacion.evaluar_digitos("123", [3, 1, 2], "secuenciacion")
        )

    def test_secuenciacion_incorrecto(self):
        self.assertFalse(
            MotorEvaluacion.evaluar_digitos("312", [3, 1, 2], "secuenciacion")
        )

    def test_caracteres_invalidos_letras(self):
        self.assertFalse(
            MotorEvaluacion.evaluar_digitos("1a2", [1, 2], "directo")
        )

    def test_input_vacio(self):
        self.assertFalse(
            MotorEvaluacion.evaluar_digitos("", [1, 2], "directo")
        )

    def test_modalidad_desconocida(self):
        with self.assertRaises(ValueError):
            MotorEvaluacion.evaluar_digitos("12", [1, 2], "inexistente")


class TestEvalDibujos(unittest.TestCase):
    """Tests para evaluar_dibujos() y evaluar_dibujos_puntuacion()."""

    # ── evaluar_dibujos (booleano) ──

    def test_dibujos_correcto_string(self):
        self.assertTrue(MotorEvaluacion.evaluar_dibujos("A B", "AB"))

    def test_dibujos_correcto_lista(self):
        self.assertTrue(MotorEvaluacion.evaluar_dibujos(" a b c ", ["A", "B", "C"]))

    def test_dibujos_incorrecto(self):
        self.assertFalse(MotorEvaluacion.evaluar_dibujos("A C", "AB"))

    # ── evaluar_dibujos_puntuacion (0/1/2) ──

    def test_puntuacion_2_secuencia_identica(self):
        self.assertEqual(
            MotorEvaluacion.evaluar_dibujos_puntuacion("ABC", ["A", "B", "C"]), 2
        )

    def test_puntuacion_2_con_espacios(self):
        self.assertEqual(
            MotorEvaluacion.evaluar_dibujos_puntuacion("A B C", ["A", "B", "C"]), 2
        )

    def test_puntuacion_2_minusculas(self):
        self.assertEqual(
            MotorEvaluacion.evaluar_dibujos_puntuacion("abc", ["A", "B", "C"]), 2
        )

    def test_puntuacion_1_mismo_elementos_diferente_orden(self):
        self.assertEqual(
            MotorEvaluacion.evaluar_dibujos_puntuacion("CBA", ["A", "B", "C"]), 1
        )

    def test_puntuacion_1_parcialmente_reordenado(self):
        self.assertEqual(
            MotorEvaluacion.evaluar_dibujos_puntuacion("BAC", ["A", "B", "C"]), 1
        )

    def test_puntuacion_0_elementos_diferentes(self):
        self.assertEqual(
            MotorEvaluacion.evaluar_dibujos_puntuacion("AXC", ["A", "B", "C"]), 0
        )

    def test_puntuacion_0_longitud_diferente(self):
        self.assertEqual(
            MotorEvaluacion.evaluar_dibujos_puntuacion("AB", ["A", "B", "C"]), 0
        )

    def test_puntuacion_0_vacio(self):
        self.assertEqual(
            MotorEvaluacion.evaluar_dibujos_puntuacion("", ["A"]), 0
        )

    def test_puntuacion_2_una_letra(self):
        self.assertEqual(
            MotorEvaluacion.evaluar_dibujos_puntuacion("A", ["A"]), 2
        )


class TestNavegacionItems(unittest.TestCase):
    """Tests para la navegación de ítems del JSON."""

    @classmethod
    def setUpClass(cls):
        cls.motor = MotorEvaluacion()

    def test_items_directo_existen(self):
        items = self.motor.obtener_items_digitos("orden_directo")
        self.assertGreater(len(items), 0)
        self.assertIn("intentos", items[0])

    def test_items_inverso_existen(self):
        items = self.motor.obtener_items_digitos("orden_inverso")
        self.assertGreater(len(items), 0)

    def test_items_creciente_existen(self):
        items = self.motor.obtener_items_digitos("orden_creciente")
        self.assertGreater(len(items), 0)

    def test_items_dibujos_existen(self):
        items = self.motor.obtener_items_dibujos()
        self.assertGreater(len(items), 0)
        self.assertIn("respuesta_correcta", items[0])

    def test_items_dibujos_total_29(self):
        items = self.motor.obtener_items_dibujos()
        self.assertEqual(len(items), 29)

    def test_modalidad_inexistente_retorna_vacio(self):
        items = self.motor.obtener_items_digitos("modalidad_falsa")
        self.assertEqual(items, [])


class TestBaremos(unittest.TestCase):
    """Tests para los cálculos de baremos."""

    @classmethod
    def setUpClass(cls):
        cls.motor = MotorEvaluacion()

    def test_pe_digitos_rango(self):
        # DS_d "0-12" → PE 1
        pe = self.motor.calcular_puntuacion_escalar(10, "DS_d")
        self.assertEqual(pe, 1)

    def test_pe_digitos_valor_exacto(self):
        # DS_d "31" → PE 11
        pe = self.motor.calcular_puntuacion_escalar(31, "DS_d")
        self.assertEqual(pe, 11)

    def test_pe_dibujos(self):
        # PS_sd "0-9" → PE 1
        pe = self.motor.calcular_puntuacion_escalar(5, "PS_sd")
        self.assertEqual(pe, 1)

    def test_pe_fuera_de_rango(self):
        pe = self.motor.calcular_puntuacion_escalar(999, "DS_d")
        self.assertIsNone(pe)

    def test_imt_calculo(self):
        # Suma PE = 20 → IMT 100, percentil 50
        resultado = self.motor.calcular_imt(10, 10)
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["imt_wmi"], 100)
        self.assertEqual(resultado["rango_percentil"], "50")

    def test_imt_fuera_de_tabla(self):
        resultado = self.motor.calcular_imt(1, 0)
        self.assertIsNone(resultado)


class TestDiscontinuacion(unittest.TestCase):
    """Tests para la detección del punto de discontinuación."""

    def test_sin_discontinuacion(self):
        resultados = [
            {"item": "1", "es_ejemplo": False, "intentos_resultado": [
                {"correcto": True}, {"correcto": False}
            ]},
            {"item": "2", "es_ejemplo": False, "intentos_resultado": [
                {"correcto": False}, {"correcto": True}
            ]},
        ]
        punto = MotorEvaluacion.detectar_discontinuacion_digitos(resultados)
        self.assertIsNone(punto)

    def test_con_discontinuacion(self):
        resultados = [
            {"item": "1", "es_ejemplo": False, "intentos_resultado": [
                {"correcto": True}, {"correcto": True}
            ]},
            {"item": "2", "es_ejemplo": False, "intentos_resultado": [
                {"correcto": False}, {"correcto": False}
            ]},
            {"item": "3", "es_ejemplo": False, "intentos_resultado": [
                {"correcto": False}, {"correcto": False}
            ]},
        ]
        punto = MotorEvaluacion.detectar_discontinuacion_digitos(resultados)
        self.assertEqual(punto, "3")

    def test_discontinuacion_salta_ejemplos(self):
        resultados = [
            {"item": "Ej", "es_ejemplo": True, "intentos_resultado": [
                {"correcto": False}, {"correcto": False}
            ]},
            {"item": "1", "es_ejemplo": False, "intentos_resultado": [
                {"correcto": False}, {"correcto": False}
            ]},
            {"item": "2", "es_ejemplo": False, "intentos_resultado": [
                {"correcto": True}, {"correcto": False}
            ]},
        ]
        punto = MotorEvaluacion.detectar_discontinuacion_digitos(resultados)
        self.assertIsNone(punto)

    def test_discontinuacion_dibujos(self):
        resultados = [
            {"item": "4", "es_ejemplo": False, "puntuacion": 2},
            {"item": "5", "es_ejemplo": False, "puntuacion": 0},
            {"item": "6", "es_ejemplo": False, "puntuacion": 0},
        ]
        punto = MotorEvaluacion.detectar_discontinuacion_dibujos(resultados)
        self.assertEqual(punto, "6")


if __name__ == "__main__":
    unittest.main()
