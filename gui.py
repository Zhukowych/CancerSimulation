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
from time import perf_counter


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
    def __init__(self, automaton):
        super().__init__()
        self.setStyleSheet("background-color: black;")
        self.automaton = automaton
        self.grid = []
        # self.setFixedSize(500, 500)

        self.layout = QGridLayout()
        self.layout.setSpacing(0)

        for row in range(self.automaton.grid.height):
            new_row = []
            self.grid.append(new_row)
            for col in range(self.automaton.grid.width):

                label = QLabel()
                new_row.append(label)

                self.layout.addWidget(label, row, col)

        self.setLayout(self.layout)

    def render_colors(self):
        start = perf_counter()
        for i in range(self.automaton.grid.height):
            for j in range(self.automaton.grid.width):
                self.grid[i][j].setStyleSheet(
                    f"background-color: {self.automaton.grid.grid[i][j].color};"
                )
        print("render:", perf_counter() - start)

        start = perf_counter()
        self.automaton.next()
        print("simulation:", perf_counter() - start)


class MainWindow(QMainWindow):
    def __init__(self, height: int, width: int):
        super().__init__()

        self.setWindowTitle("Main Window with Sidebar")

        # Create sidebar widget instance
        self.sidebar_widget = SidebarWidget()

        # Create content widget instance
        cell = BiologicalCell()

        grid = Grid(width, height)
        automaton = FiniteAutomaton(grid)

        grid.place_entity(cell, 2, 2)

        self.content_widget = GridWidget(automaton)

        self.timer = QTimer(self)
        self.start_automaton()
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

    def start_automaton(self):
        self.timer.timeout.connect(self.content_widget.render_colors)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(100, 100)
    window.show()

    # window.start_automaton(grid)

    sys.exit(app.exec())
