from flask import Flask, request, jsonify, send_from_directory
import shutil
from pathlib import Path
import os

app = Flask(__name__)

# Get the user's desktop directory
DESKTOP_PATH = Path.home() / "Desktop"

# The folder name
FOLDER_NAME = "apiVideos"

# Create the folder if it doesn't exist
FOLDER_PATH = DESKTOP_PATH / FOLDER_NAME
FOLDER_PATH.mkdir(parents=True, exist_ok=True)

NO_CONTENT_RESPONSE = "No saved record YET."

@app.route("/api/upload", methods=["POST"])
def upload_file():
    try:
        # Check if a file is included in the request
        if "file" not in request.files:
            return jsonify({"error": "Bad Request", "message": "File not included"}), 400

        file = request.files["file"]

        # Check if the file name is not empty
        if file.filename == "":
            return jsonify({"error": "Bad Request", "message": "File has no name"}), 400

        file_path = os.path.join(FOLDER_PATH, file.filename)

        # Save the file to the specified path
        file.save(file_path)

        return jsonify({"message": "File saved successfully to apiVideos folder on your desktop"}), 201

    except Exception as e:
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

@app.route("/api/videos", methods=["GET"])
def get_folder_contents():
    contents = os.listdir(FOLDER_PATH)

    if len(contents) == 0:
        return jsonify({"message": NO_CONTENT_RESPONSE}), 200
    else:
        return jsonify({"folder_contents": contents}), 200

@app.route("/api/video/recent", methods=["GET"])
def get_recent_content():
    try:
        contents = os.listdir(FOLDER_PATH)

        if not contents:
            return jsonify({"message": NO_CONTENT_RESPONSE}), 200

        # Sort based on modification time
        contents_sorted = sorted(
            contents,
            key=lambda x: os.path.getmtime(os.path.join(FOLDER_PATH, x)),
            reverse=True,
        )

        return jsonify({"recent_file": contents_sorted[0]}), 200

    except IndexError:
        return jsonify({"message": NO_CONTENT_RESPONSE}), 200

if __name__ == "__main__":
    app.run(debug=True)
