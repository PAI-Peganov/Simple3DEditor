from QtApp import *


class AddingWidget(QDialog):
    def __init__(self, ):
        super().__init__()
        self.setWindowTitle("Ввод данных")
        # self.setFixedSize(300, 200)

        self.layout = QVBoxLayout()

        # Поля для ввода
        self.name_label = QLabel("Имя:")
        self.name_input = QLineEdit()

        self.age_label = QLabel("Возраст:")
        self.age_input = QLineEdit()

        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()

        # Кнопка подтверждения
        self.submit_btn = QPushButton("Подтвердить")
        self.submit_btn.clicked.connect(self.validate_input)

        # Добавляем элементы в layout
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.age_label)
        self.layout.addWidget(self.age_input)
        self.layout.addWidget(self.email_label)
        self.layout.addWidget(self.email_input)
        self.layout.addWidget(self.submit_btn)

        self.setLayout(self.layout)

    def validate_input(self):
        name = self.name_input.text().strip()
        age = self.age_input.text().strip()
        email = self.email_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите имя")
            return

        if not age.isdigit():
            QMessageBox.warning(self, "Ошибка", "Возраст должен быть числом")
            return

        self.accept()  # Закрываем диалог с результатом QDialog.Accepted