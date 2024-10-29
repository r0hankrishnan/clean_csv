import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QFileDialog, QWidget, QLabel,
    QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt5 import QtCore
import os
import sys

app = QApplication([])

# Create the main window
main_window = QWidget()
main_window.setWindowTitle("Billing CSV File Cleaner")
main_window.setGeometry(0, 0, 600, 800)  # Set window geometry
main_window.setStyleSheet("background-color: #2C2C2C;")  # Dark background

# Main layout
master_layout = QVBoxLayout()
master_layout.setContentsMargins(10, 10, 10, 10)

# Title and description
title = QLabel("Use this app to clean your billing CSV file")
title.setAlignment(QtCore.Qt.AlignCenter)
title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF; margin: 20px;")

description = QLabel("Click the upload button below and upload your billing file. "
                     "The program will make all the necessary filters and unlock the download button. "
                     "Once unlocked, you can download and save the filtered data as a CSV.")
description.setAlignment(QtCore.Qt.AlignCenter)
description.setStyleSheet("font-size: 16px; color: #B0B0B0; margin: 0 20px;")

# Add title and description to layout
master_layout.addWidget(title)
master_layout.addWidget(description)

# Style for buttons
button_style = """
    QPushButton {
        background-color: #444444; /* Dark gray */
        color: white;
        border: none;
        border-radius: 5px; /* Slightly rounded edges */
        padding: 10px;
        font-size: 18px;
        margin: 15px;
    }
    QPushButton:disabled {
        background-color: #7F7F7F; /* Greyed out color */
        color: #FFFFFF;
    }
    QPushButton:hover:not(:disabled) {
        background-color: #555555; /* Darker shade on hover */
    }
"""

upload = QPushButton("Upload a file")
download = QPushButton("Download CSV")
download.setEnabled(False)  # Initially disable the download button

# Small circular exit button
exit_button = QPushButton("X")
exit_button.setStyleSheet("""
    QPushButton {
        background-color: #E74C3C; /* Red color for exit */
        color: white;
        border: none;
        border-radius: 15px; /* Circular button */
        width: 30px;
        height: 30px;
        font-size: 16px;
        position: absolute; /* Positioning */
        top: 10px; /* Distance from the top */
        right: 10px; /* Distance from the right */
    }
""")
exit_button.clicked.connect(sys.exit)

# Apply styles
upload.setStyleSheet(button_style)
download.setStyleSheet(button_style)

# Add buttons to layout
master_layout.addWidget(upload)

# Table for displaying filtered data
filtered_table = QTableWidget()
filtered_table.setColumnCount(9)  # Adjust based on number of columns in filtered DataFrame
filtered_table.setHorizontalHeaderLabels([
    "Provider Name", "Patient Name", "Patient DOB", "Facility Name", 
    "Place of Service", "ICD10", "CPT", "Modifiers", 
    "Date of Service (Facility Timezone)"
])
filtered_table.setRowCount(5)  # Set to show a maximum of 5 rows

# Set dark table styling
filtered_table.setStyleSheet("""
    QTableWidget {
        font-size: 14px;
        border: none;
        padding: 10px;
        background-color: #3C3C3C; /* Dark background */
        gridline-color: #555555;
        border-radius: 5px; /* Slightly rounded corners */
    }
    QHeaderView::section {
        background-color: #4C4C4C;
        font-weight: bold;
        border: none;
        color: white;
        padding: 8px;
        font-size: 16px;
    }
    QTableWidget::item {
        padding: 8px;
        color: white;
    }
""")
filtered_table.verticalHeader().setVisible(False)  # Hide vertical header
filtered_table.setVisible(False)  # Initially hide the table

filtered_df_global = None  # Global variable to hold filtered DataFrame

def clean_billing_csv(df: pd.DataFrame) -> pd.DataFrame:
    
    columns_to_keep = [
        "Provider Name",
        "Patient Name",
        "Patient DOB",
        "Facility Name",
        "Place of Service",
        "ICD10",
        "CPT",
        "Modifiers",
        "Date of Service (Facility Timezone)"
    ]

    missing_columns = [col for col in columns_to_keep if col not in df.columns]
    if missing_columns:
        error_message = f"Error: The uploaded dataset is missing the following columns: {', '.join(missing_columns)}"
        print(error_message)

        return pd.DataFrame()  # Return an empty DataFrame

    # Initialize the filtered DataFrame
    filtered_df = df[columns_to_keep].copy()

    # Convert the 'Date of Service (Facility Timezone)' column to datetime
    try:
        filtered_df["Date of Service (Facility Timezone)"] = pd.to_datetime(
            filtered_df["Date of Service (Facility Timezone)"],
            format='%m/%d/%Y %H:%M',  # Specify the format
            errors='raise'  # Raise an error if any entries cannot be converted
        )
    except Exception as e:
        print(f"Error converting dates: {e}")
        # Optionally handle the error, such as setting NaT or logging
        return filtered_df  # You can return the unfiltered df or handle as needed

    # Sort by the datetime column
    filtered_df = filtered_df.sort_values("Date of Service (Facility Timezone)")

    new_ICD_codes = []
    for index, row in filtered_df.iterrows():
        new_code_list = filtered_df["ICD10"].iloc[index].split(",")[0:6]
        new_code_list = ", ".join(new_code_list)
        new_ICD_codes.append(new_code_list)

    filtered_df["ICD10"] = new_ICD_codes
    return filtered_df

def browsefiles():
    global filtered_df_global  # Use the global variable
    fname = QFileDialog.getOpenFileName(caption="Upload a file",
                                         directory=os.getcwd(),
                                         filter="*.csv")
    if fname[0]:  # Check if a file was selected
        df = pd.read_csv(fname[0])
        filtered_df_global = clean_billing_csv(df)  # Update global filtered DataFrame

        # Populate the table with the first 5 rows of the filtered DataFrame
        filtered_table.setRowCount(min(5, len(filtered_df_global)))  # Show up to 5 rows
        for i in range(min(5, len(filtered_df_global))):
            for j in range(len(filtered_df_global.columns)):
                filtered_table.setItem(i, j, QTableWidgetItem(str(filtered_df_global.iat[i, j])))

        # Resize columns to fit content
        filtered_table.resizeColumnsToContents()

        # Show the table after data is uploaded
        filtered_table.setVisible(True)
        master_layout.insertWidget(3, filtered_table)  # Insert the table

        # Enable the download button after processing
        download.setEnabled(True)

def save_csv():
    global filtered_df_global  # Access the global filtered DataFrame
    if filtered_df_global is not None:
        save_fname = QFileDialog.getSaveFileName(caption="Save CSV File",
                                                  directory=os.getcwd(),
                                                  filter="CSV Files (*.csv)")

        if save_fname[0]:  # Check if a save path was selected
            filtered_df_global.to_csv(save_fname[0], index=False)  # Save the filtered DataFrame

# Connect signals
upload.clicked.connect(browsefiles)
download.clicked.connect(save_csv)

# Add the download button to the layout
master_layout.addWidget(download)  # This will now be placed in the layout after upload button

# Set the main layout
main_window.setLayout(master_layout)

# Show the window
main_window.show()
app.exec_()
