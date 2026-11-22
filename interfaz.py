import tkinter as tk
from tkinter import messagebox, ttk
from datos import MATERIAS_CREDITOS, cargar_alumnos, guardar_alumnos
from logica import (
    validar_datos_alumno,
    validar_materias_seleccionadas,
    buscar_alumno,
    eliminar_alumno,
    calcular_promedio_ponderado,
    registrar_calificaciones_alumno,
)


class AppPonderador:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Ponderador Académico")
        self.root.geometry("410x500")
        self.alumnos = cargar_alumnos()
        self._construir_menu_principal()

    def _construir_menu_principal(self):
        tk.Label(self.root, text="Sistema de Promedio Ponderado", font=("Arial", 12, "bold")).pack(pady=15)

        marco = tk.Frame(self.root, bg="light blue", padx=25, pady=20)
        marco.pack(padx=20, pady=10, fill="both", expand=True)

        botones = [
            ("1. Registrar alumno", self.abrir_registro_alumno),
            ("2. Calcular promedio por ID", self.abrir_busqueda_promedio),
            ("3. Ver todos los alumnos", self.abrir_todos_los_datos),
            ("4. Eliminar registro por ID", self.abrir_eliminar_alumno),
            ("5. Resetear registros", self.resetear_datos),
            ("6. Salir", self.salir),
        ]
        for texto, accion in botones:
            tk.Button(marco, text=texto, width=28, command=accion).pack(pady=8)

    def abrir_registro_alumno(self):
        ventana_reg = tk.Toplevel(self.root)
        ventana_reg.title("Registrar Alumno")
        ventana_reg.geometry("400x260")

        marco = tk.Frame(ventana_reg, bg="light blue", padx=20, pady=20)
        marco.pack(fill="both", expand=True)

        campos = [
            ("ID del alumno:", 0),
            ("Nombre completo:", 1),
            ("Carrera:", 2),
            ("Correo electrónico:", 3),
        ]
        entradas: dict[str, tk.Entry] = {}
        claves = ["id", "nombre", "carrera", "correo"]

        for (etiqueta, fila), clave in zip(campos, claves):
            tk.Label(marco, text=etiqueta, bg="light blue").grid(row=fila, column=0, sticky="w", padx=5, pady=7)
            caja = tk.Entry(marco, width=26)
            caja.grid(row=fila, column=1, padx=5, pady=7)
            entradas[clave] = caja

        entradas["id"].focus()

        def continuar(event=None):
            try:
                id_valido, datos_personales = validar_datos_alumno(
                    entradas["id"].get(),
                    entradas["nombre"].get(),
                    entradas["carrera"].get(),
                    entradas["correo"].get(),
                    self.alumnos,
                )
            except ValueError as error:
                messagebox.showerror("Datos inválidos", str(error), parent=ventana_reg)
                return

            ventana_reg.destroy()
            self._abrir_seleccion_materias(id_valido, datos_personales)

        entradas["correo"].bind("<Return>", continuar)
        tk.Button(marco, text="Continuar a materias", command=continuar).grid(
            row=4, column=0, columnspan=2, pady=15
        )

    def _abrir_seleccion_materias(self, id_alumno: str, datos_personales: dict[str, str]):
        ventana_mat = tk.Toplevel(self.root)
        ventana_mat.title(f"Materias - {id_alumno}")
        ventana_mat.geometry("430x430")

        marco = tk.Frame(ventana_mat, bg="light blue", padx=20, pady=15)
        marco.pack(fill="both", expand=True)

        tk.Label(
            marco,
            text=f"Alumno: {datos_personales['nombre']} ({id_alumno})",
            bg="light blue",
            font=("Arial", 10, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        checks = {}
        for materia, creditos in MATERIAS_CREDITOS.items():
            var = tk.BooleanVar(value=False)
            checks[materia] = var
            tk.Checkbutton(
                marco,
                text=f"{materia} ({creditos} créd.)",
                variable=var,
                bg="light blue",
            ).pack(anchor="w", pady=3)

        def guardar():
            seleccionadas = [m for m, var in checks.items() if var.get()]
            try:
                validar_materias_seleccionadas(seleccionadas)
            except ValueError as error:
                messagebox.showerror("Selección inválida", str(error), parent=ventana_mat)
                return

            self.alumnos[id_alumno] = {
                **datos_personales,
                "materias": seleccionadas,
                "calificaciones": {},
                "promedio": None,
            }
            guardar_alumnos(self.alumnos)
            ventana_mat.destroy()
            messagebox.showinfo(
                "Registro guardado",
                f"Alumno '{datos_personales['nombre']}' (ID: {id_alumno}) guardado con {len(seleccionadas)} materias.",
            )

        tk.Button(marco, text="Guardar registro", command=guardar).pack(pady=15)

    def abrir_busqueda_promedio(self):
        if not self.alumnos:
            messagebox.showwarning("Sin registros", "Primero debes registrar al menos un alumno.")
            return

        ventana_busq = tk.Toplevel(self.root)
        ventana_busq.title("Buscar Alumno por ID")
        ventana_busq.geometry("380x160")

        marco = tk.Frame(ventana_busq, bg="light blue", padx=20, pady=20)
        marco.pack(fill="both", expand=True)

        tk.Label(marco, text="Ingresa el ID del alumno:", bg="light blue").grid(row=0, column=0, padx=5, pady=10)
        entrada_id = tk.Entry(marco, width=20)
        entrada_id.grid(row=0, column=1, padx=5, pady=10)
        entrada_id.focus()

        def buscar(event=None):
            try:
                id_encontrado, _ = buscar_alumno(entrada_id.get(), self.alumnos)
            except ValueError as error:
                messagebox.showerror("Búsqueda sin resultados", str(error), parent=ventana_busq)
                return

            ventana_busq.destroy()
            self._abrir_captura_calificaciones(id_encontrado)

        entrada_id.bind("<Return>", buscar)
        tk.Button(marco, text="Buscar materias", command=buscar).grid(row=1, column=0, columnspan=2, pady=10)

    def _abrir_captura_calificaciones(self, id_alumno: str):
        datos = self.alumnos[id_alumno]
        ventana_cal = tk.Toplevel(self.root)
        ventana_cal.title(f"Calificaciones - {id_alumno}")
        ventana_cal.geometry("480x440")

        marco = tk.Frame(ventana_cal, bg="light blue", padx=20, pady=15)
        marco.pack(fill="both", expand=True)

        ficha = tk.LabelFrame(marco, text="Datos del Alumno", bg="light blue", padx=10, pady=8)
        ficha.pack(fill="x", pady=(0, 12))

        tk.Label(ficha, text=f"ID: {id_alumno}", bg="light blue", anchor="w").pack(fill="x")
        tk.Label(ficha, text=f"Nombre: {datos['nombre']}", bg="light blue", anchor="w").pack(fill="x")
        tk.Label(ficha, text=f"Carrera: {datos['carrera']}", bg="light blue", anchor="w").pack(fill="x")
        tk.Label(ficha, text=f"Correo: {datos['correo']}", bg="light blue", anchor="w").pack(fill="x")

        marco_materias = tk.Frame(marco, bg="light blue")
        marco_materias.pack(fill="x")

        tk.Label(
            marco_materias,
            text="Ingresa las calificaciones (0 a 10):",
            bg="light blue",
            font=("Arial", 10, "bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        califs_previas = datos.get("calificaciones", {})
        entradas: dict[str, tk.Entry] = {}
        for fila, materia in enumerate(datos["materias"], start=1):
            creditos = MATERIAS_CREDITOS[materia]
            tk.Label(marco_materias, text=f"{materia} ({creditos} créd.):", bg="light blue").grid(
                row=fila, column=0, sticky="w", padx=(0, 10), pady=4
            )
            caja = tk.Entry(marco_materias, width=8)
            if materia in califs_previas:
                caja.insert(0, str(califs_previas[materia]))
            caja.grid(row=fila, column=1, pady=4)
            entradas[materia] = caja

        def procesar():
            datos_capturados = {mat: caja.get() for mat, caja in entradas.items()}
            try:
                promedio, califs = calcular_promedio_ponderado(datos_capturados)
            except ValueError as error:
                messagebox.showerror("Dato inválido", str(error), parent=ventana_cal)
                return

            registrar_calificaciones_alumno(id_alumno, promedio, califs, self.alumnos)
            guardar_alumnos(self.alumnos)

            detalle_materias = "\n".join(
                f"  • {mat} ({MATERIAS_CREDITOS[mat]} créd.): {nota}"
                for mat, nota in califs.items()
            )
            resumen = (
                f"ID: {id_alumno} | Nombre: {datos['nombre']}\n"
                f"Carrera: {datos['carrera']} | Correo: {datos['correo']}\n"
                f"--------------------------------------------------\n"
                f"Materias evaluadas:\n{detalle_materias}\n"
                f"--------------------------------------------------\n"
                f"Promedio ponderado guardado: {promedio}"
            )
            messagebox.showinfo("Promedio Guardado", resumen, parent=ventana_cal)

        tk.Button(marco, text="Calcular y Guardar Promedio", command=procesar).pack(pady=15)

    def abrir_todos_los_datos(self):
        if not self.alumnos:
            messagebox.showwarning("Sin registros", "No hay alumnos registrados todavía.")
            return

        ventana_datos = tk.Toplevel(self.root)
        ventana_datos.title("Todos los Alumnos Registrados")
        ventana_datos.geometry("620x540")

        contenedor = tk.Frame(ventana_datos, bg="light blue", padx=15, pady=15)
        contenedor.pack(fill="both", expand=True)

        tk.Label(
            contenedor,
            text=f"Registros guardados ({len(self.alumnos)} alumnos)",
            bg="light blue",
            font=("Arial", 11, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        canvas = tk.Canvas(contenedor, bg="light blue", highlightthickness=0)
        scrollbar = ttk.Scrollbar(contenedor, orient="vertical", command=canvas.yview)
        frame_lista = tk.Frame(canvas, bg="light blue")

        frame_lista.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        ventana_interna = canvas.create_window((0, 0), window=frame_lista, anchor="nw")
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(ventana_interna, width=e.width),
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for id_alumno, datos in self.alumnos.items():
            ficha = tk.LabelFrame(
                frame_lista,
                text=f"ID: {id_alumno} - {datos['nombre']}",
                bg="white",
                font=("Arial", 10, "bold"),
                padx=12,
                pady=8,
            )
            ficha.pack(fill="x", pady=6)

            tk.Label(ficha, text=f"Carrera: {datos['carrera']}", bg="white", anchor="w").pack(fill="x")
            tk.Label(ficha, text=f"Correo: {datos['correo']}", bg="white", anchor="w").pack(fill="x", pady=(0, 6))

            califs = datos.get("calificaciones", {})
            tk.Label(ficha, text="Materias:", bg="white", font=("Arial", 9, "bold"), anchor="w").pack(fill="x")

            for mat in datos["materias"]:
                cred = MATERIAS_CREDITOS[mat]
                nota = califs[mat] if mat in califs else "Sin evaluar"
                tk.Label(
                    ficha,
                    text=f"  • {mat} ({cred} créd.): {nota}",
                    bg="white",
                    anchor="w",
                ).pack(fill="x")

            promedio = datos.get("promedio")
            texto_prom = f"{promedio:.2f}" if promedio is not None else "Sin calcular"
            tk.Label(
                ficha,
                text=f"Promedio ponderado: {texto_prom}",
                bg="white",
                font=("Arial", 10, "bold"),
                fg="#0F5132" if promedio is not None else "#6C757D",
                anchor="w",
            ).pack(fill="x", pady=(6, 0))

    def abrir_eliminar_alumno(self):
        if not self.alumnos:
            messagebox.showwarning("Sin registros", "No hay alumnos registrados para eliminar.")
            return

        ventana_del = tk.Toplevel(self.root)
        ventana_del.title("Eliminar Registro")
        ventana_del.geometry("380x160")

        marco = tk.Frame(ventana_del, bg="light blue", padx=20, pady=20)
        marco.pack(fill="both", expand=True)

        tk.Label(marco, text="ID a eliminar:", bg="light blue").grid(row=0, column=0, padx=5, pady=10)
        entrada_id = tk.Entry(marco, width=22)
        entrada_id.grid(row=0, column=1, padx=5, pady=10)
        entrada_id.focus()

        def buscar_y_eliminar(event=None):
            try:
                id_encontrado, datos = buscar_alumno(entrada_id.get(), self.alumnos)
            except ValueError as error:
                messagebox.showerror("Búsqueda sin resultados", str(error), parent=ventana_del)
                return

            lista_materias = ", ".join(datos["materias"])
            confirmado = messagebox.askyesno(
                "Confirmar eliminación",
                f"¿Eliminar el registro de '{datos['nombre']}' (ID: {id_encontrado})?\n"
                f"Carrera: {datos['carrera']}\n"
                f"Materias: {lista_materias}",
                parent=ventana_del,
            )
            if confirmado:
                eliminar_alumno(id_encontrado, self.alumnos)
                guardar_alumnos(self.alumnos)
                ventana_del.destroy()
                messagebox.showinfo("Registro eliminado", f"El alumno con ID '{id_encontrado}' fue eliminado.")

        entrada_id.bind("<Return>", buscar_y_eliminar)
        tk.Button(marco, text="Buscar y eliminar", command=buscar_y_eliminar).grid(
            row=1, column=0, columnspan=2, pady=10
        )

    def resetear_datos(self):
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar todos los alumnos registrados?"):
            self.alumnos.clear()
            guardar_alumnos(self.alumnos)
            messagebox.showinfo("Reseteo", "Todos los registros han sido eliminados.")

    def salir(self):
        messagebox.showinfo("Hasta luego", "Gracias por usar el sistema.")
        self.root.destroy()