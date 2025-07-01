from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout,
    QHBoxLayout, QPushButton, QButtonGroup
)
import mplcursors
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd


class AnalysisPage(QWidget):
    def __init__(self):
        super().__init__()
        self.data = None
        self.current_chart = "Гантт"
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # 🔹 Новый заголовок
        title = QLabel("Сравнительный анализ плановых и фактических значений для этапов проекта")
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.description = QLabel("Выберите тип анализа.")
        layout.addWidget(self.description)

        # Кнопки переключения графиков
        chart_buttons_layout = QHBoxLayout()
        self.chart_buttons = {}

        for chart_type in ["Гантт", "Затраты", "Ресурсы", "Отклонения", "Время выполнения", "Динамика бюджета"]:
            btn = QPushButton(chart_type)
            btn.setCheckable(True)
            btn.setObjectName(f"chartBtn{chart_type}")
            btn.setFixedHeight(30)
            chart_buttons_layout.addWidget(btn)
            self.chart_buttons[chart_type] = btn

        self.chart_buttons["Гантт"].setChecked(True)

        button_group = QButtonGroup(self)
        button_group.setExclusive(True)
        for btn in self.chart_buttons.values():
            button_group.addButton(btn)
        button_group.buttonClicked.connect(self.change_chart)

        layout.addLayout(chart_buttons_layout)

        # Место для графика
        self.figure = plt.figure(figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Подпись под графиком
        self.chart_caption = QLabel("")
        self.chart_caption.setWordWrap(True)
        self.chart_caption.setStyleSheet("font-size: 14px; color: #333;")
        layout.addWidget(self.chart_caption)

        self.setLayout(layout)

    def set_data(self, data):
        self.data = data
        if data is not None:
            self.description.setText("Данные загружены. Выберите тип анализа.")
            self.run_analysis()
        else:
            self.description.setText("Нет данных для анализа.")

    def run_analysis(self):
        df = self.data.copy()

        # Приведение дат к datetime с обработкой ошибок
        date_cols = ["Дата начала", "Дата окончания", "Факт начала", "Факт окончания"]
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        # Проверка дат
        if df[date_cols].isna().any().any():
            QMessageBox.warning(self, "Ошибка", "Некоторые даты указаны некорректно.")
            return

        # Расчёт отклонений
        df["∆T"] = (df["Факт окончания"] - df["Факт начала"]) - (df["Дата окончания"] - df["Дата начала"])
        df["∆T_days"] = df["∆T"].dt.days
        df["∆C"] = df["Факт. бюджет"] - df["План. бюджет"]

        self.df_analysis = df

        # Отрисовка текущего графика
        self.change_chart(self.chart_buttons[self.current_chart])

    def change_chart(self, button):
        self.current_chart = button.text()
        self.figure.clear()

        df = self.df_analysis if hasattr(self, "df_analysis") else self.data

        if self.current_chart == "Гантт":
            self.plot_gantt(df)
            self.chart_caption.setText("Гантт-диаграмма сравнивает плановые и фактические сроки выполнения этапов.\n"
                                       "Превышение значения План. значением Факт. означает задержку этапа")
        elif self.current_chart == "Затраты":
            self.plot_budget_comparison(df)
            self.chart_caption.setText("Диаграмма затрат показывает разницу между плановым и фактическим бюджетом.")
        elif self.current_chart == "Ресурсы":
            self.plot_resource_distribution(df)
            self.chart_caption.setText("Круговая диаграмма отражает распределение ресурсов по этапам проекта.")
        elif self.current_chart == "Отклонения":
            self.plot_time_deviation(df)
            self.chart_caption.setText("Линейный график отклонений по времени. \n"
                                       "Отрицательное значение — опережение графика.")
        elif self.current_chart == "Время выполнения":
            self.plot_time_metrics(df)
            self.chart_caption.setText(
                "Время выполнения процесса: нормативное время (идеальные условия), фактическая трудоемкость (реальное время исполнителя), календарная длительность (разница между началом и завершением задачи), в днях.")
        elif self.current_chart == "Динамика бюджета":
            self.plot_budget_dynamics(df)
            self.chart_caption.setText(
                "График динамики бюджета: линии показывают изменение планового и фактического бюджета по датам или этапам."
                "Помогает выявить моменты перерасхода.")

        self.figure.tight_layout()
        self.canvas.draw()

    def plot_gantt(self, df):
        ax = self.figure.add_subplot(111)
        ax.clear()

        df = df.dropna(subset=["Дата начала", "Дата окончания", "Факт начала", "Факт окончания"])
        if df.empty:
            ax.text(0.5, 0.5, "Недостаточно данных для построения диаграммы", ha="center", va="center")
            return

        stages = df["Этап"].tolist()
        y_pos = range(len(stages))

        duration_plan = (df["Дата окончания"] - df["Дата начала"]).dt.days
        duration_fact = (df["Факт окончания"] - df["Факт начала"]).dt.days
        start_plan = df["Дата начала"]
        start_fact = df["Факт начала"]

        # Цвета прямоугольников
        plan_color = "#2c3e50"  # темно-синий для плана
        fact_color = "#1abc9c"  # зеленый для факта
        # Цвета обводки по статусу
        status_colors = {
            'не начат': '#b0bec5',      # серый
            'в работе': '#42a5f5',      # синий
            'выполнен': '#66bb6a',      # зеленый
            'просрочен': '#ef5350',     # красный
        }
        def get_status(row):
            if pd.isna(row['Факт начала']) or row['Факт начала'] > today:
                return 'не начат'
            elif pd.notna(row['Факт окончания']) and row['Факт окончания'] <= today:
                return 'выполнен'
            elif row['Дата окончания'] < today and (pd.isna(row['Факт окончания']) or row['Факт окончания'] > row['Дата окончания']):
                return 'просрочен'
            else:
                return 'в работе'
        today = pd.Timestamp.now().normalize()
        statuses = df.apply(get_status, axis=1)
        edge_colors = [status_colors.get(status, '#b0bec5') for status in statuses]

        bars_plan = ax.barh(
            [y - 0.2 for y in y_pos], duration_plan, height=0.3,
            left=start_plan, color=plan_color, edgecolor=edge_colors, linewidth=3, label="План"
        )
        bars_fact = ax.barh(
            [y + 0.2 for y in y_pos], duration_fact, height=0.3,
            left=start_fact, color=fact_color, edgecolor=edge_colors, linewidth=3, label="Факт"
        )

        # Настройки осей
        ax.set_yticks(y_pos)
        ax.set_yticklabels(stages)
        ax.set_xlabel("Период")
        ax.set_title("Гантт-диаграмма проекта")
        ax.legend()

        min_date = min(df["Дата начала"].min(), df["Факт начала"].min())
        max_date = max(df["Дата окончания"].max(), df["Факт окончания"].max())
        ax.set_xlim(min_date, max_date)
        plt.gcf().autofmt_xdate()

        # Tooltip — объединённая подсказка
        all_rects = bars_plan + bars_fact
        cursor = mplcursors.cursor(all_rects, hover=True)

        @cursor.connect("add")
        def on_add(sel):
            try:
                y = sel.artist.get_y()
                stage_idx = round(y)

                if stage_idx < 0 or stage_idx >= len(df):
                    return

                stage = df.iloc[stage_idx]["Этап"]
                plan_start = df.iloc[stage_idx]["Дата начала"].strftime("%d.%m.%Y")
                plan_end = df.iloc[stage_idx]["Дата окончания"].strftime("%d.%m.%Y")
                fact_start = df.iloc[stage_idx]["Факт начала"].strftime("%d.%m.%Y")
                fact_end = df.iloc[stage_idx]["Факт окончания"].strftime("%d.%m.%Y")

                plan_days = duration_plan.iloc[stage_idx]
                fact_days = duration_fact.iloc[stage_idx]

                text = f"{stage}\nПлан: {plan_start} – {plan_end} ({plan_days} дн.)\nФакт: {fact_start} – {fact_end} ({fact_days} дн.)"
                sel.annotation.set(text=text)
                sel.annotation.arrow_patch.set(arrowstyle="simple", facecolor="black")
                sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)
            except Exception as e:
                print(f"[Ошибка tooltip]: {e}")

        @cursor.connect("remove")
        def on_remove(sel):
            if sel.annotation is not None and sel.annotation.figure is not None:
                sel.annotation.set_visible(False)
                sel.annotation.figure.canvas.draw_idle()

        # Удаление всех старых подписей при каждом вызове plot_gantt
        def clear_annotations():
            for txt in [t for t in ax.texts]:
                txt.remove()
            self.canvas.draw_idle()

        # При уходе мыши с области графика — очищаем всё
        def on_leave_axes(event):
            clear_annotations()

        # Подписываемся на событие, но избегаем дублирования обработчиков
        canvas = ax.figure.canvas
        for cid in getattr(ax, '_tooltip_cids', []):
            canvas.mpl_disconnect(cid)
        ax._tooltip_cids = []

        cid1 = canvas.mpl_connect('axes_leave_event', on_leave_axes)
        ax._tooltip_cids.append(cid1)

        # Сохраняем cursor, чтобы он не исчез преждевременно
        if not hasattr(self, '_gantt_cursor'):
            self._gantt_cursor = cursor
        else:
            self._gantt_cursor = cursor

        self.figure.subplots_adjust(bottom=0.2)
        ax.grid(True, axis='x', linestyle='--', alpha=0.6)
        # Добавим легенду по статусам
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#b0bec5', edgecolor='black', label='Не начат'),
            Patch(facecolor='#42a5f5', edgecolor='black', label='В работе'),
            Patch(facecolor='#66bb6a', edgecolor='black', label='Выполнен'),
            Patch(facecolor='#ef5350', edgecolor='black', label='Просрочен'),
        ]
        ax.legend(handles=legend_elements + list(ax.get_legend_handles_labels()[0]), loc='upper right')

        self.canvas.draw()

    def plot_budget_comparison(self, df):
        ax = self.figure.add_subplot(111)
        width = 0.35
        indices = range(len(df))

        ax.bar(indices, df["План. бюджет"], width, label="План", color="#2c3e50")
        ax.bar([i + width for i in indices], df["Факт. бюджет"], width, label="Факт", color="#1abc9c")

        ax.set_title("Сравнение бюджета (план vs факт)")
        ax.set_ylabel("Бюджет, руб.")
        ax.set_xticks([i + width / 2 for i in indices])
        ax.set_xticklabels(df["Этап"], rotation=45)
        ax.legend()

    def plot_resource_distribution(self, df):
        ax = self.figure.add_subplot(111)
        labels = df["Этап"]
        sizes = df["Ресурсы"]
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
        ax.axis('equal')
        ax.set_title("Распределение ресурсов")

    def plot_time_deviation(self, df):
        ax = self.figure.add_subplot(111)

        df = df.dropna(subset=["Дата начала", "Дата окончания", "Факт начала", "Факт окончания"])
        if df.empty:
            ax.text(0.5, 0.5, "Недостаточно данных для построения графика", ha="center", va="center")
            return

        df["∆T_days"] = (df["Факт окончания"] - df["Факт начала"]) - (df["Дата окончания"] - df["Дата начала"])
        df["∆T_days"] = df["∆T_days"].dt.days

        # Цвета и типы отклонений
        colors = []
        labels = []
        for val in df["∆T_days"]:
            if val > 0:
                colors.append("#ef5350")  # красный — задержка
                labels.append("Задержка")
            elif val < 0:
                colors.append("#66bb6a")  # зеленый — опережение
                labels.append("Опережение")
            else:
                colors.append("#b0bec5")  # серый — норма
                labels.append("В срок")

        # Точки с цветовой индикацией
        ax.scatter(df["Этап"], df["∆T_days"], color=colors, s=80, zorder=3)
        # Линия для наглядности
        ax.plot(df["Этап"], df["∆T_days"], color="#e67e22", alpha=0.5, zorder=2)

        # Подписи над точками
        for i, (x, y, label) in enumerate(zip(df["Этап"], df["∆T_days"], labels)):
            if y > 0:
                txt = f"+{y} дн. ({label})"
            elif y < 0:
                txt = f"{y} дн. ({label})"
            else:
                txt = f"0 дн. (В срок)"
            ax.annotate(txt, (x, y), textcoords="offset points", xytext=(0,8), ha='center', fontsize=10, color=colors[i])

        ax.set_title("Отклонения по времени по этапам проекта")
        ax.set_ylabel("Отклонение, дни")
        ax.axhline(0, color='gray', linestyle='--')
        plt.xticks(rotation=45)
        ax.grid(axis='y', linestyle=':', alpha=0.5)

        # Легенда
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='Задержка', markerfacecolor='#ef5350', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='Опережение', markerfacecolor='#66bb6a', markersize=10),
            Line2D([0], [0], marker='o', color='w', label='В срок', markerfacecolor='#b0bec5', markersize=10),
        ]
        ax.legend(handles=legend_elements, loc='upper right')

        # Подробная подпись под графиком
        self.chart_caption.setText(
            "График отклонений по времени: каждая точка — этап проекта.\n"
            "Красный — задержка (этап выполнен позже плана), зеленый — опережение (этап завершён раньше), серый — выполнено в срок.\n"
            "Подписи над точками показывают величину и тип отклонения для каждого этапа."
        )
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_execution_time(self, df):
        ax = self.figure.add_subplot(111)

        df = df.dropna(subset=["Дата начала", "Дата окончания", "Факт начала", "Факт окончания"])
        if df.empty:
            ax.text(0.5, 0.5, "Недостаточно данных для построения графика", ha="center", va="center")
            return

        df["Время выполнения"] = (df["Факт окончания"] - df["Факт начала"]).dt.total_seconds() / 3600  # Часы
        df["Плановое время"] = (df["Дата окончания"] - df["Дата начала"]).dt.total_seconds() / 3600  # Часы

        x = df["Этап"]
        y1 = df["Плановое время"]
        y2 = df["Время выполнения"]

        width = 0.35
        ax.bar(x, y1, width, label="Плановое время", color="#2c3e50")
        ax.bar(x, y2, width, label="Фактическое время", color="#1abc9c", bottom=y1)

        ax.set_title("Время выполнения этапов")
        ax.set_ylabel("Время, часы")
        ax.legend()

    def load_time_metrics_from_knowledge_base(self):
        import os, json
        time_file = os.path.join(os.path.dirname(__file__), 'knowledge_base_time.json')
        if os.path.exists(time_file):
            with open(time_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Преобразуем в DataFrame
            df = pd.DataFrame(data)
            df.rename(columns={"stage": "Этап", "norm": "Нормативное время выполнения (дни)", "fact": "Фактическая трудоемкость (дни)"}, inplace=True)
            # Преобразуем значения в float
            df["Нормативное время выполнения (дни)"] = pd.to_numeric(df["Нормативное время выполнения (дни)"], errors='coerce')
            df["Фактическая трудоемкость (дни)"] = pd.to_numeric(df["Фактическая трудоемкость (дни)"], errors='coerce')
            return df
        return None

    def plot_time_metrics(self, df):
        # Если есть база знаний по времени — используем её
        kb_df = self.load_time_metrics_from_knowledge_base()
        if kb_df is not None and not kb_df.empty:
            df = kb_df
        ax = self.figure.add_subplot(111)
        ax.clear()
        required_cols = ["Этап"]
        for col in required_cols:
            if col not in df.columns:
                ax.text(0.5, 0.5, f"Нет данных: {col}", ha="center", va="center")
                return
        norm = df["Нормативное время выполнения (дни)"] if "Нормативное время выполнения (дни)" in df.columns else [None]*len(df)
        fact = df["Фактическая трудоемкость (дни)"] if "Фактическая трудоемкость (дни)" in df.columns else [None]*len(df)
        # Календарная длительность — если есть даты, иначе None
        if "Дата начала" in df.columns and "Факт окончания" in df.columns:
            cal = (df["Факт окончания"] - df["Дата начала"]).dt.days
        elif "Дата начала" in df.columns and "Дата окончания" in df.columns:
            cal = (df["Дата окончания"] - df["Дата начала"]).dt.days
        else:
            cal = [None]*len(df)
        x = df["Этап"]
        bar_width = 0.25
        indices = range(len(x))
        ax.bar([i - bar_width for i in indices], norm, width=bar_width, color="#3CB371", label="Нормативное время выполнения")
        ax.bar(indices, fact, width=bar_width, color="#90EE90", label="Фактическая трудоемкость")
        ax.bar([i + bar_width for i in indices], cal, width=bar_width, color="#FF6347", label="Календарная длительность")
        ax.set_xticks(indices)
        ax.set_xticklabels(x, rotation=30, ha="right")
        ax.set_ylabel("Время, дни")
        ax.set_title("Время выполнения бизнес-процесса, дни")
        ax.legend()
        ax.grid(axis="y", linestyle=":", alpha=0.5)
        self.figure.subplots_adjust(bottom=0.3)
        self.canvas.draw()

    def plot_budget_dynamics(self, df):
        ax = self.figure.add_subplot(111)
        # Сортировка по дате окончания этапа (или по этапу, если дат нет)
        if "Дата окончания" in df.columns:
            df_sorted = df.sort_values("Дата окончания")
            x = df_sorted["Дата окончания"]
            x_label = "Дата окончания этапа"
        else:
            df_sorted = df.copy()
            x = df_sorted["Этап"]
            x_label = "Этап"
        y_plan = df_sorted["План. бюджет"]
        y_fact = df_sorted["Факт. бюджет"]

        # Проверка на NaN
        if y_plan.isnull().all() or y_fact.isnull().all():
            ax.text(0.5, 0.5, "Нет данных для построения графика", ha="center", va="center")
            return

        # Построение графика с маркерами, цветами и заливкой между линиями
        ax.plot(x, y_plan, marker="o", label="Плановый бюджет", color="#2c3e50", linewidth=2)
        ax.plot(x, y_fact, marker="o", label="Фактический бюджет", color="#e74c3c", linewidth=2)
        ax.fill_between(x, y_plan, y_fact, where=(y_fact > y_plan), color="#ffcccc", alpha=0.5, label="Перерасход")
        ax.fill_between(x, y_plan, y_fact, where=(y_fact < y_plan), color="#c8e6c9", alpha=0.5, label="Экономия")

        # Подписи значений на точках
        for i, (xv, yp, yf) in enumerate(zip(x, y_plan, y_fact)):
            ax.annotate(f"{int(yp)}", (xv, yp), textcoords="offset points", xytext=(0,8), ha='center', fontsize=9, color="#2c3e50")
            ax.annotate(f"{int(yf)}", (xv, yf), textcoords="offset points", xytext=(0,-12), ha='center', fontsize=9, color="#e74c3c")

        ax.set_xlabel(x_label)
        ax.set_ylabel("Бюджет, руб.")
        ax.set_title("Динамика бюджета во времени")
        ax.legend(loc="upper left")
        ax.grid(True, linestyle=":", alpha=0.5)
        plt.xticks(rotation=30, ha="right")
        self.figure.tight_layout()
        self.canvas.draw()

    def save_charts(self):
        import tempfile
        chart_types = ["Гантт", "Затраты", "Ресурсы", "Отклонения", "Динамика бюджета"]
        chart_files = []

        for chart_type in chart_types:
            self.figure.clear()
            if chart_type == "Гантт":
                self.plot_gantt(self.df_analysis)
            elif chart_type == "Затраты":
                self.plot_budget_comparison(self.df_analysis)
            elif chart_type == "Ресурсы":
                self.plot_resource_distribution(self.df_analysis)
            elif chart_type == "Отклонения":
                self.plot_time_deviation(self.df_analysis)
            elif chart_type == "Динамика бюджета":
                self.plot_budget_dynamics(self.df_analysis)

            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            self.figure.savefig(temp_file.name, bbox_inches="tight")
            chart_files.append((chart_type, temp_file.name))

        self.change_chart(self.chart_buttons[self.current_chart])  # Восстановить текущий график
        return chart_files
