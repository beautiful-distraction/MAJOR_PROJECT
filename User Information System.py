import sys
import cv2
import os
from IPython.display import display, HTML
import webbrowser
import threading
import subprocess
from PIL import Image, ImageTk
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtGui import QImage, QPixmap,QFont
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThreadPool, QObject, pyqtSignal, QRunnable
import face_recognition
import mysql.connector
import matplotlib.pyplot as plt

class FaceRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Recognition App")
        self.thread_pool = QThreadPool()

        self.setGeometry(0, 0, 1920,1080)
        background_image = QPixmap("C:\\Users\\KARTHIK\\Downloads\\666381-blood-tests.jpg")  # Replace with the actual image path

        # Create a QLabel for the background image
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.setPixmap(background_image)
        self.background_label.lower() 


#


        self.setGeometry(200, 200, 1200, 800)  # Set initial window size

        self.title_label = QLabel("User Information Collector", self)
        self.title_label.setGeometry(0, 0, 1400, 60)  # Set position and size
        title_font = QFont("Arial", 24)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignCenter)

        self.name_label = QLabel("Name:", self)
        self.name_label.setGeometry(100, 100, 100, 40)  # Set position and size

        self.name_entry = QLineEdit(self)
        self.name_entry.setGeometry(210, 100, 200, 40)  # Set position and size
        self.name_entry.setFont(QFont("Arial", 20))

    

        self.new_user_button = QPushButton("Registration", self)
        self.new_user_button.setGeometry(100, 700, 150, 60)  # Set position and size
        self.new_user_button.clicked.connect(self.capture_user)

        self.existing_user_button = QPushButton("Face Recognition", self)
        self.existing_user_button.setGeometry(300, 700, 150, 60)  # Set position and size
        self.existing_user_button.clicked.connect(self.start_face_detection)

        self.update_button = QPushButton("Data", self)
        self.update_button.setGeometry(500, 700, 150, 60)  # Set position and size
        self.update_button.clicked.connect(self.generate_hyperlink)

          # Set position and size
        

        self.image_label = QLabel(self)
        self.image_label.setGeometry(1000, 100, 200, 200)  # Set position and size

        self.age_label = QLabel("Age:", self)
        self.age_label.setGeometry(100, 200, 100, 40)  # Set position and size

        self.age_entry = QLineEdit(self)
        self.age_entry.setGeometry(210, 200, 200, 40)  # Set position and size
        self.age_entry.setFont(QFont("Arial", 20))

        self.blood_group_label = QLabel("Blood Group:", self)
        self.blood_group_label.setGeometry(100, 300, 100, 40)  # Set position and size

        self.blood_group_entry = QLineEdit(self)
        self.blood_group_entry.setGeometry(210, 300, 200, 40)  # Set position and size
        self.blood_group_entry.setFont(QFont("Arial", 20))

        self.visualize_age_button = QPushButton("Visualize Data", self)
        self.visualize_age_button.setGeometry(700, 700, 150, 60)  # Set position and size
        self.visualize_age_button.clicked.connect(self.visualize_combined_data)

    # Initialize database connection and other variables...


        self.captured_image = None
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="face_recognition_db",
            port=3306
        )
        self.db_cursor = self.db_connection.cursor()
        self.selected_user_data = {}

        self.cap = cv2.VideoCapture(0)

    def visualize_age_distribution(self):
        sql = "SELECT age FROM users"
        self.db_cursor.execute(sql)
        user_ages = self.db_cursor.fetchall()
        ages = [age[0] for age in user_ages]

        plt.figure(figsize=(12, 6))
        # Histogram
        plt.subplot(1, 2, 1)
        plt.hist(ages, bins=10, edgecolor='black')
        plt.title("Age Distribution")
        plt.xlabel("Age")
        plt.ylabel("Frequency")

        # Box Plot
        plt.subplot(1, 2, 2)
        plt.boxplot(ages)
        plt.title("Age Distribution - Box Plot")
        plt.ylabel("Age")
        plt.xticks([1], ['Ages'])

        plt.tight_layout()
        plt.show()

    def visualize_blood_group_frequency(self):
        sql = "SELECT blood_group FROM users"
        self.db_cursor.execute(sql)
        blood_groups = self.db_cursor.fetchall()
        blood_group_counts = {blood_group[0]: blood_groups.count(blood_group) for blood_group in set(blood_groups)}

        plt.figure(figsize=(12, 6))
        # Pie Chart
        plt.subplot(1, 2, 1)
        labels = blood_group_counts.keys()
        sizes = blood_group_counts.values()
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title("Blood Group Frequency - Pie Chart")

        # Bar Chart
        plt.subplot(1, 2, 2)
        plt.bar(labels, sizes)
        plt.title("Blood Group Frequency - Bar Chart")
        plt.xlabel("Blood Group")
        plt.ylabel("Frequency")

        plt.tight_layout()
        plt.show()

    def visualize_combined_data(self):
        plt.figure(figsize=(12, 6))
        # Age Distribution (Histogram and Box Plot)
        plt.subplot(1, 2, 1)
        self.visualize_age_distribution()

        # Blood Group Frequency (Pie Chart and Bar Chart)
        plt.subplot(1, 2, 2)
        self.visualize_blood_group_frequency()

        plt.tight_layout()
        plt.show()

    def validate_input(self):
        name = self.name_entry.text()
        age = self.age_entry.text()
        blood_group = self.blood_group_entry.text()

        if not name or not age or not blood_group:
            QMessageBox.critical(self, "Input Error", "Please fill in all fields.")
            return False

        return True


    def generate_hyperlink(url):
        webbrowser.open(url)
        try:
            subprocess.run(["xdg-open", url], check=True)  # Linux
        except subprocess.CalledProcessError:
            try:
                subprocess.run(["open", url], check=True)  # macOS
            except subprocess.CalledProcessError:
                try:
                    subprocess.run(["start", "", url], check=True, shell=True)  # Windows
                except subprocess.CalledProcessError:
                    print("Unable to open the browser.")
    url = "http://localhost/phpmyadmin/index.php?route=/sql&db=face_recognition_db&table=users&pos=0"
    generate_hyperlink(url)
