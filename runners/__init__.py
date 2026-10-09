from runners.registry import RunnerRegistry

# Автоматически обнаруживаем все runner'ы при импорте
RunnerRegistry.auto_discover()
