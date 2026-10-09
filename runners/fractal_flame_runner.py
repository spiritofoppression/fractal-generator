import os
import random
from datetime import datetime
from generators import fractal_flame
from utils import metadata
from runners.base_runner import BaseRunner


class FractalFlameRunner(BaseRunner):
    """Runner для fractal flame"""
    
    @property
    def fractal_type(self) -> str:
        return "fractal_flame"
    
    def get_default_params(self):
        return {
            'width': 4096,
            'height': 4096,
            'num_transforms': 5,
            'num_points': 1000000,
            'variations': None,
            'color_palette': None,
            'gamma': 2.5,
            'brightness': 1.0,
            'background_color': (0, 0, 0),
            'zoom': 1.0,
            'center_x': None,
            'center_y': None
        }
    
    def get_random_params(self):
        """Генерирует случайные параметры для fractal flame"""
        # Адаптивное количество точек в зависимости от зума
        zoom = random.uniform(1.0, 3.0)
        base_points = random.randint(500000, 1500000)
        num_points = int(base_points * (zoom ** 2))
        num_points = min(num_points, 50_000_000)  # Максимум 50M
        
        return {
            'width': 4096,
            'height': 4096,
            'num_transforms': random.randint(4, 8),
            'num_points': num_points,
            'variations': None,
            'color_palette': None,
            'gamma': random.uniform(0.5, 4.0),
            'brightness': random.uniform(0.5, 2.0),
            'background_color': (20, 20, 20),
            'zoom': zoom,
            'center_x': None,
            'center_y': None
        }
    
    def run(self, params, output_dir):
        type_output = os.path.join(output_dir, self.fractal_type)
        os.makedirs(type_output, exist_ok=True)
        
        img = fractal_flame.generate_fractal_flame(**params)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = os.path.join(type_output, f"{self.fractal_type}_{timestamp}.png")
        
        metadata.save_with_metadata(img, filename, self.fractal_type, params, timestamp)
        
        return filename
