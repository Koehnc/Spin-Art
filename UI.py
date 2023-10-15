import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QFileDialog
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint

from Spinboard import Spinboard

class ImageDisplayApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Handle the drawing code
        self.image = "images/cat.png"
        self.spinboard = Spinboard(self.image, nails=[])

        # Set up the main window with the updated geometry
        self.setWindowTitle("Image Display App")
        self.setGeometry(500, 300, 825, 500)  # Updated geometry

        # Create a central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create layout for central widget
        central_layout = QVBoxLayout(self.central_widget)

        # Create an options bar widget
        options_bar = QWidget()
        options_layout = QHBoxLayout(options_bar)
        central_layout.addWidget(options_bar)

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
        runButton = QPushButton("Run SpinBoard")
        load_button = QPushButton("Load Left Image")  # New button for loading left image
        clear_button = QPushButton("Clear Right Image")  # New button for clearing right image

        # Connect functions to button clicks
        runButton.clicked.connect(self.runSpinboard)
        load_button.clicked.connect(self.load_left_image)  # Connect the load button to a function
        clear_button.clicked.connect(self.clear_right_image)  # Connect the clear button to a function

        # Add buttons to the options layout
        options_layout.addWidget(runButton)
        options_layout.addWidget(load_button)
        options_layout.addWidget(clear_button)

    def load_and_display_images(self):
        # Load and display initial images as QPixmapItems in left and right scenes
        left_image_item = QGraphicsPixmapItem()
        left_image_item.setPixmap(QPixmap(self.image).scaledToWidth(400))
        self.left_scene.addItem(left_image_item)

        right_image_item = QGraphicsPixmapItem()
        right_image_item.setPixmap(QPixmap("Spinboard.png").scaledToWidth(400))
        self.right_scene.addItem(right_image_item)

    def runSpinboard(self):
        if (self.spinboard.getNumNails() == 0):
            self.spinboard = Spinboard(self.image)
            self.spinboard.drawLines(100000)
        else:
            self.spinboard.drawLines(100000)
        
    def clear_right_image(self):
        # Clear the image in the right QGraphicsView
        self.right_scene.clear()
        self.spinboard = Spinboard(self.image, nails=[])
        self.load_and_display_images()

    def load_left_image(self):
        # Function to load and display a user-selected left image
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)", options=options)
        if file_path:
            left_image_item = QGraphicsPixmapItem()
            left_image_item.setPixmap(QPixmap(file_path).scaledToWidth(400))
            self.image = file_path
            self.left_scene.clear()  # Clear the existing scene
            self.left_scene.addItem(left_image_item)

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageDisplayApp()
    window.show()
    sys.exit(app.exec_())

