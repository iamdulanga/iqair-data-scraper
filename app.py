import os
from flask import Flask, render_template, send_file

app = Flask(__name__)

# Folders where the files are already stored
ALL_STATIONS_MAPS_FOLDER = 'all_stations_maps'
PROVINCE_MAPS_FOLDER = 'province_maps'
CHARTS_FOLDER = 'charts'

# Ensure directories exist (not needed if files are pre-generated, but kept for safety)
os.makedirs(ALL_STATIONS_MAPS_FOLDER, exist_ok=True)
os.makedirs(PROVINCE_MAPS_FOLDER, exist_ok=True)
os.makedirs(CHARTS_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/list_files')
def list_files():
    # List all files in the folders
    all_stations_maps_files = os.listdir(ALL_STATIONS_MAPS_FOLDER)
    province_maps_files = os.listdir(PROVINCE_MAPS_FOLDER)
    charts_files = os.listdir(CHARTS_FOLDER)
    return {
        "all_stations_maps": all_stations_maps_files,
        "province_maps": province_maps_files,
        "charts": charts_files
    }


@app.route('/download/<folder>/<filename>')
def download_file(folder, filename):
    # Determine the correct folder path based on input
    folder_paths = {
        'all_stations_maps': ALL_STATIONS_MAPS_FOLDER,
        'province_maps': PROVINCE_MAPS_FOLDER,
        'charts': CHARTS_FOLDER
    }
    folder_path = folder_paths.get(folder)

    if folder_path:
        file_path = os.path.join(folder_path, filename)
        return send_file(file_path, as_attachment=True)
    return "Folder not found", 404


if __name__ == '__main__':
    app.run(debug=True)
