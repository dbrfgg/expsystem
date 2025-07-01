from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
import pandas as pd
from PyQt5.QtWidgets import QMessageBox


class CalculationsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.data = None
        self.init_ui()
        self.calculations_data = None

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # Новый современный стиль для заголовка, описания и таблицы
        self.setStyleSheet("""
            QLabel#calcTitle {
                font-size: 20px;
                font-weight: bold;
                color: #232526;
                margin-bottom: 8px;
            }
            QLabel#calcDesc {
                font-size: 15px;
                color: #4a4a4a;
                margin-bottom: 18px;
            }
            QTableWidget {
                background: #f8fafc;
                border: 1px solid #e0e7ef;
                border-radius: 10px;
                font-size: 15px;
                color: #232526;
                selection-background-color: #e0f7fa;
                selection-color: #00796b;
                gridline-color: #e0e7ef;
                padding: 4px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background: #b2ebf2;
                color: #00796b;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e0e7ef, stop:1 #f8fafc);
                color: #232526;
                font-weight: bold;
                font-size: 15px;
                border: 1px solid #e0e7ef;
                border-radius: 8px;
                padding: 8px;
                min-width: 120px;
                max-width: 300px;
                word-break: break-word;
                white-space: normal;
            }
            QTableWidget QHeaderView {
                font-size: 15px;
            }
        """)

        title = QLabel("Вкладка: Рассчитанные значения")
        title.setObjectName("calcTitle")
        layout.addWidget(title)

        self.description = QLabel(
            "Здесь представлены рассчитанные метрики проекта:\n\n"
            "• ΔT — отклонение по срокам (%)\n"
            "• ΔC — перерасход бюджета (%)\n"
            "• E — эффективность использования ресурсов"
        )
        self.description.setObjectName("calcDesc")
        layout.addWidget(self.description)

        # Таблица
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)

    def set_data(self, data):
        self.data = data
        if data is not None:
            self.calculate_metrics(data)
        else:
            self.description.setText("Нет данных для расчёта.")

    def calculate_metrics(self, df):
        df = df.copy()

        # Приведение дат к datetime
        date_cols = ["Дата начала", "Дата окончания", "Факт начала", "Факт окончания"]
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        # Проверка на пустые значения
        if df[date_cols].isna().any().any():

            QMessageBox.warning(self, "Ошибка", "Некоторые даты указаны некорректно.")
            return

        # Расчёт длительности
        df["План длительность"] = (df["Дата окончания"] - df["Дата начала"]).dt.days
        df["Факт длительность"] = (df["Факт окончания"] - df["Факт начала"]).dt.days

        # ΔT — отклонение по времени (%)
        df["ΔT"] = ((df["Факт длительность"] - df["План длительность"]) / df["План длительность"]) * 100

        # ΔC — перерасход бюджета (%)
        df["ΔC"] = ((df["Факт. бюджет"] - df["План. бюджет"]) / df["План. бюджет"]) * 100

        # E — эффективность ресурсов
        df["E"] = 1 - (df["План длительность"] / df["Факт длительность"])

        # Округление
        df[["ΔT", "ΔC", "E"]] = df[["ΔT", "ΔC", "E"]].round(2)

        # Добавляем символ процента к ΔT и ΔC
        df["ΔT"] = df["ΔT"].astype(str) + " %"
        df["ΔC"] = df["ΔC"].astype(str) + " %"

        self.update_table(df)
        self.calculations_data = df.copy()

    def update_table(self, df):
        cols = ["Этап", "ΔT", "ΔC", "E"]
        self.table.setColumnCount(len(cols))
        self.table.setHorizontalHeaderLabels([
            "Этап",
            "ΔT",
            "ΔC",
            "E"
        ])
        self.table.setRowCount(df.shape[0])

        for i in range(df.shape[0]):
            for j, col in enumerate(cols):
                item = QTableWidgetItem(str(df.iloc[i][col]))
                self.table.setItem(i, j, item)

        # Фиксируем ширину столбцов
        self.table.setColumnWidth(0, 180)  # Этап
        self.table.setColumnWidth(1, 160)  # ΔT
        self.table.setColumnWidth(2, 160)  # ΔC
        self.table.setColumnWidth(3, 140)  # E

        from PyQt5.QtWidgets import QHeaderView
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)


        self.table.setStyleSheet("""
            QTableView {
                border: 1px solid #dcdcdc;
                gridline-color: #e0e0e0;
                font-size: 14px;
                background-color: #ffffff;
            }
            QTableView::item {
                padding: 8px;
                border-right: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
            }
            QTableView::item:alternate {
                background-color: #f5f5f5;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                border: 1px solid #dcdcdc;
                font-weight: bold;
                font-size: 14px;
            }
            QTableView::item:selected {
                background-color: #1abc9c;
                color: white;
            }
        """)
