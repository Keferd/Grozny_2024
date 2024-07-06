import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt

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
            #header {
                background-color: #68A069;
                color: white;
                font-size: 20px;
                font-weight: bold;
                padding: 10px 30px; /* Left padding adjusted */
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
            #footer {
                background-color: #68A069;
                color: #345835;
                font-size: 14px;
                font-weight: bold;
                text-align: right;
                padding: 10px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = QLabel('Формирование регистраций животных', self)
        header.setObjectName("header")
        # main_layout.addWidget(header)

        # Main layout for sidebar and table
        main_inner_layout = QHBoxLayout()
        main_inner_layout.setContentsMargins(0, 0, 0, 0)
        main_inner_layout.setSpacing(0)

        # Sidebar layout
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(10)

        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setLayout(sidebar_layout)

        self.directory_path = QLineEdit(self)
        self.directory_path.setPlaceholderText("Директория...")
        self.directory_path.setMinimumWidth(220)  # Adjust width as needed
        self.directory_path.setFixedHeight(30)
        
        browse_button = QPushButton('...', self)
        browse_button.setFixedWidth(30)  # Set fixed width for browse_button
        browse_button.setFixedHeight(30)
        browse_button.clicked.connect(self.browse_directory)
        
        run_button = QPushButton('Запустить', self)
        run_button.setMinimumWidth(100)  # Adjust minimum width as needed
        run_button.clicked.connect(self.process_data)

        spacer = QWidget()
        spacer.setFixedSize(260, 3)
        spacer.setStyleSheet("background-color: #FFFFFF;")

        # Spacer with 40 pixels height
        spacer_bottom = QWidget()
        spacer_bottom.setFixedSize(260, 40)
        spacer_bottom.setObjectName("spacer_bottom")
        
        self.download_button = QPushButton('Скачать таблицу', self)
        self.download_button.setEnabled(False)
        self.download_button.setObjectName("downloadButton")
        self.download_button.setFixedWidth(150)
        self.download_button.setCursor(Qt.PointingHandCursor)
        self.download_button.clicked.connect(self.download_table)
        
        sidebar_layout.addWidget(QLabel('Выберите директорию:'))
        
        # Horizontal layout for directory_path and browse_button
        directory_layout = QHBoxLayout()
        directory_layout.addWidget(self.directory_path)
        directory_layout.addWidget(browse_button)
        directory_layout.addStretch(1)
        
        sidebar_layout.addLayout(directory_layout)
        
        # Add margin above the run_button
        sidebar_layout.addSpacing(20)  # Adjust spacing as needed
        
        sidebar_layout.addWidget(run_button)
        sidebar_layout.addWidget(spacer)
        sidebar_layout.addWidget(spacer_bottom)
        sidebar_layout.addWidget(self.download_button)
        sidebar_layout.addStretch(1)

        sidebar_widget.setMaximumWidth(300)
        main_inner_layout.addWidget(sidebar_widget)

        # Table view
        self.table = QTableWidget(self)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setContentsMargins(0, 0, 0, 0)
        self.table.itemChanged.connect(self.update_dataframe)
        main_inner_layout.addWidget(self.table)

        main_layout.addLayout(main_inner_layout)

        # Footer
        # footer = QLabel('Это база', self)
        # footer.setObjectName("footer")
        # footer.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # main_layout.addWidget(footer)

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
        
        # Example data processing, create a DataFrame
        data = {
            'Исполнитель': ['Львовский городской округ'] * 5,
            'Группа тем': ['Благоустройство'] * 5,
            'Текст инцидента': ['Текст инцидента'] * 5,
            'Тема': ['Ямы во дворах'] * 5,
        }
        self.df = pd.DataFrame(data)
        
        self.display_table()
        self.download_button.setEnabled(True)

    def display_table(self):
        self.table.blockSignals(True)
        self.table.clear()
        self.table.setColumnCount(len(self.df.columns))
        self.table.setRowCount(len(self.df.index))
        self.table.setHorizontalHeaderLabels(self.df.columns)
        
        for i in range(len(self.df.index)):
            for j in range(len(self.df.columns)):
                item = QTableWidgetItem(str(self.df.iat[i, j]))
                self.table.setItem(i, j, item)
        
        self.table.resizeColumnsToContents()
        self.table.blockSignals(False)

    def update_dataframe(self, item):
        row = item.row()
        column = item.column()
        value = item.text()
        self.df.iat[row, column] = value

    def download_table(self):
        file_path, _ = QFileDialog.getSaveFileName(self, 'Сохранить файл', '', 'Excel files (*.xlsx)')
        if file_path:
            self.df.to_excel(file_path, index=False)
            QMessageBox.information(self, 'Успех', 'Таблица успешно сохранена.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AnimalRegistrationApp()
    ex.show()
    sys.exit(app.exec_())
