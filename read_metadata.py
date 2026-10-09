import sys
from utils import metadata

if len(sys.argv) < 2:
    print("Использование: python3 read_metadata.py <путь_к_изображению>")
    sys.exit(1)

filename = sys.argv[1]
data = metadata.read_metadata(filename)

print(f"Тип фрактала: {data['fractal_type']}")
print(f"Время создания: {data['timestamp']}")
print("\nПараметры генерации:")
print(data['generation_params'])
