import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
                             QHBoxLayout, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QGridLayout, QSizePolicy, QSpacerItem, QProgressBar,
                             QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from ml.detection import get_df_from_predictions, detection

class ImageDialog(QDialog):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle('Изображение')
        layout = QVBoxLayout()
        self.label = QLabel()

        pixmap = QPixmap(image_path)
        # Calculate the size based on a percentage of the screen size
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        relative_width = int(screen_size.width() * 0.5)  # Adjust as needed
        scaled_pixmap = pixmap.scaledToWidth(relative_width, Qt.SmoothTransformation)

        self.label.setPixmap(scaled_pixmap)
        layout.addWidget(self.label)
        self.setLayout(layout)


class AnimalRegistrationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Формирование регистраций животных')
        self.setGeometry(100, 100, 1000, 700)

        self.setStyleSheet("""
            QWidget {
                background-color: #E8F5E9;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #BDBDBD;
                padding: 5px;
            }
            QPushButton {
                background-color: #8BC34A;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton#downloadButton {
                background-color: #E53935;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #BDBDBD;
            }
        """)

        self.current_page = 0
        self.rows_per_page = 100

        layout = QGridLayout()

        title_label = QLabel('Формирование регистраций животных', self)
        title_label.setAlignment(Qt.AlignCenter)

        self.directory_path = QLineEdit(self)

        browse_button = QPushButton('...', self)
        browse_button.clicked.connect(self.browse_directory)

        run_button = QPushButton('Запустить', self)
        run_button.clicked.connect(self.process_data)

        self.download_button = QPushButton('Скачать таблицу', self)
        self.download_button.setEnabled(False)
        self.download_button.setObjectName("downloadButton")
        self.download_button.clicked.connect(self.download_table)

        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel('Выберите директорию:'))
        dir_layout.addWidget(self.directory_path)
        dir_layout.addWidget(browse_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(run_button)
        button_layout.addWidget(self.download_button)

        self.table = QTableWidget(self)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellClicked.connect(self.show_image_dialog)

        pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton('Назад', self)
        self.prev_button.clicked.connect(self.prev_page)
        self.prev_button.setEnabled(False)
        self.next_button = QPushButton('Вперед', self)
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)
        pagination_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.next_button)

        layout.addWidget(title_label, 0, 0, 1, 3)
        layout.addLayout(dir_layout, 1, 0, 1, 3)
        layout.addLayout(button_layout, 2, 0, 1, 3)
        layout.addWidget(self.table, 3, 0, 1, 3)
        layout.addLayout(pagination_layout, 4, 0, 1, 3)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar, 5, 0, 1, 3)

        self.setLayout(layout)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Выберите директорию')
        if directory:
            self.directory_path.setText(directory)

    def process_data(self):
        directory = self.directory_path.text()
        if not directory:
            QMessageBox.warning(self, 'Предупреждение', 'Пожалуйста, выберите директорию.')
            return

        self.progress_bar.setValue(0)
        predictions = detection(src_dir=directory, progress_callback=self.update_progress)
        self.df = get_df_from_predictions(list_predictions=predictions)
        # FIXME add here post processing

        self.current_page = 0
        self.display_table()
        self.download_button.setEnabled(True)
        self.update_pagination_buttons()

    def show_image(self, row, column):
        if column == self.df.columns.get_loc("image_name"):
            folder_name = self.df.iloc[row]['folder_name']
            image_name = self.df.iloc[row]['image_name']
            full_image_path = os.path.join(folder_name, image_name)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def display_table(self):
        self.table.clear()
        start_index = self.current_page * self.rows_per_page
        end_index = min(start_index + self.rows_per_page, len(self.df))
        page_data = self.df.iloc[start_index:end_index]

        self.table.setColumnCount(len(self.df.columns))
        self.table.setRowCount(len(page_data.index))
        self.table.setHorizontalHeaderLabels(self.df.columns)

        for i in range(len(page_data.index)):
            for j in range(len(page_data.columns)):
                self.table.setItem(i, j, QTableWidgetItem(str(page_data.iat[i, j])))

        self.table.resizeColumnsToContents()

    def update_pagination_buttons(self):
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled((self.current_page + 1) * self.rows_per_page < len(self.df))

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_table()
            self.update_pagination_buttons()

    def next_page(self):
        if (self.current_page + 1) * self.rows_per_page < len(self.df):
            self.current_page += 1
            self.display_table()
            self.update_pagination_buttons()

    def download_table(self):
        file_path, _ = QFileDialog.getSaveFileName(self, 'Сохранить файл', '', 'Excel files (*.xlsx)')
        if file_path:
            self.df.to_excel(file_path, index=False)
            QMessageBox.information(self, 'Успех', 'Таблица успешно сохранена.')

    def show_image_dialog(self, row, column):
        if column == self.df.columns.get_loc('image_name'):
            folder_name = self.df.iloc[row]['folder_name']
            image_name = self.df.iloc[row]['image_name']
            full_image_path = os.path.join(folder_name, image_name)
            self.image_dialog = ImageDialog(full_image_path)
            self.image_dialog.setWindowModality(Qt.NonModal)
            self.image_dialog.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AnimalRegistrationApp()
    ex.show()
    sys.exit(app.exec_())