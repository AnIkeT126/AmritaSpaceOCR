from flask import Flask, render_template, request, send_file, make_response
import os
import cv2
import pytesseract
import tempfile
from docx import Document
from io import BytesIO
from urllib.parse import quote as url_quote



app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

tesseract_path = os.getenv('TESSERACT_PATH')

# If the environment variable is not set, use a default path
if not tesseract_path:
    tesseract_path = '/usr/bin/tesseract'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            image_filename = file.filename
            file.save(os.path.join(UPLOAD_FOLDER, image_filename))
            image = cv2.imread(os.path.join(UPLOAD_FOLDER, image_filename))
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            text = pytesseract.image_to_string(gray, lang='eng', config='--psm 6')
            return render_template('download.html', image_filename=image_filename, text=text)
    return 'No file uploaded', 400

@app.route('/uploads/<filename>')
def uploaded_image(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename))

@app.route('/download_text/<text>')
def download_text(text):
    # Create a new document
    doc = Document()
    
    # Add the text to the document
    doc.add_paragraph(text)
    
    # Save the document to a BytesIO object
    doc_buffer = BytesIO()
    doc.save(doc_buffer)
    doc_buffer.seek(0)
    
    # Create a response with the document as an attachment
    response = make_response(doc_buffer.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=output.docx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    
    return response

if __name__ == '__main__':
    app.run(debug=True)
