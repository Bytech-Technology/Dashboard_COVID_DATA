from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from ui.kpi_widget import KPIWidget
from ui.mpl_canvas import MplCanvas
from ui.table_model import PandasModel


class BentoWindow(QtWidgets.QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.df = df.copy()
        self.setWindowTitle("Dashboard COVID-19")
        self.resize(1300, 850)

        # === Layout base ===
        self._central = QtWidgets.QWidget()
        self.setCentralWidget(self._central)
        self.main_layout = QtWidgets.QVBoxLayout(self._central)

        # === Inicialización modular ===
        self._init_theme_icons()
        self._init_top_controls()
        self._init_kpi_section()
        self._init_body_layout()

        # === Estado inicial ===
        self.current_theme = "light"
        self.update_kpis()
        self.populate_table()
        self.draw_charts()
        self.set_theme("light")

    # ----------------------------------------------------------------
    # Inicialización de secciones
    # ----------------------------------------------------------------
    def _init_theme_icons(self):
        """Crea los iconos para cambiar tema"""
        self.theme_dark_icon = self._create_icon_button("assets/dark_icon.png", lambda: self.set_theme("dark"))
        self.theme_light_icon = self._create_icon_button("assets/light_icon.png", lambda: self.set_theme("light"))

        icon_layout = QtWidgets.QHBoxLayout()
        icon_layout.addStretch()
        icon_layout.addWidget(self.theme_light_icon)
        icon_layout.addWidget(self.theme_dark_icon)
        self.main_layout.insertLayout(0, icon_layout)

    def _create_icon_button(self, path, on_click):
        btn = QtWidgets.QPushButton()
        btn.setIcon(QtGui.QIcon(path))
        btn.setFixedSize(32, 32)
        btn.setIconSize(QtCore.QSize(32, 32))
        btn.setFlat(True)
        btn.clicked.connect(on_click)
        return btn

    def _init_top_controls(self):
        """Selector de país"""
        top_controls = QtWidgets.QHBoxLayout()
        top_controls.addStretch()

        self.lbl_select_country = QtWidgets.QLabel("Seleccionar país:")
        self.combo_country = QtWidgets.QComboBox()
        countries = sorted(self.df["Country/Region"].astype(str).unique().tolist())
        self.combo_country.addItem("")
        self.combo_country.addItems(countries)
        self.combo_country.currentTextChanged.connect(self.on_country_changed)

        top_controls.addWidget(self.lbl_select_country)
        top_controls.addWidget(self.combo_country)
        top_controls.addStretch()
        self.main_layout.addLayout(top_controls)

    def _init_kpi_section(self):
        """Crea las tarjetas KPI"""
        kpi_layout = QtWidgets.QHBoxLayout()
        kpi_layout.setSpacing(12)
        kpi_layout.addStretch()
        self.kpis = {k: KPIWidget(k) for k in ["Confirmed", "Deaths", "Recovered", "Active"]}
        for w in self.kpis.values():
            kpi_layout.addWidget(w)
        kpi_layout.addStretch()
        self.main_layout.addLayout(kpi_layout)

    def _init_body_layout(self):
        """Tabla + gráficos con divisor redimensionable"""
        splitter = QtWidgets.QSplitter(Qt.Horizontal)

        # --- Tabla ---
        self.table_view = QtWidgets.QTableView()
        table_card = self._card_container("Data Table", self.table_view)

        # --- Panel derecho (gráficos) ---
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setSpacing(12)
        self.canvas_top = MplCanvas(width=6, height=3)
        self.canvas_bottom = MplCanvas(width=6, height=3)
        right_layout.addWidget(self._card_container("Top 10 Countries - Confirmed", self.canvas_top))
        right_layout.addWidget(self._card_container("Top 10 Countries - Deaths", self.canvas_bottom))

        # --- Agregar al splitter ---
        splitter.addWidget(table_card)
        splitter.addWidget(right_widget)

        splitter.setSizes([400, 800])  # tamaño inicial relativo
        splitter.setHandleWidth(4)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: transparent;
            }
            QSplitter::handle:hover {
                background-color: rgba(0,0,0,0.1);
            }
        """)

        self.main_layout.addWidget(splitter)


    # ----------------------------------------------------------------
    # Layouts auxiliares
    # ----------------------------------------------------------------
    def _card_container(self, title, widget):
        frame = QtWidgets.QFrame(objectName="card")
        v = QtWidgets.QVBoxLayout(frame)
        lbl = QtWidgets.QLabel(title, objectName="cardTitle")
        v.addWidget(lbl)
        v.addWidget(widget)
        return frame

    # ----------------------------------------------------------------
    # KPI
    # ----------------------------------------------------------------
    def update_kpis(self, country=None):
        df = self.df
        if country and country.strip():
            df = df[df["Country/Region"] == country]
        vals = {k: int(df[k].sum()) if not df.empty else 0 for k in self.kpis.keys()}
        for k, w in self.kpis.items():
            w.set_value(vals[k])

    # ----------------------------------------------------------------
    # Gráficos
    # ----------------------------------------------------------------
    def draw_charts(self, highlight_country=None):
        is_dark = self.current_theme == "dark"
        colors = {
            "confirmed": "#7ec0ff" if is_dark else "#4a90e2",
            "deaths": "#ff9999" if is_dark else "#ff6b6b",
            "text": "white" if is_dark else "black",
            "bg": "#2c2c2c" if is_dark else "white",
        }

        self._draw_chart(self.canvas_top, "Confirmed", colors["confirmed"], colors)
        self._draw_chart(self.canvas_bottom, "Deaths", colors["deaths"], colors)

    def _draw_chart(self, canvas, column, color, colors):
        ax = canvas.axes
        fig = canvas.figure
        fig.patch.set_facecolor(colors["bg"])
        ax.set_facecolor(colors["bg"])
        ax.clear()
        self._style_axes(ax)

        top_data = self.df.sort_values(column, ascending=False).head(10)
        ax.barh(top_data["Country/Region"], top_data[column], color=color)
        ax.set_title(f"Top 10 - {column}", fontsize=14, fontweight="bold", color=colors["text"])
        ax.tick_params(axis="x", labelsize=10, colors=colors["text"])
        ax.tick_params(axis="y", labelsize=8, colors=colors["text"])
        ax.grid(axis="x", linestyle="--", alpha=0.3, color="gray" if colors["bg"] == "#2c2c2c" else "black")
        canvas.draw()

    def _style_axes(self, ax):
        for side in ["top", "right", "bottom", "left"]:
            ax.spines[side].set_linewidth(0)

    # ----------------------------------------------------------------
    # Tabla
    # ----------------------------------------------------------------
    def populate_table(self):
        cols = ["Country/Region", "Confirmed", "Deaths", "Recovered", "Active"]
        dfv = self.df[cols].sort_values("Confirmed", ascending=False).reset_index(drop=True)
        model = PandasModel(dfv)
        self.table_view.setModel(model)
        self.table_view.setSortingEnabled(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.verticalHeader().setVisible(False)
        header = self.table_view.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        
        for i in range(header.count()):
            header.setDefaultAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

    # ----------------------------------------------------------------
    # Eventos y temas
    # ----------------------------------------------------------------
    def on_country_changed(self, text):
        self.update_kpis(text if text else None)
        self.draw_charts(text if text else None)

    def set_theme(self, mode):
        """Aplica el modo de tema (oscuro o claro)"""
        self.current_theme = mode

        themes = {
            "dark": {
                "bg_main": "#1e1e1e",
                "bg_card": "#2c2c2c",
                "text": "white",
                "kpi_val": "#4ac1ff",
                "table_bg": "#2c2c2c",
                "table_grid": "#444",
                "header_bg": "#3a3a3a",
            },
            "light": {
                "bg_main": "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #e6f0ff, stop:1 #f3f7ff)",
                "bg_card": "white",
                "text": "#234b8a",
                "kpi_val": "#0b51a1",
                "table_bg": "white",
                "table_grid": "#eee",
                "header_bg": "#f4f7ff",
            },
        }[mode]

        self.setStyleSheet(f"""
            QMainWindow {{ background: {themes['bg_main']}; }}
            #card {{ background: {themes['bg_card']}; border-radius: 10px; padding: 10px; color: {themes['text']}; }}
            #kpiCard {{ background: transparent; border: none; }}
            #kpiTitle {{ color: {themes['text']}; font-weight:600; }}
            #kpiValue {{ font-size: 20px; font-weight: 700; color: {themes['kpi_val']}; }}
            QLabel#cardTitle {{ font-size:14px; font-weight:600; color: {themes['text']}; margin-bottom:6px; }}
            QTableView {{ background: {themes['table_bg']}; color: {themes['text']}; border: none; gridline-color: {themes['table_grid']}; }}
            QHeaderView::section {{ background: {themes['header_bg']}; color: {themes['text']}; padding:6px; border: none; }}
            QComboBox {{ padding: 4px; min-width: 180px; color: {themes['text']}; border-radius:4px; background: {themes['bg_card']}; border: 1px solid {themes['table_grid']}; }}
        """)

        self.lbl_select_country.setStyleSheet(f"color: {themes['text']}; font-weight:600;")
        self.theme_dark_icon.setVisible(mode != "dark")
        self.theme_light_icon.setVisible(mode == "dark")
        self.draw_charts()
