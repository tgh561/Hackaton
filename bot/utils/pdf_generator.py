from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

# Попробуем использовать стандартные шрифты
try:
    # Для русского текола попробуем использовать стандартный шрифт
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # Если есть шрифт с поддержкой кириллицы
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    FONT_NAME = 'Arial'
except:
    # Используем стандартный шрифт
    FONT_NAME = 'Helvetica'


def generate_users_pdf(users_data, filename="users_list.pdf"):
    """Генерирует PDF файл со списком пользователей"""

    # Создаем документ
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []

    # Стили
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1,  # center
        textColor=colors.darkblue
    )

    # Заголовок
    title = Paragraph("СПИСОК ПОЛЬЗОВАТЕЛЕЙ", title_style)
    elements.append(title)

    # Дата генерации
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        textColor=colors.gray
    )
    date_text = Paragraph(f"Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}", date_style)
    elements.append(date_text)
    elements.append(Spacer(1, 20))

    # Подготовка данных для таблицы
    table_data = [['ID', 'Имя', 'Фамилия', 'Роль', 'Телефон', 'Статус']]

    for user_id, user_data in users_data.items():
        status = "Активен" if user_data.get('is_active', True) else "Неактивен"
        role_names = {
            'worker': 'Рабочий',
            'manager': 'Руководитель',
            'inspector': 'Проверяющий',
            'admin': 'Администратор'
        }
        role = role_names.get(user_data['role'], user_data['role'])

        table_data.append([
            str(user_data['telegram_id']),
            user_data['first_name'],
            user_data.get('last_name', ''),
            role,
            user_data.get('phone', ''),
            status
        ])

    # Создаем таблицу
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        # Заголовок таблицы
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), FONT_NAME),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

        # Данные таблицы
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), FONT_NAME),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),

        # Перенос текста для длинных ячеек
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ]))

    elements.append(table)

    # Статистика в конце
    elements.append(Spacer(1, 20))
    total_users = len(users_data)
    active_users = sum(1 for user in users_data.values() if user.get('is_active', True))

    stats_style = ParagraphStyle(
        'StatsStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=0,  # left
        textColor=colors.darkgreen
    )

    stats_text = f"Всего пользователей: {total_users}\nАктивных: {active_users}"
    stats_paragraph = Paragraph(stats_text, stats_style)
    elements.append(stats_paragraph)

    # Генерируем PDF
    doc.build(elements)
    return filename