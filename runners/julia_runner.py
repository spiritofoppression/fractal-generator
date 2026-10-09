import os
import random
import math
from datetime import datetime
from generators import julia
from utils import metadata
from runners.base_runner import BaseRunner

class JuliaRunner(BaseRunner):
    """Runner для множества Жюлиа"""
    
    @property
    def fractal_type(self) -> str:
        return "julia"
    
    def get_default_params(self):
        """Возвращает параметры по умолчанию для множества Жюлиа"""
        return {
            'width': 4096,
            'height': 4096,
            'c_real': -0.7,
            'c_imag': 0.27015,
            'zoom': 1.0,
            'center_x': 0.0,
            'center_y': 0.0,
            'max_iter': 200,
            'escape_radius': 2.0,
            'color_min': 100,
            'color_max': 255,
            'gamma': 1.0,
            'background_color': (0, 0, 0)
        }
    
    def get_random_params(self):
        """
        Генерирует случайные параметры для множества Жюлиа.
        
        Параметр c генерируется в полярных координатах, чтобы получать
        визуально интересные формы (связные множества, а не "пыль").
        """
        # Полярные координаты для c
        r = random.uniform(0.3, 0.9)
        theta = random.uniform(0, 2 * math.pi)
        c_real = r * math.cos(theta)
        c_imag = r * math.sin(theta)
        
        return {
            'width': 4096,
            'height': 4096,
            'c_real': c_real,
            'c_imag': c_imag,
            'zoom': random.uniform(1.0, 3.0),
            'center_x': random.uniform(-0.5, 0.5),
            'center_y': random.uniform(-0.5, 0.5),
            'max_iter': random.randint(100, 300),
            'escape_radius': 2.0,
            'color_min': random.randint(50, 150),
            'color_max': random.randint(180, 255),
            'gamma': random.uniform(0.3, 2.5),
            'background_color': (0, 0, 0)
        }
    
    def run(self, params, output_dir):
        """Запускает генерацию множества Жюлиа"""
        type_output = os.path.join(output_dir, self.fractal_type)
        os.makedirs(type_output, exist_ok=True)
        
        img = julia.generate_julia(**params)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = os.path.join(type_output, f"{self.fractal_type}_{timestamp}.png")
        
        metadata.save_with_metadata(img, filename, self.fractal_type, params, timestamp)
        
        return filename
