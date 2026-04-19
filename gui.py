# gui.py
import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
    QMessageBox,
    QWidget,
)
from PyQt6.QtCore import Qt


class TopicDialog(QDialog):
    """Dialog for adding a new topic (Ported from Citation 1)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить тему")
        self.resize(400, 300)

        layout = QVBoxLayout()

        # Name input
        layout.addWidget(QLabel("Название:", self))
        self.name_entry = QLineEdit(self)
        layout.addWidget(self.name_entry)

        # Description input
        layout.addWidget(QLabel("Описание:", self))
        self.desc_entry = QTextEdit(self)
        layout.addWidget(self.desc_entry)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        cancel_button = QPushButton("Отмена")

        save_button.clicked.connect(self.save_topic)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def save_topic(self):
        """Simulate saving a topic to the database"""
        name = self.name_entry.text().strip()
        desc = self.desc_entry.toPlainText().strip()

        if not name:
            QMessageBox.warning(
                self, "Предупреждение", "Введите название темы!"
            )
            return

        # Simulate successful save
        QMessageBox.information(
            self,
            "Успех",
            f"Тема '{name}' добавлена в базу данных.\nДля полноценной работы необходимо добавить генератор задач.",
        )
        self.accept()  # Close the dialog


class StatisticsWindow(QMainWindow):
    """Statistics window (Ported from Citation 2)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Статистика")
        self.resize(500, 400)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        label = QLabel("Статистика за последние 7 дней", central_widget)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 14px; font-weight: bold;")
        main_layout.addWidget(label)

        # Create a tree view (QTreeWidget)
        self.tree_widget = QTreeWidget(central_widget)
        self.tree_widget.setHeaderLabels(["Тема", "Всего", "Правильно", "Точность"])
        main_layout.addWidget(self.tree_widget)

        central_widget.setLayout(main_layout)

        # Example data
        item1 = QTreeWidgetItem(self.tree_widget)
        item1.setText(0, "Арифметика")
        item1.setText(1, "50")
        item1.setText(2, "45")
        item1.setText(3, "90%")


class MainApplication(QMainWindow):
    """Main window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Математический Тренажер")
        self.resize(800, 600)

        # Central widget for main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        self.topic_combo_label = QLabel("Выберите тему:")
        self.topic_combo = QLineEdit()  # Simplified as a line edit
        self.topic_combo.setPlaceholderText("Нажмите 'Загрузить темы'")

        self.add_topic_button = QPushButton("Добавить тему")
        self.stats_button = QPushButton("Показать статистику")
        self.problem_label = QLabel("Задача: 2 + 2", central_widget)
        self.answer_input = QLineEdit(central_widget)
        self.check_button = QPushButton("Проверить")
        self.result_label = QLabel("", central_widget)

        # Connect buttons (logic would be connected to your app)
        self.add_topic_button.clicked.connect(self._show_add_topic_dialog)
        self.stats_button.clicked.connect(self._show_statistics)

        layout.addWidget(self.topic_combo_label)
        layout.addWidget(self.topic_combo)
        layout.addWidget(self.add_topic_button)
        layout.addWidget(self.stats_button)
        layout.addWidget(self.problem_label)
        layout.addWidget(self.answer_input)
        layout.addWidget(self.check_button)
        layout.addWidget(self.result_label)

        central_widget.setLayout(layout)

        # Keep reference to statistics window to prevent garbage collection
        self.stats_window = None

    def _show_add_topic_dialog(self):
        """Open the topic dialog"""
        dialog = TopicDialog(self)
        if dialog.exec():
            self.topic_combo.setText(dialog.name_entry.text())

    def _show_statistics(self):
        """Open the statistics window"""
        self.stats_window = StatisticsWindow(self)
        self.stats_window.show()


# Entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApplication()
    window.show()
    sys.exit(app.exec())
