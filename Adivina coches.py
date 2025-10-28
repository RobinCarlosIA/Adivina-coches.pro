
# -*- coding: utf-8 -*-
"""
Adivina Quién de Carros 
Autor: Robin Emmanuel Carlos Gonzalez  (mi versión comentada)
Fecha: 23/10/2025

Qué hace:
- Hace preguntas UNA POR UNA (12 en total) para adivinar el auto pensado.
- Muestra progreso (Paso X/12) y barra de avance.
- Antes de adivinar, enseña un RESUMEN de mis respuestas para confirmar.
- Si no acierta, puedo enseñar el auto y lo guarda en coches_db.json (aprende).
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import tkinter as tk
from tkinter import ttk, messagebox

# OJO: si quiero usar otro nombre/ubicación del JSON, cambio esta constante:
DB_PATH = "coches_db.json"


# ============================ CAPA DE DATOS ====================================
class CarDB:
    """
    Clase de base de datos MUY simple (archivo JSON).
    - attributes: lista de preguntas con sus opciones (o tipo bool).
    - cars: lista de autos conocidos, cada uno con sus campos.
    """

    def __init__(self, ruta: str = DB_PATH):
        self.ruta = ruta
        self.attributes: List[Dict[str, Any]] = []
        self.cars: List[Dict[str, Any]] = []

    # Esquema oficial (SIN "marca" como pregunta, CON "segmento")
    def _schema_attributes(self) -> List[Dict[str, Any]]:
        return [
            {"key": "tipo",        "pregunta": "Tipo de carrocería", "opciones": [
                "sedan","hatchback","suv","pickup","coupe","convertible","crossover","van"
            ]},
            {"key": "electrico",   "pregunta": "¿Es eléctrico?", "tipo": "bool"},
            {"key": "hibrido",     "pregunta": "¿Es híbrido?", "tipo": "bool"},
            {"key": "combustible", "pregunta": "Combustible", "opciones": [
                "gasolina","diesel","electrico","hibrido"
            ]},
            {"key": "origen",      "pregunta": "Origen de la marca", "opciones": [
                "japonesa","americana","europea","china","coreana"
            ]},
            {"key": "lujo",        "pregunta": "¿Es de lujo/premium?", "tipo": "bool"},
            {"key": "puertas",     "pregunta": "Número de puertas", "opciones": ["2","3","4","5"]},
            {"key": "traccion",    "pregunta": "Tracción", "opciones": ["delantera","trasera","AWD","4x4"]},
            {"key": "transmision", "pregunta": "Transmisión", "opciones": ["manual","automatica","cvt","dct"]},
            {"key": "anio",        "pregunta": "Año (rango)", "opciones": ["≤2010","2011-2015","2016-2020","2021+"]},
            {"key": "precio",      "pregunta": "Rango de precio", "opciones": ["economico","medio","premium","lujo"]},
            {"key": "segmento",    "pregunta": "Segmento", "opciones": [
                "subcompacto","compacto","mediano","grande","SUV/Crossover","Pickup","Deportivo"
            ]},
        ]

    def cargar(self) -> None:
        """
        Carga el JSON. Si no existe, genero una semilla (varios autos).
        Si existe pero está "viejo", hago MIGRACIÓN para completar campos.
        """
        if not os.path.exists(self.ruta):
            self._semilla()
            self.guardar()
            return

        with open(self.ruta, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Cargo coches existentes y fuerzo esquema actual de preguntas
        self.cars = data.get("cars", [])
        self.attributes = self._schema_attributes()

        # Intento actualizar coches viejos para evitar KeyError y vacíos
        if self._upgrade_schema():
            self.guardar()

    def guardar(self) -> None:
        """Persisto en JSON (legible con indent=2)."""
        with open(self.ruta, "w", encoding="utf-8") as f:
            json.dump({"attributes": self.attributes, "cars": self.cars},
                      f, ensure_ascii=False, indent=2)

    def _semilla(self) -> None:
        """Base inicial (40+ autos). Suficiente para que el juego sea útil."""
        self.attributes = self._schema_attributes()

        # Nota: guardo 'marca' en cada coche SOLO para mostrar/ayudar,
        # ya no la pregunto explícitamente (reemplazada por 'segmento').
        def car(name, marca, tipo, electrico, hibrido, combustible, origen, lujo,
                puertas, traccion, transmision, anio, precio, segmento):
            return {
                "name": name, "marca": marca, "tipo": tipo, "electrico": electrico,
                "hibrido": hibrido, "combustible": combustible, "origen": origen,
                "lujo": lujo, "puertas": puertas, "traccion": traccion,
                "transmision": transmision, "anio": anio, "precio": precio,
                "segmento": segmento
            }

        self.cars = [
            car("Toyota Corolla","Toyota","sedan",False,False,"gasolina","japonesa",False,"4","delantera","automatica","2021+","medio","compacto"),
            car("Toyota Camry","Toyota","sedan",False,False,"gasolina","japonesa",False,"4","delantera","automatica","2021+","medio","mediano"),
            car("Toyota Prius","Toyota","hatchback",False,True,"hibrido","japonesa",False,"5","delantera","cvt","2021+","medio","compacto"),
            car("Toyota RAV4","Toyota","suv",False,False,"gasolina","japonesa",False,"5","AWD","automatica","2021+","medio","SUV/Crossover"),
            car("Honda Civic","Honda","sedan",False,False,"gasolina","japonesa",False,"4","delantera","automatica","2021+","medio","compacto"),
            car("Honda CR-V","Honda","suv",False,False,"gasolina","japonesa",False,"5","AWD","automatica","2021+","medio","SUV/Crossover"),
            car("Ford F-150","Ford","pickup",False,False,"gasolina","americana",False,"4","4x4","automatica","2021+","medio","Pickup"),
            car("Ford Mustang","Ford","coupe",False,False,"gasolina","americana",False,"2","trasera","manual","2021+","premium","Deportivo"),
            car("Tesla Model 3","Tesla","sedan",True,False,"electrico","americana",True,"4","AWD","automatica","2021+","premium","mediano"),
            car("Tesla Model Y","Tesla","crossover",True,False,"electrico","americana",True,"5","AWD","automatica","2021+","premium","SUV/Crossover"),
            car("BMW Serie 3","BMW","sedan",False,False,"gasolina","europea",True,"4","trasera","automatica","2021+","premium","mediano"),
            car("BMW X5","BMW","suv",False,False,"gasolina","europea",True,"5","AWD","automatica","2016-2020","lujo","SUV/Crossover"),
            car("Audi A4","Audi","sedan",False,False,"gasolina","europea",True,"4","AWD","automatica","2021+","premium","mediano"),
            car("Audi Q5","Audi","suv",False,False,"gasolina","europea",True,"5","AWD","automatica","2021+","premium","SUV/Crossover"),
            car("Mercedes Clase C","Mercedes","sedan",False,False,"gasolina","europea",True,"4","trasera","automatica","2021+","lujo","mediano"),
            car("Volkswagen Golf","Volkswagen","hatchback",False,False,"gasolina","europea",False,"5","delantera","manual","2016-2020","medio","compacto"),
            car("Volkswagen Jetta","Volkswagen","sedan",False,False,"gasolina","europea",False,"4","delantera","automatica","2021+","medio","compacto"),
            car("Volkswagen Tiguan","Volkswagen","suv",False,False,"gasolina","europea",False,"5","AWD","automatica","2021+","medio","SUV/Crossover"),
            car("Nissan Leaf","Nissan","hatchback",True,False,"electrico","japonesa",False,"5","delantera","automatica","2016-2020","medio","compacto"),
            car("Nissan Sentra","Nissan","sedan",False,False,"gasolina","japonesa",False,"4","delantera","cvt","2021+","medio","compacto"),
            car("Mazda 3 Hatch","Mazda","hatchback",False,False,"gasolina","japonesa",False,"5","delantera","automatica","2021+","medio","compacto"),
            car("Mazda MX-5 Miata","Mazda","convertible",False,False,"gasolina","japonesa",False,"2","trasera","manual","2016-2020","premium","Deportivo"),
            car("Kia Sportage","Kia","suv",False,False,"gasolina","coreana",False,"5","delantera","automatica","2021+","medio","SUV/Crossover"),
            car("Kia Rio","Kia","sedan",False,False,"gasolina","coreana",False,"4","delantera","manual","2016-2020","economico","subcompacto"),
            car("Hyundai Tucson","Hyundai","suv",False,False,"gasolina","coreana",False,"5","delantera","automatica","2021+","medio","SUV/Crossover"),
            car("Hyundai Elantra","Hyundai","sedan",False,False,"gasolina","coreana",False,"4","delantera","cvt","2021+","medio","compacto"),
            car("Chevrolet Suburban","Chevrolet","suv",False,False,"gasolina","americana",False,"5","4x4","automatica","2016-2020","premium","grande"),
            car("Chevrolet Onix","Chevrolet","sedan",False,False,"gasolina","americana",False,"4","delantera","manual","2016-2020","economico","subcompacto"),
            car("Jeep Wrangler","Jeep","suv",False,False,"gasolina","americana",False,"4","4x4","automatica","2021+","medio","SUV/Crossover"),
            car("Porsche 911","Porsche","coupe",False,False,"gasolina","europea",True,"2","trasera","dct","2021+","lujo","Deportivo"),
            car("BYD Atto 3","BYD","suv",True,False,"electrico","china",False,"5","delantera","automatica","2021+","medio","SUV/Crossover"),
            car("Subaru Outback","Subaru","crossover",False,False,"gasolina","japonesa",False,"5","AWD","automatica","2016-2020","medio","SUV/Crossover"),
            car("Renault Duster","Renault","suv",False,False,"gasolina","europea",False,"5","delantera","manual","2016-2020","economico","SUV/Crossover"),
            car("Peugeot 208","Peugeot","hatchback",False,False,"gasolina","europea",False,"5","delantera","manual","2016-2020","economico","subcompacto"),
            car("Dodge Charger","Dodge","sedan",False,False,"gasolina","americana",False,"4","trasera","automatica","2016-2020","premium","grande"),
            car("Mercedes G-Class","Mercedes","suv",False,False,"gasolina","europea",True,"5","4x4","automatica","2016-2020","lujo","SUV/Crossover"),
            car("Toyota Hilux","Toyota","pickup",False,False,"diesel","japonesa",False,"4","4x4","manual","2016-2020","medio","Pickup"),
            car("Ford Ranger","Ford","pickup",False,False,"diesel","americana",False,"4","4x4","manual","2016-2020","medio","Pickup"),
            car("BMW i3","BMW","hatchback",True,False,"electrico","europea",True,"4","trasera","automatica","2011-2015","premium","compacto"),
            car("Toyota Land Cruiser","Toyota","suv",False,False,"gasolina","japonesa",True,"5","4x4","automatica","2011-2015","lujo","SUV/Crossover"),
        ]

    def _upgrade_schema(self) -> bool:
        """
        MIGRA cada coche al esquema actual. Llena campos faltantes y normaliza.
        Devuelve True si hubo cambios (para luego guardar).
        """
        changed = False
        for car in self.cars:
            # Normalizaciones rápidas
            if "puertas" in car and isinstance(car["puertas"], int):
                car["puertas"] = str(car["puertas"]); changed = True

            # name/marca mínimos para no romper UI
            if "name" not in car:
                car["name"] = car.get("marca", "Auto"); changed = True
            if "marca" not in car or not car["marca"]:
                nm = car.get("name", "")
                car["marca"] = nm.split()[0] if nm else "Marca"; changed = True

            # Banderas y combustible coherentes
            if "electrico" not in car:
                car["electrico"] = False; changed = True
            if "hibrido" not in car:
                car["hibrido"] = True if car.get("combustible") == "hibrido" else False; changed = True
            if "combustible" not in car or not car["combustible"]:
                if car.get("electrico"): car["combustible"] = "electrico"
                elif car.get("hibrido"): car["combustible"] = "hibrido"
                else: car["combustible"] = "gasolina"
                changed = True

            # Otros por defecto sensatos (evitan None/clave faltante)
            if "origen" not in car or not car["origen"]:
                car["origen"] = "americana"; changed = True
            if "lujo" not in car:
                car["lujo"] = False; changed = True
            if "puertas" not in car or not car["puertas"]:
                car["puertas"] = "2" if car.get("tipo") in {"coupe","convertible"} else "4"; changed = True
            if "traccion" not in car or not car["traccion"]:
                car["traccion"] = "4x4" if car.get("traccion4x4") else "delantera"; changed = True
            if "transmision" not in car or not car["transmision"]:
                car["transmision"] = "automatica"; changed = True
            if "anio" not in car or not car["anio"]:
                car["anio"] = "2016-2020"; changed = True
            if "precio" not in car or not car["precio"]:
                car["precio"] = "medio"; changed = True

            # Nuevo campo: segmento (si no viene, lo infiero de tipo/precio)
            if "segmento" not in car or not car["segmento"]:
                t = (car.get("tipo") or "").lower()
                if t in {"suv","crossover"}: seg = "SUV/Crossover"
                elif t == "pickup": seg = "Pickup"
                elif t in {"coupe","convertible"}: seg = "Deportivo"
                else:
                    p = car.get("precio","medio")
                    seg = {"economico":"subcompacto","medio":"compacto","premium":"mediano","lujo":"grande"}.get(p,"compacto")
                car["segmento"] = seg; changed = True

        return changed

    # --- Búsquedas (coincidencia exacta o por puntaje) ---
    def candidatos_exactos(self, respuestas: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Devuelve autos que coinciden EXACTO con todas las respuestas no vacías.
        """
        outs = []
        for c in self.cars:
            ok = True
            for k, v in respuestas.items():
                if v in ("", None):   # si no respondí esa, la ignoro
                    continue
                if k not in c:        # si el coche no trae ese campo, lo ignoro
                    continue
                if c[k] != v:         # si no coincide, descarto
                    ok = False
                    break
            if ok:
                outs.append(c)
        return outs

    def mejor_coincidencia(self, respuestas: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], int]:
        """
        Si no hay exactos, me quedo con el que MÁS coincide (score mayor).
        Devuelvo (coche, puntos_coincidencia).
        """
        best, score = None, -1
        for c in self.cars:
            s = 0
            for k, v in respuestas.items():
                if v in ("", None):
                    continue
                if k in c and c[k] == v:
                    s += 1
            if s > score:
                best, score = c, s
        return best, score

    def aprender(self, nombre: str, respuestas: Dict[str, Any]) -> None:
        """
        Si no acerté, uso esto para guardar/actualizar un auto nuevo.
        - Si ya existía por nombre, actualizo campos.
        - Si no, lo creo con los valores actuales.
        """
        if not nombre.strip():
            return

        # Actualizo si ya existe (case-insensitive)
        for car in self.cars:
            if car["name"].lower() == nombre.strip().lower():
                car.update({k: v for k, v in respuestas.items() if v not in ("", None)})
                if "marca" not in car or not car["marca"]:
                    car["marca"] = nombre.strip().split()[0]  # infiero marca del nombre
                self.guardar()
                return

        # Nuevo coche
        nuevo = {"name": nombre.strip(), "marca": nombre.strip().split()[0]}
        for a in self.attributes:
            k = a["key"]
            nuevo[k] = respuestas.get(k, "")
        self.cars.append(nuevo)
        self.guardar()


