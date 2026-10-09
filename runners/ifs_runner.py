import os
import random
from datetime import datetime
from generators import ifs
from utils import metadata
from runners.base_runner import BaseRunner


class IFSRunner(BaseRunner):
    """Runner для IFS-фракталов"""
    
    @property
    def fractal_type(self) -> str:
        return "ifs"
    
    def get_default_params(self):
        return {
            'width': 4096,
            'height': 4096,
            'num_transforms': 4,
            'num_points': 500000,
            'transforms': None,
            'probabilities': None,
            'color_min': 100,
            'color_max': 255,
            'background_color': (20, 20, 20),
            'point_size': 1,
            'preset': 'fern',
            'zoom': 1.0,
            'center_x': None,
            'center_y': None
        }
    
    def get_random_params(self):
        """
        Генерирует случайные параметры.
        preset='random' всегда использует случайные преобразования.
        """
        # Всегда используем случайные преобразования при random режиме
        num_transforms = random.randint(3, 7)
        
        return {
            'width': 4096,
            'height': 4096,
            'num_transforms': num_transforms,
            'num_points': random.randint(1000000, 2000000),
            'transforms': None,
            'probabilities': None,
            'color_min': random.randint(80, 160),
            'color_max': random.randint(200, 255),
            'background_color': (20, 20, 20),
            'point_size': random.choice([2, 2, 2, 3]),
            'preset': 'random',  # Всегда random!
            'zoom': random.uniform(2.0, 2.5),
            'center_x': None,
            'center_y': None
        }
    
    def run(self, params, output_dir):
        type_output = os.path.join(output_dir, self.fractal_type)
        os.makedirs(type_output, exist_ok=True)
        
        img = ifs.generate_ifs(**params)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = os.path.join(type_output, f"{self.fractal_type}_{timestamp}.png")
        
        metadata.save_with_metadata(img, filename, self.fractal_type, params, timestamp)
        
        return filename
