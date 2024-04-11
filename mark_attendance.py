import csv
from datetime import datetime

def read_csv_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data.append(row)
    return data

def write_csv_file(file_path, data):
    with open(file_path, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(data)

# Function to generate current date in d_m_y format
def get_current_date():
    return datetime.now().strftime('%d_%m_%Y')

# Function to update attendance in final.csv for students present in current date file
def update_attendance(final_csv_data, current_date_csv_data):
    current_date = get_current_date()
    date_column_index = final_csv_data[0].index(current_date) if current_date in final_csv_data[0] else None
    if date_column_index is not None:
        for row in final_csv_data[1:]:
            student_name = row[0].lower()  # Convert student name to lowercase for case-insensitive comparison
            present = False
            for current_row in current_date_csv_data:
                if current_row and len(current_row) > 0 and student_name == current_row[0].lower():
                    present = True
                    break
            row[date_column_index] = "Present" if present else "Absent"

# Example usage for reading 'final.csv':
final_csv_path = 'final.csv'
final_csv_data = read_csv_file(final_csv_path)

# Example usage for reading CSV file with current date as filename:
current_date_csv_path = f"{get_current_date()}.csv"
current_date_csv_data = read_csv_file(current_date_csv_path)

# Update attendance in 'final.csv' for students present in current date file
update_attendance(final_csv_data, current_date_csv_data)

# Write updated data back to 'final.csv'
write_csv_file(final_csv_path, final_csv_data)

print("Attendance updated successfully in 'final.csv'")
