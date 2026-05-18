# -*- coding: utf-8 -*-

import sys
import sqlite3

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QTableWidget, QTableWidgetItem, QPushButton,
    QLineEdit, QTextEdit, QDialog, QFormLayout, QSpinBox,
    QDoubleSpinBox, QDateEdit, QMessageBox
)

from PyQt6.QtCore import QDate


DB_NAME = "game_assets1.db"


class SortableItem(QTableWidgetItem):
    def __init__(self, text, sort_value=None):
        super().__init__(text)
        self.sort_value = sort_value if sort_value is not None else text

    def __lt__(self, other):
        if isinstance(other, SortableItem):
            return self.sort_value < other.sort_value
        return super().__lt__(other)


class CategoryDialog(QDialog):
    def __init__(self, category_id=None):
        super().__init__()
        self.category_id = category_id
        self.setWindowTitle("Добавление категории" if category_id is None else "Редактирование категории")

        layout = QFormLayout()

        self.category_name = QLineEdit()

        self.description = QTextEdit()
        self.description.setFixedHeight(80)

        self.uniqueness_type = QComboBox()
        self.uniqueness_type.addItems(["уникальный", "переиспользуемый"])

        self.detail_level = QSpinBox()
        self.detail_level.setMinimum(1)
        self.detail_level.setMaximum(3)

        self.average_file_size = QDoubleSpinBox()
        self.average_file_size.setMaximum(1000000)
        self.average_file_size.setDecimals(2)

        layout.addRow("Название категории", self.category_name)
        layout.addRow("Описание", self.description)
        layout.addRow("Тип использования", self.uniqueness_type)
        layout.addRow("Уровень детализации", self.detail_level)
        layout.addRow("Средний размер файла", self.average_file_size)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_category)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        if self.category_id is not None:
            self.load_category_data()

    def load_category_data(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT category_name, description, uniqueness_type, detail_level, average_file_size
            FROM asset_categories
            WHERE category_id = ?
        """, (self.category_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            self.category_name.setText(row[0])
            self.description.setPlainText(row[1])
            index = self.uniqueness_type.findText(row[2])
            if index >= 0:
                self.uniqueness_type.setCurrentIndex(index)
            self.detail_level.setValue(row[3])
            self.average_file_size.setValue(row[4])

    def save_category(self):
        if not self.category_name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название категории.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        if self.category_id is None:
            cursor.execute("""
                INSERT INTO asset_categories
                (category_name, description, uniqueness_type, detail_level, average_file_size)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.category_name.text(),
                self.description.toPlainText(),
                self.uniqueness_type.currentText(),
                self.detail_level.value(),
                self.average_file_size.value()
            ))
        else:
            cursor.execute("""
                UPDATE asset_categories
                SET category_name = ?,
                    description = ?,
                    uniqueness_type = ?,
                    detail_level = ?,
                    average_file_size = ?
                WHERE category_id = ?
            """, (
                self.category_name.text(),
                self.description.toPlainText(),
                self.uniqueness_type.currentText(),
                self.detail_level.value(),
                self.average_file_size.value(),
                self.category_id
            ))

        conn.commit()
        conn.close()
        self.accept()


