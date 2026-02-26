import os
import zipfile
import io
import time
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, send_from_directory, send_file, session
from werkzeug.utils import secure_filename
from .utils.augmentor import ImageAugmentor
from .utils.text_augmentor import TextAugmentor

main_bp = Blueprint('main', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@main_bp.route('/augment_text', methods=['POST'])
def augment_text():
    text = request.form.get('input_text')
    operations = request.form.getlist('text_operations')
    # ISO 639-3 language code for synonym replacement (default: English)
    lang = request.form.get('synonym_lang', 'eng').strip() or 'eng'

    if not text:
        flash('No text provided')
        return redirect(url_for('main.index'))

    if not operations:
        flash('No text augmentation operations selected')
        return redirect(url_for('main.index'))

    augmentor = TextAugmentor()

    augmented_texts = augmentor.process_text(text, operations, lang=lang)
    
    output_path = current_app.config['OUTPUT_FOLDER']
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    timestamp = int(time.time())
    saved_files = []
    
    for i, (aug_type, aug_text) in enumerate(augmented_texts):
        filename = f"text_aug_{timestamp}_{i}_{aug_type.replace(' ', '_').lower()}.txt"
        filepath = os.path.join(output_path, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(aug_text)
        saved_files.append(filename)
        
    session['generated_text_files'] = saved_files
    flash(f'Successfully generated {len(saved_files)} augmented text files!', 'success')
    return redirect(url_for('main.text_results'))

@main_bp.route('/text_results')
def text_results():
    output_path = current_app.config['OUTPUT_FOLDER']
    files = []
    generated_files = session.get('generated_text_files', [])
    
    if os.path.exists(output_path):
        files = [f for f in generated_files if os.path.exists(os.path.join(output_path, f))]
        
    # Read content for preview
    file_contents = []
    for f in files:
        try:
            with open(os.path.join(output_path, f), 'r') as file:
                content = file.read()
                file_contents.append({'filename': f, 'content': content})
        except:
            pass
            
    return render_template('results.html', text_files=file_contents)

@main_bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        input_mode = request.form.get('input_mode', 'files')
        operations = request.form.getlist('operations')
        
        if not operations:
            flash('No augmentation operations selected')
            return redirect(request.url)
        
        # Process images - append to existing output folder instead of clearing
        output_path = current_app.config['OUTPUT_FOLDER']
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        if input_mode == 'folder':
            # Handle folder upload mode
            if 'folder_files[]' not in request.files:
                flash('No folder files part')
                return redirect(request.url)
                
            files = request.files.getlist('folder_files[]')
            
            if not files or files[0].filename == '':
                flash('No files selected in folder')
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
                    filename = secure_filename(os.path.basename(file.filename))
                    file.save(os.path.join(upload_path, filename))
                    saved_files.append(filename)
                    
            if not saved_files:
                flash('No valid images found in the uploaded folder')
                return redirect(request.url)
            
            # Process images from upload folder (same as single file mode now)
            augmentor = ImageAugmentor(upload_path, output_path)
            
            # Extract configuration from form
            config = {
                'scale_up': request.form.get('scale_up', 20),
                'scale_down': request.form.get('scale_down', 20),
                'brightness_up': request.form.get('brightness_up', 30),
                'brightness_down': request.form.get('brightness_down', 30),
                'contrast_up': request.form.get('contrast_up', 30),
                'contrast_down': request.form.get('contrast_down', 30)
            }
            
            count, generated_files, errors = augmentor.process_images(operations, config)
            
        else:
            # Handle file upload mode
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
            
            augmentor = ImageAugmentor(upload_path, output_path)
            
            # Extract configuration from form
            config = {
                'scale_up': request.form.get('scale_up', 20),
                'scale_down': request.form.get('scale_down', 20),
                'brightness_up': request.form.get('brightness_up', 30),
                'brightness_down': request.form.get('brightness_down', 30),
                'contrast_up': request.form.get('contrast_up', 30),
                'contrast_down': request.form.get('contrast_down', 30)
            }
            
            count, generated_files, errors = augmentor.process_images(operations, config)
        
        # Store generated filenames in session
        session['generated_files'] = generated_files
        
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
    
    # Only get images that were just generated (from session)
    generated_files = session.get('generated_files', [])
    
    if os.path.exists(output_path):
        # Filter files that exist in output folder and were in the generated list
        images = [f for f in generated_files if os.path.exists(os.path.join(output_path, f))]
        
        # Fallback: if session is empty (e.g. direct access), show nothing or maybe last batch?
        # For now let's stick to showing only what's in session to solve the user's issue
        
    return render_template('results.html', images=images)

@main_bp.route('/generated/<filename>')
def generated_file(filename):
    return send_from_directory(current_app.config['OUTPUT_FOLDER'], filename)

@main_bp.route('/save_texts', methods=['POST'])
def save_texts():
    selected_texts = request.form.getlist('selected_texts')
    output_path = request.form.get('output_path', '').strip()

    if not selected_texts:
        flash('No text files selected for saving', 'error')
        return redirect(url_for('main.text_results'))

    if not output_path:
        flash('No output folder path provided', 'error')
        return redirect(url_for('main.text_results'))

    output_path = os.path.expanduser(output_path)
    if not os.path.isabs(output_path):
        output_path = os.path.abspath(output_path)

    try:
        os.makedirs(output_path, exist_ok=True)
    except Exception as e:
        flash(f'Error creating output directory: {str(e)}', 'error')
        return redirect(url_for('main.text_results'))

    generated_path = current_app.config['OUTPUT_FOLDER']
    saved_count = 0
    errors = []

    for text_filename in selected_texts:
        source_path = os.path.join(generated_path, text_filename)
        if os.path.exists(source_path):
            try:
                dest_path = os.path.join(output_path, text_filename)
                counter = 1
                base_name, ext = os.path.splitext(text_filename)
                while os.path.exists(dest_path):
                    dest_path = os.path.join(output_path, f"{base_name}_{counter}{ext}")
                    counter += 1
                with open(source_path, 'rb') as src, open(dest_path, 'wb') as dst:
                    dst.write(src.read())
                saved_count += 1
            except Exception as e:
                errors.append(f"Error saving {text_filename}: {str(e)}")
        else:
            errors.append(f"File not found: {text_filename}")

    if errors:
        for error in errors:
            flash(error, 'error')

    if saved_count > 0:
        flash(f'Successfully saved {saved_count} text file(s)', 'success')

    return redirect(url_for('main.text_results'))


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
        flash(f'Successfully saved {saved_count} images', 'success')
    
    return redirect(url_for('main.results'))
