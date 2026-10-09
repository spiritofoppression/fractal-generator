import sys
import os
from runners import RunnerRegistry

def parse_args(args_str):
    """Превращает строку 'degree=4 zoom=1.5' в словарь"""
    kwargs = {}
    if not args_str or args_str == "-":
        return kwargs
    for pair in args_str.split():
        if '=' in pair:
            key, val = pair.split('=', 1)
            try:
                kwargs[key] = int(val)
            except ValueError:
                try:
                    kwargs[key] = float(val)
                except ValueError:
                    kwargs[key] = val
    return kwargs

def main():
    available_types = RunnerRegistry.list_available()
    
    if len(sys.argv) < 4:
        print("Использование: python3 main.py <тип> <параметры> <кол-во>")
        print(f"Доступные типы: {', '.join(available_types)}")
        print("Пример 1 (случайные): python3 main.py newton random 5")
        print("Пример 2 (фиксированные): python3 main.py newton \"degree=4 zoom=2.0 gamma=1.5\" 3")
        print("Пример 3 (дефолтные): python3 main.py newton \"-\" 3")
        sys.exit(1)

    f_type = sys.argv[1].lower()
    args_str = sys.argv[2]
    
    try:
        n_images = int(sys.argv[3])
    except ValueError:
        print("Ошибка: количество изображений должно быть целым числом.")
        sys.exit(1)

    # Получаем runner из реестра
    try:
        runner = RunnerRegistry.get(f_type)
    except KeyError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

    output_dir = "output"
    print(f"Генерация {n_images} изображений типа '{f_type}'...")
    
    for i in range(n_images):
        print(f"  [{i+1}/{n_images}] Генерация...", end="\r")
        
        # Определяем параметры
        if args_str == "random":
            params = runner.get_random_params()
        else:
            params = runner.get_default_params()
            user_params = parse_args(args_str)
            params.update(user_params)
        
        # Запускаем генерацию
        filename = runner.run(params, output_dir)
    
    print(f"\nГотово! Изображения сохранены в: {os.path.abspath(output_dir)}/{f_type}/")

if __name__ == "__main__":
    main()
