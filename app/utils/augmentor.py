import os
import time
from PIL import Image, ImageFilter, ImageOps
import numpy as np
import random

class ImageAugmentor:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def process_images(self, operations):
        processed_count = 0
        generated_files = []
        errors = []
        timestamp = int(time.time())
        
        try:
            files = [f for f in os.listdir(self.input_path) 
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            
            for filename in files:
                try:
                    img_path = os.path.join(self.input_path, filename)
                    with Image.open(img_path) as img:
                        # Convert to RGB if necessary
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # Apply selected operations
                        augmented_images = self._apply_augmentations(img, operations)
                        
                        # Save augmented images with timestamp to avoid conflicts
                        base_name = os.path.splitext(filename)[0]
                        for idx, aug_img in enumerate(augmented_images):
                            save_name = f"{base_name}_aug_{timestamp}_{idx}.jpg"
                            save_path = os.path.join(self.output_path, save_name)
                            aug_img.save(save_path, 'JPEG')
                            generated_files.append(save_name)
                            processed_count += 1
                            
                except Exception as e:
                    errors.append(f"Error processing {filename}: {str(e)}")
                    
        except Exception as e:
            errors.append(f"System error: {str(e)}")
            
        return processed_count, generated_files, errors

    def _apply_augmentations(self, image, operations):
        augmented_results = []
        
        # Always include the original image
        augmented_results.append(image.copy())
        
        if 'rotate' in operations:
            # Generate 3 rotated versions
            for angle in [90, 180, 270]:
                augmented_results.append(image.rotate(angle, expand=True))
                
        if 'flip' in operations:
            augmented_results.append(ImageOps.mirror(image))
            augmented_results.append(ImageOps.flip(image))
            
        if 'noise' in operations:
            # Add Gaussian noise
            img_array = np.array(image)
            noise = np.random.normal(0, 25, img_array.shape)
            noisy_img = np.clip(img_array + noise, 0, 255).astype(np.uint8)
            augmented_results.append(Image.fromarray(noisy_img))
            
        if 'blur' in operations:
            augmented_results.append(image.filter(ImageFilter.BLUR))
            
        if 'grayscale' in operations:
            augmented_results.append(ImageOps.grayscale(image).convert('RGB'))
            
        return augmented_results
