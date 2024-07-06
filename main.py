import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
                             QHBoxLayout, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QGridLayout, QSizePolicy, QSpacerItem, QProgressBar,
                             QDialog)
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
                             QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from ml.detection import get_df_from_predictions, detection
from registration_algorithms import threshold, base
from max_count import set_max_count
from submit import get_submit_dataframe


class ImageDialog(QDialog):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle('Изображение')
        layout = QVBoxLayout()
        self.label = QLabel()

        pixmap = QPixmap(image_path)
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        relative_width = int(screen_size.width() * 0.5)
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

        # Set the style sheet
        self.setStyleSheet("""
            QWidget {
                background-color: #CBDCCB;
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
                background-color: #617C8A;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton#downloadButton {
                background-color: #CF726B;
            }
            QPushButton#downloadButton:hover {
                background-color: #D68982;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: none;
            }
            #sidebar {
                background-color: #B4D0B4;
                padding: 10px;
            }
            #sidebar QLabel {
                color: #345835;
                font-size: 16px;
                font-weight: bold;
                background-color: none;
            }
            #spacer_bottom {
                background-color: none;
            }
        """)

        # Directory path
        self.directory_path = QLineEdit(self)
        self.directory_path.setPlaceholderText("Директория...")
        self.directory_path.setMinimumWidth(220)  # Adjust width as needed
        self.directory_path.setFixedHeight(30)

        # Browse button
        browse_button = QPushButton('...', self)
        browse_button.setFixedWidth(30)  # Set fixed width for browse_button
        browse_button.setFixedHeight(30)
        browse_button.clicked.connect(self.browse_directory)

        # run buttton
        run_button = QPushButton('Запустить', self)
        run_button.setMinimumWidth(100)  # Adjust minimum width as needed
        run_button.clicked.connect(self.process_data)

        # Spacer
        spacer = QWidget()
        spacer.setFixedSize(260, 3)
        spacer.setStyleSheet("background-color: #FFFFFF;")

        # Spacer bottom
        spacer_bottom = QWidget()
        spacer_bottom.setFixedSize(260, 40)
        spacer_bottom.setObjectName("spacer_bottom")

        # Download button
        self.download_button = QPushButton('Скачать таблицу', self)
        self.download_button.setEnabled(False)
        self.download_button.setObjectName("downloadButton")
        self.download_button.setFixedWidth(150)
        self.download_button.setCursor(Qt.PointingHandCursor)
        self.download_button.clicked.connect(self.download_table)

        # Horizontal layout for directory_path and browse_button
        directory_layout = QHBoxLayout()
        directory_layout.addWidget(self.directory_path)
        directory_layout.addWidget(browse_button)
        directory_layout.addStretch(1)

        self.current_page = 0
        self.rows_per_page = 100

        self.prev_button = QPushButton('Назад', self)
        self.prev_button.clicked.connect(self.prev_page)
        self.prev_button.setEnabled(False)
        self.next_button = QPushButton('Вперед', self)
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)

        pagination_layout = QHBoxLayout()
        pagination_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.next_button)

        # Sidebar layout
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(10)
        sidebar_layout.addWidget(QLabel('Выберите директорию:'))
        sidebar_layout.addLayout(directory_layout)
        sidebar_layout.addSpacing(20)  # Adjust spacing as needed
        sidebar_layout.addWidget(run_button)
        sidebar_layout.addWidget(spacer)
        sidebar_layout.addWidget(spacer_bottom)
        sidebar_layout.addWidget(self.download_button)
        sidebar_layout.addStretch(1)
        sidebar_layout.addLayout(pagination_layout)
        sidebar_layout.addWidget(self.progress_bar)

        # Sidebar widget
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setMaximumWidth(300)

        # Table view
        self.table = QTableWidget(self)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setContentsMargins(0, 0, 0, 0)
        self.table.itemChanged.connect(self.update_dataframe)
        self.table.cellClicked.connect(self.show_image_dialog)

        # Main inner layout for sidebar and table
        main_inner_layout = QHBoxLayout()
        main_inner_layout.setContentsMargins(0, 0, 0, 0)
        main_inner_layout.setSpacing(0)
        main_inner_layout.addWidget(sidebar_widget)
        main_inner_layout.addWidget(self.table)

        # Main layout for sidebar and table
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addLayout(main_inner_layout)
        pagination_layout = QHBoxLayout()
        pagination_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.next_button)

        # Final
        self.setLayout(main_layout)

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

        # Постпроцессинг
        self.df = base(self.df)
        self.df = set_max_count(self.df)

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
        # self.table.blockSignals(True)
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

        self.table.blockSignals(False)

    def update_dataframe(self, item):
        row = item.row()
        column = item.column()
        value = item.text()
        self.df.iat[row, column] = value

    def download_table(self):
        file_path, _ = QFileDialog.getSaveFileName(self, 'Сохранить файл', '', 'CSV files (*.csv)')
        if file_path:
            self.df = get_submit_dataframe(self.df)
            self.df.to_csv(file_path, index=False, sep=',')
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
