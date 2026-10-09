import os
import random
from datetime import datetime
from generators import lyapunov
from utils import metadata
from runners.base_runner import BaseRunner


class LyapunovRunner(BaseRunner):
    """Runner для фракталов Ляпунова"""
    
    @property
    def fractal_type(self) -> str:
        return "lyapunov"
    
    def get_default_params(self):
        return {
            'width': 4096,
            'height': 4096,
            'sequence': "AABAB",
            'a_min': 0.0,
            'a_max': 4.0,
            'b_min': 0.0,
            'b_max': 4.0,
            'num_iterations': 1000,
            'warmup_iterations': 500,
            'color_positive': None,
            'color_negative': None,
            'gamma': 1.0,
            'background_color': (0, 0, 0)
        }
    
    def get_random_params(self):
        """Генерирует случайные параметры для фрактала Ляпунова"""
        # Генерируем случайную последовательность из 'A' и 'B' длиной 3-7
        seq_length = random.randint(3, 7)
        sequence = ''.join(random.choice(['A', 'B']) for _ in range(seq_length))
        
        # Случайные цвета
        color_positive = (
            random.randint(150, 255),
            random.randint(150, 255),
            random.randint(150, 255)
        )
        color_negative = (
            random.randint(0, 80),
            random.randint(0, 80),
            random.randint(0, 80)
        )
        
        # Случайные диапазоны параметров (но в разумных пределах)
        # Обычно фракталы Ляпунова строятся в диапазоне [0, 4]
        a_min = random.uniform(0.0, 1.0)
        a_max = random.uniform(3.0, 4.0)
        b_min = random.uniform(0.0, 1.0)
        b_max = random.uniform(3.0, 4.0)
        
        return {
            'width': 4096,
            'height': 4096,
            'sequence': sequence,
            'a_min': a_min,
            'a_max': a_max,
            'b_min': b_min,
            'b_max': b_max,
            'num_iterations': random.randint(500, 2000),
            'warmup_iterations': random.randint(200, 1000),
            'color_positive': color_positive,
            'color_negative': color_negative,
            'gamma': random.uniform(0.5, 2.5),
            'background_color': (0, 0, 0)
        }
    
    def run(self, params, output_dir):
        type_output = os.path.join(output_dir, self.fractal_type)
        os.makedirs(type_output, exist_ok=True)
        
        img = lyapunov.generate_lyapunov(**params)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = os.path.join(type_output, f"{self.fractal_type}_{timestamp}.png")
        
        metadata.save_with_metadata(img, filename, self.fractal_type, params, timestamp)
        
        return filename
