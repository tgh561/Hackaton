"""
Менеджер для автоматического ежедневного обновления сводного отчета
"""
import schedule
import time
from pathlib import Path
from datetime import datetime
from monthly_report_generator import MonthlyReportGenerator, DailyReportProcessor

class MonthlyReportManager:
    """
    Автоматический менеджер для ежедневного обновления отчетов
    """
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.load_config()
        
    def load_config(self):
        """Загружает конфигурацию"""
        self.template_path = Path("monthly_report_template.json")
        self.output_dir = Path("reports")
        self.daily_reports_dir = Path("daily_reports")
        self.report_time = "18:00"  # Время ежедневного обновления
        
        # Создаем директории если нужно
        self.output_dir.mkdir(exist_ok=True)
        self.daily_reports_dir.mkdir(exist_ok=True)
    
    def daily_update(self):
        """Ежедневное обновление отчета"""
        print(f"Запуск ежедневного обновления отчета: {datetime.now()}")
        
        try:
            generator = MonthlyReportGenerator(self.template_path, self.output_dir)
            processor = DailyReportProcessor(generator, self.daily_reports_dir)
            
            # Обрабатываем отчеты за текущий день
            processor.process_daily_reports()
            
            # Генерируем обновленный Excel отчет
            report_path = generator.generate_excel_report()
            
            print(f"Отчет успешно обновлен: {report_path}")
            
            # Можно добавить отправку по email или в мессенджер
            self._notify_completion(report_path)
            
        except Exception as e:
            print(f"Ошибка при обновлении отчета: {e}")
            self._notify_error(str(e))
    
    def _notify_completion(self, report_path: Path):
        """Уведомление о завершении (заглушка для реализации)"""
        print(f"Отчет готов: {report_path}")
        # Здесь можно добавить отправку email, уведомление в Telegram и т.д.
    
    def _notify_error(self, error_message: str):
        """Уведомление об ошибке (заглушка для реализации)"""
        print(f"Ошибка: {error_message}")
        # Здесь можно добавить отправку уведомлений об ошибках
    
    def start_scheduler(self):
        """Запускает планировщик ежедневных обновлений"""
        schedule.every().day.at(self.report_time).do(self.daily_update)
        
        print(f"Планировщик запущен. Ежедневное обновление в {self.report_time}")
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def manual_update(self, day: int = None):
        """Ручное обновление отчета"""
        self.daily_update()

# Скрипт для тестирования с mock данными
def test_with_mock_data():
    """Тестирование с mock данными"""
    from monthly_report_generator import MonthlyReportGenerator
    import random
    
    template_path = Path("monthly_report_template.json")
    output_dir = Path("test_reports")
    output_dir.mkdir(exist_ok=True)
    
    generator = MonthlyReportGenerator(template_path, output_dir)
    
    # Добавляем mock данные за несколько дней
    departments = ["1.1", "1.2", "1.3", "1.4", "2", "3", "5", "6.1", "6.2"]
    
    for day in range(1, 16):  # Первые 15 дней месяца
        for dept_id in departments:
            # Генерируем случайную оценку от 4.5 до 6.0
            score = round(random.uniform(4.5, 6.0), 1)
            generator.add_daily_report(dept_id, day, score)
    
    # Сохраняем данные
    generator.save_monthly_data()
    
    # Генерируем отчет
    report_path = generator.generate_excel_report()
    print(f"Тестовый отчет создан: {report_path}")
    
    # Выводим статистику
    for dept in generator.monthly_data["departments"]:
        if dept["type"] == "leaf":
            stats = generator.get_department_stats(dept["id"])
            print(f"{dept['name']}: {stats['current_score']} (динамика: {stats['dynamics']})")
