import os
import random
from datetime import datetime
from generators import stochastic
from utils import metadata
from runners.base_runner import BaseRunner

class StochasticRunner(BaseRunner):
    """Runner для стохастических фракталов"""
    
    @property
    def fractal_type(self) -> str:
        return "stochastic"
    
    def get_default_params(self):
        """Возвращает параметры по умолчанию для стохастического фрактала"""
        return {
            'width': 4096,
            'height': 4096,
            'roughness': 0.5,
            'seed': None,
            'color_min': 50,
            'color_max': 255,
            'gradient_type': 'linear',
            'color_mode': 'grayscale',
            'num_layers': 1,
            'layer_blend': 'multiply'
        }
    
    def get_random_params(self):
        """Генерирует случайные параметры для стохастического фрактала"""
        return {
            'width': 4096,
            'height': 4096,
            'roughness': random.uniform(0.3, 0.8),
            'seed': None,
            'color_min': random.randint(20, 100),
            'color_max': random.randint(180, 255),
            'gradient_type': random.choice(['linear', 'radial', 'diagonal']),
            'color_mode': random.choice(['grayscale', 'rgb', 'palette']),
            'num_layers': random.randint(1, 3),
            'layer_blend': random.choice(['multiply', 'screen', 'overlay'])
        }
    
    def run(self, params, output_dir):
        """Запускает генерацию стохастического фрактала"""
        type_output = os.path.join(output_dir, self.fractal_type)
        os.makedirs(type_output, exist_ok=True)
        
        img = stochastic.generate_stochastic(**params)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = os.path.join(type_output, f"{self.fractal_type}_{timestamp}.png")
        
        metadata.save_with_metadata(img, filename, self.fractal_type, params, timestamp)
        
        return filename
