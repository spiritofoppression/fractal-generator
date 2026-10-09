import os
import random
from datetime import datetime
from generators import newton
from utils import metadata
from runners.base_runner import BaseRunner

class NewtonRunner(BaseRunner):
    """Runner для фракталов Ньютона"""
    
    @property
    def fractal_type(self) -> str:
        return "newton"
    
    def get_default_params(self):
        """Возвращает параметры по умолчанию для фрактала Ньютона"""
        return {
            'width': 4096,
            'height': 4096,
            'degree': 3,
            'zoom': 1.0,
            'center_x': 0.0,
            'center_y': 0.0,
            'max_iter': 80,
            'formula_offset': 0.5,
            'formula_exponent_offset': 0.5,
            'epsilon': 1e-6,
            'convergence_threshold': 1e-5,
            'log_base': 10.0,
            'color_min': 140,
            'color_max': 255,
            'gamma': 1.85
        }
    
    def get_random_params(self):
        """Генерирует случайные параметры для фрактала Ньютона"""
        return {
            'width': 4096,
            'height': 4096,
            'degree': random.randint(3, 7),
            'zoom': random.uniform(1.0, 1.0),
            'center_x': random.uniform(-1.0, 1.0),
            'center_y': random.uniform(-1.0, 1.0),
            'max_iter': random.randint(60, 100),
            'formula_offset': random.uniform(0.5, 0.5),
            'formula_exponent_offset': random.uniform(0.5, 1.0),
            'epsilon': random.choice([1e-8, 1e-7, 1e-6, 1e-5]),
            'convergence_threshold': random.choice([1e-6, 1e-5]),
            'log_base': random.uniform(2.0, 20.0),
            'color_min': random.randint(50, 180),
            'color_max': random.randint(180, 255),
            'gamma': random.uniform(0.3, 2.3)
        }
    
    def run(self, params, output_dir):
        """Запускает генерацию фрактала Ньютона"""
        type_output = os.path.join(output_dir, self.fractal_type)
        os.makedirs(type_output, exist_ok=True)
        
        img = newton.generate_newton(**params)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = os.path.join(type_output, f"{self.fractal_type}_{timestamp}.png")
        
        metadata.save_with_metadata(img, filename, self.fractal_type, params, timestamp)
        
        return filename
