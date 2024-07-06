import sys
import os
import pandas as pd

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
                             QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
                             QSpacerItem, QProgressBar, QDialog)
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
                             QHBoxLayout, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem,
                             QHeaderView, QGridLayout, QSizePolicy, QSpacerItem, QProgressBar,
                             QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from ml.detection import get_df_from_predictions, detection
from registration_algorithms import threshold, base
from utils import set_max_count, set_duration, get_folder_name
from submit import get_submit_dataframe

from PyQt5.QtGui import QFontDatabase
from PyQt5.QtGui import QIcon


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
        self.setWindowIcon(QIcon('icon.ico'))

        # Load the custom fonts
        regular_id = QFontDatabase.addApplicationFont("MontserratAlternates-Regular.ttf")
        bold_id = QFontDatabase.addApplicationFont("MontserratAlternates-Bold.ttf")
        regular_font_family = QFontDatabase.applicationFontFamilies(regular_id)[0]
        bold_font_family = QFontDatabase.applicationFontFamilies(bold_id)[0]

        # Set the style sheet
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #CBDCCB;
                font-family: '{regular_font_family}';  /* Regular шрифт */
            }}
            QLabel {{
                font-size: 16px;
                font-weight: bold;
                font-family: '{bold_font_family}';  /* Bold шрифт */
            }}
            QLineEdit {{
                background-color: #FFFFFF;
                border: 1px solid #BDBDBD;
                padding: 5px;
            }}
            QPushButton {{
                background-color: #8BC34A;
                color: white;
                border: none;
                padding: 10px;
                font-size: 14px;
            }}
            QPushButton#downloadButton {{
                background-color: #E53935;
            }}
            QPushButton#downloadButton:hover {{
                background-color: #E54F4F;
            }}
            QPushButton:disabled {{
                background-color: #c5d8c5;
            }}
            QTableWidget {{
                background-color: #FFFFFF;
                border: none;
            }}
            #sidebar {{
                background-color: #B4D0B4;
                padding: 10px;
            }}
            #sidebar QLabel {{
                color: #345835;
                font-size: 16px;
                font-weight: bold;
                background-color: none;
                font-family: '{bold_font_family}';  /* Bold шрифт для сайдбар Label */
            }}
            #spacer_bottom {{
                background-color: none;
            }}
            QHeaderView::section {{
                font-weight: bold;
                font-family: '{bold_font_family}';  /* Bold шрифт для сайдбар Label */
                background-color: #68A069;  /* Задаем цвет фона заголовков */
                color: #ffffff;
            }}
            QTableWidget {{
                background-color: white; /* Цвет фона для нечетных строк */
                alternate-background-color: #f2f2f2; /* Цвет фона для четных строк */
            }}
        """)

        # Directory path
        self.directory_path = QLineEdit(self)
        self.directory_path.setPlaceholderText("Директория...")
        self.directory_path.setMinimumWidth(220)  # Adjust width as needed
        self.directory_path.setFixedHeight(30)

        # Browse button
        browse_button = QPushButton('📂', self)
        browse_button.setFixedWidth(30)  # Set fixed width for browse_button
        browse_button.setFixedHeight(30)
        browse_button.setCursor(Qt.PointingHandCursor)
        browse_button.clicked.connect(self.browse_directory)

        # run buttton
        run_button = QPushButton('Запустить', self)
        run_button.setMinimumWidth(100)  # Adjust minimum width as needed
        run_button.setCursor(Qt.PointingHandCursor)
        run_button.clicked.connect(self.process_data)

        # Spacer
        spacer = QWidget()
        spacer.setFixedSize(260, 3)
        spacer.setStyleSheet("background-color: #FFFFFF;")


        # recalculation buttton
        self.recalculation_button = QPushButton('Пересчитать', self)
        self.recalculation_button.setEnabled(False)
        self.recalculation_button.setMinimumWidth(100)  # Adjust minimum width as needed
        self.recalculation_button.setCursor(Qt.PointingHandCursor)
        self.recalculation_button.clicked.connect(self.recalculation_data)


        # Spacer bottom
        spacer_bottom = QWidget()
        spacer_bottom.setFixedSize(260, 40)
        spacer_bottom.setObjectName("spacer_bottom")

        # Download button
        self.download_button = QPushButton('Сохранить таблицу', self)
        self.download_button.setEnabled(False)
        self.download_button.setObjectName("downloadButton")
        self.download_button.setFixedWidth(200)
        self.download_button.setCursor(Qt.PointingHandCursor)
        self.download_button.clicked.connect(self.download_table)


        # Horizontal layout for centering the download button
        download_button_layout = QHBoxLayout()
        download_button_layout.addStretch(1)  # Add stretchable space on the left
        download_button_layout.addWidget(self.download_button)  # Add the button in the center
        download_button_layout.addStretch(1)  # Add stretchable space on the right


        # Horizontal layout for directory_path and browse_button
        directory_layout = QHBoxLayout()
        directory_layout.addWidget(self.directory_path)
        directory_layout.addWidget(browse_button)
        directory_layout.addStretch(1)

        self.current_page = 0
        self.rows_per_page = 50

        self.prev_button = QPushButton('Назад', self)
        self.prev_button.setCursor(Qt.PointingHandCursor)
        self.prev_button.clicked.connect(self.prev_page)
        self.prev_button.setEnabled(False)
        self.next_button = QPushButton('Вперед', self)
        self.next_button.setCursor(Qt.PointingHandCursor)
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)

        # Spacer_of_pagination
        spacer_of_pagination = QWidget()
        spacer_of_pagination.setFixedSize(1, 38)
        spacer_of_pagination.setStyleSheet("background-color: #FFFFFF;")

        pagination_layout = QHBoxLayout()
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(spacer_of_pagination)
        pagination_layout.addWidget(self.next_button)
        pagination_layout.setStretch(0, 1)  # Make prev_button take 50% of the width
        pagination_layout.setStretch(2, 1)  # Make next_button take 50% of the width

        # Sidebar layout
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(10)
        sidebar_layout.addWidget(QLabel('Выберите директорию:'))
        sidebar_layout.addLayout(directory_layout)
        sidebar_layout.addSpacing(20)  # Adjust spacing as needed
        sidebar_layout.addWidget(run_button)
        sidebar_layout.addWidget(spacer)
        sidebar_layout.addWidget(self.recalculation_button)
        sidebar_layout.addWidget(spacer_bottom)
        sidebar_layout.addLayout(download_button_layout) 
        sidebar_layout.addStretch(1)
        sidebar_layout.addWidget(self.progress_bar)

        # sidebar_layout.addLayout(pagination_layout)


        # Sidebar widget
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setMaximumWidth(300)

        # Table view
        self.table = QTableWidget(self)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setContentsMargins(0, 0, 0, 0)
        self.table.setAlternatingRowColors(True)
        self.table.itemChanged.connect(self.update_dataframe)
        self.table.cellClicked.connect(self.show_image_dialog)


        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.addWidget(self.table)
        # table_layout.addWidget(self.progress_bar)
        table_layout.addLayout(pagination_layout)


        # Main inner layout for sidebar and table
        main_inner_layout = QHBoxLayout()
        main_inner_layout.setContentsMargins(0, 0, 0, 0)
        main_inner_layout.setSpacing(0)
        main_inner_layout.addWidget(sidebar_widget)
        main_inner_layout.addLayout(table_layout)


        # Main layout for sidebar and table
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addLayout(main_inner_layout)

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
        self.df = set_duration(self.df)

        self.df['folder_name'] = self.df.apply(lambda row: get_folder_name(directory, row['folder_name'], row['image_name']), axis=1)

        self.current_page = 0
        self.display_table()
        self.download_button.setEnabled(True)
        self.recalculation_button.setEnabled(True)
        self.update_pagination_buttons()

    def recalculation_data(self):
        
        # self.df = base(self.df)
        # self.df = set_max_count(self.df)
        # self.df = set_duration(self.df)
        
        self.current_page = 0
        self.display_table()
        self.update_pagination_buttons()


    def show_image(self, row, column):
        if column == self.df.columns.get_loc("image_name"):
            folder_name = self.df.iloc[row]['folder_name']
            image_name = self.df.iloc[row]['image_name']
            full_image_path = os.path.join(folder_name, image_name)



    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def display_table(self):
        self.table.blockSignals(True)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.table.clear()
        start_index = self.current_page * self.rows_per_page
        end_index = min(start_index + self.rows_per_page, len(self.df))
        page_data = self.df.iloc[start_index:end_index]

        self.table.setColumnCount(len(self.df.columns))
        self.table.setRowCount(len(page_data.index))
        self.table.setHorizontalHeaderLabels(self.df.columns)

        for i in range(len(page_data.index)):
            row_number = page_data.index[i] + 1  # Получаем оригинальный номер строки из DataFrame
            self.table.setVerticalHeaderItem(i, QTableWidgetItem(str(row_number)))
            for j in range(len(page_data.columns)):
                self.table.setItem(i, j, QTableWidgetItem(str(page_data.iat[i, j])))

        # self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        self.table.blockSignals(False)

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
        row = item.row() + self.current_page * self.rows_per_page  # Вычисляем реальный индекс строки в датафрейме
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
            image_name = self.df.iloc[row]['image_name']
            directory_path = self.directory_path.text()
            image_path = f"{directory_path}/{image_name}"
            self.image_dialog = ImageDialog(image_path)
            self.image_dialog.setWindowModality(Qt.NonModal)
            self.image_dialog.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon.ico'))
    ex = AnimalRegistrationApp()
    ex.show()
    sys.exit(app.exec_())
