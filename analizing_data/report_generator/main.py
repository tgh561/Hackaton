from pathlib import Path
from report_generator import ReportGenerator
from score_calculator import ScoreCalculator
from excel_generator import ExcelGenerator
from json_loader import JsonLoader  # Добавляем импорт JsonLoader

if __name__ == "__main__":
    
    calculator = ScoreCalculator()
    excel_generator = ExcelGenerator()
    generator = ReportGenerator(calculator, excel_generator)
    
    BASE_DIR = Path(__file__).parent.parent
    
    JSON_TEMPLATES_DIR = BASE_DIR / "json-templates"
    
    OUTPUT_DIR = BASE_DIR / "filled_reports"
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    json_files = ["form1.json", "form2.json", "form3.json", "form4.json", "form5.json", "form6.json"]
    
    for json_file in json_files:
        json_path = JSON_TEMPLATES_DIR / json_file
        
        if not json_path.exists():
            print(f"Файл не найден: {json_path}")
            continue
            
        output_filename = f"{Path(json_file).stem}_report.xlsx"
        output_path = OUTPUT_DIR / output_filename
        
        try:
            loader = JsonLoader()
            data = loader.load(json_path)
            
            generator.generate_report(data, output_path)
            print(f"Сгенерирован: {output_path}")
        except Exception as e:
            print(f"Ошибка при обработке {json_file}: {e}")