from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame
)
from PyQt5.QtCore import Qt
from view.pages.project_page import ProjectPage
from view.pages.analysis_page import AnalysisPage
from view.pages.recommendations_page import RecommendationsPage
from view.pages.reports_page import ReportsPage
from view.pages.calculations_page import CalculationsPage
from PyQt5.QtWidgets import QDesktopWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.project_data = None

        # Установка заголовка
        self.setWindowTitle("Анализ проектов")

        # Минимальный размер
        self.setMinimumSize(800, 600)

        # Автоматическая адаптация под экран
        screen = QDesktopWidget().screenGeometry()
        width = int(screen.width() * 0.8)
        height = int(screen.height() * 0.8)
        self.resize(width, height)

        # Центрирование окна
        self.move(
            (screen.width() - width) // 2,
            (screen.height() - height) // 2
        )

        # Центральный виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)

        # Светлый современный стиль для меню
        self.setStyleSheet("""
            #menuButton {
                min-height: 56px;
                min-width: 0px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f8fafc, stop:1 #e0e7ef);
                color: #232526;
                padding: 16px 18px;
                font-size: 16px;
                border: none;
                border-radius: 12px;
                margin: 10px 10px 10px 10px;
                text-align: left;
                transition: background 0.3s, color 0.3s, box-shadow 0.3s;
                box-shadow: 0 2px 8px rgba(44,62,80,0.06);
                letter-spacing: 0.5px;
                word-break: break-word;
                white-space: normal;
                line-height: 1.2;
            }
            #menuButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e0f7fa, stop:1 #b2ebf2);
                color: #00796b;
                box-shadow: 0 4px 16px rgba(26,188,156,0.10);
            }
            #menuButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fffde4, stop:1 #f7e8a4);
                color: #b28704;
                font-weight: bold;
                border: 2px solid #ffe082;
                box-shadow: 0 4px 24px rgba(255,215,0,0.12);
            }
            QFrame {
                background: #f8fafc;
                border-top-left-radius: 18px;
                border-bottom-left-radius: 18px;
            }
        """)

        # Меню
        menu_frame = QFrame()
        menu_layout = QVBoxLayout(menu_frame)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(0)

        self.buttons = []

        for name in ["Проект", "Анализ", "Рекомендации", "Отчёты", "Рассчитанные значения"]:
            btn = QPushButton(name)
            btn.setObjectName("menuButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, n=name: self.switch_page(n))
            menu_layout.addWidget(btn)
            self.buttons.append(btn)

        menu_frame.setFixedWidth(300)

        # Контент
        self.content_area = QStackedWidget()

        # Добавление страниц
        self.pages = {
            "Проект": ProjectPage(),
            "Анализ": AnalysisPage(),
            "Рекомендации": RecommendationsPage(),
            "Отчёты": ReportsPage(),
            "Рассчитанные значения": CalculationsPage(),
        }

        for page in self.pages.values():
            self.content_area.addWidget(page)

        # Установить первую страницу
        self.switch_page("Проект")

        # Компоновка
        layout.addWidget(menu_frame)
        layout.addWidget(self.content_area)

    def switch_page(self, page_name):
        for btn in self.buttons:
            btn.setChecked(btn.text() == page_name)
        self.content_area.setCurrentWidget(self.pages[page_name])

        # Если открываем "Рекомендации" — передаём актуальные расчеты
        if page_name == "Рекомендации":
            calc_page = self.pages.get("Рассчитанные значения")
            rec_page = self.pages.get("Рекомендации")

            if calc_page and hasattr(calc_page, "calculations_data") and rec_page and hasattr(rec_page,
                                                                                              "set_calculations"):
                if calc_page.calculations_data is not None:
                    rec_page.set_calculations(calc_page.calculations_data)

    def set_project_data(self, data):
        self.project_data = data
        for page in self.pages.values():
            if hasattr(page, "set_data"):
                page.set_data(data)

        # Передача рассчитанных значений во вкладку "Рекомендации"
        calc_page = self.pages.get("Рассчитанные значения")
        if calc_page and hasattr(calc_page, "calculations_data") and calc_page.calculations_data is not None:
            rec_page = self.pages.get("Рекомендации")
            if rec_page and hasattr(rec_page, "set_calculations"):
                rec_page.set_calculations(calc_page.calculations_data)


    def get_project_data(self):
        return self.project_data
