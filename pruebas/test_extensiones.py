import unittest

from datos.cargador import (
    agregar_regla,
    agregar_sospechoso,
    cargar_base,
    diagnosticar_culpabilidad,
    validar_adicion,
    validar_consistencia,
)


class PruebasNuevasFunciones(unittest.TestCase):
    def setUp(self):
        self.base = cargar_base()

    def test_agregar_sospechoso_actualiza_e1_y_e2(self):
        base_nueva = agregar_sospechoso(self.base, "G", "Gabriel")
        self.assertIn("G", base_nueva.variables)
        self.assertIn("G", base_nueva.significados)

        # Verificar que la regla E1 ahora incluye a G
        regla_e1 = next(r for r in base_nueva.reglas if r.identificador == "E1")
        variables_e1 = {lit.variable for lit in regla_e1.fnc[0]}
        self.assertEqual({"D", "E", "F", "G"}, variables_e1)

        # Regla E2 debe tener combinaciones de 4 tomados de a 2 = 6 clausulas
        regla_e2 = next(r for r in base_nueva.reglas if r.identificador == "E2")
        self.assertEqual(6, len(regla_e2.fnc))

        # La base debe ser consistente
        validacion = validar_consistencia(base_nueva)
        self.assertTrue(validacion.consistente)
        self.assertFalse(validacion.clausula_vacia)

    def test_agregar_regla_y_validar_consistencia(self):
        # Agregar una regla compatible
        base_nueva = agregar_regla(
            self.base,
            "R_TEST",
            "Si Diego es inocente entonces Elena o Fabián",
            "~D -> (E | F)",
        )
        self.assertTrue(any(r.identificador == "R_TEST" for r in base_nueva.reglas))
        val_compatible = validar_consistencia(base_nueva)
        self.assertTrue(val_compatible.consistente)

        # Agregar una regla contradictoria directa
        # En la base original E3: N -> A y E6: A -> ~K.
        # Si agregamos regla N & K:
        base_contradictoria = agregar_regla(
            base_nueva, "R_CONTRA", "Noche y llave juntos", "N & K"
        )
        val_inconsistente = validar_consistencia(base_contradictoria)
        self.assertFalse(val_inconsistente.consistente)
        self.assertTrue(val_inconsistente.clausula_vacia)

    def test_validar_adicion(self):
        base_mod, val = validar_adicion(
            self.base,
            nuevo_sospechoso=("G", "Gabriel"),
            nueva_regla=("R_G", "Gabriel estaba en el lab", "G -> N"),
        )
        self.assertIn("G", base_mod.variables)
        self.assertTrue(val.consistente)

    def test_diagnostico_culpable_caso_1(self):
        # Caso 1: Evidencia A, AD, AE -> Fabián (F) culpable demostrado
        diag = diagnosticar_culpabilidad(self.base, evidencia=["A", "AD", "AE"])
        self.assertTrue(diag.consistente)
        self.assertEqual("CULPABLE_ENCONTRADO", diag.estado)
        self.assertEqual("F", diag.culpable)
        self.assertIn("Fabián", diag.mensaje)

    def test_diagnostico_multiples_soluciones_caso_2(self):
        # Caso 2: Sin evidencia adicional -> Dos posibles soluciones (E y F)
        diag = diagnosticar_culpabilidad(self.base, evidencia=[])
        self.assertTrue(diag.consistente)
        self.assertEqual("MULTIPLES_SOLUCIONES", diag.estado)
        self.assertIsNone(diag.culpable)
        self.assertEqual(set(diag.posibles_culpables), {"E", "F"})
        self.assertIn("posibles soluciones", diag.mensaje)

    def test_diagnostico_contradiccion_caso_3(self):
        # Caso 3: Evidencia contradictoria K y A
        diag = diagnosticar_culpabilidad(self.base, evidencia=["K", "A"])
        self.assertFalse(diag.consistente)
        self.assertEqual("CONTRADICCION", diag.estado)
        self.assertTrue(diag.clausula_vacia)
        self.assertIn("contradicción", diag.mensaje.lower())

    def test_diagnostico_culpable_caso_4(self):
        # Caso 4: Evidencia K -> Elena (E) culpable demostrada
        diag = diagnosticar_culpabilidad(self.base, evidencia=["K"])
        self.assertTrue(diag.consistente)
        self.assertEqual("CULPABLE_ENCONTRADO", diag.estado)
        self.assertEqual("E", diag.culpable)
        self.assertIn("Elena", diag.mensaje)


    def test_agregar_sospechoso_rechaza_variable_existente(self):
        for nombre in ("K", "k", "D", "AD"):
            with self.subTest(variable=nombre):
                with self.assertRaises(ValueError):
                    agregar_sospechoso(self.base, nombre, "Alguien")
        # La base original no se modifica
        regla_e1 = next(r for r in self.base.reglas if r.identificador == "E1")
        self.assertEqual({"D", "E", "F"}, {lit.variable for lit in regla_e1.fnc[0]})
        self.assertEqual("Se usó una llave", self.base.significados["K"])

    def test_agregar_sospechoso_rechaza_nombre_invalido(self):
        for nombre in ("", "1X", "G H", "G-1"):
            with self.subTest(variable=nombre):
                with self.assertRaises(ValueError):
                    agregar_sospechoso(self.base, nombre, "Alguien")

    def test_agregar_regla_rechaza_variable_desconocida(self):
        with self.assertRaises(ValueError) as contexto:
            agregar_regla(self.base, "R9", "typo", "Ad -> K")
        self.assertIn("AD", str(contexto.exception))  # sugiere el nombre correcto
        # No se creó la variable ni la regla
        self.assertNotIn("Ad", self.base.variables)
        self.assertFalse(any(r.identificador == "R9" for r in self.base.reglas))

    def test_agregar_regla_permite_variable_nueva_si_se_pide(self):
        base_nueva = agregar_regla(
            self.base, "R9", "variable nueva", "Ad -> K", permitir_variables_nuevas=True
        )
        self.assertIn("Ad", base_nueva.variables)
        self.assertTrue(validar_consistencia(base_nueva).consistente)

    def test_validar_adicion_acepta_regla_con_sospechoso_recien_agregado(self):
        base_mod, val = validar_adicion(
            self.base,
            nuevo_sospechoso=("G", "Gabriel"),
            nueva_regla=("R_G", "Gabriel de noche", "G -> N"),
        )
        self.assertIn("G", base_mod.variables)
        self.assertTrue(val.consistente)


if __name__ == "__main__":
    unittest.main()