# ============================ CAPA DE UI (TKINTER) =============================
class LearnDialog(tk.Toplevel):
    """
    Ventana modal para guardar el auto correcto cuando el programa no acierta.
    """

    def __init__(self, parent, db: CarDB, respuestas: Dict[str, Any], guess: Optional[str] = None):
        super().__init__(parent)
        self.title("Aprender nuevo auto")
        self.db = db
        self.respuestas = respuestas
        self.resizable(False, False)

        frm = ttk.Frame(self, padding=16)
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="No acerté 😅 ¿Cuál es el auto correcto?",
                  style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0,12))
        ttk.Label(frm, text="Nombre (Marca y Modelo):").grid(row=1, column=0, sticky="w")
        self.ent_nombre = ttk.Entry(frm, width=40)
        self.ent_nombre.grid(row=1, column=1, sticky="ew", pady=6)
        if guess:
            self.ent_nombre.insert(0, guess)  # idea: prellenar con el más cercano

        # Muestra rápida de lo que respondí (para revisar antes de guardar)
        row = 2
        for a in self.db.attributes:
            k = a["key"]
            ttk.Label(frm, text=a["pregunta"] + ":").grid(row=row, column=0, sticky="w")
            val = self.respuestas.get(k, "")
            if a.get("tipo") == "bool":
                val = "Sí" if val is True else ("No" if val is False else "")
            ttk.Label(frm, text=str(val)).grid(row=row, column=1, sticky="w")
            row += 1

        # Botones
        btns = ttk.Frame(frm)
        btns.grid(row=row, column=0, columnspan=2, pady=(12,0))
        ttk.Button(btns, text="Guardar", command=self._guardar).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text="Cancelar", command=self.destroy).grid(row=0, column=1, padx=6)

        self.grab_set()
        self.ent_nombre.focus()

    def _guardar(self):
        nombre = self.ent_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Aprender", "Escribe el nombre del auto.")
            return
        self.db.aprender(nombre, self.respuestas)
        messagebox.showinfo("Aprender", f"¡Guardado!\nAprendí: {nombre}")
        self.destroy()


