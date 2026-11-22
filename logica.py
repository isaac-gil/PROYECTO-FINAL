from datos import MATERIAS_CREDITOS


def validar_datos_alumno(
    id_alumno: str,
    nombre: str,
    carrera: str,
    correo: str,
    alumnos: dict[str, dict],
) -> tuple[str, dict[str, str]]:
    id_limpio = id_alumno.strip()
    nombre_limpio = nombre.strip()
    carrera_limpia = carrera.strip()
    correo_limpio = correo.strip()

    if not id_limpio:
        raise ValueError("El ID del alumno no puede estar vacío.")
    if id_limpio in alumnos:
        raise ValueError(f"El ID '{id_limpio}' ya se encuentra registrado.")
    if not nombre_limpio:
        raise ValueError("El nombre del alumno es obligatorio.")
    if not carrera_limpia:
        raise ValueError("La carrera es obligatoria.")
    if not correo_limpio or "@" not in correo_limpio or "." not in correo_limpio.split("@")[-1]:
        raise ValueError("Ingresa un correo electrónico válido.")

    datos_personales = {
        "nombre": nombre_limpio,
        "carrera": carrera_limpia,
        "correo": correo_limpio,
    }
    return id_limpio, datos_personales


def validar_materias_seleccionadas(materias: list[str]) -> list[str]:
    if not materias:
        raise ValueError("Debes seleccionar al menos una materia.")
    return materias


def buscar_alumno(id_alumno: str, alumnos: dict[str, dict]) -> tuple[str, dict]:
    id_limpio = id_alumno.strip()
    if not id_limpio:
        raise ValueError("Debes ingresar un ID para buscar.")
    if id_limpio not in alumnos:
        raise ValueError(f"No se encontró ningún alumno con el ID '{id_limpio}'.")
    return id_limpio, alumnos[id_limpio]


def eliminar_alumno(id_alumno: str, alumnos: dict[str, dict]) -> dict:
    id_limpio, _ = buscar_alumno(id_alumno, alumnos)
    return alumnos.pop(id_limpio)


def calcular_promedio_ponderado(calificaciones_texto: dict[str, str]) -> tuple[float, dict[str, float]]:
    suma_ponderada = 0.0
    total_creditos = 0
    calificaciones_validas: dict[str, float] = {}

    for materia, texto in calificaciones_texto.items():
        valor = texto.strip()
        if not valor:
            raise ValueError(f"Falta ingresar la calificación de '{materia}'.")
        try:
            calificacion = float(valor)
        except ValueError:
            raise ValueError(f"La calificación de '{materia}' debe ser un número válido.")

        if not (0.0 <= calificacion <= 10.0):
            raise ValueError(f"La calificación de '{materia}' debe estar entre 0 y 10.")

        creditos = MATERIAS_CREDITOS[materia]
        suma_ponderada += calificacion * creditos
        total_creditos += creditos
        calificaciones_validas[materia] = calificacion

    if total_creditos == 0:
        raise ValueError("El alumno no tiene créditos asignados.")

    return round(suma_ponderada / total_creditos, 2), calificaciones_validas


def registrar_calificaciones_alumno(
    id_alumno: str,
    promedio: float,
    calificaciones: dict[str, float],
    alumnos: dict[str, dict],
) -> None:
    _, datos = buscar_alumno(id_alumno, alumnos)
    datos["promedio"] = promedio
    datos["calificaciones"] = calificaciones