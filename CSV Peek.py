import sys
import csv
import open3d as o3d
import numpy as np
from PyQt5.QtWidgets import QApplication, QSizePolicy, QMainWindow, QMenuBar, QAction, QVBoxLayout, QWidget, QFileDialog, QComboBox, QPushButton, QCheckBox, QMessageBox, QLabel
from PyQt5.QtGui import QPixmap, QIcon

class MeshViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        icon = QIcon('peice.ico')
        self.setWindowIcon(icon)
        
    def initUI(self):
        self.setWindowTitle('CSV Peek')

        self.setGeometry(100, 100, 200, 300)
        self.setupMenuBar()
        self.setupCentralWidget()
        self.header = []

    def setupMenuBar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('Main')

        open_action = QAction('Open CSV', self)
        open_action.triggered.connect(self.openCSV)
        file_menu.addAction(open_action)
                
    def setupCentralWidget(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        banner = QLabel(self)
        pixmap = QPixmap('banner.png')
        banner.setPixmap(pixmap)
        banner.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        banner.setFixedSize(225, 30)
        layout.addWidget(banner)

        self.central_widget.setLayout(layout)

        # Set the central widget, ensuring it doesn't overlap with the menu bar
        self.setCentralWidget(self.central_widget)
        # Skip first line box
        self.central_widget.setStyleSheet("background-color: darkcyan; border: 2px solid black; border-radius: 10px")
        
        self.skip_first_line_checkbox = self.createStyledCheckBox('Skip First Line', "yellow", default_checked=True)
        self.skip_first_line_checkbox.setStyleSheet("background-color: lightyellow; border: 1px solid yellow; border-radius: 10px; padding: 3px;")
        self.skip_first_line_checkbox.setFixedSize(100 ,30)
        layout.addWidget(self.skip_first_line_checkbox)
        # Export box
        self.test = self.createStyledCheckBox2('◁ EXPORT: OBJ, PLY, STL files', "darkcyan", default_checked=False)
        self.test.setStyleSheet("background-color: lightcyan; font-size: 14px; border: 1px solid black; border-radius: 8px; padding: 3px;")
        self.test.setFixedSize(225, 30)  # Set the size you want (width, height)
        layout.addWidget(self.test)

        # Clear box
        self.clear_button = QPushButton('Clear')
        self.clear_button.setStyleSheet("background-color: #232323; color: red; font-size: 12px; padding: 2px")
        self.clear_button.setFixedSize(100 ,30)
        self.clear_button.clicked.connect(self.clearState)
        layout.addWidget(self.clear_button)
        # Path text
        self.file_path_combobox = QComboBox()
        layout.addWidget(self.file_path_combobox)
        # X POS
        self.x_label = self.createStyledLabel('Select X Column:', "pink", "2")
        layout.addWidget(self.x_label)
        self.x_column_combobox = self.createStyledComboBox("pink")
        layout.addWidget(self.x_column_combobox)
        # Y POS
        self.y_label = self.createStyledLabel('Select Y Column:', "lightgreen", "2")
        layout.addWidget(self.y_label)
        self.y_column_combobox = self.createStyledComboBox("lightgreen")
        layout.addWidget(self.y_column_combobox)
        # Z POS
        self.z_label = self.createStyledLabel('Select Z Column:', "lightblue", "2")
        layout.addWidget(self.z_label)
        self.z_column_combobox = self.createStyledComboBox("lightblue")
        layout.addWidget(self.z_column_combobox)
        
        # Add the "Convert Point Cloud" button
        self.convert_button = QPushButton('Point Cloud')
        self.convert_button.setStyleSheet("Background-color: gray; font-size: 16px; border: 1px solid; border-radius: 10px;")
        self.convert_button.clicked.connect(self.convertPointCloud)  # Connect the button to the convertPointCloud function
        self.convert_button.setFixedSize(100, 20)

        layout.addWidget(self.convert_button)
        # View & Export button
        self.view_button = QPushButton('✳ View Mesh / Export ✳')
        self.view_button.setStyleSheet("Background-color: darkorange; font-size: 20px;")
        self.view_button.clicked.connect(self.viewMesh)
        layout.addWidget(self.view_button)

        self.central_widget.setLayout(layout)

    # Modify the createStyledCheckBox function to accept a default state
    def createStyledCheckBox(self, text, bg_color, default_checked=True):
        checkbox = QCheckBox(text)
        checkbox.setChecked(default_checked)
        checkbox.setStyleSheet(f"background-color: {bg_color}")
        return checkbox
    # Checkbox Export
    def createStyledCheckBox2(self, text, bg_color, default_checked=False):
        checkbox = QCheckBox(text)
        checkbox.setChecked(default_checked)
        checkbox.setStyleSheet(f"background-color: {bg_color}")
        return checkbox
    
    # Label maker
    def createStyledLabel(self, text, bg_color, pd):
        label = QLabel(text)
        label.setStyleSheet(f"background-color: {bg_color}; padding: {pd}px; font: bold;")
        return label
    # checkbox Skip Line
    def createStyledComboBox(self, bg_color):
        combobox = QComboBox()
        combobox.setStyleSheet(f"background-color: {bg_color}; font-size: 14px; border: 2px solid {bg_color}; border-radius: 10px;")
        return combobox

    def openCSV(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open CSV File', '', 'CSV Files (*.csv);;All Files (*)', options=options)

        if file_path:
            self.file_path_combobox.addItem(file_path)
            self.populateColumnComboBoxes(file_path)

    def populateColumnComboBoxes(self, file_path):
        try:
            with open(file_path, 'r') as csvfile:
                csvreader = csv.reader(csvfile)
                self.header = next(csvreader)  # Read the header row

                selected_items = set()
                # Populate combo boxes while excluding selected items
                for combo_box in [self.x_column_combobox, self.y_column_combobox, self.z_column_combobox]:
                    #combo_box.clear()  # Clear the combo box before populating
                    combo_box.addItems([item for item in self.header if item not in selected_items])
                    if combo_box.currentText():
                        selected_items.add(combo_box.currentText())  # Add the selected item to the set

        except Exception as e:
            self.showErrorMessage(f'Error reading CSV file: {str(e)}')
                            
    def convertPointCloud(self):
        file_path = self.file_path_combobox.currentText()
        skip_first_line = self.skip_first_line_checkbox.isChecked()

        x_column = self.x_column_combobox.currentText()
        y_column = self.y_column_combobox.currentText()
        z_column = self.z_column_combobox.currentText()

        try:
            with open(file_path, 'r') as csvfile:
                csvreader = csv.reader(csvfile)

                if skip_first_line:
                    next(csvreader)  # Skip the first line

                x_coords, y_coords, z_coords = [], [], []

                for row in csvreader:
                    if len(row) >= 3:
                        x_coords.append(float(row[self.header.index(x_column)]))
                        y_coords.append(float(row[self.header.index(y_column)]))
                        z_coords.append(float(row[self.header.index(z_column)]))

                point_cloud = o3d.geometry.PointCloud()
                points = np.column_stack((x_coords, y_coords, z_coords))
                point_cloud.points = o3d.utility.Vector3dVector(points)

                mesh_color = [0.0, 1.0, 0.0]  # Green color in RGB format
                # Paint the entire mesh with the specified color
                point_cloud.paint_uniform_color(mesh_color)
                # Estimate normals for the point cloud
                point_cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

                # Convert point cloud to a 3D mesh with faces using Poisson reconstruction
                mesh, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(point_cloud, depth=30)
                mesh.compute_vertex_normals()
                
                # Apply Laplacian smoothing
                laplacian_iterations = 10  # Adjust the number of smoothing iterations as needed
                mesh = mesh.filter_smooth_laplacian(laplacian_iterations)
                
                # Visualization code (your existing code for visualization)
                vis_settings = o3d.visualization.VisualizerWithKeyCallback()
                vis_settings.create_window(width=500, height=600)
                vis_settings.add_geometry(mesh)

                vis_set = vis_settings.get_render_option()
                vis_set.background_color = [0.0, 0.0, 0.0]  # Black background
                vis_set.mesh_show_wireframe = False
                vis_set.mesh_show_back_face = True
                vis_set.show_coordinate_frame = True

                vis_settings.run()

        except Exception as e:
            self.showErrorMessage(f'Error converting point cloud: {str(e)}')

    def viewMesh(self):
        file_path = self.file_path_combobox.currentText()
        skip_first_line = self.skip_first_line_checkbox.isChecked()

        x_column = self.x_column_combobox.currentText()
        y_column = self.y_column_combobox.currentText()
        z_column = self.z_column_combobox.currentText()

        try:
            with open(file_path, 'r') as csvfile:
                csvreader = csv.reader(csvfile)

                if skip_first_line:
                    next(csvreader)  # Skip the first line

                x_coords, y_coords, z_coords = [], [], []

                for row in csvreader:
                    if len(row) >= 3:
                        x_coords.append(float(row[self.header.index(x_column)]))
                        y_coords.append(float(row[self.header.index(y_column)]))
                        z_coords.append(float(row[self.header.index(z_column)]))

                point_cloud = o3d.geometry.PointCloud()
                points = np.column_stack((x_coords, y_coords, z_coords))
                point_cloud.points = o3d.utility.Vector3dVector(points)

                num_points = len(points)
                num_triangles = num_points - 2
                triangles = []

                triangle_mesh = o3d.geometry.TriangleMesh()
                triangle_mesh.vertices = point_cloud.points
                triangle_mesh.triangles = o3d.utility.Vector3iVector(triangles)

                # Make sure the faces are facing out
                for i in range(num_triangles):
                    if i % 3 == 0:
                        # Get the vertices of the current triangle
                        vertex_indices = [i, i + 1, i + 2]

                        # Extract the vertices
                        vertices = [triangle_mesh.vertices[j] for j in vertex_indices]

                        # Compute the normal vector of the triangle
                        normal = np.cross(vertices[1] - vertices[0], vertices[2] - vertices[0])

                        # Check the direction of the normal vector
                        if normal[2] < 0:
                            # If the normal points inward, reverse the order of vertices
                            vertex_indices = [i + 2, i + 1, i]
                        else:
                            # If the normal points outward, keep the order of vertices
                            vertex_indices = [i, i + 2, i + 1]

                        triangles.append(vertex_indices)

                # Estimate normals for the point cloud
                point_cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30), fast_normal_computation=False)

                # Update the triangles of the TriangleMesh
                triangle_mesh.triangles = o3d.utility.Vector3iVector(triangles)

                mesh_color = [0.0, 1.0, 0.0]  # Green color in RGB format
                triangle_mesh.paint_uniform_color(mesh_color)
                # Compute vertex normals for smooth shading
                triangle_mesh.compute_vertex_normals()

                if self.test.isChecked():
                    print("Export is On")

                    # Specify the file paths for STL, OBJ, and PLY files
                    file_path_stl = "3D_STL.stl"
                    file_path_obj = "3D_OBJ.obj"
                    file_path_ply = "3D_PLY.ply"

                    # Write the mesh to STL, OBJ, and PLY files
                    o3d.io.write_triangle_mesh(file_path_ply, triangle_mesh)

                    # Load the OBJ file
                    mesh = o3d.io.read_triangle_mesh(file_path_ply)

                    # Smooth out the normals
                    mesh.compute_vertex_normals()

                    # Save the smoothed mesh as a new OBJ file
                    o3d.io.write_triangle_mesh(file_path_obj, mesh)

                    print(f"Smoothed mesh saved to {file_path_obj}")

                    #o3d.io.write_triangle_mesh(file_path_ply, triangle_mesh)

                    info_msg = f"Number of vertices: {len(triangle_mesh.vertices)}\nNumber of faces: {len(triangle_mesh.triangles)}\n⇩ Saved Files:\n{file_path_stl}\n{file_path_obj}\n{file_path_ply}"
                    QMessageBox.information(self, "Mesh Information", info_msg)

                else:
                    print("Export is Off")

                vis_settings = o3d.visualization.VisualizerWithKeyCallback()
                vis_settings.create_window(width=500, height=600)
                vis_settings.add_geometry(triangle_mesh)

                vis_set = vis_settings.get_render_option()
                vis_set.background_color = [0.0, 0.0, 0.0]  # Black background
                vis_set.mesh_show_wireframe = True
                vis_set.mesh_show_back_face = True
                vis_set.show_coordinate_frame = True
                vis_settings.run()

        except Exception as e:
            self.showErrorMessage(f'Error reading CSV file: {str(e)}')

    def showErrorMessage(self, message):
        QMessageBox.critical(self, 'Error', message, QMessageBox.Ok)
        
    def clearState(self):
        # Clear the selected CSV file and reset combo boxes
        self.file_path_combobox.clear()
        self.x_column_combobox.clear()
        self.y_column_combobox.clear()
        self.z_column_combobox.clear()
        self.header = []

def main():
    app = QApplication(sys.argv)
    window = MeshViewerApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
