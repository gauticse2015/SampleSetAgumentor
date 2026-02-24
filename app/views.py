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

@main_bp.route('/save', methods=['POST'])
def save_images():
    selected_images = request.form.getlist('selected_images')
    output_path = request.form.get('output_path', '').strip()
    
    if not selected_images:
        flash('No images selected for saving', 'error')
        return redirect(url_for('main.results'))
    
    if not output_path:
        flash('No output folder path provided', 'error')
        return redirect(url_for('main.results'))
    
    # Expand user home directory if path starts with ~
    output_path = os.path.expanduser(output_path)
    
    # Convert to absolute path if relative
    if not os.path.isabs(output_path):
        output_path = os.path.abspath(output_path)
    
    # Create output directory if it doesn't exist
    try:
        os.makedirs(output_path, exist_ok=True)
    except Exception as e:
        flash(f'Error creating output directory: {str(e)}', 'error')
        return redirect(url_for('main.results'))
    
    generated_path = current_app.config['OUTPUT_FOLDER']
    saved_count = 0
    errors = []
    
    for image_name in selected_images:
        source_path = os.path.join(generated_path, image_name)
        if os.path.exists(source_path):
            try:
                dest_path = os.path.join(output_path, image_name)
                # Handle duplicate filenames
                counter = 1
                base_name, ext = os.path.splitext(image_name)
                while os.path.exists(dest_path):
                    dest_path = os.path.join(output_path, f"{base_name}_{counter}{ext}")
                    counter += 1
                
                # Copy file
                with open(source_path, 'rb') as src, open(dest_path, 'wb') as dst:
                    dst.write(src.read())
                saved_count += 1
            except Exception as e:
                errors.append(f"Error saving {image_name}: {str(e)}")
        else:
            errors.append(f"File not found: {image_name}")
    
    if errors:
        for error in errors:
            flash(error, 'error')
    
    if saved_count > 0:
        flash(f'Successfully saved {saved_count} images to {output_path}', 'success')
    
    return redirect(url_for('main.results'))