# Example usage
    

    def capture_user(self):
        if not self.validate_input():
            return

        name = self.name_entry.text()
        age = self.age_entry.text()
        blood_group = self.blood_group_entry.text()

        folder_path = r"C:\Users\KARTHIK\OneDrive\Desktop\Data\Kartik"
        image_name = f"{name}_{age}_{blood_group}.jpg"

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        image_path = os.path.join(folder_path, image_name)

        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(image_path, frame)
        cap.release()

        self.display_captured_image(frame)
        print("Image captured and saved successfully.")

        # Insert user data into the database
        sql = "INSERT INTO users (name, age, blood_group, image_path) VALUES (%s, %s, %s, %s)"
        values = (name, age, blood_group, image_path)

        try:
            self.db_cursor.execute(sql, values)
            self.db_connection.commit()
            print("User data inserted into the database.")
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.db_connection.rollback()

    def display_captured_image(self, frame):
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)

    def start_face_detection(self):
        cap = cv2.VideoCapture(0)

        known_face_encodings = []
        known_face_names = []

    # Load face encodings for the stored images
        image_folder = "C:\\Users\\KARTHIK\\OneDrive\\Desktop\\Data\\Kartik"
        image_files = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.jpeg', '.png'))]

        for file in image_files:
            img_path = os.path.join(image_folder, file)
            img = face_recognition.load_image_file(img_path)
            encoding = face_recognition.face_encodings(img)[0]

            known_face_encodings.append(encoding)
            known_face_names.append(file)

    #

    def _face_detection(self, cap, known_face_encodings, known_face_names):
        while True:
            ret, frame = cap.read()

            if not ret:
                break

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)

                if True in matches:
                    matched_index = matches.index(True)
                    name = known_face_names[matched_index]

                    QMessageBox.information(self, "Face Detected", f"Detected: {name}")
                    cap.release()
                    return

            cv2.imshow('Live Face Detection', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


# Load face encodings for the stored images


if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = FaceRecognitionApp()
    window.show()
    sys.exit(app.exec_())

        