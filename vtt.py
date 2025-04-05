import sys
import os
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QToolBar, QFileDialog, QGraphicsPixmapItem, QSpinBox,
    QDockWidget, QTableWidget, QTableWidgetItem, QPushButton,
    QVBoxLayout, QWidget, QDialog, QLabel, QLineEdit, QComboBox,
    QDialogButtonBox, QGraphicsTextItem, QHBoxLayout, QTextEdit,
    QMenu, QInputDialog
)
from PySide6.QtGui import QPixmap, QPen, QPainter, QBrush, QColor, QFont, QTransform
from PySide6.QtCore import Qt, QPointF, QRectF, QDir, QRandomGenerator, QDateTime


# Dialog for selecting and naming tokens
class TokenSelectionDialog(QDialog):
    def __init__(self, token_dir, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Token")
        self.token_dir = token_dir
        
        self.layout = QVBoxLayout(self)
        
        self.token_combo = QComboBox()
        self.token_combo.addItems(self.get_available_tokens())
        
        self.layout.addWidget(QLabel("Select Token:"))
        self.layout.addWidget(self.token_combo)
        
        self.name_input = QLineEdit()
        self.layout.addWidget(QLabel("Token Name:"))
        self.layout.addWidget(self.name_input)
        
        # New input for HP
        self.hp_input = QSpinBox()
        self.hp_input.setMinimum(0)
        self.hp_input.setMaximum(1000)
        self.hp_input.setValue(100)  # Default HP
        self.layout.addWidget(QLabel("Token HP:"))
        self.layout.addWidget(self.hp_input)
        
        # New input for AC
        self.ac_input = QSpinBox()
        self.ac_input.setMinimum(0)
        self.ac_input.setMaximum(100)
        self.ac_input.setValue(10)  # Default AC
        self.layout.addWidget(QLabel("Token AC:"))
        self.layout.addWidget(self.ac_input)
        
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)
    
    def get_available_tokens(self):
        tokens = []
        for file in os.listdir(self.token_dir):
            if file.endswith(".png"):
                tokens.append(file)
        return tokens
    
    def get_selected_token(self):
        return (self.token_combo.currentText(), 
                self.name_input.text(), 
                self.hp_input.value(), 
                self.ac_input.value())


