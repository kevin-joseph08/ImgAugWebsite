from flask import Flask, request, jsonify, render_template, send_file
import torch
import torchvision.transforms as transforms
from PIL import Image
import io
import base64
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Define augmentations
AUGMENTATIONS = {
    'rotate': transforms.RandomRotation(30),
    'flip_horizontal': transforms.RandomHorizontalFlip(p=1.0),
    'flip_vertical': transforms.RandomVerticalFlip(p=1.0),
    'brightness': transforms.ColorJitter(brightness=0.5),
    'contrast': transforms.ColorJitter(contrast=0.5),
    'blur': transforms.GaussianBlur(kernel_size=5),
    'grayscale': transforms.Grayscale(num_output_channels=3)
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/augment', methods=['POST'])
def augment_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    augmentation = request.form.get('augmentation')
    
    if not file or not augmentation or augmentation not in AUGMENTATIONS:
        return jsonify({'error': 'Invalid input'}), 400
    
    try:
        # Load and process image
        image = Image.open(file.stream).convert('RGB')
        transform = AUGMENTATIONS[augmentation]
        augmented_image = transform(image)
        
        # Convert to base64
        buffer = io.BytesIO()
        augmented_image.save(buffer, format='JPEG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({'image': f'data:image/jpeg;base64,{img_str}'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)