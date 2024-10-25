from flask import Flask, render_template, request, send_from_directory, jsonify
import requests
import os
import yt_dlp
import re
import platform

app = Flask(__name__)

# Default download directories
DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")

def get_download_directory():
    """Get appropriate download directory based on platform."""
    system = platform.system()
    if system == 'ANDROID_STORAGE' in os.environ:
        return '/storage/emulated/0/Download'
    elif system == 'Mac':
        return os.path.join(os.path.expanduser("~"), "Downloads")
    elif system == 'Windows':
        return os.path.join(os.path.expanduser("~"), "Downloads")
    return DOWNLOAD_DIR

def rename_mp4_to_mp3(mp4_filepath):
    """Rename the .mp4 file to .mp3."""
    mp3_filepath = mp4_filepath.replace('.mp4', '.mp3')
    os.rename(mp4_filepath, mp3_filepath)
    return mp3_filepath

def download_file(link):
    """Download YouTube video or file from a link in MP4 format and convert to MP3."""
    download_dir = get_download_directory()
    filepath = None

    try:
        if re.match(r'^(https?://)?(www\.)?(youtube\.com|youtu\.be|music\.youtube\.com)/.+', link):
            ydl_opts = {
                'format': 'best[ext=mp4]',  # Always download as mp4
                'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
                'quiet': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                filename = ydl.prepare_filename(info)
                filepath = os.path.join(download_dir, os.path.basename(filename))

                # Convert to MP3 after downloading
                if filepath.endswith('.mp4'):
                    mp3_filepath = rename_mp4_to_mp3(filepath)
                    return filepath, mp3_filepath

        else:
            response = requests.get(link, stream=True)
            response.raise_for_status()
            filename = link.split('/')[-1] or 'downloaded_file'
            filename += '.mp4'  # Always append .mp4
            filepath = os.path.join(download_dir, filename)

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Convert to MP3 after downloading
            if filepath.endswith('.mp4'):
                mp3_filepath = rename_mp4_to_mp3(filepath)
                return filepath, mp3_filepath

        return filepath, None

    except Exception as e:
        print(f"Error: {e}")
        return None, None

@app.route('/')
def ConvertToMp3():
    return render_template('ConvertToMp3.html')

@app.route('/download', methods=['POST'])
def download():
    link = request.form.get('link')
    filepath, mp3_filepath = download_file(link)

    if filepath and mp3_filepath:
        return send_from_directory(directory=get_download_directory(), path=os.path.basename(mp3_filepath), as_attachment=True)

    return jsonify({'error': 'Download failed'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=0000, debug=True)  # Set a valid port number (e.g., 5000)
