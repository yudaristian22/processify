from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image
from io import BytesIO
from flask import send_file
import base64 
import io,os
import subprocess
import soundfile as sf
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/contact")
def contact():
	return render_template("contact.html")

@app.route("/audioprocessing")
def audio():
	return render_template("audioprocessing.html")

@app.route("/compress_audio", methods=["POST"])
def compress_audio():
    if "audio_file" not in request.files:
        return "Tidak ada file yang diunggah", 400

    audio_file = request.files["audio_file"]
    if audio_file.filename == "":
        return "Tidak ada file yang dipilih", 400

    # Simpan file audio yang diunggah ke server
    filename = secure_filename(audio_file.filename)
    audio_file.save(filename)

    # Lakukan proses kompresi audio menggunakan subprocess
    subprocess.run(["ffmpeg", "-i", filename, "-b:a", "64k", "-compression_level", "10", "compressed_audio.mp3"])

    # Hapus file asli yang diunggah
    os.remove(filename)

    # Kirim file audio yang telah dikompres ke pengguna
    return send_file("compressed_audio.mp3", as_attachment=True)
      
@app.route("/imageprocessing", methods=["GET", "POST"])
def process_image():
    if request.method == "POST":
        # Periksa apakah file diunggah
        if "image_file" not in request.files:
            return "Tidak ada file yang diunggah", 400
        
        image_file = request.files["image_file"]
        if image_file.filename == "":
            return "Tidak ada file yang dipilih", 400
        
        # Ubah ukuran gambar
        img = Image.open(image_file)
        img_resize = img.resize((300, 300)) # Ubah ukuran sesuai kebutuhan

        # Simpan gambar yang telah diubah ukuran ke dalam BytesIO
        img_io = BytesIO()
        img_resize.save(img_io, "JPEG", quality=85) # Sesuaikan kualitas gambar
        img_io.seek(0)

        # Konversi gambar yang telah diubah ukuran menjadi base64
        processed_image_url = f"data:image/jpeg;base64,{base64.b64encode(img_io.getvalue()).decode()}"

        return render_template("imageprocessing.html", processed_image_url=processed_image_url)

    return render_template("imageprocessing.html", processed_image_url=None)