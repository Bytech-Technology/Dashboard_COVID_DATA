from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from ui.kpi_widget import KPIWidget
from ui.mpl_canvas import MplCanvas
from ui.table_model import PandasModel
import matplotlib.pyplot as plt


class BentoWindow(QtWidgets.QMainWindow):
    def __init__(self, df):
        super().__init__()
        self.df = df.copy()
        self.setWindowTitle("Bento Dashboard")
        self.resize(1400, 850)

        # === Layout principal ===
        self._central = QtWidgets.QWidget()
        self.setCentralWidget(self._central)
        self.grid = QtWidgets.QGridLayout(self._central)
        self.grid.setContentsMargins(20, 20, 20, 20)
        self.grid.setSpacing(18)

        # === Componentes ===
        self._init_top_panel()
        self._init_table()
        self._init_charts()

        # === Datos iniciales ===
        self.update_kpis()
        self.populate_table()
        self.draw_charts()

        # === Aplicar tema Bento ===
        self.apply_bento_theme()

        # === Ajustes proporcionales ===
        self.grid.setColumnStretch(0, 2)  # tabla 50%
        self.grid.setColumnStretch(1, 1)
        self.grid.setColumnStretch(2, 1)
        self.grid.setRowStretch(0, 2)
        self.grid.setRowStretch(1, 2)

    # ----------------------------------------------------------------
    # Panel superior (KPI + selector)
    # ----------------------------------------------------------------
    def _init_top_panel(self):
        self.top_frame = self._glass_card()
        top_layout = QtWidgets.QVBoxLayout(self.top_frame)
        top_layout.setContentsMargins(40, 40, 40, 40)
        top_layout.setSpacing(30)

        # --- Selector de país ---
        selector_layout = QtWidgets.QHBoxLayout()
        selector_layout.setSpacing(12)
        self.lbl_select_country = QtWidgets.QLabel("Seleccionar país:")
        self.lbl_select_country.setObjectName("labelTitle")
        self.combo_country = QtWidgets.QComboBox()
        countries = sorted(self.df["Country/Region"].astype(str).unique().tolist())
        self.combo_country.addItem("")
        self.combo_country.addItems(countries)
        self.combo_country.currentTextChanged.connect(self.on_country_changed)
        selector_layout.addStretch()
        selector_layout.addWidget(self.lbl_select_country)
        selector_layout.addWidget(self.combo_country)
        selector_layout.addStretch()

        # --- KPIs centradas ---
        kpi_layout = QtWidgets.QHBoxLayout()
        kpi_layout.setSpacing(40)
        kpi_layout.setContentsMargins(0, 0, 0, 0)
        kpi_layout.addStretch()
        self.kpis = {k: KPIWidget(k) for k in ["Confirmed", "Deaths", "Recovered", "Active"]}
        for w in self.kpis.values():
            w.setFixedSize(160, 100)
            kpi_layout.addWidget(w)
        kpi_layout.addStretch()

        top_layout.addLayout(selector_layout)
        top_layout.addLayout(kpi_layout)
        self.grid.addWidget(self.top_frame, 0, 1, 1, 2)

    # ----------------------------------------------------------------
    # Tabla lateral izquierda
    # ----------------------------------------------------------------
    def _init_table(self):
        self.table_frame = self._glass_card()
        table_layout = QtWidgets.QVBoxLayout(self.table_frame)
        table_layout.setContentsMargins(16, 16, 16, 16)
        table_layout.setSpacing(8)

        lbl = QtWidgets.QLabel("Tabla de Datos")
        lbl.setObjectName("cardTitle")

        self.table_view = QtWidgets.QTableView()
        self.table_view.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.table_view.horizontalScrollBar().setEnabled(False)
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table_view.setAlternatingRowColors(True)

        table_layout.addWidget(lbl)
        table_layout.addWidget(self.table_view)
        self.grid.addWidget(self.table_frame, 0, 0, 2, 1)

    # ----------------------------------------------------------------
    # Gráficos inferiores
    # ----------------------------------------------------------------
    def _init_charts(self):
        self.chart1 = self._glass_card()
        self.chart2 = self._glass_card()
        layout1 = QtWidgets.QVBoxLayout(self.chart1)
        layout2 = QtWidgets.QVBoxLayout(self.chart2)
        layout1.setContentsMargins(16, 16, 16, 16)
        layout2.setContentsMargins(16, 16, 16, 16)

        lbl1 = QtWidgets.QLabel("Top 10 Countries - Confirmed")
        lbl1.setObjectName("cardTitle")
        lbl2 = QtWidgets.QLabel("Top 10 Countries - Deaths")
        lbl2.setObjectName("cardTitle")

        self.canvas_top = MplCanvas(width=6, height=3)
        self.canvas_bottom = MplCanvas(width=6, height=3)

        layout1.addWidget(lbl1)
        layout1.addWidget(self.canvas_top)
        layout2.addWidget(lbl2)
        layout2.addWidget(self.canvas_bottom)
        self.grid.addWidget(self.chart1, 1, 1)
        self.grid.addWidget(self.chart2, 1, 2)

    # ----------------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------------
    def _glass_card(self):
        frame = QtWidgets.QFrame()
        frame.setObjectName("glassCard")
        shadow = QtWidgets.QGraphicsDropShadowEffect(
            blurRadius=30, xOffset=0, yOffset=6, color=QtGui.QColor(0, 0, 0, 180)
        )
        frame.setGraphicsEffect(shadow)
        return frame

    # ----------------------------------------------------------------
    # KPI, tabla y gráficos
    # ----------------------------------------------------------------
    def update_kpis(self, country=None):
        df = self.df
        if country and country.strip():
            df = df[df["Country/Region"] == country]
        vals = {k: int(df[k].sum()) if not df.empty else 0 for k in self.kpis.keys()}
        for k, w in self.kpis.items():
            w.set_value(vals[k])

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

    def draw_charts(self, highlight_country=None):
        colors = {
            "confirmed": "#4ac1ff",
            "deaths": "#ff6b6b",
            "text": "#ffffff",
            "bg": "#1b1d29",
        }
        # Primer gráfico: DONUT (Confirmed)
        self._draw_donut_chart(self.canvas_top, "Confirmed", colors)

        # Segundo gráfico: barras horizontales (Deaths)
        self._draw_bar_chart(self.canvas_bottom, "Deaths", colors["deaths"], colors)

    def _draw_donut_chart(self, canvas, column, colors):
        ax = canvas.axes
        fig = canvas.figure
        fig.patch.set_facecolor(colors["bg"])
        ax.clear()
        ax.set_facecolor(colors["bg"])

        # Datos top 10
        top_data = self.df.sort_values(column, ascending=False).head(10)
        values = top_data[column]
        labels = top_data["Country/Region"]

        # Paleta de colores
        cmap = plt.get_cmap("tab10")
        pie_colors = [cmap(i / len(values)) for i in range(len(values))]

        # === Donut limpio ===
        wedges, texts = ax.pie(
            values,
            startangle=90,
            wedgeprops={'width': 0.4, 'edgecolor': colors["bg"]},
            colors=pie_colors
        )

        # === Leyenda al costado derecho ===
        ax.legend(
            wedges,
            labels, 
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            labelcolor=colors["text"],
            frameon=False,
            edgecolor='none'
        )

        # === Centro hueco del donut ===
        centre_circle = plt.Circle((0, 0), 0.70, fc=colors["bg"])
        fig.gca().add_artist(centre_circle)

        # === Título ===
        ax.set_title(
            f"Top 10 - {column}",
            fontsize=14,
            fontweight="bold",
            color=colors["text"],
            pad=30
        )

        ax.axis("equal")
        canvas.draw()



    def _draw_bar_chart(self, canvas, column, color, colors):
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
        ax.grid(axis="x", linestyle="--", alpha=0.3, color="#444")
        canvas.draw()
        
    def _style_axes(self, ax):
        for side in ["top", "right", "bottom", "left"]:
            ax.spines[side].set_linewidth(0)

    # ----------------------------------------------------------------
    # Tema visual
    # ----------------------------------------------------------------
    def on_country_changed(self, text):
        self.update_kpis(text if text else None)
        self.draw_charts(text if text else None)

    def apply_bento_theme(self):
        """Tema oscuro con efecto glassmorphism."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1c1e2a;
            }
            #glassCard {
                background-color: rgba(29, 31, 43, 0.55);
                border: 1px solid rgba(255, 255, 255, 0.07);
                border-radius: 18px;
            }
            QLabel#cardTitle {
                font-size: 15px;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 8px;
            }
            QLabel#labelTitle {
                font-size: 14px;
                font-weight: 600;
                color: #ffffff;
            }
            #kpiCard {
                background: rgba(255,255,255,0.05);
                border-radius: 12px;
                border: 1px solid rgba(255,255,255,0.1);
                padding: 8px;
            }
            #kpiTitle {
                color: #b8c6ff;
                font-weight: 600;
                font-size: 13px;
            }
            #kpiValue {
                font-size: 24px;
                font-weight: 700;
                color: #5fd1ff;
            }
            QComboBox {
                padding: 6px;
                min-width: 180px;
                color: #ffffff;
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            QTableView {
                background: transparent;
                color: #ffffff;
                gridline-color: rgba(255, 255, 255, 0.08);
                selection-background-color: rgba(74, 193, 255, 0.2);
                border: none;
                alternate-background-color: rgba(255,255,255,0.03);
            }
            QHeaderView::section {
                background: rgba(74, 193, 255, 0.2);
                color: #000000;
                font-weight: 600;
                border: none;
                padding: 6px;
            }
            QScrollBar:vertical {
                background: rgba(255,255,255,0.05);
                width: 5px;
                margin: 4px 0 4px 0;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background: rgba(74, 193, 255, 0.7);
                min-height: 15px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background: rgba(74, 193, 255, 0.4);
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }

            QScrollBar:horizontal {
                background: rgba(255,255,255,0.05);
                height: 10px;
                margin: 0 4px 0 4px;
                border-radius: 5px;
            }

            QScrollBar::handle:horizontal {
                background: rgba(74, 193, 255, 0.4);
                min-width: 25px;
                border-radius: 5px;
            }

            QScrollBar::handle:horizontal:hover {
                background: rgba(74, 193, 255, 0.7);
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0;
            }

        """)
