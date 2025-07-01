from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QFrame
)
from PyQt5.QtCore import Qt


class RecommendationsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.calculations_data = None  # данные из CalculationsPage
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # Новый дизайн только для верхней части (заголовок, описание, кнопка)
        self.setStyleSheet("""
            QLabel#recTitle {
                font-size: 20px;
                font-weight: bold;
                color: #232526;
                margin-bottom: 8px;
            }
            QLabel#recDesc {
                font-size: 15px;
                color: #4a4a4a;
                margin-bottom: 18px;
            }
            QPushButton#recGenBtn {
                min-height: 44px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f8fafc, stop:1 #e0e7ef);
                color: #232526;
                padding: 12px 22px;
                font-size: 16px;
                border: none;
                border-radius: 10px;
                margin: 8px 0 18px 0;
                text-align: left;
                transition: background 0.3s, color 0.3s, box-shadow 0.3s;
                box-shadow: 0 2px 8px rgba(44,62,80,0.06);
                letter-spacing: 0.5px;
                word-break: break-word;
                white-space: normal;
                line-height: 1.2;
            }
            QPushButton#recGenBtn:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #e0f7fa, stop:1 #b2ebf2);
                color: #00796b;
                box-shadow: 0 4px 16px rgba(26,188,156,0.10);
            }
        """)

        title = QLabel("Вкладка: Рекомендации")
        title.setObjectName("recTitle")
        layout.addWidget(title)

        self.description = QLabel("Нажмите [Сгенерировать рекомендации], чтобы увидеть предложения по оптимизации.")
        self.description.setObjectName("recDesc")
        layout.addWidget(self.description)

        self.generate_btn = QPushButton("🔄 Сгенерировать рекомендации")
        self.generate_btn.setObjectName("recGenBtn")
        self.generate_btn.clicked.connect(self.show_recommendations)
        layout.addWidget(self.generate_btn)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)

    def set_calculations(self, calculations_data):
        """Получаем данные из раздела 'Рассчитанные значения'"""
        self.calculations_data = calculations_data

    def show_recommendations(self):
        if self.calculations_data is None or self.calculations_data.empty:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Нет данных для формирования рекомендаций")
            return

        df = self.calculations_data.copy()

        # Преобразуем ΔT и ΔC из строк с "%" в числа
        try:
            df["ΔT"] = df["ΔT"].str.replace(" %", "").astype(float)
            df["ΔC"] = df["ΔC"].str.replace(" %", "").astype(float)
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Ошибка", f"Ошибка обработки данных: {str(e)}")
            return

        # Очищаем таблицу
        self.table.setRowCount(0)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Этап", "Проблема", "Причина", "Рекомендация", "Ожидаемый эффект"])

        # Генерируем рекомендации
        recommendations = []

        for i in range(len(df)):
            stage = df.iloc[i]["Этап"]
            delta_t = df.iloc[i]["ΔT"]  # Отклонение по времени в %
            delta_c = df.iloc[i]["ΔC"]  # Перерасход бюджета в %
            e = df.iloc[i]["E"]         # Эффективность ресурсов
            reason = ""
            recommendation = ""
            effect = ""
            problem = ""
            # Проблема по срокам
            if delta_t > 10:
                problem = f"Задержка по срокам: превышение на {delta_t:.2f}% от плана"
                reason = "Значительное превышение сроков выполнения этапа. Возможные причины: нехватка ресурсов, задержки поставок, ошибки в планировании."
                recommendation = (
                    "Провести анализ причин задержки: проверить наличие всех необходимых ресурсов, "
                    "оценить работу поставщиков, пересмотреть план-график. Рассмотреть возможность привлечения "
                    "дополнительных исполнителей или перераспределения задач между сотрудниками."
                )
                effect = f"Ожидаемое сокращение задержки: с {delta_t:.2f}% до {delta_t*0.5:.2f}%"
                recommendations.append([
                    str(stage),
                    problem,
                    reason,
                    recommendation,
                    effect
                ])
            elif 0 < delta_t <= 10:
                problem = f"Небольшая задержка: превышение на {delta_t:.2f}% от плана"
                reason = "Небольшое превышение сроков. Возможные причины: незначительные организационные сбои, погодные условия, неэффективное распределение задач."
                recommendation = (
                    "Провести оперативное совещание с командой, скорректировать приоритеты, "
                    "при необходимости временно увеличить рабочее время или привлечь дополнительные ресурсы."
                )
                effect = f"Ожидаемое сокращение задержки: с {delta_t:.2f}% до {delta_t*0.5:.2f}%"
                recommendations.append([
                    str(stage),
                    problem,
                    reason,
                    recommendation,
                    effect
                ])
            elif delta_t < 0:
                problem = f"Опережение графика: выполнение быстрее на {-delta_t:.2f}%"
                reason = "Работы выполнены с опережением графика. Возможные причины: высокая мотивация персонала, оптимизация процессов."
                recommendation = (
                    "Зафиксировать успешные практики, поощрить команду, рассмотреть возможность перераспределения "
                    "освободившихся ресурсов на другие этапы или проекты."
                )
                effect = f"Потенциал ускорения других этапов: до {-delta_t:.2f}%"
                recommendations.append([
                    str(stage),
                    problem,
                    reason,
                    recommendation,
                    effect
                ])
            # Проблема по бюджету
            if delta_c > 10:
                problem = f"Перерасход бюджета: превышение на {delta_c:.2f}% от плана"
                reason = "Существенный перерасход бюджета. Возможные причины: рост цен, дополнительные работы, ошибки в смете."
                recommendation = (
                    "Провести детальный анализ затрат, выявить статьи перерасхода, согласовать корректировку бюджета с руководством. "
                    "Проверить договоры с поставщиками, рассмотреть альтернативные варианты закупок."
                )
                effect = f"Ожидаемое снижение перерасхода: с {delta_c:.2f}% до {delta_c*0.5:.2f}%"
                recommendations.append([
                    str(stage),
                    problem,
                    reason,
                    recommendation,
                    effect
                ])
            elif 0 < delta_c <= 10:
                problem = f"Умеренный перерасход бюджета: превышение на {delta_c:.2f}% от плана"
                reason = "Умеренный перерасход бюджета. Возможные причины: незначительные дополнительные расходы, корректировки в процессе."
                recommendation = (
                    "Провести сверку сметы, оптимизировать закупки, пересмотреть условия договоров, "
                    "контролировать расходы на следующих этапах."
                )
                effect = f"Ожидаемое снижение перерасхода: с {delta_c:.2f}% до {delta_c*0.5:.2f}%"
                recommendations.append([
                    str(stage),
                    problem,
                    reason,
                    recommendation,
                    effect
                ])
            elif delta_c < 0:
                problem = f"Экономия бюджета: снижение затрат на {-delta_c:.2f}% от плана"
                reason = "Экономия бюджета. Возможные причины: скидки, оптимизация закупок, эффективное управление."
                recommendation = (
                    "Зафиксировать успешные решения, рассмотреть возможность перераспределения сэкономленных средств "
                    "на другие этапы или проекты."
                )
                effect = f"Потенциал экономии: {-delta_c:.2f}%"
                recommendations.append([
                    str(stage),
                    problem,
                    reason,
                    recommendation,
                    effect
                ])
            # Проблема по эффективности
            if e < -0.1:
                problem = f"Низкая эффективность ресурсов: показатель {e:.2f} (ниже нормы)"
                reason = "Низкая эффективность использования ресурсов. Возможные причины: простаивание техники, неравномерная загрузка персонала."
                recommendation = (
                    "Провести аудит загрузки ресурсов, выявить и устранить узкие места, "
                    "перепланировать график работ для равномерного распределения нагрузки."
                )
                effect = "Ожидаемый рост эффективности: до нормы"
                recommendations.append([
                    str(stage),
                    problem,
                    reason,
                    recommendation,
                    effect
                ])
            elif e > 0.1:
                problem = f"Высокая эффективность ресурсов: показатель {e:.2f} (выше нормы)"
                reason = "Высокая эффективность использования ресурсов. Возможные причины: грамотное планирование, автоматизация процессов."
                recommendation = (
                    "Использовать выявленные эффективные подходы на других этапах, "
                    "поощрить команду, внедрять лучшие практики в будущих проектах."
                )
                effect = "Возможность тиражирования успешных практик"
                recommendations.append([
                    str(stage),
                    problem,
                    reason,
                    recommendation,
                    effect
                ])
            else:
                problem = f"Эффективность ресурсов в норме: показатель {e:.2f}"
                reason = "Эффективность ресурсов в пределах нормы."
                recommendation = "Действия не требуются. Продолжать работу по текущему плану."
                effect = "Стабильная работа, изменений не требуется"
                recommendations.append([
                    str(stage),
                    problem,
                    reason,
                    recommendation,
                    effect
                ])

        if not recommendations:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Информация", "Рекомендации отсутствуют.")
            return

        self.update_table(recommendations)

    def update_table(self, recommendations):
        """Обновляет таблицу рекомендаций"""
        self.table.clear()  # Очищаем полностью, чтобы сбросить старые заголовки
        self.table.setRowCount(len(recommendations))
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Этап", "Проблема", "Причина", "Рекомендация", "Ожидаемый эффект"
        ])

        for i, row in enumerate(recommendations):
            for j, val in enumerate(row):
                item = QTableWidgetItem(str(val))
                self.table.setItem(i, j, item)

        # Устанавливаем фиксированную ширину столбцов
        self.table.setColumnWidth(0, 180)  # Этап
        self.table.setColumnWidth(1, 250)  # Проблема
        self.table.setColumnWidth(2, 300)  # Причина
        self.table.setColumnWidth(3, 350)  # Рекомендация
        self.table.setColumnWidth(4, 260)  # Ожидаемый эффект

        # Применяем CSS-стили
        self.table.setStyleSheet("""
            QTableView {
                border: 1.5px solid #dcdcdc;
                border-radius: 10px;
                gridline-color: #e0e0e0;
                font-size: 14px;
                background-color: #ffffff;
                selection-background-color: #1abc9c;
                selection-color: #fff;
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
                border: 1.5px solid #dcdcdc;
                font-weight: bold;
                font-size: 14px;
                border-radius: 6px;
            }
            QTableView::item:selected {
                background-color: #1abc9c;
                color: white;
            }
        """)

        # Запрещаем растягивание столбцов пользователем
        from PyQt5.QtWidgets import QHeaderView
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

        self.table.resizeRowsToContents()
        self.description.setText(f"Сформировано {len(recommendations)} рекомендаций.")
