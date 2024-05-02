import sys

from grid import Grid
from automaton import FiniteAutomaton
from entity import BiologicalCell
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
)
from PySide6.QtCore import QTimer
from time import sleep

from random import randint


class SidebarWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Create sidebar widgets
        label1 = QLabel("Sidebar Item 1")
        label2 = QLabel("Sidebar Item 2")
        label3 = QLabel("Sidebar Item 3")

        self.setFixedWidth(100)

        # Create a layout for the sidebar
        layout = QVBoxLayout()
        layout.addWidget(label1)
        layout.addWidget(label2)
        layout.addWidget(label3)

        # Set the layout for the sidebar widget
        self.setLayout(layout)


class GridWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: black;")
        self.grid = []
        # self.setFixedSize(500, 500)

        self.layout = QGridLayout()
        self.layout.setSpacing(0)

        board_size = 100

        for row in range(board_size):
            new_row = []
            self.grid.append(new_row)
            for col in range(board_size):

                label = QLabel()
                new_row.append(label)

                self.layout.addWidget(label, row, col)

        self.setLayout(self.layout)

    def render_colors(self):
        print("I want to listen to music")
        for i in range(100):
            for j in range(100):
                self.grid[i][j].setStyleSheet(
                    f"background-color: rgb({randint(0,255)},{randint(0,255)},{randint(0,255)});"
                )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window with Sidebar")

        # Create sidebar widget instance
        self.sidebar_widget = SidebarWidget()

        # Create content widget instance
        self.content_widget = GridWidget()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.content_widget.render_colors)
        self.timer.start(0)  # Update every second

        # Create a main layout for the MainWindow
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.sidebar_widget)
        main_layout.addWidget(self.content_widget)

        # Create a central widget to hold the main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)

        # Set the central widget for the MainWindow
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    cell = BiologicalCell()

    grid = Grid(1000, 1000)
    automaton = FiniteAutomaton(grid)

    grid.place_entity(cell, 20, 20)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
