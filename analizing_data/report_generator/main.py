from pathlib import Path
from report_generator import ReportGenerator
from json_loader import JsonLoader
from score_calculator import ScoreCalculator
from excel_generator import ExcelGenerator

if __name__ == "__main__":
    generator = ReportGenerator(JsonLoader(), ScoreCalculator(), ExcelGenerator())
    
    # Определяем базовую директорию проекта
    BASE_DIR = Path(__file__).parent.parent  # Поднимаемся на уровень выше из report_generator
    
    # Путь к папке с JSON шаблонами
    JSON_TEMPLATES_DIR = BASE_DIR / "json-templates"
    
    # Путь к папке для заполненных отчетов
    OUTPUT_DIR = BASE_DIR / "filled_reports"
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Список JSON файлов для обработки
    json_files = ["form1.json", "form2.json", "form3.json", "form4.json", "form5.json", "form6.json"]
    
    for json_file in json_files:
        # Полный путь к исходному JSON файлу
        json_path = JSON_TEMPLATES_DIR / json_file
        
        # Проверяем существование файла
        if not json_path.exists():
            print(f"Файл не найден: {json_path}")
            continue
            
        # Создаем имя для выходного файла
        output_filename = f"{Path(json_file).stem}_report.xlsx"
        output_path = OUTPUT_DIR / output_filename
        
        try:
            # Генерируем отчет
            generator.generate_report(json_path, output_path)
            print(f"Сгенерирован: {output_path}")
        except Exception as e:
            print(f"Ошибка при обработке {json_file}: {e}")