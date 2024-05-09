import sys
import tempfile
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit,
                             QCheckBox, QLabel, QScrollArea, QComboBox, QPushButton, QFileDialog)
from datetime import datetime
import fitz

class PdfFormApp(QMainWindow):
    def __init__(self):
        super().__init__()
        if getattr(sys, 'frozen', False):
            # If the script is running as an executable
            executable_path = sys.executable
            executable_dir = os.path.dirname(executable_path)
            self.template_folder = os.path.join(executable_dir, "templates")
        else:
            # If the script is running as a Python script
            self.template_folder = "templates"
        
        self.pdf_library = self.load_templates()
        self.pdf_doc = None
        self.init_ui()
        self.load_default_pdf()

    def load_templates(self):
        pdf_library = {}
        if os.path.exists(self.template_folder):
            for filename in os.listdir(self.template_folder):
                if filename.endswith(".pdf"):
                    pdf_library[os.path.splitext(filename)[0]] = os.path.join(self.template_folder, filename)
        return pdf_library

    def init_ui(self):
        self.setWindowTitle('PDF Form Filler')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Dropdown for sheet selection
        self.dropdown = QComboBox()
        self.dropdown.addItems(self.pdf_library.keys())
        self.dropdown.currentIndexChanged.connect(self.load_selected_pdf)
        layout.addWidget(self.dropdown)

        # Buttons for save, print, and open in Adobe
        button_layout = QVBoxLayout()
        save_button = QPushButton("Save PDF")
        save_button.clicked.connect(self.save_pdf)
        button_layout.addWidget(save_button)

        print_button = QPushButton("Print PDF")
        print_button.clicked.connect(self.print_pdf)
        button_layout.addWidget(print_button)

        open_button = QPushButton("Open in Adobe")
        open_button.clicked.connect(self.open_in_adobe)
        button_layout.addWidget(open_button)

        layout.addLayout(button_layout)

        # Scroll area for form fields
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.form_layout = QVBoxLayout()
        scroll_widget.setLayout(self.form_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

    def load_default_pdf(self):
        if self.pdf_library:
            default_template = next(iter(self.pdf_library.values()))
            self.open_pdf(default_template)
        else:
            print("No PDF templates found in the 'templates' folder.")

    def load_selected_pdf(self):
        selected_sheet = self.dropdown.currentText()
        file_path = self.pdf_library[selected_sheet]
        self.open_pdf(file_path)

    def open_pdf(self, file_path):
        try:
            self.pdf_doc = fitz.open(file_path)
            self.load_form_fields(self.pdf_doc)
        except Exception as e:
            print(f"Error opening PDF: {e}")

    def load_form_fields(self, pdf):
        # Clear previous layout
        while self.form_layout.count():
            child = self.form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        page = pdf[0]
        fields = page.widgets()
        self.form_widgets = {}

        for field in fields:
            print(f"Field: {field.field_name}, Type: {field.field_type}, Value: {field.field_value}")
            
            label = QLabel(f"{field.field_name}:")
            self.form_layout.addWidget(label)

            input_widget = None
            if field.field_type == 7:  # Text fields
                if field.field_name in ["Item Title", "Notes"]:  # Multiline text fields
                    input_widget = QLineEdit()
                    input_widget.setMinimumHeight(100)  # Set a larger height for multiline fields
                else:
                    input_widget = QLineEdit()
                input_widget.setText(field.field_value)
                input_widget.returnPressed.connect(self.focus_next_widget)
            elif field.field_type == 2:  # Checkbox fields
                input_widget = QCheckBox()
                input_widget.setChecked(field.field_value.lower() in ["yes", "true", "on"])
            elif field.field_name == "Condition":  # Condition field
                input_widget = QComboBox()
                input_widget.addItems(["New", "Used", "Parts & Repair"])
                input_widget.setCurrentText(field.field_value)
            else:
                input_widget = QLabel("Unsupported Field Type")

            self.form_layout.addWidget(input_widget)
            self.form_widgets[field.field_name] = input_widget

    def scroll_to_widget(self, widget):
        scroll_area = self.centralWidget().findChild(QScrollArea)
        if scroll_area:
            scroll_area.ensureWidgetVisible(widget)

    def focus_next_widget(self):
        widget = QApplication.focusWidget()
        index = self.form_layout.indexOf(widget)
        next_widget = self.form_layout.itemAt(index + 2).widget()
        if next_widget:
            next_widget.setFocus()
            self.scroll_to_widget(next_widget)

    def save_pdf(self):
        if not self.pdf_doc:
            return

        file_dialog = QFileDialog()
        output_path, _ = file_dialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")

        if output_path:
            self.update_form_fields()
            timestamp = self.generate_timestamp()
            page = self.pdf_doc[0]  # Access the first page
            page.set_rotation(0)  # Ensure the page rotation is set to 0 before adding the timestamp
            page_rect = page.rect
            # Adjust the position: move left by reducing x-coordinate, adjust y-coordinate as needed
            timestamp_pos = fitz.Point(page_rect.width - 180, page_rect.height - 20)  # Example adjustment
            page.insert_text(
                timestamp_pos,
                timestamp,  # Updated to use the new timestamp format
                fontsize=10,  # Reduced font size
                fontname="Helvetica",
                rotate=0,
                color=(0, 0, 0)
            )
            self.pdf_doc.save(output_path)
            print(f"PDF saved to {output_path}")

    def print_pdf(self):
        if not self.pdf_doc:
            return

        self.update_form_fields()
        
        # Create a temporary file for printing
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            temp_path = temp_pdf.name
        
        try:
            # Save the PDF to the temporary file
            timestamp = self.generate_timestamp()
            page = self.pdf_doc[0]  # Access the first page
            page.set_rotation(0)  # Ensure the page rotation is set to 0 before adding the timestamp
            page_rect = page.rect
            timestamp_pos = fitz.Point(page_rect.width - 180, page_rect.height - 20)  # Adjusted position
            page.insert_text(
                timestamp_pos,
                timestamp,  # Use the simplified timestamp format
                fontsize=10,  # Adjusted font size
                fontname="Helvetica",  # Adjust the font name as needed
                rotate=0,  # Ensure the rotation is set to 0
                color=(0, 0, 0)  # Set the color of the timestamp (black)
            )
            self.pdf_doc.save(temp_path)
            
            # Path to Adobe Reader (update if necessary)
            acrobat_path = r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"
            
            if not os.path.exists(acrobat_path):
                raise Exception("Adobe Reader not found at the specified path")

            # Print using Adobe Reader
            try:
                subprocess.run([acrobat_path, "/t", temp_path], check=True)
                print("PDF sent to printer successfully")
            except subprocess.CalledProcessError as e:
                if e.returncode == 1:
                    print("PDF sent to printer successfully (ignoring Adobe Reader's non-zero exit status)")
                else:
                    raise
        
        except Exception as e:
            print(f"An error occurred: {e}")
        
        finally:
            # Delete the temporary file
            os.remove(temp_path)

    def open_in_adobe(self):
        if not self.pdf_doc:
            return

        self.update_form_fields()
        
        # Create a temporary file for opening in Adobe Reader
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
            temp_path = temp_pdf.name
        
        try:
            # Save the PDF to the temporary file
            timestamp = self.generate_timestamp()
            page = self.pdf_doc[0]  # Access the first page
            page.set_rotation(0)  # Ensure the page rotation is set to 0 before adding the timestamp
            page_rect = page.rect
            timestamp_pos = fitz.Point(page_rect.width - 180, page_rect.height - 20)  # Adjusted position
            page.insert_text(
                timestamp_pos,
                timestamp,  # Use the simplified timestamp format
                fontsize=10,  # Adjusted font size
                fontname="Helvetica",  # Adjust the font name as needed
                rotate=0,  # Ensure the rotation is set to 0
                color=(0, 0, 0)  # Set the color of the timestamp (black)
            )
            self.pdf_doc.save(temp_path)
            
            # Path to Adobe Reader (update if necessary)
            acrobat_path = r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"
            
            if not os.path.exists(acrobat_path):
                raise Exception("Adobe Reader not found at the specified path")

            # Open the PDF in Adobe Reader
            subprocess.Popen([acrobat_path, temp_path])
            print("PDF opened in Adobe Reader")
        
        except Exception as e:
            print(f"An error occurred: {e}")

    def update_form_fields(self):
        page = self.pdf_doc[0]  # Assuming the form fields are on the first page
        for field in page.widgets():
            widget = self.form_widgets.get(field.field_name)
            if isinstance(widget, QLineEdit):
                field.field_value = widget.text()
                field.update()
                print(f"Updated {field.field_name} to {widget.text()}")
            elif isinstance(widget, QCheckBox):
                field.field_value = "Yes" if widget.isChecked() else "No"
                field.update()
                print(f"Updated {field.field_name} to {'Yes' if widget.isChecked() else 'No'}")
            elif isinstance(widget, QComboBox):
                field.field_value = widget.currentText()
                field.update()
                print(f"Updated {field.field_name} to {widget.currentText()}")

    def generate_timestamp(self):
        current_time = datetime.now()
        timestamp = current_time.strftime("%B %d, %Y %I:%M %p")
        return timestamp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PdfFormApp()
    ex.show()
    sys.exit(app.exec_())
    sys.exit(app.exec_())