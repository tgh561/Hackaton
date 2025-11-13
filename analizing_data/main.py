from pathlib import Path
from report_generator.report_generator import ReportGenerator
from report_generator.score_calculator import ScoreCalculator
from report_generator.excel_generator import ExcelGenerator
from report_generator.json_loader import JsonLoader
from violation_report_generator.violation_report_facade import ViolationReportFacade

def main():
    """Генерация основного отчета и отчета о нарушениях"""
    
    # Создаем компоненты
    calculator = ScoreCalculator()
    excel_generator = ExcelGenerator()
    report_generator = ReportGenerator(calculator, excel_generator)
    violation_facade = ViolationReportFacade()
    json_loader = JsonLoader()
    
    BASE_DIR = Path(__file__).parent
    JSON_EXAMPLES_DIR = BASE_DIR / "json-examples"
    OUTPUT_DIR = BASE_DIR / "filled_reports"
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    json_files = ["form1.json", "form2.json", "form3.json", "form4.json", "form5.json", "form6.json"]
    
    for json_file in json_files:
        json_path = JSON_EXAMPLES_DIR / json_file
        
        if not json_path.exists():
            print(f"Файл не найден: {json_path}")
            continue
            
        print(f"Обработка файла: {json_file}")
        
        try:
            # Загружаем данные
            data = json_loader.load(json_path)
            print(f"Данные загружены: {data.section_name}")
            
            # Генерируем основной отчет (без изменений)
            main_output_filename = f"{Path(json_file).stem}_report.xlsx"
            main_output_path = OUTPUT_DIR / main_output_filename
            report_generator.generate_report(data, main_output_path)
            print(f"Основной отчет создан: {main_output_filename}")
            
            # Анализируем нарушения
            violation_data = violation_facade.analyze_violations_only(data)
            print(f"Найдено нарушений: {violation_data.total_violations}")
            
            # Генерируем отчет о нарушениях (если есть нарушения)
            if violation_data.has_violations:
                violation_output_filename = f"{Path(json_file).stem}_violations.xlsx"
                violation_output_path = OUTPUT_DIR / violation_output_filename
                violation_facade.generate_violation_report(data, violation_output_path)
                print(f"Отчет о нарушениях создан: {violation_output_filename}")
                
                # Выводим информацию о нарушениях
                print("\nСписок нарушений:")
                for i, violation in enumerate(violation_data.violations, 1):
                    subsection_info = f" / {violation.subsection_name}" if violation.subsection_name else ""
                    print(f"   {i}. {violation.section_name}{subsection_info}")
                    print(f"      Нарушение #{violation.criterion_number}: {violation.criterion_description}")
                    print(f"      Комментарий: {violation.comment}")
            else:
                print("Нарушений не обнаружено")
                
        except Exception as e:
            print(f"Ошибка при обработке {json_file}: {e}")
    
    print(f"\nОтчеты сохранены в: {OUTPUT_DIR.absolute()}")

if __name__ == "__main__":
    main()