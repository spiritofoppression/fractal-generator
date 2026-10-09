# Fractal Generator

A modular Python framework for procedural fractal generation and automated publishing.

## Architecture

The project uses a decoupled architecture separating mathematical generation from execution orchestration:
- `generators/`: Pure generation algorithms. Each module exports a function accepting configuration parameters and returning a `PIL.Image.Image`.
- `runners/`: Parameter resolution, execution flow, and file I/O. Dynamically discovers generators via `RunnerRegistry`.
- `utils/`: Shared utilities, including metadata embedding into output PNG files.
- `main.py`: Command-line interface entry point.
- `auto_post.py` / `tg_auto_post.py`: Background services for automated social media publishing.

## Usage

Generate fractals via the command-line interface:

```bash
python3 main.py <fractal_type> [preset|random|param_string] [count]
```

Examples:
```bash
python3 main.py ifs random 5
python3 main.py newton "degree=4 zoom=2.0 formula_offset=0.5" 1
```

Generated images are saved to `output/<fractal_type>/` with embedded JSON metadata containing the exact generation parameters.

## Extensibility

To add a new fractal algorithm, implement a Generator module and a corresponding Runner class.

### Generator Interface
Create a new file in `generators/` (e.g., `custom.py`). Implement a generation function that accepts keyword arguments and returns a `PIL.Image.Image`:

```python
import numpy as np
from PIL import Image

def generate_custom(width=1024, height=1024, **kwargs):
    image_array = np.zeros((height, width, 3), dtype=np.uint8)
    # Algorithm implementation
    return Image.fromarray(image_array)
```

### Runner Interface
Create a new file in `runners/` (e.g., `custom_runner.py`). Inherit from `BaseRunner` and implement the required methods:

```python
import os
import random
from datetime import datetime
from generators import custom
from utils import metadata
from runners.base_runner import BaseRunner

class CustomRunner(BaseRunner):
    @property
    def fractal_type(self) -> str:
        return "custom"

    def get_default_params(self):
        return {"width": 1024, "height": 1024, "custom_param": 1.0}

    def get_random_params(self):
        return {"width": 1024, "height": 1024, "custom_param": random.uniform(0.0, 1.0)}

    def run(self, params, output_dir):
        type_output = os.path.join(output_dir, self.fractal_type)
        os.makedirs(type_output, exist_ok=True)
        
        img = custom.generate_custom(**params)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = os.path.join(type_output, f"{self.fractal_type}_{timestamp}.png")
        
        metadata.save_with_metadata(img, filename, self.fractal_type, params, timestamp)
        return filename
```

The `RunnerRegistry` automatically discovers new runners via `importlib` during initialization. No manual registration is required. Ensure the new module is importable from the project root.
