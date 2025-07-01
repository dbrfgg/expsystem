from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout,
    QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QTreeView, QHBoxLayout
)
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import pandas as pd
import os


class ProjectPage(QWidget):
    def __init__(self):
        super().__init__()
        self.data = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # Заголовок
        title = QLabel("Вкладка: Проект")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Кнопка импорта
        self.import_btn = QPushButton("📁 Импортировать проект")
        self.import_btn.clicked.connect(self.load_project)
        self.import_btn.setObjectName("menuButton")
        layout.addWidget(self.import_btn)

        # Горизонтальный контейнер для таблицы и дерева
        content_layout = QHBoxLayout()

        # Таблица
        self.table = QTableWidget()
        self.table.setWordWrap(True)
        self.table.verticalHeader().setVisible(False)  # Скрыть первый (номерной) столбец
        self.table.horizontalHeader().setMinimumSectionSize(120)
        self.table.horizontalHeader().setDefaultSectionSize(150)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section {padding: 8px;}")
        content_layout.addWidget(self.table, stretch=2)

        # Дерево этапов
        self.tree_view = QTreeView()
        self.tree_model = QStandardItemModel()
        self.tree_model.setHorizontalHeaderLabels(["Этапы проекта"])
        self.tree_view.setModel(self.tree_model)
        content_layout.addWidget(self.tree_view, stretch=1)

        layout.addLayout(content_layout)
        self.setLayout(layout)

        self.goto_analysis_btn = QPushButton("➡ Перейти к анализу")
        self.goto_analysis_btn.clicked.connect(self.goto_analysis)
        self.goto_analysis_btn.setObjectName("menuButton")
        layout.addWidget(self.goto_analysis_btn)

        # Применяем стиль для кнопок раздела Проект
        self.setStyleSheet("""
            #projectButton {
                min-height: 44px;
                min-width: 0px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f8fafc, stop:1 #e0e7ef);
                color: #232526;
                padding: 12px 22px;
                font-size: 16px;
                border: none;
                border-radius: 10px;
                margin: 8px 0 8px 0;
                text-align: left;
                transition: background 0.3s, color 0.3s, box-shadow 0.3s;
                box-shadow: 0 2px 8px rgba(44,62,80,0.06);
                letter-spacing: 0.5px;
                word-break: break-word;
                white-space: normal;
                line-height: 1.2;
            }
            #projectButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e0f7fa, stop:1 #b2ebf2);
                color: #00796b;
                box-shadow: 0 4px 16px rgba(26,188,156,0.10);
            }
            #projectButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fffde4, stop:1 #f7e8a4);
                color: #b28704;
                font-weight: bold;
                border: 2px solid #ffe082;
                box-shadow: 0 4px 24px rgba(255,215,0,0.12);
            }
        """)

        # Применяем стиль для таблицы и дерева
        self.setStyleSheet("""
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
            QTreeView {
                background: #f8fafc;
                border: 1px solid #e0e7ef;
                border-radius: 10px;
                font-size: 15px;
                color: #232526;
                selection-background-color: #e0f7fa;
                selection-color: #00796b;
                padding: 4px;
            }
            QTreeView::item {
                padding: 6px 8px;
            }
            QTreeView::item:selected {
                background: #b2ebf2;
                color: #00796b;
            }
            QTreeView::branch:selected {
                background: #b2ebf2;
            }
        """)

    def load_project(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл проекта",
            "",
            "Excel Files (*.xlsx);;CSV Files (*.csv);;JSON Files (*.json)"
        )

        if not file_path:
            return

        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".xlsx":
                df = pd.read_excel(file_path)
            elif ext == ".csv":
                df = pd.read_csv(file_path)
            elif ext == ".json":
                df = pd.read_json(file_path)
            else:
                raise ValueError("Неподдерживаемый формат файла")

            # Сохраняем данные
            self.data = df

            # Валидация структуры
            required_columns = [
                "Этап", "Ответственный", "Дата начала", "Дата окончания",
                "Факт начала", "Факт окончания", "План. бюджет", "Факт. бюджет", "Ресурсы"
            ]
            missing = [col for col in required_columns if col not in df.columns]
            if missing:
                raise ValueError(f"Отсутствуют столбцы: {', '.join(missing)}")

            # Обновить таблицу и дерево
            self.update_table(df)
            self.update_tree(df)

        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Ошибка", str(e))

    def update_table(self, df):
        self.table.setRowCount(df.shape[0])
        self.table.setColumnCount(df.shape[1])
        self.table.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iat[i, j]))
                self.table.setItem(i, j, item)

    def update_tree(self, df):
        self.tree_model.clear()
        self.tree_model.setHorizontalHeaderLabels(["Этапы проекта"])

        root_item = self.tree_model.invisibleRootItem()

        for _, row in df.iterrows():
            stage = QStandardItem(row["Этап"])
            responsible = QStandardItem(f"Ответственный: {row['Ответственный']}")
            duration = QStandardItem(f"Срок: {row['Дата начала']} – {row['Дата окончания']}")
            budget = QStandardItem(f"Бюджет: {row['План. бюджет']} руб.")

            stage.appendRow(responsible)
            stage.appendRow(duration)
            stage.appendRow(budget)

            root_item.appendRow(stage)

    def goto_analysis(self):
        if self.data is not None:
            self.window().set_project_data(self.data)  # Обновляем данные для всех страниц
            self.window().switch_page("Анализ")
        else:
            QMessageBox.warning(self, "Ошибка", "Сначала загрузите данные проекта.")
