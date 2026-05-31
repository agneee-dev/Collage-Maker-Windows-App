# Grid Layout Maker Pro
# QGraphicsView-based main_window.py scaffold

from pathlib import Path
from PIL.ImageQt import ImageQt

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import *

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import *

from core.grid_generator import GridGenerator

from PySide6.QtCore import Qt, QSize, Signal

from PySide6.QtGui import (
    QPixmap,
    QIcon,
    QShortcut,
    QKeySequence,
)

from PIL import Image
from pathlib import Path

class ImageGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene())
        self.zoom_factor = 1.0
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)
        self.zoom_factor *= factor

    def zoom_in(self):
        self.scale(1.2, 1.2)

    def zoom_out(self):
        self.scale(1 / 1.2, 1 / 1.2)

    def fit_image(self):
        if self.scene().items():
            self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

class ImageGraphicsView(QGraphicsView):

    page_scroll_requested = Signal(int)

    def __init__(self):
        super().__init__()

        self.setScene(QGraphicsScene())

        self.zoom_factor = 1.0

        self.setDragMode(
            QGraphicsView.ScrollHandDrag
        )

        self.setTransformationAnchor(
            QGraphicsView.AnchorUnderMouse
        )

    def wheelEvent(self, event):

        # CTRL + Wheel => Zoom
        if event.modifiers() & Qt.ControlModifier:

            factor = (
                1.15
                if event.angleDelta().y() > 0
                else 1 / 1.15
            )

            self.scale(factor, factor)
            self.zoom_factor *= factor

            return

        # Wheel only => Page Navigation
        if event.angleDelta().y() > 0:
            self.page_scroll_requested.emit(-1)
        else:
            self.page_scroll_requested.emit(1)

    def zoom_in(self):

        self.scale(1.2, 1.2)

    def zoom_out(self):

        self.scale(1 / 1.2, 1 / 1.2)

    def fit_image(self):

        if self.scene().items():

            self.fitInView(
                self.sceneRect(),
                Qt.KeepAspectRatio
            )

