import os
import zipfile
import io
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_from_directory, send_file
from werkzeug.utils import secure_filename
from .utils.augmentor import ImageAugmentor

main_bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'files[]' not in request.files:
            flash('No file part')
            return redirect(request.url)
            
        files = request.files.getlist('files[]')
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if not files or files[0].filename == '':
            flash('No selected file')
            return redirect(request.url)
            
        operations = request.form.getlist('operations')
        if not operations:
            flash('No augmentation operations selected')
            return redirect(request.url)

        # Clear previous uploads
        upload_path = current_app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
            
        for f in os.listdir(upload_path):
            os.remove(os.path.join(upload_path, f))
            
        # Save uploaded files
        saved_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(upload_path, filename))
                saved_files.append(filename)
                
        if not saved_files:
            flash('No valid images uploaded')
            return redirect(request.url)

        # Process images
        output_path = current_app.config['OUTPUT_FOLDER']
        # Clear previous outputs
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        if os.path.exists(output_path):
            for f in os.listdir(output_path):
                os.remove(os.path.join(output_path, f))
        
        augmentor = ImageAugmentor(upload_path, output_path)
        count, errors = augmentor.process_images(operations)
        
        if errors:
            for error in errors:
                flash(error, 'error')
        
        flash(f'Successfully generated {count} augmented images!', 'success')
        return redirect(url_for('main.results'))

    return render_template('index.html')

@main_bp.route('/results')
def results():
    output_path = current_app.config['OUTPUT_FOLDER']
    images = []
    if os.path.exists(output_path):
        images = [f for f in os.listdir(output_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        images.sort()
    return render_template('results.html', images=images)

@main_bp.route('/generated/<filename>')
def generated_file(filename):
    return send_from_directory(current_app.config['OUTPUT_FOLDER'], filename)

@main_bp.route('/download', methods=['POST'])
def download_images():
    selected_images = request.form.getlist('selected_images')
    
    if not selected_images:
        flash('No images selected for download', 'error')
        return redirect(url_for('main.results'))
        
    output_path = current_app.config['OUTPUT_FOLDER']
    memory_file = io.BytesIO()
    
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for image_name in selected_images:
            file_path = os.path.join(output_path, image_name)
            if os.path.exists(file_path):
                zf.write(file_path, image_name)
                
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='augmented_images.zip'
    )