class App(tk.Tk):
    """
    Ventana principal: controla el flujo de preguntas y la lógica de adivinar.
    """

    def __init__(self, db: CarDB):
        super().__init__()
        self.db = db
        self.title("Adivina Quién — Carros 🚗")
        self.geometry("820x580")

        # Estado del cuestionario (índice 0..N-1 y las respuestas dadas)
        self.attr_index = 0
        self.respuestas: Dict[str, Any] = {}

        self._create_styles()
        self._build_ui()
        self._show_current_question()

    # Estilos mínimos (lo dejo simple y limpio)
    def _create_styles(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        style.configure("Accent.TButton", padding=8)

    # Construcción de la interfaz
    def _build_ui(self):
        # Header con título y contador Paso X/12
        self.header = ttk.Frame(self, padding=(16,12))
        self.header.pack(fill="x")
        self.lbl_title = ttk.Label(self.header, text="Adivina Quién — Carros", style="Title.TLabel")
        self.lbl_title.pack(side="left")
        self.lbl_step = ttk.Label(self.header, text="Paso 1/12", style="Subtitle.TLabel")
        self.lbl_step.pack(side="right")

        # Tarjeta central
        self.card = ttk.Frame(self, padding=20)
        self.card.pack(fill="both", expand=True, padx=16, pady=10)

        # Barra de progreso (de 0 a total)
        self.progress = ttk.Progressbar(self.card, mode="determinate")
        self.progress.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0,12))

        # Título de la pregunta actual
        self.lbl_q = ttk.Label(self.card, text="", style="Title.TLabel")
        self.lbl_q.grid(row=1, column=0, columnspan=3, sticky="w", pady=(4,12))

        # Controles (se regeneran por pregunta)
        self.frm_ctrls = ttk.Frame(self.card, padding=(0,6))
        self.frm_ctrls.grid(row=2, column=0, columnspan=3, sticky="w")

        # Botones navegación
        self.btn_back = ttk.Button(self.card, text="⬅ Atrás", command=self._back)
        self.btn_skip = ttk.Button(self.card, text="Saltar", command=self._skip)
        self.btn_next = ttk.Button(self.card, text="Siguiente ➡",
                                   style="Accent.TButton", command=self._next_from_controls)
        self.btn_back.grid(row=3, column=0, sticky="w", pady=10)
        self.btn_skip.grid(row=3, column=1, sticky="w", pady=10)
        self.btn_next.grid(row=3, column=2, sticky="e", pady=10)

        # Barra inferior con acciones rápidas
        self.bottom = ttk.Frame(self, padding=(16,8))
        self.bottom.pack(fill="x")
        ttk.Button(self.bottom, text="🎯 Adivinar ahora", style="Accent.TButton",
                   command=self._adivinar).pack(side="left", padx=6)
        ttk.Button(self.bottom, text="➕ Aprender este auto",
                   command=self._aprender_directo).pack(side="left", padx=6)
        ttk.Button(self.bottom, text="🔄 Reiniciar",
                   command=self._reiniciar).pack(side="left", padx=6)

        # Layout flexible
        for col in (0, 1, 2):
            self.card.grid_columnconfigure(col, weight=1)
        self.card.grid_rowconfigure(2, weight=1)

    # Helpers de flujo
    def _current_attr(self) -> Optional[Dict[str, Any]]:
        """Devuelvo el dict de la pregunta actual (o None si ya acabé)."""
        if 0 <= self.attr_index < len(self.db.attributes):
            return self.db.attributes[self.attr_index]
        return None

    def _update_progress(self):
        """
        Actualizo texto "Paso X/12" y el valor de la barra de progreso.
        Lógica: mientras estoy en pregunta i (0-based), muestro Paso i+1.
        Al terminar todas, muestro Paso total/total y barra llena.
        """
        total = len(self.db.attributes)
        on_attr = self._current_attr() is not None
        paso = (self.attr_index + 1) if on_attr else total
        self.lbl_step.config(text=f"Paso {paso}/{total}")
        self.progress["maximum"] = total
        # La barra refleja preguntas YA contestadas (0..total)
        self.progress["value"] = self.attr_index if on_attr else total

    def _show_current_question(self):
        """Redibujo la pregunta actual (controles) o muestro resumen si ya no hay preguntas."""
        # Borro controles anteriores
        for w in self.frm_ctrls.winfo_children():
            w.destroy()

        attr = self._current_attr()
        self._update_progress()

        if not attr:
            # Ya contesté todo: enseño resumen para confirmar antes de adivinar
            self._show_summary()
            return

        # Texto de la pregunta
        self.lbl_q.config(text=attr["pregunta"])

        # Dependiendo del tipo, muestro botones Sí/No o un combobox
        if attr.get("tipo") == "bool":
            ttk.Button(self.frm_ctrls, text="Sí", style="Accent.TButton",
                       command=lambda: self._answer(attr["key"], True)).grid(row=0, column=0, padx=6, pady=6, sticky="w")
            ttk.Button(self.frm_ctrls, text="No",
                       command=lambda: self._answer(attr["key"], False)).grid(row=0, column=1, padx=6, pady=6, sticky="w")
            self.btn_next.state(["disabled"])  # no hace falta "Siguiente" aquí
        elif "opciones" in attr:
            self.combo = ttk.Combobox(self.frm_ctrls, state="readonly",
                                      values=[""] + attr["opciones"], width=26)
            self.combo.current(0)
            self.combo.grid(row=0, column=0, padx=6, pady=6, sticky="w")
            self.btn_next.state(["!disabled"])
        else:
            # Entrada libre (no la uso casi, pero la dejo por si extiendo)
            self.entry = ttk.Entry(self.frm_ctrls, width=28)
            self.entry.grid(row=0, column=0, padx=6, pady=6, sticky="w")
            self.btn_next.state(["!disabled"])

        # El botón Atrás solo se habilita si no estoy en la primera
        if self.attr_index == 0:
            self.btn_back.state(["disabled"])
        else:
            self.btn_back.state(["!disabled"])

        # El botón Saltar siempre disponible (deja la respuesta vacía)
        self.btn_skip.state(["!disabled"])
        self.btn_next.config(text="Siguiente ➡")

    # Resumen previo a adivinar (para que pueda revisar)
    def _show_summary(self):
        for w in self.frm_ctrls.winfo_children():
            w.destroy()
        self.lbl_q.config(text="Resumen de tus respuestas (confirma antes de adivinar)")

        text = tk.Text(self.frm_ctrls, width=70, height=12)
        text.grid(row=0, column=0, columnspan=3, sticky="nsew")
        text.insert("end", self._build_summary_text())
        text.config(state="disabled")

        # Aquí sí puedo regresar a corregir algo, o pasar a adivinar
        self.btn_back.state(["!disabled"])
        self.btn_skip.state(["disabled"])
        self.btn_next.state(["!disabled"])
        self.btn_next.config(text="Adivinar ➡", command=self._adivinar)

    def _build_summary_text(self) -> str:
        """Armo un texto legible con cada pregunta y mi respuesta."""
        lines = []
        for a in self.db.attributes:
            k = a["key"]
            label = a["pregunta"]
            v = self.respuestas.get(k, "")
            if a.get("tipo") == "bool":
                if v is True:
                    vtxt = "Sí"
                elif v is False:
                    vtxt = "No"
                else:
                    vtxt = "—"
            else:
                vtxt = v if v else "—"
            lines.append(f"• {label}: {vtxt}")
        return "\n".join(lines)

    # Guardado de respuesta y avanzar
    def _answer(self, key: str, value: Any):
        self.respuestas[key] = value
        self.attr_index += 1
        self._show_current_question()

    # Leer control (combo/entry) y avanzar
    def _next_from_controls(self):
        attr = self._current_attr()
        if not attr:
            return
        val = ""
        if hasattr(self, "combo"):
            val = (self.combo.get() or "").strip()
        elif hasattr(self, "entry"):
            val = (self.entry.get() or "").strip()
        self._answer(attr["key"], val)

    # Dejar pregunta sin responder y avanzar
    def _skip(self):
        attr = self._current_attr()
        if not attr:
            return
        self._answer(attr["key"], "")

    # Retroceder una pregunta (borro la respuesta para re-contestar)
    def _back(self):
        if self.attr_index > 0:
            self.attr_index -= 1
            key = self.db.attributes[self.attr_index]["key"]
            if key in self.respuestas:
                del self.respuestas[key]
            self._show_current_question()

    # ========= Lógica de adivinar / aprender =========
    def _adivinar(self):
        """
        1) Intento coincidencia EXACTA: si solo hay una, pregunto si es esa.
        2) Si hay varias exactas, aviso para refinar respuestas o aprender.
        3) Si no hay exactas, propongo la MEJOR COINCIDENCIA (por puntaje).
        4) Si falla, ofrezco aprender el auto.
        """
        exactos = self.db.candidatos_exactos(self.respuestas)
        if len(exactos) == 1:
            name = exactos[0].get("name", "—")
            if messagebox.askyesno("¿Es este?", f"Creo que es: {name}\n\n¿Acerté?"):
                messagebox.showinfo("¡Adiviné!", "🎯 ¡Excelente!")
                return
            self._adivinar_fallido(nombre_propuesto=name)
            return

        if len(exactos) > 1:
            messagebox.showinfo(
                "Varias opciones",
                "Hay varias coincidencias exactas. Puedes regresar y refinar tus respuestas "
                "o pulsar «Aprender este auto» si quieres guardarlo ya."
            )
            return

        best, score = self.db.mejor_coincidencia(self.respuestas)
        if best and score > 0:
            name = best.get("name", "—")
            if messagebox.askyesno("Tal vez sea…", f"No hay coincidencia perfecta, pero podría ser: {name}.\n\n¿Acerté?"):
                messagebox.showinfo("¡Adiviné!", "🎯 ¡Bien por aproximación!")
                return
            self._adivinar_fallido(nombre_propuesto=name)
        else:
            self._adivinar_fallido()

    def _adivinar_fallido(self, nombre_propuesto: Optional[str] = None):
        """Modal para enseñar el auto correcto y que el programa lo aprenda."""
        if messagebox.askyesno("Aprender", "No acerté 😅 ¿Quieres enseñarme ese auto para recordarlo la próxima?"):
            dlg = LearnDialog(self, self.db, self.respuestas, guess=nombre_propuesto)
            self.wait_window(dlg)

    def _aprender_directo(self):
        """Atajo si quiero guardar el auto sin pasar por 'adivinar'."""
        dlg = LearnDialog(self, self.db, self.respuestas)
        self.wait_window(dlg)

    def _reiniciar(self):
        """Reinicio el flujo de preguntas desde cero."""
        self.attr_index = 0
        self.respuestas = {}
        self._show_current_question()


# ============================ PUNTO DE ENTRADA =================================
def main():
    db = CarDB(DB_PATH)
    db.cargar()   
    app = App(db)
    app.mainloop()

if __name__ == "__main__":
    main()