class MainWindow(QMainWindow):
    def export_pdf(self):
        
        pdf_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF",
            "grid_layout.pdf",
            "PDF Files (*.pdf)"
        )
    
        if not pdf_path:
            return
    
        pages = []
    
        for page in self.generated_pages:
        
            if page.mode != "RGB":
                page = page.convert("RGB")
    
            pages.append(page)
    
        first = pages[0]
    
        first.save(
            pdf_path,
            save_all=True,
            append_images=pages[1:]
        )
    
        QMessageBox.information(
            self,
            "Export Complete",
            f"PDF saved:\n{pdf_path}"
        )
    def export_images(self, extension):

        output_dir = QFileDialog.getExistingDirectory(
            self,
            f"Select {extension.upper()} Export Folder"
        )

        if not output_dir:
            return

        output_dir = Path(output_dir)

        for idx, page in enumerate(
            self.generated_pages,
            start=1
        ):

            filename = (
                output_dir /
                f"page_{idx:03d}.{extension}"
            )

            page.save(filename)

        QMessageBox.information(
            self,
            "Export Complete",
            f"{len(self.generated_pages)} pages exported."
        )


    def export_pages(self):
        if not self.generated_pages:

            QMessageBox.warning(
                self,
                "No Pages",
                "Generate pages first."
            )
            return

        export_type = self.export_format.currentText()

        if export_type == "PDF":
            self.export_pdf()

        elif export_type == "JPG":
            self.export_images("jpg")

        elif export_type == "PNG":
            self.export_images("png")
    
    def handle_page_scroll(self, direction):
        if direction > 0:
            self.next_page()
        else:
            self.previous_page()


    def __init__(self):
        super().__init__()

        self.generated_pages = []
        self.current_page_index = 0

        self.setWindowTitle("Grid Layout Maker Pro")
        self.resize(1700, 1000)

        self.build_ui()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)

        top = QHBoxLayout()
        self.folder_input = QLineEdit()
        browse = QPushButton("Browse")
        browse.clicked.connect(self.select_folder)

        top.addWidget(self.folder_input)
        top.addWidget(browse)
        root.addLayout(top)

        splitter = QSplitter(Qt.Horizontal)
        root.addWidget(splitter)

        # self.image_list = QListWidget()
        # splitter.addWidget(self.image_list)

        left_panel = QWidget()  
        left_layout = QVBoxLayout(left_panel)

        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems([
            "List View",
            "Grid View"
        ])

        left_layout.addWidget(self.view_mode_combo)

        self.left_stack = QStackedWidget()

        # List View
        self.image_list = QListWidget()

        # Grid View
        self.thumbnail_list = QListWidget()
        self.thumbnail_list.setViewMode(QListWidget.IconMode)
        self.thumbnail_list.setResizeMode(QListWidget.Adjust)
        self.thumbnail_list.setMovement(QListView.Static)
        self.thumbnail_list.setWrapping(True)
        self.thumbnail_list.setUniformItemSizes(True)
        self.thumbnail_list.setIconSize(QSize(120, 120))
        self.thumbnail_list.setGridSize(QSize(140, 160))
        self.thumbnail_list.setSpacing(10)

        self.left_stack.addWidget(self.image_list)
        self.left_stack.addWidget(self.thumbnail_list)

        left_layout.addWidget(self.left_stack)

        self.view_mode_combo.currentIndexChanged.connect(
            self.left_stack.setCurrentIndex
        )

        splitter.addWidget(left_panel)
        


        center = QWidget()
        center_layout = QVBoxLayout(center)

        nav = QHBoxLayout()
        self.zoom_out_btn = QPushButton("-")
        self.zoom_in_btn = QPushButton("+")
        self.fit_btn = QPushButton("Fit")
        self.prev_btn = QPushButton("Prev")
        self.next_btn = QPushButton("Next")
        self.page_label = QLabel("Page 0/0")

        nav.addWidget(self.zoom_out_btn)
        nav.addWidget(self.zoom_in_btn)
        nav.addWidget(self.fit_btn)
        nav.addStretch()
        nav.addWidget(self.prev_btn)
        nav.addWidget(self.page_label)
        nav.addWidget(self.next_btn)

        center_layout.addLayout(nav)

        self.preview_view = ImageGraphicsView()
        self.preview_view.page_scroll_requested.connect(
            self.handle_page_scroll
        )
        center_layout.addWidget(self.preview_view)

        splitter.addWidget(center)

        settings = QWidget()
        form = QFormLayout(settings)

        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["A4", "A3", "Letter"])

        self.cols_spin = QSpinBox()
        self.cols_spin.setValue(2)

        self.rows_spin = QSpinBox()
        self.rows_spin.setValue(3)

        self.margin_spin = QDoubleSpinBox()
        self.margin_spin.setValue(1.0)

        self.padding_spin = QDoubleSpinBox()
        self.padding_spin.setValue(0.3)

        self.page_numbers = QCheckBox()
        self.page_numbers.setChecked(True)

        self.export_format = QComboBox()
        self.export_format.addItems([
            "PDF",
            "JPG",
            "PNG"
        ])

        self.generate_btn = QPushButton("Generate")
        self.export_btn = QPushButton("Export")

        form.addRow("Page Size", self.page_size_combo)
        form.addRow("Columns", self.cols_spin)
        form.addRow("Rows", self.rows_spin)
        form.addRow("Margin", self.margin_spin)
        form.addRow("Grid Padding", self.padding_spin)
        form.addRow("Page Numbers", self.page_numbers)
        form.addRow("Export Format", self.export_format)
        form.addRow(self.generate_btn)
        form.addRow(self.export_btn)

        splitter.addWidget(settings)

        self.zoom_in_btn.clicked.connect(self.preview_view.zoom_in)
        self.zoom_out_btn.clicked.connect(self.preview_view.zoom_out)
        self.fit_btn.clicked.connect(self.preview_view.fit_image)
        self.generate_btn.clicked.connect(self.generate_pages)
        self.prev_btn.clicked.connect(self.previous_page)
        self.next_btn.clicked.connect(self.next_page)

        self.export_btn.clicked.connect(self.export_pages)


        QShortcut(
            QKeySequence(Qt.Key_Left),
            self,
            self.previous_page
        )

        QShortcut(
            QKeySequence(Qt.Key_Right),
            self,
            self.next_page
        )

        QShortcut(
            QKeySequence("Ctrl++"),
            self,
            self.preview_view.zoom_in
        )

        QShortcut(
            QKeySequence("Ctrl+-"),
            self,
            self.preview_view.zoom_out
        )

        QShortcut(
            QKeySequence("Ctrl+0"),
            self,
            self.preview_view.fit_image
        )

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_input.setText(folder)
            self.load_folder_images(folder)

    def load_folder_images(self, folder):

        self.image_list.clear()
        self.thumbnail_list.clear()

        valid_ext = {
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".webp"
        }

        for p in sorted(Path(folder).iterdir()):

            if not p.is_file():
                continue

            if p.suffix.lower() not in valid_ext:
                continue

            # List View
            self.image_list.addItem(p.name)

            # Grid View
            pixmap = QPixmap(str(p))

            if not pixmap.isNull():

                thumb = pixmap.scaled(
                    120,
                    120,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                item = QListWidgetItem(
                    QIcon(thumb),
                    p.name
                )

                item.setToolTip(str(p))

                self.thumbnail_list.addItem(item)

    def generate_pages(self):
        generator = GridGenerator(
            page_size=self.page_size_combo.currentText(),
            cols=self.cols_spin.value(),
            rows=self.rows_spin.value(),
            margin_cm=self.margin_spin.value(),
            padding_cm=self.padding_spin.value(),
            show_page_numbers=self.page_numbers.isChecked(),
        )
        self.generated_pages = generator.generate_pages(self.folder_input.text())
        self.current_page_index = 0
        self.show_page()

    def show_page(self):
        if not self.generated_pages:
            return
        page = self.generated_pages[self.current_page_index]
        qt_image = ImageQt(page)
        pixmap = QPixmap.fromImage(qt_image)

        scene = self.preview_view.scene()
        scene.clear()
        scene.addPixmap(pixmap)
        scene.setSceneRect(pixmap.rect())

        self.page_label.setText(
            f"Page {self.current_page_index + 1}/{len(self.generated_pages)}"
        )

    def previous_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self.show_page()

    def next_page(self):
        if self.current_page_index < len(self.generated_pages) - 1:
            self.current_page_index += 1
            self.show_page()
