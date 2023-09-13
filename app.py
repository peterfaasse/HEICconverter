import os
from tempfile import NamedTemporaryFile

from flask import Flask, render_template, request, send_file
from PIL import Image
from pillow_heif import register_heif_opener

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = "converted"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["CONVERTED_FOLDER"] = CONVERTED_FOLDER


register_heif_opener()

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(CONVERTED_FOLDER):
    os.makedirs(CONVERTED_FOLDER)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return "No file part"

    file = request.files["file"]

    if file.filename == "":
        return "No selected file"

    if file:
        temp_file = NamedTemporaryFile(delete=False)
        file.save(temp_file)
        temp_file.close()

        output_format = request.form.get("format", "jpeg")

        # Convert the HEIF image to the selected format (JPEG by default)
        heif_file = temp_file.name
        register_heif_opener()
        temp_img = Image.open(heif_file)

        converted_filename = os.path.splitext(file.filename)[0] + "." + output_format
        converted_filepath = os.path.join(
            app.config["CONVERTED_FOLDER"], converted_filename
        )

        temp_img.save(converted_filepath)

        # Clean up the temporary file
        os.remove(temp_file.name)

        return send_file(converted_filepath, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
