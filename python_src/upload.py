import os
import json
from flask import (
    Flask,
    request,
    send_from_directory,
    render_template,
    render_template_string
)
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

from utils.database import DocDatabaseWhoosh
from utils.pdf2txt import extract_text_from_pdf

with open('./storage_path_config.json') as f:
    storage_paths = json.load(f)
os.makedirs(storage_paths['original_doc_files_dir'], exist_ok=True)
os.makedirs(storage_paths['doc_database_dir'], exist_ok=True)

app = Flask(
    __name__,
    static_url_path='/static',
    static_folder=os.path.join(
        os.getcwd(),
        storage_paths['original_doc_files_dir']
    )
)
app.config['ORIGINAL_DOCS_FOLDER'] = storage_paths['original_doc_files_dir']
app.config['DOC_DATABASE_DIR'] = storage_paths['doc_database_dir']
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

ALLOWED_EXTENSIONS = set(['.pdf'])
def allowed_file(filename):
    _name, extension = os.path.splitext(filename)
    return '.' in extension and \
           extension in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/list_files', methods=['GET'])
def list_files():
    filenames = os.listdir(app.config['ORIGINAL_DOCS_FOLDER'])
    return render_template('list_files.html', filenames=filenames)

file_upload_template_str =  """
<html>
    <body>
        <h2>{{ msg }} Redirecting...</h2>
        <script>
            setTimeout(function(){
                window.location.href = '/';
            }, 3000);
        </script>
    </body>
</html>
"""

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_files = request.files.getlist("file[]")
        if not all(
                allowed_file(file.filename)
                for file in uploaded_files
            ):
            return render_template_string(
                file_upload_template_str,
                msg='Files Uploaded Failed. Reason: Bad file.'
            )

        database_item_list = []
        for file in uploaded_files:
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(
                    app.config['ORIGINAL_DOCS_FOLDER'],
                    filename
                ))
            extracted_text = extract_text_from_pdf(file.stream)
            database_item_list.append({
                'filename': file.filename,
                'content': extracted_text
            })

        database = DocDatabaseWhoosh(app.config['DOC_DATABASE_DIR'])
        database.add_batch(database_item_list)

        return render_template_string(
            file_upload_template_str,
            msg='Files Uploaded Successfully!'
        )

if __name__ == '__main__':
    app.run(debug=True)