# Custom view to handle fog of war interactions
class VTTView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        
        self.fog_tool_active = False
        self.brush_size = 1
        self.fog_grid_size = 50
        self.fog_state = None
        self.fog_pixmap_item = None
        self.map_pixmap_item = None
    
    def set_fog_state(self, fog_state, fog_pixmap_item, map_pixmap_item):
        self.fog_state = fog_state
        self.fog_pixmap_item = fog_pixmap_item
        self.map_pixmap_item = map_pixmap_item
    
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            item = self.itemAt(event.pos())
            if isinstance(item, QGraphicsPixmapItem):
                # Show context menu for the token
                self.parent().show_token_context_menu(event.pos(), item)
                return  # Prevent further processing
        if self.fog_tool_active:
            self.handle_fog_event(event)
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.fog_tool_active and event.buttons() != Qt.NoButton:
            self.handle_fog_event(event)
        else:
            super().mouseMoveEvent(event)
    
    def handle_fog_event(self, event):
        if not self.fog_state or not self.map_pixmap_item:
            return
        
        scene_pos = self.mapToScene(event.pos())
        grid_x = int(scene_pos.x() // self.fog_grid_size)
        grid_y = int(scene_pos.y() // self.fog_grid_size)
        
        if 0 <= grid_x < len(self.fog_state[0]) and 0 <= grid_y < len(self.fog_state):
            reveal = event.button() == Qt.LeftButton
            self.update_fog(grid_x, grid_y, reveal)
    
    def update_fog(self, grid_x, grid_y, reveal):
        for i in range(max(0, grid_x - self.brush_size + 1), min(len(self.fog_state[0]), grid_x + self.brush_size)):
            for j in range(max(0, grid_y - self.brush_size + 1), min(len(self.fog_state), grid_y + self.brush_size)):
                self.fog_state[j][i] = reveal
        self.redraw_fog()
    
    def redraw_fog(self):
        pixmap = QPixmap(self.map_pixmap_item.pixmap().size())
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setBrush(QBrush(QColor(0, 0, 0, 230)))
        
        for j, row in enumerate(self.fog_state):
            for i, revealed in enumerate(row):
                if not revealed:
                    painter.drawRect(i * self.fog_grid_size, j * self.fog_grid_size, 
                                    self.fog_grid_size, self.fog_grid_size)
        
        painter.end()
        self.fog_pixmap_item.setPixmap(pixmap)


# Main VTT application window
class VirtualTabletop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virtual Tabletop")
        self.setGeometry(100, 100, 800, 600)
        
        # Apply dark mode
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; color: #ffffff; }
            QToolBar { background-color: #3c3f41; color: #ffffff; }
            QToolButton { color: #ffffff; }
            QDockWidget { background-color: #3c3f41; color: #ffffff; }
            QTableWidget { background-color: #2b2b2b; color: #ffffff; }
            QTextEdit { background-color: #2b2b2b; color: #ffffff; border: 1px solid #555555; }
            QPushButton { background-color: #4c4c4c; color: #ffffff; border: 1px solid #555555; padding: 5px; }
            QPushButton:hover { background-color: #5c5c5c; }
        """)
        
        # Set up directories
        self.vtt_dir = "vtt"
        self.token_dir = os.path.join(self.vtt_dir, "tokens")
        if not os.path.exists(self.token_dir):
            os.makedirs(self.token_dir)
        self.generate_default_tokens()
        
        # Set up scene and view
        self.scene = QGraphicsScene()
        self.view = VTTView()
        self.view.setScene(self.scene)
        self.setCentralWidget(self.view)
        
        # Toolbar
        self.toolbar = QToolBar("Tools")
        self.addToolBar(self.toolbar)
        self.toolbar.addAction("Load Map", self.load_map).setToolTip("Load a map image")
        self.toolbar.addAction("Add Token", self.add_token).setToolTip("Add a token to the map")
        self.fog_tool_action = self.toolbar.addAction("Fog Tool", self.toggle_fog_tool)
        self.fog_tool_action.setToolTip("Toggle fog of war tool")
        self.toolbar.addAction("Clear Fog", self.clear_fog).setToolTip("Clear all fog of war")
        self.toolbar.addAction("Toggle Grid", self.toggle_grid).setToolTip("Show or hide grid")
        self.toolbar.addAction("Toggle Interface", self.toggle_interface).setToolTip("Show or hide toolbar")
        
        # Add zoom in and zoom out actions
        self.toolbar.addAction("Zoom In", self.zoom_in).setToolTip("Zoom in")
        self.toolbar.addAction("Zoom Out", self.zoom_out).setToolTip("Zoom out")
        
        # Grid size spinbox
        self.grid_size_spin = QSpinBox()
        self.grid_size_spin.setMinimum(10)
        self.grid_size_spin.setMaximum(500)
        self.grid_size_spin.setValue(50)
        self.grid_size_spin.setSuffix(" px")
        self.toolbar.addWidget(self.grid_size_spin)
        self.grid_size_spin.valueChanged.connect(self.update_grid)
        
        # Brush size spinbox for fog tool
        self.brush_size_spin = QSpinBox()
        self.brush_size_spin.setMinimum(1)
        self.brush_size_spin.setMaximum(10)
        self.brush_size_spin.setValue(1)
        self.brush_size_spin.setVisible(False)
        self.toolbar.addWidget(self.brush_size_spin)
        
        # Variables
        self.grid_visible = False
        self.grid_lines = []
        self.tokens = []
        self.fog_tool_active = False
        self.fog_state = None
        self.fog_pixmap_item = None
        self.map_pixmap_item = None
        self.fog_grid_size = 50
    
    def generate_default_tokens(self):
        colors = ["red", "blue", "green", "yellow", "purple"]
        for color in colors:
            pixmap = QPixmap(50, 50)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setBrush(QBrush(QColor(color)))
            painter.drawEllipse(5, 5, 40, 40)
            painter.end()
            pixmap.save(os.path.join(self.token_dir, f"default_{color}.png"))
    
    def load_map(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Map", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.scene.clear()
            pixmap = QPixmap(file_path)
            self.map_pixmap_item = self.scene.addPixmap(pixmap)
            self.map_pixmap_item.setZValue(0)
            self.scene.setSceneRect(0, 0, pixmap.width(), pixmap.height())
            self.init_fog_of_war(pixmap.width(), pixmap.height())
            
            if self.grid_visible:
                self.add_grid()
    
    def init_fog_of_war(self, width, height):
        self.fog_state = [[False for _ in range(int(width // self.fog_grid_size) + 1)]
                          for _ in range(int(height // self.fog_grid_size) + 1)]
        
        self.fog_pixmap_item = QGraphicsPixmapItem()
        self.fog_pixmap_item.setZValue(1)
        self.scene.addItem(self.fog_pixmap_item)
        
        self.view.set_fog_state(self.fog_state, self.fog_pixmap_item, self.map_pixmap_item)
        self.view.redraw_fog()
    
    def add_token(self):
        dialog = TokenSelectionDialog(self.token_dir, self)
        if dialog.exec() == QDialog.Accepted:
            token_file, token_name, token_hp, token_ac = dialog.get_selected_token()
            token_path = os.path.join(self.token_dir, token_file)
            
            pixmap = QPixmap(token_path).scaled(50, 50, Qt.KeepAspectRatio)
            token = QGraphicsPixmapItem(pixmap)
            token.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
            token.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)  # Make token selectable
            
            center = self.view.mapToScene(self.view.viewport().rect().center())
            token.setPos(center)
            self.scene.addItem(token)
            token.setZValue(2)
            
            # Add name label
            name_item = QGraphicsTextItem(token_name, token)
            name_item.setDefaultTextColor(Qt.white)
            name_item.setFont(QFont("Arial", 10, QFont.Bold))
            
            # Center the text below the token
            text_rect = name_item.boundingRect()
            token_width = pixmap.width()  # Get the width of the token
            name_item.setPos(-text_rect.width() / 2 + token_width / 2, 50)  # Center below the token
            
            self.scene.addItem(name_item)
            
            # Add HP label
            hp_item = QGraphicsTextItem(f"HP: {token_hp}", token)
            hp_item.setDefaultTextColor(Qt.white)
            hp_item.setFont(QFont("Arial", 10, QFont.Normal))
            hp_item.setPos(-text_rect.width() / 2 + token_width / 2, 70)  # Position below the name
            
            self.scene.addItem(hp_item)
            
            self.tokens.append({
                "path": token_path, 
                "item": token, 
                "name_item": name_item, 
                "hp_item": hp_item,  # Store the HP item
                "name": token_name,
                "hp": token_hp,  # Set HP from dialog
                "ac": token_ac   # Set AC from dialog
            })
    
    def show_token_context_menu(self, pos, token_item):
        # Find the token data associated with the token_item
        token_data = next((t for t in self.tokens if t["item"] == token_item), None)
        if not token_data:
            return  # If no token data found, exit

        context_menu = QMenu(self)
        
        # Change Name Action
        change_name_action = context_menu.addAction("Change Name")
        change_name_action.triggered.connect(lambda: self.change_token_name(token_data))
        
        # Change HP Action
        change_hp_action = context_menu.addAction("Change HP")
        change_hp_action.triggered.connect(lambda: self.change_token_hp(token_data))
        
        # Change AC Action
        change_ac_action = context_menu.addAction("Change AC")
        change_ac_action.triggered.connect(lambda: self.change_token_ac(token_data))
        
        # Delete Action
        delete_action = context_menu.addAction("Delete")
        delete_action.triggered.connect(lambda: self.delete_token(token_data))
        
        context_menu.exec_(self.view.mapToGlobal(pos))

    def change_token_name(self, token):
        new_name, ok = QInputDialog.getText(self, "Change Token Name", "Enter new name:", text=token["name"])
        if ok and new_name:
            token["name"] = new_name
            token["name_item"].setPlainText(new_name)

    def change_token_hp(self, token):
        new_hp, ok = QInputDialog.getInt(self, "Change Token HP", "Enter new HP:", token["hp"], 0, 1000)
        if ok:
            token["hp"] = new_hp  # Update HP

    def change_token_ac(self, token):
        new_ac, ok = QInputDialog.getInt(self, "Change Token AC", "Enter new AC:", token["ac"], 0, 100)
        if ok:
            token["ac"] = new_ac  # Update AC

    def delete_token(self, token):
        self.scene.removeItem(token["item"])  # Remove token from scene
        self.scene.removeItem(token["name_item"])  # Remove name label from scene
        self.scene.removeItem(token["hp_item"])  # Remove HP label from scene
        self.tokens.remove(token)  # Remove from tokens list
    
    def toggle_fog_tool(self):
        self.fog_tool_active = not self.fog_tool_active
        self.view.fog_tool_active = self.fog_tool_active
        self.brush_size_spin.setVisible(self.fog_tool_active)
        self.view.brush_size = self.brush_size_spin.value()
        
        if self.fog_tool_active:
            self.fog_tool_action.setText("Fog Tool (on) ")
        else:
            self.fog_tool_action.setText("Fog Tool (off)")
    
    def toggle_grid(self):
        if self.grid_visible:
            self.remove_grid()
            self.grid_visible = False
        else:
            self.add_grid()
            self.grid_visible = True
    
    def add_grid(self):
        if not self.map_pixmap_item:
            return
        
        width = self.map_pixmap_item.pixmap().width()
        height = self.map_pixmap_item.pixmap().height()
        grid_size = self.grid_size_spin.value()
        
        pen = QPen(Qt.white, 1, Qt.DashLine)
        
        for x in range(0, width, grid_size):
            line = self.scene.addLine(x, 0, x, height, pen)
            self.grid_lines.append(line)
        
        for y in range(0, height, grid_size):
            line = self.scene.addLine(0, y, width, y, pen)
            self.grid_lines.append(line)
    
    def remove_grid(self):
        for line in self.grid_lines:
            self.scene.removeItem(line)
        self.grid_lines = []
    
    def update_grid(self):
        if self.grid_visible:
            self.remove_grid()
            self.add_grid()
        
        # Update the fog grid size to match the current grid size
        self.fog_grid_size = self.grid_size_spin.value()
    
    def toggle_interface(self):
        self.toolbar.setVisible(not self.toolbar.isVisible())
    
    def zoom_in(self):
        """Zoom in the view"""
        self.view.scale(1.15, 1.15)

    def zoom_out(self):
        """Zoom out the view"""
        self.view.scale(1 / 1.15, 1 / 1.15)

    def wheelEvent(self, event):
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            self.view.scale(zoom_factor, zoom_factor)
        else:
            self.view.scale(1 / zoom_factor, 1 / zoom_factor)

    def clear_fog(self):
        """Clear all fog of war from the map"""
        if not self.fog_state or not self.map_pixmap_item:
            return
            
        # Set all fog cells to revealed (True)
        for j in range(len(self.fog_state)):
            for i in range(len(self.fog_state[j])):
                self.fog_state[j][i] = True
                
        # Redraw the fog (which will now be completely clear)
        self.view.redraw_fog()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VirtualTabletop()
    window.show()
    sys.exit(app.exec())