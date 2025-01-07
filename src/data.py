import os
import json
from firebase_admin import firestore, credentials, initialize_app

# Initialize Firebase
cred = credentials.Certificate("./credentials.json")  # Replace with your Firebase credentials JSON file
initialize_app(cred)

# Firestore client
db = firestore.client()

# Define the collection name
COLLECTION_NAME = "whale_activity"

# Path to the local data folder
DATA_FOLDER = "data/whale_activity"

# Convert .txt files to JSON and upload to Firestore
def convert_and_upload_txt_to_firestore():
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".txt"):
            txt_path = os.path.join(DATA_FOLDER, filename)

            # Derive the document ID from the file name
            document_id = filename.replace(".txt", "")

            # Read the .txt file content
            with open(txt_path, "r") as file:
                file_content = file.read()

            # Parse the content as JSON
            data = json.loads(file_content.replace("'", "\""))

            # Upload data to Firestore
            db.collection(COLLECTION_NAME).document(document_id).set(data)
            print(f"Uploaded '{filename}' to Firestore as document ID '{document_id}'.")

if __name__ == "__main__":
    convert_and_upload_txt_to_firestore()
