from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image
from io import BytesIO
from flask import send_file
import base64 
import io
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
    try:
        if request.method == "POST":
            # Periksa apakah file diunggah
            if "audio_file" not in request.files:
                return "Tidak ada file yang diunggah", 400
            
            audio_file = request.files["audio_file"]
            if audio_file.filename == "":
                return "Tidak ada file yang dipilih", 400

            # Baca audio dari stream
            audio_data = audio_file.read()

            # Tentukan path untuk menyimpan audio sementara
            temp_audio_path = "/tmp/temp_audio.wav"

            # Simpan audio ke file sementara
            with open(temp_audio_path, "wb") as temp_audio_file:
                temp_audio_file.write(audio_data)

            # Baca audio dari file sementara
            audio, samplerate = sf.read(temp_audio_path)

            # Kompresi audio
            compressed_audio = audio[::2]  # Contoh kompresi setengah sampel

            # Tentukan path untuk menyimpan audio yang sudah dikompresi
            compressed_audio_path = "/tmp/compressed_audio.wav"

            # Simpan audio yang sudah dikompresi
            sf.write(compressed_audio_path, compressed_audio, samplerate)

            # Baca audio yang sudah dikompresi
            with open(compressed_audio_path, "rb") as compressed_audio_file:
                compressed_audio_data = compressed_audio_file.read()

            # Kirim file audio yang sudah dikompresi untuk diunduh
            return send_file(
                io.BytesIO(compressed_audio_data),
                mimetype="audio/wav",
                as_attachment=True,
                download_name="compressed_audio.wav"
            )

        return jsonify({"error": "Metode request tidak valid"}), 405
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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