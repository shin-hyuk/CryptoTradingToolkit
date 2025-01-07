import smtplib
import zipfile
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Gmail credentials
GMAIL_USERNAME = "shinhyuk.contact"  # Replace with your Gmail address (without "@gmail.com")
GMAIL_APP_PASSWORD = "mpinjlrloudqgxqp"  # Replace with your Gmail App Password

# Recipients
recipients = ["shinhyuk.contact@gmail.com"]

# Function to zip whale activity files
def create_zip_file(folder_path, output_path):
    """Create a zip file containing all files in the specified folder."""
    with zipfile.ZipFile(output_path, 'w') as zipf:
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                zipf.write(file_path, os.path.basename(file_path))

# Paths
whale_activity_folder = "data/whale_activity"
zipped_file_path = "data/whale_activity.zip"

# Create the zip file
if not os.path.exists(whale_activity_folder):
    print("Whale activity folder does not exist.")
else:
    create_zip_file(whale_activity_folder, zipped_file_path)

# Create the email
msg = MIMEMultipart()
msg["Subject"] = "Crypto Data"
msg["To"] = ", ".join(recipients)
msg["From"] = f"{GMAIL_USERNAME}@gmail.com"

# Attach the zip file
if os.path.exists(zipped_file_path):
    with open(zipped_file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(zipped_file_path)}",
        )
        msg.attach(part)
else:
    print("Zipped whale activity file does not exist.")

# Send the email
try:
    # Connect to Gmail SMTP server
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(GMAIL_USERNAME, GMAIL_APP_PASSWORD)
    smtp_server.sendmail(msg["From"], recipients, msg.as_string())
    smtp_server.quit()
    print("Email sent successfully.")
except Exception as e:
    print(f"Failed to send email. Error: {e}")
