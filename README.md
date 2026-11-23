# Proyecto 1 - Investigación de incidentes con lógica proposicional

Implementación propia de los dos algoritmos solicitados:

- inferencia por enumeración de modelos;
- resolución proposicional por refutación.

El caso estudiado es la desaparición de una laptop del laboratorio. La base usa
las 8 variables y las 14 cláusulas CNF del informe corregido. Los datos están
separados de los algoritmos para que una regla, evidencia o consulta pueda
cambiarse sin modificar el procedimiento de inferencia.

## Estructura

```text
proyecto1_logica/
|-- algoritmos/
|   |-- enumeracion.py
|   `-- resolucion.py
|-- casos_prueba/
|   |-- base_conocimiento.json
|   |-- caso_1_unica_explicacion.json
|   |-- caso_2_varias_explicaciones.json
|   |-- caso_3_contradictorio.json
|   `-- caso_4_nueva_evidencia.json
|-- datos/
|   `-- cargador.py          # Incluye agregar_sospechoso, agregar_regla, validar_consistencia
|-- nucleo/
|   |-- cnf.py
|   |-- estados.py
|   `-- formulas.py
|-- pruebas/
|   |-- test_algoritmos.py
|   |-- test_casos.py
|   `-- test_extensiones.py  # Tests de sospechosos, reglas, consistencia y veredictos
|-- index.html               # Interfaz web interactiva con menú, modelos, trazas y diagnóstico
`-- ejecutar.py              # CLI para ejecución, pruebas y servidor web local
```

No se requieren bibliotecas externas; basta Python 3.10 o posterior.

## Funciones para Extensión y Validación

El módulo `datos.cargador` incorpora las siguientes funciones clave:

* `agregar_sospechoso(base, variable, nombre, actualizar_reglas_culpable=True)`: Registra un nuevo sospechoso y actualiza automáticamente las cláusulas de "al menos uno" ($E1$) y "a lo sumo uno" ($E2$).
* `agregar_regla(base, identificador, descripcion, formula)`: Parsea una fórmula proposicional arbitraria, la convierte a Forma Normal Conjuntiva (FNC) y la agrega a la base.
* `validar_consistencia(base, evidencia=(), metodo="ambos")`: Evalúa si la base es consistente o deriva en contradicción (cláusula vacía $\square$).
* `validar_adicion(base, nuevo_sospechoso=None, nueva_regla=None, evidencia=())`: Agrega sospechosos/reglas y valida inmediatamente la consistencia.
* `diagnosticar_culpabilidad(base, evidencia=(), sospechosos=None)`: Determina explícitamente:
  1. Si la base es consistente y se encontró un culpable único (quién fue).
  2. Si es consistente y no es posible encontrar un culpable único (el estado de la base llega a 2 o más posibles soluciones / indeterminación).
  3. Si se llega a una contradicción (cláusula vacía $\square$) o la base es inconsistente y falta información coherente.

## Interfaz Web (`index.html`)

Se incluye una interfaz web interactiva que no requiere instalación ni librerías externas. Puede abrirse directamente en el navegador:

* **Directamente:** Haga doble clic sobre `index.html` en el explorador de archivos o ábralo con su navegador favorito.
* **O mediante servidor local:**
  ```powershell
  python ejecutar.py --servidor 8000
  ```
  y visite `http://localhost:8000/index.html`.

La interfaz incluye:
* Menú selector de casos (Caso 1, Caso 2, Caso 3, Caso 4 y Modo Personalizado).
* Panel para añadir sospechosos y reglas proposicionales dinámicamente con validación inmediata.
* Visualizador de resolución por enumeración (tabla de modelos y asignaciones de verdad).
* Visualizador de resolución por refutación paso a paso con pivote y resolventes hasta la cláusula vacía $\square$.
* Panel final de veredicto con diagnóstico explícito del culpable o la contradicción.

## Ejecución en Consola

Desde esta carpeta:

```powershell
python ejecutar.py
```

El comando anterior ejecuta los cuatro casos, compara ambos algoritmos e imprime el diagnóstico explícito de culpabilidad de cada uno.

Para añadir sospechosos o reglas en tiempo de ejecución:

```powershell
# Base consistente: con un cuarto sospechoso quedan 3 soluciones posibles
python ejecutar.py --caso caso_2 --sospechoso G Gabriel --consulta G

# Base contradictoria: Gabriel usó llave, pero solo Diego y Elena tienen llave (E4)
python ejecutar.py --caso caso_2 --sospechoso G Gabriel --regla R9 "G -> K" "Gabriel usó llave" --evidencia G
```

Validaciones al añadir datos (en consola y en la interfaz web):

* El nombre de un sospechoso nuevo no puede coincidir con una variable que ya
  existe (por ejemplo `K`) y debe empezar con una letra.
* Una regla que usa una variable inexistente se rechaza, porque casi siempre es
  un error de escritura (`Ad` en lugar de `AD`) y crearía una variable nueva en
  silencio. El mensaje sugiere el nombre parecido. Si la variable nueva es
  intencional, use `--permitir-variables-nuevas` (en la web aparece una
  confirmación).

Para validar únicamente consistencia:

```powershell
python ejecutar.py --caso caso_3 --validar
```

Para ver los modelos y una secuencia completa de resolución:

```powershell
python ejecutar.py --caso caso_2 --consulta D --traza
```

Para simular durante la exposición una consulta o evidencia diferente:

```powershell
python ejecutar.py --caso caso_2 --consulta "~N -> E" --evidencia K --traza
```

Los literales negativos se escriben con `~`, por ejemplo `~K`. En las consultas
se aceptan `~` (negación), `&` (conjunción), `|` (disyunción), `->`
(implicación), `<->` (bicondicional) y paréntesis.

## Pruebas automáticas

```powershell
python -m unittest discover -s pruebas -v
```

Las pruebas comprueban los conteos esperados de modelos (1, 10, 0 y 2), la
clasificación de todas las consultas, la detección de contradicción y la
coincidencia entre enumeración y resolución.
