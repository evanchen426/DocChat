import os
import re
import sys
from flask import (
    Flask,
    request,
    render_template,
    render_template_string
)
# from werkzeug.utils import secure_filename

from utils.database import storage_configs, MyDocDatabase
from utils.pdf2txt import extract_text_from_pdf

os.makedirs(storage_configs['original_doc_files_dir'], exist_ok=True)
os.makedirs(storage_configs['doc_database_dir'], exist_ok=True)

app = Flask(
    __name__,
    static_url_path='/static',
    static_folder=os.path.join(
        os.getcwd(),
        storage_configs['original_doc_files_dir']
    )
)
app.config['ORIGINAL_DOCS_FOLDER'] = storage_configs['original_doc_files_dir']
app.config['DOC_DATABASE_DIR'] = storage_configs['doc_database_dir']
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

@app.route('/text/<path:filename>', methods=['GET'])
def get_raw_text(filename):
    database = MyDocDatabase(app.config['DOC_DATABASE_DIR'])
    all_docs = database.get_all()
    print([doc for doc in all_docs if 'x-100' in doc['filename']])
    filter_iter = (doc['content'] for doc in all_docs if doc['filename'] == filename)
    content = next(filter_iter, None)
    if content is None:
        return '404 File not found', 404
    return content.replace('\n', '<br />')

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

def my_secure_filename(filename: str) -> str:
    my_secure_filter = r'[^A-Za-z0-9_\u4e00-\u9fbf\.\-]'
    filtered_filename = re.sub(my_secure_filter, '', filename)
    filtered_filename = filtered_filename.strip()
    return filtered_filename

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
                filename = my_secure_filename(file.filename)
                try:
                    extracted_text = extract_text_from_pdf(file.stream)
                except:
                    continue
                file.save(os.path.join(
                    app.config['ORIGINAL_DOCS_FOLDER'],
                    filename
                ))
                database_item_list.append({
                    'filename': filename,
                    'content': extracted_text
                })
                print(f'Saved file {filename}')

        database = MyDocDatabase(app.config['DOC_DATABASE_DIR'])
        database.add_batch(database_item_list)

        return render_template_string(
            file_upload_template_str,
            msg='Files Uploaded Successfully!'
        )

if __name__ == '__main__':
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = 80
    app.run(host='0.0.0.0', port=port)
