import json
from pathlib import Path

MATERIAS_CREDITOS = {
    "Matemáticas Superiores": 10,
    "Química": 7,
    "Algoritmos y Programación": 6,
    "Diseño por Computadora": 3,
    "Ser Universitario": 6,
    "Taller de Comunicación": 3,
    "Temas Selectos Interdisciplinarios": 6,
}

ARCHIVO_DATOS = Path("alumnos.json")


def cargar_alumnos() -> dict[str, dict]:
    if ARCHIVO_DATOS.exists():
        with ARCHIVO_DATOS.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)

        for aid, info in list(datos.items()):
            if isinstance(info, list):
                datos[aid] = {
                    "nombre": "No registrado",
                    "carrera": "No registrada",
                    "correo": "No registrado",
                    "materias": info,
                    "calificaciones": {},
                    "promedio": None,
                }
            else:
                info.setdefault("calificaciones", {})
                info.setdefault("promedio", None)
        return datos
    return {}


def guardar_alumnos(alumnos: dict[str, dict]) -> None:
    with ARCHIVO_DATOS.open("w", encoding="utf-8") as archivo:
        json.dump(alumnos, archivo, indent=2, ensure_ascii=False)