from flask import Flask, request, jsonify, send_file,send_from_directory
from pathlib import Path
import os
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

#get the users desktop directory

DESKTOP_PATH = Path.home() / "Desktop"

#folder name
FOLDER_NAME = "Videos"

#create a folder if it doesn't exist
FOLDER_PATH = DESKTOP_PATH/ FOLDER_NAME
FOLDER_PATH.mkdir(parents= True, exist_ok = True)

@app.route("/api/upload", methods=["POST"])
def upload_file():
    try :
        #check if the file is in the request
        if "file" not in request.files:
            return jsonify({"error": "Bad request, file not included"}), 400
        file = request.files["file"]

        #check if the file not is not empty
        if file.filename == "":
            return jsonify({"error":"Bad request, file has no name"}), 400

        file_path = os.path.join(FOLDER_PATH, file.filename)
        #save the file
        file.save(file_path)

        #check the video size
        file_size = os.path.getsize(file_path)
        #define thershold
        max_video_size = 250*1024*1024 #250MB

        #check if the size exceeds the thershold
        if file_size> max_video_size:
            compressed_video_path = os.path.join(FOLDER_PATH, f"compressed{file.filename}")
            ffmpeg_cmd =[
                "ffmpeg",
                "-i", file_path,
                "-vf", "scale=640:-1",
                "-c:v", "libx264",
                "-crf", "23",
                compressed_video_path
            ]
            subprocess.run(ffmpeg_cmd, check=True)

            #remove the original video path
            os.remove(file_path)
            #use the compressed video path for futher need
            file_path = compressed_video_path
            return jsonify({"messsage":"file saved after compression"}),200


        return jsonify({"message":"file saved successfully"}), 201
    except Exception as e:
        return jsonify (str(e))    
@app.route("/api/videos", methods=["GET"])
def get_contents():
    contents = os.listdir(FOLDER_PATH)
    if len(contents) == 0:
        return jsonify({"message":"no contents availavle"}),200 
    else:    
        return jsonify({"contents": contents}), 200

@app.route("/api/videos/recent", methods=["GET"])
def get_last_video():
    try:
        contents = os.listdir(FOLDER_PATH)
        if not contents:
            return jsonify({"message": "theres is no video"})
        contents_sorted = sorted(contents, key= lambda x:os.path.getmtime(
            os.path.join(FOLDER_PATH, x)), reverse= True )

        return jsonify({"most_recent_file":contents_sorted[0]}), 200
    except IndexError:
        return jsonify({"message": "no contents"})
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=80100,debug=True)                
