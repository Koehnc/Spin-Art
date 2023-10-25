import sys
import multiprocessing
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QFileDialog, QLineEdit, QLabel
from PyQt5.QtGui import QPixmap, QPainter, QPen, QIntValidator
from PyQt5.QtCore import Qt, QPoint, QTimer, QObject

from Spinboard import Spinboard

class ImageDisplayApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Handle the drawing code
        self.image = "images/Monroe_crop.png"
        self.process = None

        # Handle the options
        self.numThreads = QLineEdit()
        self.numThreads.setValidator(QIntValidator())  # Restrict input to integers
        self.numThreads.setText("1000")

        self.numNails = QLineEdit()
        self.numNails.setValidator(QIntValidator())  # Restrict input to integers
        self.numNails.setText("100")

        # Set up the main window with the updated geometry
        self.setWindowTitle("Image Display App")
        self.setGeometry(500, 300, 10, 10)  # Updated geometry
        self.setMaximumSize(10,10)

        # Create a central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create layout for central widget
        central_layout = QVBoxLayout(self.central_widget)

        # Create an options bar widget
        control_bar = QWidget()
        control_buttons_layout = QHBoxLayout(control_bar)
        input_bar = QWidget()
        input_bar_layout = QHBoxLayout(input_bar)
        central_layout.addWidget(control_bar)
        central_layout.addWidget(input_bar)

        # Create left and right QGraphicsViews and place them in a horizontal layout
        views_layout = QHBoxLayout()
        self.left_view = QGraphicsView()
        self.right_view = QGraphicsView()
        views_layout.addWidget(self.left_view)
        views_layout.addWidget(self.right_view)

        # Create QGraphicsScenes for left and right views
        self.left_scene = QGraphicsScene()
        self.right_scene = QGraphicsScene()

        # Set scenes for left and right views
        self.left_view.setScene(self.left_scene)
        self.right_view.setScene(self.right_scene)

        # Load and display initial images in QGraphicsViews
        self.load_and_display_images()

        # Add the views_layout (containing the views) to the central layout
        central_layout.addLayout(views_layout)

        # Create buttons for the options bar
        load_button = QPushButton("Load Image")
        runButton = QPushButton("Run SpinBoard")
        stop_button = QPushButton("Stop SpinBoard")

        # Connect functions to button clicks
        runButton.clicked.connect(self.runSpinboard)
        load_button.clicked.connect(self.load_left_image)  # Connect the load button to a function
        stop_button.clicked.connect(self.stopSpinboard)  # Connect the clear button to a function

        # Add buttons to the options layout
        control_buttons_layout.addWidget(load_button)
        control_buttons_layout.addWidget(runButton)
        control_buttons_layout.addWidget(stop_button)
        
        # Add QLabels and QLineEdits to the input bar
        input_bar_layout.addWidget(QLabel("Number of Nails:"))
        input_bar_layout.addWidget(self.numNails)
        input_bar_layout.addWidget(QLabel("Number of Threads:"))
        input_bar_layout.addWidget(self.numThreads)


    def load_and_display_images(self):
        self.left_scene.clear()
        left_image = QPixmap(self.image)
        left_image_item = QGraphicsPixmapItem(left_image)
        self.left_scene.addItem(left_image_item)
        left_image_size = left_image.size()
        self.left_view.setFixedSize(left_image_size)
        self.left_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.left_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.right_scene.clear()
        right_image = QPixmap("Spinboard.png")
        right_image_item = QGraphicsPixmapItem(right_image)
        self.right_scene.addItem(right_image_item)
        right_image_size = right_image.size()
        self.right_view.setFixedSize(right_image_size)
        self.right_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.right_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def runSpinboard(self):
        if (self.spinboard.numNails == 0):
            self.spinboard = Spinboard(self.image, int(self.numNails.text()))
            self.process = multiprocessing.Process(target=self.spinboard.drawLines, args=(int(self.numThreads.text()),))
            self.process.start()
        else:
            self.process = multiprocessing.Process(target=self.spinboard.drawLines, args=(int(self.numThreads.text()),))
            self.process.start()
        
        timer = QTimer(self)
        timer.timeout.connect(self.load_and_display_images)
        timer.start(100)
        
    def stopSpinboard(self):
        if self.process and self.process.is_alive():
            self.process.terminate()

        # Clear the image in the right QGraphicsView
        # self.right_scene.clear()
        # self.spinboard = Spinboard(self.image, nails=[])
        # self.load_and_display_images()

    def load_left_image(self):
        # Function to load and display a user-selected left image
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)", options=options)
        if file_path:
            self.image = file_path
            self.spinboard = Spinboard(self.image, nails=[])
            self.stopSpinboard()

    def mousePressEvent(self, event):
        # Handle mouse clicks in the right QGraphicsView
        if event.button() == Qt.LeftButton:
            scene_pos = self.right_view.mapTo(self.central_widget, QPoint(0, 0))
            click_pos = event.pos() - scene_pos
            
            # Draw a point at the clicked position in the right QGraphicsView
            if (click_pos.x() >= 0 and click_pos.y() >= 0):
                self.draw_point((click_pos.x(), click_pos.y()))

    def draw_point(self, pos):
        self.spinboard.addNail(pos)
        self.load_and_display_images()

    def closeEvent(self, event):
        # Handle the window close event
        if self.process and self.process.is_alive():
            self.process.terminate()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageDisplayApp()
    window.show()
    sys.exit(app.exec_())
