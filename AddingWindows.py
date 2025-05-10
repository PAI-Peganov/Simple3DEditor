from QtApp import *


class ListStringsInput(QWidget):
    def __init__(self, min_lines_count, can_add_lines=False):
        super().__init__()
        self.min_lines_count = min_lines_count
        self.layout = QVBoxLayout()
        if can_add_lines:
            self.buttons = QHBoxLayout()
            self.add_button = QPushButton(text="+")
            self.add_button.clicked.connect(self.add_line)
            self.remove_button = QPushButton(text="-")
            self.remove_button.clicked.connect(self.remove_line)
            self.buttons.addWidget(self.add_button)
            self.buttons.addWidget(self.remove_button)
            self.layout.addWidget(self.buttons)
        self.lines = list()
        for _ in range(min_lines_count):
            self.add_line()

    def add_line(self):
        self.lines.append(QLineEdit())
        self.layout.addWidget(self.lines[-1])

    def remove_line(self):
        if len(self.lines) > self.min_lines_count:
            self.layout.removeWidget(self.lines[-1])
            self.lines.remove(self.lines[-1])

    def result_list(self):
        result = list()
        for el in self.lines:
            text = el.text().strip()
            if any(sign in text for sign in {",", ";", "/n", "/r"}):
                raise ValueError()
            result.append(text)
        return result


class AddingWidget(QDialog):
    def __init__(self, name: str, input_params: list[tuple], func: callable):
        super().__init__()
        self.setWindowTitle(name)
        self.setFixedSize(200, 350)

        self.layout = QFormLayout()
        self.inputs = dict()
        self.func = func

        for param in input_params:
            if isinstance(param[2], str):
                new_input = QLineEdit()
            elif isinstance(param[2], float):
                new_input = QDoubleSpinBox()
                new_input.setRange(-1000.0, 1000.0)
                new_input.setValue(0.0)
            else:
                new_input = ListStringsInput()
            self.inputs[param[0]] = new_input
            self.layout.addRow(param[1], new_input)

        self.submit_btn = QPushButton("Создать")
        self.submit_btn.clicked.connect(self.validate_input)

        self.layout.addWidget(self.submit_btn)

        self.setLayout(self.layout)

    def validate_input(self):
        result = dict()
        for param_name, qt_input in self.inputs.items():
            if isinstance(qt_input, QLineEdit):
                result[param_name] = qt_input.text().strip()
            elif isinstance(qt_input, QDoubleSpinBox):
                result[param_name] = qt_input.value()
            else:
                result[param_name] = qt_input.result_list()

        try:
            self.func(**result)
            self.accept()
        except Exception as e:
            QMessageBox.warning(self,
                                "Ошибка"
                                "{}".format(e),
                                file=sys.stderr)
