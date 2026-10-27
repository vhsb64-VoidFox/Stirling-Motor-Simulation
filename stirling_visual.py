import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import numpy as np

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# ==========================================
# CONSTANTE UNIVERSAL
# ==========================================

R = 8.314

# ==========================================
# CLASE PRINCIPAL
# ==========================================

class StirlingSimulator:

    def __init__(self, root):

        self.root = root

        self.root.title("Simulador Motor Stirling")

        self.root.geometry("1800x900")

        self.root.configure(bg="#1e1e1e")

        # ==========================================
        # GASES
        # ==========================================

        self.gases = {
            "Aire": 0.02897,
            "Helio": 0.0040026,
            "Hidrogeno": 0.002016
        }

        # ==========================================
        # VARIABLES ANIMACIÓN
        # ==========================================

        self.angle = 0
        self.animation_speed = 0.05

        self.create_ui()

        self.animate()

    # ==========================================
    # INTERFAZ
    # ==========================================

    def create_ui(self):

        # ==========================================
        # PANEL IZQUIERDO
        # ==========================================

        left_frame = tk.Frame(
            self.root,
            bg="#252526",
            width=420
        )

        left_frame.pack(
            side="left",
            fill="y"
        )

        title = tk.Label(
            left_frame,
            text="SIMULADOR\nMOTOR STIRLING",
            bg="#252526",
            fg="white",
            font=("Arial", 20, "bold")
        )

        title.pack(pady=20)

        self.entries = {}

        fields = [
            ("Temperatura caliente Th (K)", "800"),
            ("Temperatura fría Tc (K)", "300"),
            ("Número de moles n", "1"),
            ("Volumen mínimo Vmin (m³)", "0.002"),
            ("Volumen máximo Vmax (m³)", "0.02")
        ]

        for label_text, default in fields:

            label = tk.Label(
                left_frame,
                text=label_text,
                bg="#252526",
                fg="white",
                font=("Arial", 11)
            )

            label.pack(
                anchor="w",
                padx=20,
                pady=(10, 2)
            )

            entry = tk.Entry(
                left_frame,
                font=("Arial", 11),
                width=24
            )

            entry.insert(0, default)

            entry.pack(padx=20)

            self.entries[label_text] = entry

        # ==========================================
        # SELECTOR DE GAS
        # ==========================================

        gas_label = tk.Label(
            left_frame,
            text="Tipo de gas",
            bg="#252526",
            fg="white",
            font=("Arial", 11)
        )

        gas_label.pack(
            anchor="w",
            padx=20,
            pady=(10, 2)
        )

        self.gas_var = tk.StringVar()

        self.gas_var.set("Aire")

        gas_menu = ttk.Combobox(
            left_frame,
            textvariable=self.gas_var,
            values=list(self.gases.keys()),
            state="readonly",
            width=20
        )

        gas_menu.pack(padx=20)

        # ==========================================
        # BOTÓN
        # ==========================================

        simulate_button = tk.Button(
            left_frame,
            text="CALCULAR SIMULACIÓN",
            bg="#007acc",
            fg="white",
            font=("Arial", 12, "bold"),
            relief="flat",
            padx=10,
            pady=10,
            command=self.simular
        )

        simulate_button.pack(pady=25)

        # ==========================================
        # RESULTADOS
        # ==========================================

        results_frame = tk.Frame(
            left_frame,
            bg="#252526"
        )

        results_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        scrollbar = tk.Scrollbar(results_frame)

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.results_box = tk.Text(
            results_frame,
            height=30,
            width=48,
            bg="#1e1e1e",
            fg="#00ff99",
            font=("Consolas", 10),
            yscrollcommand=scrollbar.set
        )

        self.results_box.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.config(
            command=self.results_box.yview
        )

        # ==========================================
        # PANEL CENTRAL
        # ==========================================

        center_frame = tk.Frame(
            self.root,
            bg="#1e1e1e"
        )

        center_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.canvas = tk.Canvas(
            center_frame,
            width=700,
            height=850,
            bg="#111111",
            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        # ==========================================
        # PANEL DERECHO
        # ==========================================

        right_frame = tk.Frame(
            self.root,
            bg="#1e1e1e"
        )

        right_frame.pack(
            side="right",
            fill="both",
            expand=True
        )

        self.figure = Figure(
            figsize=(7, 6),
            dpi=100
        )

        self.ax = self.figure.add_subplot(111)

        self.graph = FigureCanvasTkAgg(
            self.figure,
            master=right_frame
        )

        self.graph.get_tk_widget().pack(
            fill="both",
            expand=True
        )

    # ==========================================
    # SIMULACIÓN
    # ==========================================

    def simular(self):

        try:

            Th = float(
                self.entries["Temperatura caliente Th (K)"].get()
            )

            Tc = float(
                self.entries["Temperatura fría Tc (K)"].get()
            )

            n = float(
                self.entries["Número de moles n"].get()
            )

            Vmin = float(
                self.entries["Volumen mínimo Vmin (m³)"].get()
            )

            Vmax = float(
                self.entries["Volumen máximo Vmax (m³)"].get()
            )

            gas = self.gas_var.get()

            # ==========================================
            # VALIDACIONES
            # ==========================================

            if Tc >= Th:

                messagebox.showerror(
                    "Error",
                    "La temperatura caliente debe ser mayor."
                )

                return

            if Vmin >= Vmax:

                messagebox.showerror(
                    "Error",
                    "Vmax debe ser mayor que Vmin."
                )

                return

            # ==========================================
            # VELOCIDAD ANIMACIÓN
            # ==========================================

            self.animation_speed = (
                0.02
                + ((Th - Tc) / 50000)
            )

            # ==========================================
            # MASA
            # ==========================================

            masa_molar = self.gases[gas]

            masa = n * masa_molar

            # ==========================================
            # VOLUMEN MUERTO
            # ==========================================

            Vdead = 0.001

            # ==========================================
            # CICLO STIRLING
            # ==========================================

            V1 = np.linspace(Vmin, Vmax, 300)

            P_hot = (
                n * R * Th
            ) / (
                V1 + Vdead
            )

            V2 = np.linspace(Vmax, Vmin, 300)

            P_cold = (
                n * R * Tc
            ) / (
                V2 + Vdead
            )

            P_iso1 = np.linspace(
                P_hot[-1],
                P_cold[0],
                100
            )

            V_iso1 = np.full(100, Vmax)

            P_iso2 = np.linspace(
                P_cold[-1],
                P_hot[0],
                100
            )

            V_iso2 = np.full(100, Vmin)

            # ==========================================
            # TRABAJO POR INTEGRAL
            # ==========================================

            W_hot = np.trapezoid(P_hot, V1)

            W_cold = np.trapezoid(
                P_cold[::-1],
                V2[::-1]
            )

            W = W_hot - W_cold

            # ==========================================
            # CALORES
            # ==========================================

            Qh = (
                n
                * R
                * Th
                * np.log(
                    (Vmax + Vdead)
                    /
                    (Vmin + Vdead)
                )
            )

            Qc = (
                n
                * R
                * Tc
                * np.log(
                    (Vmax + Vdead)
                    /
                    (Vmin + Vdead)
                )
            )

            # ==========================================
            # EFICIENCIA
            # ==========================================

            eficiencia_ideal = 1 - (Tc / Th)

            regenerator_eff = 0.75

            mechanical_eff = 0.85

            thermal_loss = 0.90

            eficiencia_real = (
                eficiencia_ideal
                * regenerator_eff
                * mechanical_eff
                * thermal_loss
            )

            # ==========================================
            # ENTROPÍA
            # ==========================================

            deltaS_ciclo = 0

            irreversibility_factor = 0.08

            deltaS_universo = (
                irreversibility_factor
                * abs(Qh / Th)
            )

            # ==========================================
            # RPM ESTIMADAS
            # ==========================================

            rpm = (
                (Th - Tc)
                * 0.12
            )

            # ==========================================
            # POTENCIA
            # ==========================================

            power_output = (
                W
                * (rpm / 60)
            )

            # ==========================================
            # PRESIÓN MEDIA EFECTIVA
            # ==========================================

            MEP = (
                W
                / (Vmax - Vmin)
            )

            # ==========================================
            # PRESIÓN MÁXIMA
            # ==========================================

            max_pressure = np.max(P_hot)

            warning_text = ""

            if max_pressure > 5e6:

                warning_text = (
                    "\nADVERTENCIA: "
                    "presión extremadamente alta\n"
                )

            # ==========================================
            # GRÁFICA
            # ==========================================

            self.ax.clear()

            self.ax.plot(
                V1,
                P_hot,
                linewidth=3,
                label="Expansión isotérmica"
            )

            self.ax.plot(
                V_iso1,
                P_iso1,
                linewidth=3,
                label="Enfriamiento isocórico"
            )

            self.ax.plot(
                V2,
                P_cold,
                linewidth=3,
                label="Compresión isotérmica"
            )

            self.ax.plot(
                V_iso2,
                P_iso2,
                linewidth=3,
                label="Calentamiento isocórico"
            )

            # ==========================================
            # ÁREA DEL CICLO
            # ==========================================

            V_cycle = np.concatenate([
                V1,
                V_iso1,
                V2,
                V_iso2
            ])

            P_cycle = np.concatenate([
                P_hot,
                P_iso1,
                P_cold,
                P_iso2
            ])

            self.ax.fill(
                V_cycle,
                P_cycle,
                alpha=0.3,
                label="Trabajo neto del ciclo"
            )

            self.ax.set_title(
                "Diagrama P-V del Motor Stirling"
            )

            self.ax.set_xlabel(
                "Volumen (m³)"
            )

            self.ax.set_ylabel(
                "Presión (Pa)"
            )

            self.ax.grid(True)

            self.ax.legend()

            self.graph.draw()

            # ==========================================
            # RESULTADOS
            # ==========================================

            resultados = f"""
================================================

RESULTADOS DEL MOTOR STIRLING

================================================

Tipo de gas:
{gas}

Masa del gas:
{masa:.6f} kg

Número de moles:
{n:.2f}

Temperatura caliente:
{Th:.2f} K

Temperatura fría:
{Tc:.2f} K

Volumen muerto:
{Vdead:.5f} m³

Trabajo neto del ciclo:
{W:.2f} J

Calor absorbido:
{Qh:.2f} J

Calor cedido:
{Qc:.2f} J

Potencia estimada:
{power_output:.2f} W

RPM estimadas:
{rpm:.2f}

Presión media efectiva:
{MEP:.2f} Pa

Presión máxima:
{max_pressure:.2f} Pa

Eficiencia ideal:
{eficiencia_ideal*100:.2f} %

Eficiencia real estimada:
{eficiencia_real*100:.2f} %

Cambio de entropía del ciclo:
{deltaS_ciclo:.2f} J/K

Cambio de entropía del universo:
{deltaS_universo:.2f} J/K

{warning_text}

================================================
"""

            self.results_box.delete(
                "1.0",
                tk.END
            )

            self.results_box.insert(
                tk.END,
                resultados
            )

        except Exception as e:

            messagebox.showerror(
                "Error",
                str(e)
            )

    # ==========================================
    # ANIMACIÓN
    # ==========================================

    def animate(self):

        self.canvas.delete("all")

        # ==========================================
        # CENTRO DEL MOTOR
        # ==========================================

        center_x = 300

        # ==========================================
        # ÁNGULO
        # ==========================================

        theta = self.angle

        # ==========================================
        # VOLANTE SUPERIOR
        # ==========================================

        flywheel_x = center_x
        flywheel_y = 120
        flywheel_r = 80

        self.canvas.create_oval(
            flywheel_x - flywheel_r,
            flywheel_y - flywheel_r,
            flywheel_x + flywheel_r,
            flywheel_y + flywheel_r,
            outline="white",
            width=4
        )

        # EJE CENTRAL
        self.canvas.create_oval(
            flywheel_x - 15,
            flywheel_y - 15,
            flywheel_x + 15,
            flywheel_y + 15,
            fill="#444444",
            outline="black",
            width=2
        )

        # ==========================================
        # CIGÜEÑAL
        # ==========================================

        crank_radius = 55

        crank_x = (
            flywheel_x
            + crank_radius * np.cos(theta)
        )

        crank_y = (
            flywheel_y
            + crank_radius * np.sin(theta)
        )

        self.canvas.create_line(
            flywheel_x,
            flywheel_y,
            crank_x,
            crank_y,
            fill="cyan",
            width=5
        )

        # ==========================================
        # CILINDRO EXTERNO
        # ==========================================

        cylinder_x1 = 240
        cylinder_x2 = 360

        cylinder_y1 = 220
        cylinder_y2 = 720

        self.canvas.create_rectangle(
            cylinder_x1,
            cylinder_y1,
            cylinder_x2,
            cylinder_y2,
            outline="white",
            width=4
        )

        # ==========================================
        # ZONA FRÍA
        # ==========================================

        self.canvas.create_rectangle(
            cylinder_x1 + 2,
            cylinder_y1 + 2,
            cylinder_x2 - 2,
            430,
            fill="#2d5fff",
            outline=""
        )

        # ALETAS FRÍAS
        for y in range(260, 430, 30):

            self.canvas.create_line(
                cylinder_x1 - 40,
                y,
                cylinder_x1,
                y,
                fill="#2d5fff",
                width=4
            )

            self.canvas.create_line(
                cylinder_x2,
                y,
                cylinder_x2 + 40,
                y,
                fill="#2d5fff",
                width=4
            )

        # ==========================================
        # ZONA CALIENTE
        # ==========================================

        self.canvas.create_rectangle(
            cylinder_x1 + 2,
            520,
            cylinder_x2 - 2,
            cylinder_y2 - 2,
            fill="red",
            outline=""
        )

        # LLAMAS
        self.canvas.create_polygon(
            220, 760,
            240, 720,
            260, 760,
            fill="orange",
            outline=""
        )

        self.canvas.create_polygon(
            340, 760,
            360, 720,
            380, 760,
            fill="orange",
            outline=""
        )

        # ==========================================
        # DESPLAZADOR
        # ==========================================

        displacer_y = (
            430
            + 40 * np.sin(theta + np.pi / 2)
        )

        self.canvas.create_rectangle(
            255,
            displacer_y,
            345,
            displacer_y + 140,
            fill="#888888",
            outline="black",
            width=2
        )

        # ==========================================
        # PISTÓN SUPERIOR
        # ==========================================

        power_piston_y = (
            240
            + 20 * np.sin(theta)
        )

        self.canvas.create_rectangle(
            250,
            power_piston_y,
            350,
            power_piston_y + 45,
            fill="#aaaaaa",
            outline="black",
            width=2
        )

        # ==========================================
        # VARILLA CENTRAL
        # ==========================================

        rod_x = center_x

        self.canvas.create_line(
            rod_x,
            flywheel_y,
            rod_x,
            power_piston_y,
            fill="white",
            width=6
        )

        # ==========================================
        # BIELA
        # ==========================================

        self.canvas.create_line(
            crank_x,
            crank_y,
            rod_x,
            power_piston_y + 20,
            fill="yellow",
            width=5
        )

        # ==========================================
        # TEXTO CALOR
        # ==========================================

        self.canvas.create_text(
            430,
            640,
            text="Qh ENTRA",
            fill="white",
            font=("Arial", 14, "bold")
        )

        self.canvas.create_text(
            430,
            300,
            text="Qc SALE",
            fill="white",
            font=("Arial", 14, "bold")
        )

        # ==========================================
        # ACTUALIZAR ÁNGULO
        # ==========================================

        self.angle += self.animation_speed

        # ==========================================
        # LOOP
        # ==========================================

        self.root.after(
            16,
            self.animate
        )

# ==========================================
# EJECUCIÓN
# ==========================================

root = tk.Tk()

app = StirlingSimulator(root)

root.mainloop()