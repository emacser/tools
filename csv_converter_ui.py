import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QFileDialog,
    QTextEdit,
    QComboBox,
    QGroupBox,
    QMessageBox
)
import pandas as pd

class CSVConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CSV Converter")
        self.setGeometry(100, 100, 600, 400)  # x, y, width, height

        # Layouts
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(10, 10, 10, 10) # Margins for main window
        main_layout.setSpacing(10) # Spacing for main window elements

        # --- Input CSV Section ---
        input_group_box = QGroupBox("Input CSV")
        input_group_layout = QVBoxLayout()
        input_group_layout.setContentsMargins(10, 10, 10, 10)
        input_group_layout.setSpacing(5)
        
        input_file_layout = QHBoxLayout() # For button and line edit
        self.btn_select_input = QPushButton("Select Input CSV")
        self.input_path_label = QLineEdit()
        self.input_path_label.setReadOnly(True)
        input_file_layout.addWidget(self.btn_select_input)
        input_file_layout.addWidget(self.input_path_label)
        input_group_layout.addLayout(input_file_layout)
        input_group_box.setLayout(input_group_layout)
        main_layout.addWidget(input_group_box)

        # --- Column Mapping Section ---
        mapping_group_box = QGroupBox("Column Mapping")
        self.column_mapping_layout = QVBoxLayout() # This will contain rows of QHBoxLayouts
        self.column_mapping_layout.setContentsMargins(10, 10, 10, 10)
        self.column_mapping_layout.setSpacing(5)
        mapping_group_box.setLayout(self.column_mapping_layout)
        main_layout.addWidget(mapping_group_box)

        self.mapping_comboboxes = {} # To store QComboBoxes for non-datetime mappings
        self.datetime_date_select = None # QComboBox for datetime's date part
        self.datetime_time_select = None # QComboBox for datetime's time part
        self.source_headers = []

        # --- Output CSV Section ---
        output_group_box = QGroupBox("Output CSV")
        output_group_layout = QVBoxLayout()
        output_group_layout.setContentsMargins(10, 10, 10, 10)
        output_group_layout.setSpacing(5)

        output_file_layout = QHBoxLayout() # For button and line edit
        self.btn_select_output = QPushButton("Select Output File Path")
        self.output_path_label = QLineEdit()
        self.output_path_label.setReadOnly(True)
        output_file_layout.addWidget(self.btn_select_output)
        output_file_layout.addWidget(self.output_path_label)
        output_group_layout.addLayout(output_file_layout)
        output_group_box.setLayout(output_group_layout)
        main_layout.addWidget(output_group_box)
        
        main_layout.addSpacing(10) # Add some space before the process button

        # --- Process button ---
        self.btn_process_csv = QPushButton("Process CSV")
        main_layout.addWidget(self.btn_process_csv)
        
        main_layout.addSpacing(5) # Add some space before status display

        # --- Status/Error display ---
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        main_layout.addWidget(self.status_display)

        # --- Connect signals ---
        self.btn_select_input.clicked.connect(self.select_input_csv)
        self.btn_select_output.clicked.connect(self.select_output_file)
        self.btn_process_csv.clicked.connect(self.process_csv_file)

    def select_input_csv(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Select Input CSV", "", "CSV Files (*.csv);;All Files (*)"
        )
        if filepath:
            self.input_path_label.setText(filepath)
            self.status_display.setText(f"Selected input CSV: {filepath}")
            # Clear previous mappings
            while self.column_mapping_layout.count():
                child = self.column_mapping_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout(): # Handle nested layouts if any
                    # If it's a layout, recursively clear it
                    while child.layout().count():
                        sub_child = child.layout().takeAt(0)
                        if sub_child.widget():
                            sub_child.widget().deleteLater()
                    child.layout().deleteLater()

            self.mapping_comboboxes.clear()
            self.datetime_date_select = None
            self.datetime_time_select = None
            self.load_csv_headers(filepath)

    def load_csv_headers(self, filepath):
        try:
            # Attempt to read headers
            self.source_headers = pd.read_csv(filepath, nrows=0).columns.tolist()
            self.status_display.append("CSV headers loaded successfully. Please map columns below.")

            target_headers = ["datetime", "open", "high", "low", "close", "volume", "turnover", "open_interest"]
            
            # Clear previous specific datetime selectors if any
            self.datetime_date_select = None
            self.datetime_time_select = None

            for target_header in target_headers:
                if target_header == "datetime":
                    # Date column selection for datetime
                    date_row_layout = QHBoxLayout()
                    date_label = QLabel("datetime (Date Column):")
                    self.datetime_date_select = QComboBox()
                    self.datetime_date_select.addItem("(Select Source Column)")
                    self.datetime_date_select.addItems(self.source_headers)
                    self.datetime_date_select.addItem("N/A")
                    date_row_layout.addWidget(date_label)
                    date_row_layout.addWidget(self.datetime_date_select)
                    self.column_mapping_layout.addLayout(date_row_layout)

                    # Time column selection for datetime (optional)
                    time_row_layout = QHBoxLayout()
                    time_label = QLabel("datetime (Time Column, optional):")
                    self.datetime_time_select = QComboBox()
                    self.datetime_time_select.addItem("(Select Source Column)")
                    self.datetime_time_select.addItems(self.source_headers)
                    self.datetime_time_select.addItem("N/A") # Default to N/A, meaning no time column
                    self.datetime_time_select.setCurrentText("N/A") # Explicitly set default
                    time_row_layout.addWidget(time_label)
                    time_row_layout.addWidget(self.datetime_time_select)
                    self.column_mapping_layout.addLayout(time_row_layout)
                else:
                    row_layout = QHBoxLayout()
                    label = QLabel(f"{target_header}:")
                    combo = QComboBox()
                    combo.addItem("(Select Source Column)") # Placeholder
                    combo.addItems(self.source_headers)
                    combo.addItem("N/A") # Option for not applicable

                    row_layout.addWidget(label)
                    row_layout.addWidget(combo)
                    self.column_mapping_layout.addLayout(row_layout)
                    self.mapping_comboboxes[target_header] = combo # Store only non-datetime combos here

        except Exception as e:
            self.status_display.setText(f"Error loading CSV headers from {filepath}: {e}")
            self.source_headers = []  # Clear headers on error
            self.input_path_label.clear() # Clear the input path as it's not usable
            # Clear any potentially populated mapping UI (though it shouldn't be populated on error)
            while self.column_mapping_layout.count():
                child = self.column_mapping_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    while child.layout().count():
                        sub_child = child.layout().takeAt(0)
                        if sub_child.widget():
                            sub_child.widget().deleteLater()
                    child.layout().deleteLater()
            self.mapping_comboboxes.clear()
            self.datetime_date_select = None
            self.datetime_time_select = None
            QMessageBox.critical(self, "Input CSV Error", f"Error reading input CSV headers: {e}. Please check the file and try again.")


    def select_output_file(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save CSV File", "", "CSV Files (*.csv)"
        )
        if filepath:
            self.output_path_label.setText(filepath)
            self.status_display.append(f"Selected output file: {filepath}")
        else:
            self.status_display.append("Output file selection cancelled.")

    def process_csv_file(self):
        self.status_display.setText("Processing CSV...")
        input_filepath = self.input_path_label.text()
        output_filepath = self.output_path_label.text()

        if not input_filepath:
            msg = "Input CSV file path is not set."
            self.status_display.setText(f"Error: {msg}")
            QMessageBox.critical(self, "Error", msg)
            return
        if not output_filepath:
            msg = "Output CSV file path is not set."
            self.status_display.setText(f"Error: {msg}")
            QMessageBox.critical(self, "Error", msg)
            return

        # Gather Mappings for non-datetime columns
        column_mappings = {} # For non-datetime columns
        
        # Check if headers were loaded (source_headers is populated and either datetime_date_select or mapping_comboboxes exist)
        if not self.source_headers or (not self.datetime_date_select and not self.mapping_comboboxes):
            msg = "Input CSV headers not loaded or no mappings UI generated. Please select a valid input CSV and ensure headers are loaded."
            self.status_display.setText(f"Error: {msg}")
            # This might be too frequent for a critical message if it's just a state error, but let's follow instructions.
            QMessageBox.critical(self, "Configuration Error", msg) 
            return

        # Datetime mapping
        date_source_col = None
        time_source_col = None
        
        if self.datetime_date_select:
            date_source_col = self.datetime_date_select.currentText()
            if date_source_col == "(Select Source Column)" or date_source_col == "N/A":
                date_source_col = None
        
        if self.datetime_time_select:
            time_source_col = self.datetime_time_select.currentText()
            if time_source_col == "(Select Source Column)" or time_source_col == "N/A":
                time_source_col = None
        
        self.status_display.append(f"Datetime mapping: Date column='{date_source_col}', Time column='{time_source_col}'")

        # Mappings for other columns
        for target_header, combobox in self.mapping_comboboxes.items(): # This loop now excludes datetime
            source_column = combobox.currentText()
            if source_column == "(Select Source Column)" or source_column == "N/A":
                self.status_display.append(f"Warning: No source column selected for '{target_header}'. It will be filled with default values (0).")
                column_mappings[target_header] = None
            else:
                column_mappings[target_header] = source_column
        
        self.status_display.append(f"Other Column Mappings: {column_mappings}")

        # Read Input CSV
        try:
            input_df = pd.read_csv(input_filepath)
            self.status_display.append(f"Successfully read input CSV: {input_filepath}")
        except FileNotFoundError as e:
            msg = f"Input CSV file not found at {input_filepath}. Please check the path."
            self.status_display.setText(f"Error: {msg}")
            QMessageBox.critical(self, "File Read Error", f"{msg}\nDetails: {e}")
            return
        except Exception as e:
            msg = f"Failed to read input CSV: {input_filepath}."
            self.status_display.setText(f"Error: {msg} {e}")
            QMessageBox.critical(self, "File Read Error", f"{msg}\nError: {e}")
            return

        # Initialize Output DataFrame
        output_df = pd.DataFrame()
        target_headers_ordered = ["datetime", "open", "high", "low", "close", "volume", "turnover", "open_interest"]
        
        warnings = []

        # Process "datetime" Column
        if date_source_col and date_source_col in input_df.columns:
            datetime_series_str = input_df[date_source_col].astype(str)
            datetime_display_source = date_source_col # For warnings

            if time_source_col and time_source_col in input_df.columns:
                datetime_series_str = datetime_series_str + " " + input_df[time_source_col].astype(str)
                datetime_display_source += f" + {time_source_col}"
            elif time_source_col: # Time column selected but not found
                warnings.append(f"Warning: Selected time column '{time_source_col}' for datetime not found in input CSV. Time part will be ignored.")
            
            try:
                dt_series = pd.to_datetime(datetime_series_str, errors='coerce')
                output_df["datetime"] = dt_series.dt.strftime('%Y-%m-%d %H:%M:%S').fillna('1970-01-01 00:00:00')
                if dt_series.isna().any():
                     warnings.append(f"Warning: Some datetime values constructed from '{datetime_display_source}' were invalid or became NaT after parsing, replaced with '1970-01-01 00:00:00'.")
            except Exception as e:
                warnings.append(f"Error processing datetime from '{datetime_display_source}': {e}. Using placeholder.")
                output_df["datetime"] = '1970-01-01 00:00:00'
        elif date_source_col: # Date column selected but not found
            warnings.append(f"Warning: Selected date column '{date_source_col}' for datetime not found in input CSV. Using placeholder.")
            output_df["datetime"] = '1970-01-01 00:00:00'
        else: # No date column mapped
            warnings.append("Warning: 'datetime' (Date Column) not mapped. Using placeholder '1970-01-01 00:00:00'.")
            output_df["datetime"] = '1970-01-01 00:00:00'

        # Process Other Numeric Columns (already excludes datetime)
        numeric_cols = ["open", "high", "low", "close", "volume", "turnover", "open_interest"]
        for target_col in numeric_cols: # These are keys from self.mapping_comboboxes
            source_col_name = column_mappings.get(target_col) # This will be None if not mapped or N/A
            if source_col_name and source_col_name in input_df.columns:
                try:
                    output_df[target_col] = pd.to_numeric(input_df[source_col_name], errors='coerce').fillna(0)
                    # Check for NaNs that were filled
                    if pd.to_numeric(input_df[source_col_name], errors='coerce').isna().any():
                        warnings.append(f"Warning: Some values in '{source_col_name}' (for '{target_col}') were non-numeric or NaN and replaced with 0.")
                    # Also check if original column had non-string empty values pandas might read as NaN but not fail to_numeric
                    elif input_df[source_col_name].isna().any() and not pd.to_numeric(input_df[source_col_name], errors='coerce').isna().any():
                         warnings.append(f"Warning: Some original NaN values in '{source_col_name}' (for '{target_col}') were replaced with 0.")


                except Exception as e:
                    warnings.append(f"Error processing numeric column '{source_col_name}' for '{target_col}': {e}. Using 0.")
                    output_df[target_col] = 0
            elif source_col_name: # Mapped but not found in CSV
                 warnings.append(f"Warning: Mapped column '{source_col_name}' for '{target_col}' not found in input CSV. Using 0.")
                 output_df[target_col] = 0
            else: # Not mapped (column_mappings[target_col] was None)
                 warnings.append(f"Warning: '{target_col}' column not mapped or set to N/A. Using 0.")
                 output_df[target_col] = 0
        
        # Display warnings
        for warning in warnings:
            self.status_display.append(warning)

        # Finalize DataFrame (ensure all target columns exist in correct order)
        for col in target_headers_ordered:
            if col not in output_df:
                self.status_display.append(f"Internal Note: Column '{col}' was missing before final reindex. Populating with default.")
                if col == "datetime":
                    output_df[col] = '1970-01-01 00:00:00'
                else:
                    output_df[col] = 0
        output_df = output_df[target_headers_ordered] # Reorder/select columns

        # Save Output CSV
        try:
            output_df.to_csv(output_filepath, index=False)
            self.status_display.append(f"CSV processing complete. Output saved to: {output_filepath}")
        except Exception as e:
            msg = f"Failed to write output CSV: {output_filepath}."
            self.status_display.setText(f"Error: {msg} {e}")
            QMessageBox.critical(self, "File Write Error", f"{msg}\nError: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CSVConverterApp()
    window.show()
    sys.exit(app.exec())
