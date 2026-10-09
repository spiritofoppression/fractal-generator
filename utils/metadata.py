import json
from PIL import PngImagePlugin

def save_with_metadata(img, filename, fractal_type, params, timestamp):
    """
    Сохраняет изображение с метаданными в PNG
    """
    pnginfo = PngImagePlugin.PngInfo()
    pnginfo.add_text("fractal_type", fractal_type)
    pnginfo.add_text("generation_params", json.dumps(params, indent=2))
    pnginfo.add_text("timestamp", timestamp)
    
    img.save(filename, pnginfo=pnginfo)

def read_metadata(filename):
    """
    Читает метаданные из PNG файла
    """
    from PIL import Image
    img = Image.open(filename)
    return {
        'fractal_type': img.info.get('fractal_type'),
        'generation_params': json.loads(img.info.get('generation_params', '{}')),
        'timestamp': img.info.get('timestamp')
    }
