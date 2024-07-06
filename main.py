import sys
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QGridLayout)
from PyQt5.QtCore import Qt
from ml.detection import get_df_from_predictions, detection

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

        layout.addWidget(title_label, 0, 0, 1, 3)
        layout.addLayout(dir_layout, 1, 0, 1, 3)
        layout.addLayout(button_layout, 2, 0, 1, 3)
        layout.addWidget(self.table, 3, 0, 1, 3)

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
        predictions = detection(src_dir=directory)
        self.df = get_df_from_predictions(list_predictions=predictions)
        
        self.display_table()
        self.download_button.setEnabled(True)
    
    def display_table(self):
        self.table.clear()
        self.table.setColumnCount(len(self.df.columns))
        self.table.setRowCount(len(self.df.index))
        self.table.setHorizontalHeaderLabels(self.df.columns)
        
        for i in range(len(self.df.index)):
            for j in range(len(self.df.columns)):
                self.table.setItem(i, j, QTableWidgetItem(str(self.df.iat[i, j])))
        
        self.table.resizeColumnsToContents()
    
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
