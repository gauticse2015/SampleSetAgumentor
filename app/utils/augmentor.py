import os
import time
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import numpy as np
import random

class ImageAugmentor:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

    def process_images(self, operations, config=None):
        processed_count = 0
        generated_files = []
        errors = []
        timestamp = int(time.time())
        config = config or {}
        
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
                        augmented_images = self._apply_augmentations(img, operations, config)
                        
                        # Save augmented images with timestamp to avoid conflicts
                        base_name = os.path.splitext(filename)[0]
                        for idx, (aug_name, aug_img) in enumerate(augmented_images):
                            save_name = f"{base_name}_aug_{timestamp}_{idx}_{aug_name}.jpg"
                            save_path = os.path.join(self.output_path, save_name)
                            aug_img.save(save_path, 'JPEG')
                            generated_files.append(save_name)
                            processed_count += 1
                            
                except Exception as e:
                    errors.append(f"Error processing {filename}: {str(e)}")
                    
        except Exception as e:
            errors.append(f"System error: {str(e)}")
            
        return processed_count, generated_files, errors

    def _apply_augmentations(self, image, operations, config=None):
        augmented_results = []
        config = config or {}
        
        if 'rotate' in operations:
            # Generate 3 rotated versions
            for angle in [90, 180, 270]:
                augmented_results.append((f"rotate_{angle}", image.rotate(angle, expand=True)))
                
        if 'flip' in operations:
            augmented_results.append(("flip_mirror", ImageOps.mirror(image)))
            augmented_results.append(("flip_vertical", ImageOps.flip(image)))
            
        if 'noise' in operations:
            # Add Gaussian noise
            img_array = np.array(image)
            noise = np.random.normal(0, 25, img_array.shape)
            noisy_img = np.clip(img_array + noise, 0, 255).astype(np.uint8)
            augmented_results.append(("noise", Image.fromarray(noisy_img)))
            
        if 'blur' in operations:
            augmented_results.append(("blur", image.filter(ImageFilter.BLUR)))
            
        if 'grayscale' in operations:
            augmented_results.append(("grayscale", ImageOps.grayscale(image).convert('RGB')))
            
        if 'scale' in operations:
            # Get scale percentages (default to 20%)
            scale_up_pct = float(config.get('scale_up', 20)) / 100.0
            scale_down_pct = float(config.get('scale_down', 20)) / 100.0
            
            # Calculate factors: 1.0 + pct for zoom in, 1.0 - pct for zoom out
            factors = []
            if scale_down_pct > 0:
                factors.append(('zoom_out', max(0.1, 1.0 - scale_down_pct))) # Prevent negative or zero scale
            if scale_up_pct > 0:
                factors.append(('zoom_in', 1.0 + scale_up_pct))
                
            for name, scale_factor in factors:
                scaled_img = self._scale_image(image, scale_factor)
                augmented_results.append((f"scale_{name}", scaled_img))
                
        if 'crop' in operations:
            # Generate random crop versions
            for i in range(2):  # Generate 2 random crops
                cropped_img = self._random_crop(image)
                augmented_results.append((f"crop_{i}", cropped_img))
                
        if 'brightness' in operations:
            # Get brightness percentages (default to 30%)
            bright_up_pct = float(config.get('brightness_up', 30)) / 100.0
            bright_down_pct = float(config.get('brightness_down', 30)) / 100.0
            
            factors = []
            if bright_down_pct > 0:
                factors.append(('darker', max(0.1, 1.0 - bright_down_pct)))
            if bright_up_pct > 0:
                factors.append(('brighter', 1.0 + bright_up_pct))
                
            for name, factor in factors:
                bright_img = self._adjust_brightness(image, factor)
                augmented_results.append((f"brightness_{name}", bright_img))
                
        if 'contrast' in operations:
            # Get contrast percentages (default to 30%)
            contrast_up_pct = float(config.get('contrast_up', 30)) / 100.0
            contrast_down_pct = float(config.get('contrast_down', 30)) / 100.0
            
            factors = []
            if contrast_down_pct > 0:
                factors.append(('lower', max(0.1, 1.0 - contrast_down_pct)))
            if contrast_up_pct > 0:
                factors.append(('higher', 1.0 + contrast_up_pct))
                
            for name, factor in factors:
                contrast_img = self._adjust_contrast(image, factor)
                augmented_results.append((f"contrast_{name}", contrast_img))
        
        if 'erase' in operations:
            # Generate 2 versions with random erasing (random noise)
            for i in range(2):
                erased_img = self._random_erase(image)
                augmented_results.append((f"erase_{i}", erased_img))
                
        if 'mask' in operations:
            # Generate 2 versions with random masking (blackout)
            for i in range(2):
                masked_img = self._random_mask(image)
                augmented_results.append((f"mask_{i}", masked_img))
            
        return augmented_results
    
    def _scale_image(self, image, scale_factor):
        """
        Scale image by a given factor using standard resampling.
        scale_factor < 1.0 = zoom out
        scale_factor > 1.0 = zoom in
        """
        width, height = image.size
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        # Resize the image
        scaled = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        if scale_factor < 1.0:
            # Zoom out: place scaled image in center of original size canvas
            result = Image.new('RGB', (width, height), (0, 0, 0))
            x_offset = (width - new_width) // 2
            y_offset = (height - new_height) // 2
            result.paste(scaled, (x_offset, y_offset))
            return result
        else:
            # Zoom in: crop center region to original size
            left = (new_width - width) // 2
            top = (new_height - height) // 2
            right = left + width
            bottom = top + height
            return scaled.crop((left, top, right, bottom))
    
    def _random_crop(self, image, crop_ratio=0.8):
        """
        Randomly crop a region from the image and resize back to original size.
        crop_ratio determines the size of the crop relative to original dimensions.
        """
        width, height = image.size
        crop_width = int(width * crop_ratio)
        crop_height = int(height * crop_ratio)
        
        # Random position for crop
        max_x = width - crop_width
        max_y = height - crop_height
        left = random.randint(0, max_x) if max_x > 0 else 0
        top = random.randint(0, max_y) if max_y > 0 else 0
        right = left + crop_width
        bottom = top + crop_height
        
        # Crop and resize back to original size
        cropped = image.crop((left, top, right, bottom))
        return cropped.resize((width, height), Image.Resampling.LANCZOS)
    
    def _adjust_brightness(self, image, factor):
        """
        Adjust image brightness.
        factor < 1.0 = darker
        factor > 1.0 = brighter
        """
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)
    
    def _adjust_contrast(self, image, factor):
        """
        Adjust image contrast.
        factor < 1.0 = lower contrast
        factor > 1.0 = higher contrast
        """
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)
        
    def _random_erase(self, image, probability=1.0, sl=0.02, sh=0.4, r1=0.3):
        """
        Randomly erases a rectangular part of the image with random noise.
        """
        img_array = np.array(image)
        h, w, _ = img_array.shape
        area = h * w
        
        # Try to find a valid erase region, with limited attempts
        for _ in range(10):
            target_area = random.uniform(sl, sh) * area
            aspect_ratio = random.uniform(r1, 1/r1)
            
            h_erase = int(round(np.sqrt(target_area * aspect_ratio)))
            w_erase = int(round(np.sqrt(target_area / aspect_ratio)))
            
            # Ensure dimensions are valid and fit within the image
            if h_erase >= h or w_erase >= w or h_erase < 1 or w_erase < 1:
                continue
                
            x = random.randint(0, h - h_erase)
            y = random.randint(0, w - w_erase)
            
            # Fill with random noise
            noise = np.random.randint(0, 255, (h_erase, w_erase, 3), dtype=np.uint8)
            img_array[x:x+h_erase, y:y+w_erase, :] = noise
            
            return Image.fromarray(img_array)
        
        # If we couldn't find a valid region after 10 attempts, 
        # create a small default erase region
        h_erase = min(h // 4, max(1, h // 10))
        w_erase = min(w // 4, max(1, w // 10))
        if h_erase < h and w_erase < w:
            x = random.randint(0, h - h_erase)
            y = random.randint(0, w - w_erase)
            noise = np.random.randint(0, 255, (h_erase, w_erase, 3), dtype=np.uint8)
            img_array[x:x+h_erase, y:y+w_erase, :] = noise
            return Image.fromarray(img_array)
        
        return image

    def _random_mask(self, image, sl=0.02, sh=0.4, r1=0.3):
        """
        Randomly masks a rectangular part of the image with black color.
        """
        img_array = np.array(image)
        h, w, _ = img_array.shape
        area = h * w
        
        # Try to find a valid mask region, with limited attempts
        for _ in range(10):
            target_area = random.uniform(sl, sh) * area
            aspect_ratio = random.uniform(r1, 1/r1)
            
            h_mask = int(round(np.sqrt(target_area * aspect_ratio)))
            w_mask = int(round(np.sqrt(target_area / aspect_ratio)))
            
            # Ensure dimensions are valid and fit within the image
            if h_mask >= h or w_mask >= w or h_mask < 1 or w_mask < 1:
                continue
                
            x = random.randint(0, h - h_mask)
            y = random.randint(0, w - w_mask)
            
            # Fill with black
            img_array[x:x+h_mask, y:y+w_mask, :] = 0
            
            return Image.fromarray(img_array)
        
        # If we couldn't find a valid region after 10 attempts,
        # create a small default mask region
        h_mask = min(h // 4, max(1, h // 10))
        w_mask = min(w // 4, max(1, w // 10))
        if h_mask < h and w_mask < w:
            x = random.randint(0, h - h_mask)
            y = random.randint(0, w - w_mask)
            img_array[x:x+h_mask, y:y+w_mask, :] = 0
            return Image.fromarray(img_array)
        
        return image