class AssetDialog(QDialog):
    def __init__(self, asset_id=None):
        super().__init__()
        self.asset_id = asset_id
        self.setWindowTitle("Добавление ассета" if asset_id is None else "Редактирование ассета")

        layout = QFormLayout()

        self.asset_name = QLineEdit()
        self.source_project = QLineEdit()

        self.creation_date = QDateEdit()
        self.creation_date.setCalendarPopup(True)
        self.creation_date.setDate(QDate.currentDate())

        self.polygon_count = QSpinBox()
        self.polygon_count.setMaximum(1000000)

        self.material_count = QSpinBox()
        self.material_count.setMaximum(1000)

        self.production_hours = QSpinBox()
        self.production_hours.setMaximum(10000)

        self.asset_price = QDoubleSpinBox()
        self.asset_price.setMaximum(1000000)
        self.asset_price.setDecimals(2)

        self.category_combo = QComboBox()
        self.load_categories()

        layout.addRow("Название ассета", self.asset_name)
        layout.addRow("Проект", self.source_project)
        layout.addRow("Дата создания", self.creation_date)
        layout.addRow("Полигоны", self.polygon_count)
        layout.addRow("Материалы", self.material_count)
        layout.addRow("Часы производства", self.production_hours)
        layout.addRow("Стоимость", self.asset_price)
        layout.addRow("Категория", self.category_combo)

        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_asset)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        if self.asset_id is not None:
            self.load_asset_data()

    def load_categories(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT category_id, category_name
            FROM asset_categories
            ORDER BY category_name
        """)

        for category_id, category_name in cursor.fetchall():
            self.category_combo.addItem(category_name, category_id)

        conn.close()

    def load_asset_data(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT asset_name, source_project, creation_date, polygon_count,
                   material_count, production_hours, asset_price, category_id
            FROM game_assets
            WHERE asset_id = ?
        """, (self.asset_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            self.asset_name.setText(row[0])
            self.source_project.setText(row[1])
            self.creation_date.setDate(QDate.fromString(row[2], "yyyy-MM-dd"))
            self.polygon_count.setValue(row[3])
            self.material_count.setValue(row[4])
            self.production_hours.setValue(row[5])
            self.asset_price.setValue(row[6])

            index = self.category_combo.findData(row[7])
            if index >= 0:
                self.category_combo.setCurrentIndex(index)

    def save_asset(self):
        if not self.asset_name.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название ассета.")
            return

        if not self.source_project.text().strip():
            QMessageBox.warning(self, "Ошибка", "Введите название проекта.")
            return

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        if self.asset_id is None:
            cursor.execute("""
                INSERT INTO game_assets
                (asset_name, source_project, creation_date, polygon_count,
                 material_count, production_hours, asset_price, category_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.asset_name.text(),
                self.source_project.text(),
                self.creation_date.date().toString("yyyy-MM-dd"),
                self.polygon_count.value(),
                self.material_count.value(),
                self.production_hours.value(),
                self.asset_price.value(),
                self.category_combo.currentData()
            ))
        else:
            cursor.execute("""
                UPDATE game_assets
                SET asset_name = ?,
                    source_project = ?,
                    creation_date = ?,
                    polygon_count = ?,
                    material_count = ?,
                    production_hours = ?,
                    asset_price = ?,
                    category_id = ?
                WHERE asset_id = ?
            """, (
                self.asset_name.text(),
                self.source_project.text(),
                self.creation_date.date().toString("yyyy-MM-dd"),
                self.polygon_count.value(),
                self.material_count.value(),
                self.production_hours.value(),
                self.asset_price.value(),
                self.category_combo.currentData(),
                self.asset_id
            ))

        conn.commit()
        conn.close()
        self.accept()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Справочники игровых ассетов")
        self.resize(1000, 550)

        layout = QVBoxLayout()

        info_label = QLabel("Никандрова Мария Андреевна, 2026, 3 курс, 2 группа")
        layout.addWidget(info_label)

        self.dictionary_combo = QComboBox()
        self.dictionary_combo.addItems([
            "Категории игровых ассетов",
            "Игровые ассеты"
        ])
        self.dictionary_combo.currentIndexChanged.connect(self.load_table)
        layout.addWidget(self.dictionary_combo)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по справочнику...")
        self.search_input.textChanged.connect(self.load_table)
        layout.addWidget(self.search_input)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Добавить")
        self.edit_button = QPushButton("Редактировать")
        self.delete_button = QPushButton("Удалить")
        self.refresh_button = QPushButton("Обновить")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.refresh_button)

        layout.addLayout(button_layout)

        self.add_button.clicked.connect(self.open_add_dialog)
        self.edit_button.clicked.connect(self.open_edit_dialog)
        self.delete_button.clicked.connect(self.delete_record)
        self.refresh_button.clicked.connect(self.load_table)

        self.setLayout(layout)
        self.load_table()

    def load_table(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        selected = self.dictionary_combo.currentText()
        search_text = self.search_input.text().strip()

        if selected == "Категории игровых ассетов":
            if search_text:
                cursor.execute("""
                    SELECT category_id, category_name, description,
                           uniqueness_type, detail_level, average_file_size
                    FROM asset_categories
                    WHERE category_name LIKE ?
                       OR description LIKE ?
                       OR uniqueness_type LIKE ?
                """, (
                    f"%{search_text}%",
                    f"%{search_text}%",
                    f"%{search_text}%"
                ))
            else:
                cursor.execute("""
                    SELECT category_id, category_name, description,
                           uniqueness_type, detail_level, average_file_size
                    FROM asset_categories
                """)

            headers = [
                "ID",
                "Название категории",
                "Описание",
                "Тип использования",
                "Уровень детализации",
                "Средний размер файла"
            ]

        else:
            if search_text:
                cursor.execute("""
                    SELECT asset_id, asset_name, source_project, creation_date,
                           polygon_count, material_count, production_hours, asset_price
                    FROM game_assets
                    WHERE asset_name LIKE ?
                       OR source_project LIKE ?
                """, (
                    f"%{search_text}%",
                    f"%{search_text}%"
                ))
            else:
                cursor.execute("""
                    SELECT asset_id, asset_name, source_project, creation_date,
                           polygon_count, material_count, production_hours, asset_price
                    FROM game_assets
                """)

            headers = [
                "ID",
                "Название ассета",
                "Проект",
                "Дата создания",
                "Полигоны",
                "Материалы",
                "Часы производства",
                "Стоимость"
            ]

        rows = cursor.fetchall()
        conn.close()

        self.table.setSortingEnabled(False)
        self.table.clear()
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        for row_index, row_data in enumerate(rows):
            for column_index, value in enumerate(row_data):
                sort_value = value
                display_value = value

                if selected == "Игровые ассеты" and column_index == 3:
                    date = QDate.fromString(value, "yyyy-MM-dd")
                    display_value = date.toString("dd.MM.yyyy")
                    sort_value = value

                item = SortableItem(str(display_value), sort_value)
                self.table.setItem(row_index, column_index, item)

        self.table.setColumnHidden(0, True)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSortingEnabled(True)

    def get_selected_id(self):
        selected_row = self.table.currentRow()

        if selected_row < 0:
            return None

        return int(self.table.item(selected_row, 0).text())

    def open_add_dialog(self):
        if self.dictionary_combo.currentText() == "Категории игровых ассетов":
            dialog = CategoryDialog()
        else:
            dialog = AssetDialog()

        if dialog.exec():
            self.load_table()

    def open_edit_dialog(self):
        record_id = self.get_selected_id()

        if record_id is None:
            QMessageBox.warning(self, "Редактирование", "Выберите запись для редактирования.")
            return

        if self.dictionary_combo.currentText() == "Категории игровых ассетов":
            dialog = CategoryDialog(record_id)
        else:
            dialog = AssetDialog(record_id)

        if dialog.exec():
            self.load_table()

    def delete_record(self):
        record_id = self.get_selected_id()

        if record_id is None:
            QMessageBox.warning(self, "Удаление", "Выберите запись для удаления.")
            return

        confirm = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Удалить выбранную запись?"
        )

        if confirm != QMessageBox.StandardButton.Yes:
            return

        selected = self.dictionary_combo.currentText()

        conn = sqlite3.connect(DB_NAME)
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        try:
            if selected == "Категории игровых ассетов":
                cursor.execute(
                    "DELETE FROM asset_categories WHERE category_id = ?",
                    (record_id,)
                )
            else:
                cursor.execute(
                    "DELETE FROM game_assets WHERE asset_id = ?",
                    (record_id,)
                )

            conn.commit()

        except sqlite3.IntegrityError:
            QMessageBox.warning(
                self,
                "Ошибка удаления",
                "Нельзя удалить категорию, так как с ней связаны игровые ассеты."
            )

        finally:
            conn.close()

        self.load_table()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())