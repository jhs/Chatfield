#!/usr/bin/env python3
"""Create Food Business License Application forms in English, Spanish, Thai, and Japanese.

This creates realistic government-style forms with 8 fields in four languages.
All forms use identical field names for testing purposes.

Uses PyMuPDF (fitz) for clean, reliable form creation.
"""

import os
import fitz  # PyMuPDF


# Font mapping for Unicode support
FONT_FILES = {
    'us': None,  # Use default Helvetica
    'es': None,  # Use default Helvetica
    'th': '/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf',
    'ja': '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    'pl': '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',  # Polish diacritical marks (ą, ć, ę, ł, ń, ó, ś, ź, ż)
}


# Form content in four languages
FORM_CONTENT = {
    'us': {
        'title': 'FOOD BUSINESS LICENSE APPLICATION',
        'subtitle': 'Department of Health and Food Safety',
        'instructions': 'Please complete all sections of this form. All information must be accurate and verifiable.',
        'section1': 'SECTION 1: BUSINESS INFORMATION',
        'section2': 'SECTION 2: FACILITY & OPERATIONS',
        'section3': 'SECTION 3: FOOD SAFETY COMPLIANCE',
        'page_size': (612, 792),  # US Letter
        'labels': {
            'business_name': 'Legal Business Name:',
            'business_address': 'Business Address:',
            'business_type': 'Type of Food Business (select one):',
            'business_type_hint': '(Select only one)',
            'business_type_restaurant': 'Restaurant',
            'business_type_manufacturing': 'Food Manufacturing',
            'business_type_import_export': 'Food Import/Export',
            'business_type_catering': 'Catering',
            'num_employees': 'Number of Employees:',
            'delivery_radius': 'Delivery Radius (miles):',
            'has_refrigeration': 'Does your facility have proper refrigeration equipment?',
            'has_refrigeration_hint': '☐ Check if Yes',
            'certification_date': 'Food Safety Certification Date (MM/DD/YYYY):',
            'product_description': 'Describe your primary food products or menu items:',
            'product_description_hint': '(Provide a brief description in 1-2 sentences)',
            'safety_procedures': 'Explain your food safety and hygiene procedures:',
            'safety_procedures_hint': '(Describe key safety measures in 1-2 sentences)',
            'declaration': 'I declare that the information provided in this application is true and complete.',
            'signature': 'Signature',
            'date': 'Date',
            'page_number': 'Page 1 of 1',
        }
    },
    'es': {
        'title': 'SOLICITUD DE LICENCIA COMERCIAL DE ALIMENTOS',
        'subtitle': 'Departamento de Salud y Seguridad Alimentaria',
        'instructions': 'Por favor complete todas las secciones de este formulario. Toda la información debe ser precisa y verificable.',
        'section1': 'SECCIÓN 1: INFORMACIÓN COMERCIAL',
        'section2': 'SECCIÓN 2: INSTALACIONES Y OPERACIONES',
        'section3': 'SECCIÓN 3: CUMPLIMIENTO DE SEGURIDAD ALIMENTARIA',
        'page_size': (595, 842),  # A4
        'labels': {
            'business_name': 'Nombre Legal del Negocio:',
            'business_address': 'Dirección del Negocio:',
            'business_type': 'Tipo de Negocio de Alimentos (seleccione uno):',
            'business_type_hint': '(Seleccione solo uno)',
            'business_type_restaurant': 'Restaurante',
            'business_type_manufacturing': 'Fabricación de Alimentos',
            'business_type_import_export': 'Importación/Exportación de Alimentos',
            'business_type_catering': 'Servicio de Catering',
            'num_employees': 'Número de Empleados:',
            'delivery_radius': 'Radio de Entrega (kilómetros):',
            'has_refrigeration': '¿Su instalación tiene equipo de refrigeración adecuado?',
            'has_refrigeration_hint': '☐ Marque si Sí',
            'certification_date': 'Fecha de Certificación de Seguridad Alimentaria (AAAA-MM-DD):',
            'product_description': 'Describa sus productos alimenticios o elementos de menú principales:',
            'product_description_hint': '(Proporcione una breve descripción en 1-2 oraciones)',
            'safety_procedures': 'Explique sus procedimientos de seguridad e higiene alimentaria:',
            'safety_procedures_hint': '(Describa las medidas de seguridad clave en 1-2 oraciones)',
            'declaration': 'Declaro que la información proporcionada en esta solicitud es verdadera y completa.',
            'signature': 'Firma',
            'date': 'Fecha',
            'page_number': 'Página 1 de 1',
        }
    },
    'th': {
        'title': 'ใบสมัครใบอนุญาตประกอบธุรกิจอาหาร',
        'subtitle': 'กรมอนามัยและความปลอดภัยด้านอาหาร',
        'instructions': 'กรุณากรอกข้อมูลในทุกส่วนของแบบฟอร์มนี้ ข้อมูลทั้งหมดจะต้องถูกต้องและสามารถตรวจสอบได้',
        'section1': 'ส่วนที่ ๑: ข้อมูลธุรกิจ',
        'section2': 'ส่วนที่ ๒: สถานที่และการดำเนินงาน',
        'section3': 'ส่วนที่ ๓: การปฏิบัติตามมาตรฐานความปลอดภัยด้านอาหาร',
        'page_size': (595, 842),  # A4
        'labels': {
            'business_name': 'ชื่อธุรกิจตามกฎหมาย:',
            'business_address': 'ที่อยู่ธุรกิจ:',
            'business_type': 'ประเภทของธุรกิจอาหาร (เลือกหนึ่งรายการ):',
            'business_type_hint': '(เลือกเพียงหนึ่งรายการ)',
            'business_type_restaurant': 'ร้านอาหาร',
            'business_type_manufacturing': 'การผลิตอาหาร',
            'business_type_import_export': 'การนำเข้า/ส่งออกอาหาร',
            'business_type_catering': 'การจัดเลี้ยง',
            'num_employees': 'จำนวนพนักงาน:',
            'delivery_radius': 'รัศมีการจัดส่ง (กิโลเมตร):',
            'has_refrigeration': 'สถานที่ของคุณมีอุปกรณ์ทำความเย็นที่เหมาะสมหรือไม่?',
            'has_refrigeration_hint': '☐ ทำเครื่องหมายถ้าใช่',
            'certification_date': 'วันที่รับรองความปลอดภัยด้านอาหาร (พุทธศักราช):',
            'product_description': 'อธิบายผลิตภัณฑ์อาหารหรือรายการเมนูหลักของคุณ:',
            'product_description_hint': '(ให้คำอธิบายโดยย่อใน ๑-๒ ประโยค)',
            'safety_procedures': 'อธิบายขั้นตอนความปลอดภัยและสุขอนามัยด้านอาหารของคุณ:',
            'safety_procedures_hint': '(อธิบายมาตรการความปลอดภัยหลักใน ๑-๒ ประโยค)',
            'declaration': 'ข้าพเจ้าขอรับรองว่าข้อมูลที่ให้ไว้ในใบสมัครนี้เป็นความจริงและสมบูรณ์',
            'signature': 'ลายเซ็น',
            'date': 'วันที่',
            'page_number': 'หน้า ๑ จาก ๑',
        }
    },
    'ja': {
        'title': '食品事業許可申請書',
        'subtitle': '保健食品安全局',
        'instructions': 'この申請書のすべてのセクションにご記入ください。すべての情報は正確で検証可能でなければなりません。',
        'section1': 'セクション1：事業情報',
        'section2': 'セクション2：施設と運営',
        'section3': 'セクション3：食品安全基準の遵守',
        'page_size': (595, 842),  # A4
        'labels': {
            'business_name': '法人名:',
            'business_address': '事業所住所:',
            'business_type': '食品事業の種類（いずれかを選択）:',
            'business_type_hint': '(いずれか一つを選択)',
            'business_type_restaurant': 'レストラン',
            'business_type_manufacturing': '食品製造',
            'business_type_import_export': '食品輸入/輸出',
            'business_type_catering': 'ケータリング',
            'num_employees': '従業員数:',
            'delivery_radius': '配達範囲（キロメートル）:',
            'has_refrigeration': '施設には適切な冷蔵設備がありますか？',
            'has_refrigeration_hint': '☐ はいの場合チェック',
            'certification_date': '食品安全認証日（YYYY-MM-DD）:',
            'product_description': '主要な食品またはメニュー項目を説明してください:',
            'product_description_hint': '（1〜2文で簡単な説明を提供してください）',
            'safety_procedures': '食品の安全性と衛生手順を説明してください:',
            'safety_procedures_hint': '（1〜2文で主要な安全対策を説明してください）',
            'declaration': '私はこの申請書に記載された情報が真実かつ完全であることを宣言します。',
            'signature': '署名',
            'date': '日付',
            'page_number': 'ページ 1 / 1',
        }
    },
    'pl': {
        'title': 'WNIOSEK O LICENCJĘ NA PROWADZENIE DZIAŁALNOŚCI ŻYWNOŚCIOWEJ',
        'subtitle': 'Wydział Zdrowia i Bezpieczeństwa Żywności',
        'instructions': 'Proszę wypełnić wszystkie sekcje tego formularza. Wszystkie informacje muszą być dokładne i weryfikowalne.',
        'section1': 'SEKCJA 1: INFORMACJE O DZIAŁALNOŚCI',
        'section2': 'SEKCJA 2: OBIEKT I DZIAŁALNOŚĆ',
        'section3': 'SEKCJA 3: ZGODNOŚĆ Z PRZEPISAMI BEZPIECZEŃSTWA ŻYWNOŚCI',
        'page_size': (595, 842),  # A4
        'labels': {
            'business_name': 'Nazwa prawna firmy:',
            'business_address': 'Adres firmy:',
            'business_type': 'Rodzaj działalności żywnościowej (wybierz jeden):',
            'business_type_hint': '(Wybierz tylko jeden)',
            'business_type_restaurant': 'Restauracja',
            'business_type_manufacturing': 'Produkcja żywności',
            'business_type_import_export': 'Import/Eksport żywności',
            'business_type_catering': 'Catering',
            'num_employees': 'Liczba pracowników:',
            'delivery_radius': 'Zasięg dostaw (kilometry):',
            'has_refrigeration': 'Czy obiekt posiada odpowiednie urządzenia chłodnicze?',
            'has_refrigeration_hint': '☐ Zaznacz jeśli Tak',
            'certification_date': 'Data certyfikacji bezpieczeństwa żywności (RRRR-MM-DD):',
            'product_description': 'Opisz swoje główne produkty spożywcze lub pozycje menu:',
            'product_description_hint': '(Podaj krótki opis w 1-2 zdaniach)',
            'safety_procedures': 'Wyjaśnij swoje procedury bezpieczeństwa i higieny żywności:',
            'safety_procedures_hint': '(Opisz kluczowe środki bezpieczeństwa w 1-2 zdaniach)',
            'declaration': 'Oświadczam, że informacje podane w tym wniosku są prawdziwe i kompletne.',
            'signature': 'Podpis',
            'date': 'Data',
            'page_number': 'Strona 1 z 1',
        }
    }
}


def create_form_pdf(output_path: str, lang: str):
    """Create a complete PDF form using PyMuPDF."""

    content = FORM_CONTENT[lang]
    fontfile = FONT_FILES[lang]

    # Create new PDF document with appropriate page size
    doc = fitz.open()
    page_width, page_height_val = content['page_size']
    page = doc.new_page(width=page_width, height=page_height_val)

    # Create Font objects for Unicode support
    custom_font = None
    widget_font_name = "Helvetica"  # Default for US/ES
    if fontfile:
        custom_font = fitz.Font(fontfile=fontfile)
        widget_font_name = custom_font.name
        print(f"  Using custom font: {custom_font.name}")

    # Current Y position
    y = 50

    # Helper to insert text with correct font
    def insert_text_with_font(pos, text, fontsize, fontname_default='Helvetica', color=(0, 0, 0)):
        """Insert text using custom font if available, otherwise default font."""
        if custom_font:
            tw = fitz.TextWriter(page.rect, color=color)
            tw.append(pos, text, font=custom_font, fontsize=fontsize)
            tw.write_text(page)
        else:
            page.insert_text(pos, text, fontsize=fontsize, fontname=fontname_default, color=color)

    def insert_textbox_with_font(rect, text, fontsize, fontname_default='Helvetica', color=(0, 0, 0), align=fitz.TEXT_ALIGN_LEFT):
        """Insert textbox using custom font if available, otherwise default font."""
        if custom_font:
            # For custom fonts, calculate position based on alignment
            tw = fitz.TextWriter(page.rect, color=color)
            if align == fitz.TEXT_ALIGN_CENTER:
                # Center horizontally
                text_length = custom_font.text_length(text, fontsize=fontsize)
                x = rect.x0 + (rect.width - text_length) / 2
                y = rect.y0 + fontsize  # Baseline position
                tw.append((x, y), text, font=custom_font, fontsize=fontsize)
            elif align == fitz.TEXT_ALIGN_RIGHT:
                # Right align
                text_length = custom_font.text_length(text, fontsize=fontsize)
                x = rect.x1 - text_length
                y = rect.y0 + fontsize
                tw.append((x, y), text, font=custom_font, fontsize=fontsize)
            else:
                # Left align (default)
                tw.append((rect.x0, rect.y0 + fontsize), text, font=custom_font, fontsize=fontsize)
            tw.write_text(page)
        else:
            page.insert_textbox(rect, text, fontsize=fontsize, fontname=fontname_default, color=color, align=align)

    # ========== HEADER ==========
    # Dark blue header background
    header_rect = fitz.Rect(0, 0, page_width, 80)
    page.draw_rect(header_rect, color=None, fill=(0.1, 0.1, 0.4))

    # Title (white text, bold, large) - use textbox for centering
    insert_textbox_with_font(
        fitz.Rect(0, 20, page_width, 45),
        content['title'],
        fontsize=18,
        color=(1, 1, 1),
        align=fitz.TEXT_ALIGN_CENTER
    )

    # Subtitle (white text, smaller)
    insert_textbox_with_font(
        fitz.Rect(0, 45, page_width, 70),
        content['subtitle'],
        fontsize=12,
        color=(1, 1, 1),
        align=fitz.TEXT_ALIGN_CENTER
    )

    # ========== INSTRUCTIONS BOX ==========
    y = 90
    instr_rect = fitz.Rect(40, y, page_width - 40, y + 35)
    page.draw_rect(instr_rect, color=(0, 0, 0), fill=(0.95, 0.95, 0.95))

    # Instructions text (italic, small)
    insert_textbox_with_font(
        fitz.Rect(50, y + 5, page_width - 50, y + 30),
        content['instructions'],
        fontsize=9,
        color=(0, 0, 0),
        align=fitz.TEXT_ALIGN_LEFT
    )

    # ========== SECTION 1: BUSINESS INFORMATION ==========
    y = 140

    # Section header with background
    section_rect = fitz.Rect(30, y - 5, page_width - 30, y + 15)
    page.draw_rect(section_rect, color=(0.2, 0.2, 0.6), fill=(0.93, 0.94, 0.98))

    insert_text_with_font(
        (40, y + 10),
        content['section1'],
        fontsize=11,  # Helvetica Bold
        color=(0.2, 0.2, 0.6)
    )

    y += 30

    # 1. Business Name
    insert_text_with_font((50, y), content['labels']['business_name'], fontsize=9, color=(0.3, 0.3, 0.3))
    y += 3
    widget = fitz.Widget()
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.field_name = "business_name"
    widget.rect = fitz.Rect(50, y, page_width - 50, y + 20)
    widget.text_fontsize = 10
    widget.text_font = widget_font_name
    widget.fill_color = (1, 1, 1)
    widget.border_color = (0.7, 0.7, 0.7)
    widget.border_width = 0.5
    page.add_widget(widget)
    y += 28

    # 2. Business Address
    insert_text_with_font((50, y), content['labels']['business_address'], fontsize=9, color=(0.3, 0.3, 0.3))
    y += 3
    widget = fitz.Widget()
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.field_name = "business_address"
    widget.rect = fitz.Rect(50, y, page_width - 50, y + 20)
    widget.text_fontsize = 10
    widget.text_font = widget_font_name
    widget.fill_color = (1, 1, 1)
    widget.border_color = (0.7, 0.7, 0.7)
    widget.border_width = 0.5
    page.add_widget(widget)
    y += 28

    # 3. Business Type (checkboxes - select only one)
    insert_text_with_font((50, y), content['labels']['business_type'], fontsize=9, color=(0.3, 0.3, 0.3))
    y += 12
    insert_text_with_font((50, y), content['labels']['business_type_hint'], fontsize=8, color=(0.5, 0.5, 0.5))
    y += 8

    # Checkbox options for business types
    business_types = [
        ('business_type_restaurant', content['labels']['business_type_restaurant']),
        ('business_type_manufacturing', content['labels']['business_type_manufacturing']),
        ('business_type_import_export', content['labels']['business_type_import_export']),
        ('business_type_catering', content['labels']['business_type_catering'])
    ]

    checkbox_y = y
    for field_name, label in business_types:
        # Checkbox
        widget = fitz.Widget()
        widget.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
        widget.field_name = field_name
        widget.rect = fitz.Rect(60, checkbox_y, 72, checkbox_y + 12)
        widget.fill_color = (1, 1, 1)
        widget.border_color = (0.7, 0.7, 0.7)
        widget.border_width = 0.5
        page.add_widget(widget)

        # Label text
        insert_text_with_font((78, checkbox_y + 10), label, fontsize=9, color=(0.2, 0.2, 0.2))
        checkbox_y += 18

    y = checkbox_y + 5

    # ========== SECTION 2: FACILITY & OPERATIONS ==========
    # Section header with background
    section_rect = fitz.Rect(30, y - 5, page_width - 30, y + 15)
    page.draw_rect(section_rect, color=(0.2, 0.2, 0.6), fill=(0.93, 0.94, 0.98))

    insert_text_with_font(
        (40, y + 10),
        content['section2'],
        fontsize=11,
        color=(0.2, 0.2, 0.6)
    )
    y += 30

    # 4. Number of Employees
    insert_text_with_font((50, y), content['labels']['num_employees'], fontsize=9, color=(0.3, 0.3, 0.3))
    y += 3
    widget = fitz.Widget()
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.field_name = "num_employees"
    widget.rect = fitz.Rect(50, y, 180, y + 20)
    widget.text_fontsize = 10
    widget.text_font = widget_font_name
    widget.fill_color = (1, 1, 1)
    widget.border_color = (0.7, 0.7, 0.7)
    widget.border_width = 0.5
    page.add_widget(widget)
    y += 28

    # 5. Delivery Radius (miles for US, kilometers for others)
    insert_text_with_font((50, y), content['labels']['delivery_radius'], fontsize=9, color=(0.3, 0.3, 0.3))
    y += 3
    widget = fitz.Widget()
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.field_name = "delivery_radius"
    widget.rect = fitz.Rect(50, y, 180, y + 20)
    widget.text_fontsize = 10
    widget.text_font = widget_font_name
    widget.fill_color = (1, 1, 1)
    widget.border_color = (0.7, 0.7, 0.7)
    widget.border_width = 0.5
    page.add_widget(widget)
    y += 28

    # 6. Has Refrigeration (checkbox)
    insert_text_with_font((50, y), content['labels']['has_refrigeration'], fontsize=9, color=(0.3, 0.3, 0.3))
    y += 12
    insert_text_with_font((50, y), content['labels']['has_refrigeration_hint'], fontsize=8, color=(0.5, 0.5, 0.5))
    y += 5
    widget = fitz.Widget()
    widget.field_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
    widget.field_name = "has_refrigeration"
    widget.rect = fitz.Rect(50, y, 66, y + 16)
    widget.fill_color = (1, 1, 1)
    widget.border_color = (0.7, 0.7, 0.7)
    widget.border_width = 0.5
    page.add_widget(widget)
    y += 33

    # ========== SECTION 3: FOOD SAFETY COMPLIANCE ==========
    # Section header with background
    section_rect = fitz.Rect(30, y - 5, page_width - 30, y + 15)
    page.draw_rect(section_rect, color=(0.2, 0.2, 0.6), fill=(0.93, 0.94, 0.98))

    insert_text_with_font(
        (40, y + 10),
        content['section3'],
        fontsize=11,
        color=(0.2, 0.2, 0.6)
    )
    y += 30

    # 7. Certification Date
    insert_text_with_font((50, y), content['labels']['certification_date'], fontsize=9, color=(0.3, 0.3, 0.3))
    y += 3
    widget = fitz.Widget()
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.field_name = "certification_date"
    widget.rect = fitz.Rect(50, y, 220, y + 20)
    widget.text_fontsize = 10
    widget.text_font = widget_font_name
    widget.fill_color = (1, 1, 1)
    widget.border_color = (0.7, 0.7, 0.7)
    widget.border_width = 0.5
    page.add_widget(widget)
    y += 28

    # 8. Product Description (multi-line)
    insert_text_with_font((50, y), content['labels']['product_description'], fontsize=9, color=(0.3, 0.3, 0.3))
    y += 12
    insert_text_with_font((50, y), content['labels']['product_description_hint'], fontsize=8, color=(0.5, 0.5, 0.5))
    y += 3
    widget = fitz.Widget()
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.field_name = "product_description"
    widget.rect = fitz.Rect(50, y, page_width - 50, y + 55)
    widget.text_fontsize = 9
    widget.text_font = widget_font_name
    widget.field_flags = fitz.PDF_TX_FIELD_IS_MULTILINE
    widget.fill_color = (1, 1, 1)
    widget.border_color = (0.7, 0.7, 0.7)
    widget.border_width = 0.5
    page.add_widget(widget)
    y += 65

    # 9. Safety Procedures (multi-line)
    insert_text_with_font((50, y), content['labels']['safety_procedures'], fontsize=9, color=(0.3, 0.3, 0.3))
    y += 12
    insert_text_with_font((50, y), content['labels']['safety_procedures_hint'], fontsize=8, color=(0.5, 0.5, 0.5))
    y += 3
    widget = fitz.Widget()
    widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    widget.field_name = "safety_procedures"
    widget.rect = fitz.Rect(50, y, page_width - 50, y + 55)
    widget.text_fontsize = 9
    widget.text_font = widget_font_name
    widget.field_flags = fitz.PDF_TX_FIELD_IS_MULTILINE
    widget.fill_color = (1, 1, 1)
    widget.border_color = (0.7, 0.7, 0.7)
    widget.border_width = 0.5
    page.add_widget(widget)
    y += 70

    # ========== DECLARATION ==========
    insert_text_with_font((40, y), content['labels']['declaration'], fontsize=9)
    y += 20

    # Signature line
    page.draw_line((40, y), (280, y), color=(0, 0, 0), width=0.5)
    insert_text_with_font((40, y + 12), content['labels']['signature'], fontsize=8, color=(0.4, 0.4, 0.4))

    # Date line
    page.draw_line((320, y), (480, y), color=(0, 0, 0), width=0.5)
    insert_text_with_font((320, y + 12), content['labels']['date'], fontsize=8, color=(0.4, 0.4, 0.4))

    # ========== FOOTER ==========
    footer_y = page_height_val - 30
    insert_text_with_font((40, footer_y), f"Form Version 2.0 - {lang.upper()}", fontsize=7, color=(0.5, 0.5, 0.5))
    # Right-aligned text using textbox
    insert_textbox_with_font(
        fitz.Rect(page_width - 100, footer_y - 7, page_width - 40, footer_y + 3),
        content['labels']['page_number'],
        fontsize=7,
        color=(0.5, 0.5, 0.5),
        align=fitz.TEXT_ALIGN_RIGHT
    )

    # Save the PDF
    doc.save(output_path)
    doc.close()


def fix_font_references(pdf_path: str):
    """Fix /Helv references to /Helvetica in form field default appearances.

    PyMuPDF creates fields with /Helv in the default appearance string, but pypdf
    has a bug where it crashes when /Helv is not in the font resources. We change
    /Helv to /Helvetica which is in CORE_FONT_METRICS and avoids the bug.
    """
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import NameObject, TextStringObject

    reader = PdfReader(pdf_path)
    writer = PdfWriter(clone_from=reader)

    # Fix all field default appearances
    for page in writer.pages:
        if "/Annots" in page:
            annots = page["/Annots"]
            for annot_ref in annots:
                annot = annot_ref.get_object()
                if "/DA" in annot:
                    # Get the default appearance string
                    da = str(annot["/DA"])
                    # Replace /Helv with /Helvetica
                    if "/Helv " in da:
                        new_da = da.replace("/Helv ", "/Helvetica ")
                        annot[NameObject("/DA")] = TextStringObject(new_da)

    # Save the fixed PDF
    with open(pdf_path, "wb") as f:
        writer.write(f)


def verify_fields(pdf_path: str):
    """Verify that all form fields are present and properly named."""
    doc = fitz.open(pdf_path)
    page = doc[0]

    expected_fields = [
        'business_name',
        'business_address',
        'business_type_restaurant',
        'business_type_manufacturing',
        'business_type_import_export',
        'business_type_catering',
        'num_employees',
        'delivery_radius',
        'has_refrigeration',
        'certification_date',
        'product_description',
        'safety_procedures'
    ]

    # Get all widgets (form fields) on the page
    widgets = page.widgets()
    found_fields = [w.field_name for w in widgets]

    missing = set(expected_fields) - set(found_fields)
    extra = set(found_fields) - set(expected_fields)

    doc.close()

    if missing or extra:
        print(f"❌ ERROR: Field mismatch in {pdf_path}")
        if missing:
            print(f"   Missing: {missing}")
        if extra:
            print(f"   Extra: {extra}")
        return False

    print(f"✓ Verified {len(expected_fields)} fields in {pdf_path}")
    return True


def main():
    """Create Food Business License Application forms in four languages."""
    script_dir = os.path.dirname(os.path.abspath(__file__))

    languages = {
        'us': 'food_license_us.pdf',
        'es': 'food_license_es.pdf',
        'th': 'food_license_th.pdf',
        'ja': 'food_license_ja.pdf',
        'pl': 'food_license_pl.pdf'
    }

    print("=" * 70)
    print("Creating Food Business License Application Forms")
    print("Using PyMuPDF (fitz) for clean, reliable form generation")
    print("=" * 70)

    all_verified = True

    for lang, output_filename in languages.items():
        print(f"\n📄 Creating {lang.upper()} version...")

        output_path = os.path.join(script_dir, output_filename)

        # Create the PDF form
        create_form_pdf(output_path, lang)

        # Fix font references for pypdf compatibility
        fix_font_references(output_path)

        # Verify fields
        if verify_fields(output_path):
            print(f"✓ Created: {output_path}")
        else:
            all_verified = False

    print("\n" + "=" * 70)
    if all_verified:
        print("✓ SUCCESS: All forms created and verified!")
        print("\nGenerated files:")
        for lang, filename in languages.items():
            output_path = os.path.join(script_dir, filename)
            print(f"  • {output_path}")

        print("\nForm fields (identical across all languages):")
        print("  1. business_name - Legal Business Name")
        print("  2. business_address - Business Address")
        print("  3-6. business_type_* - Type of Food Business (4 checkboxes, select one)")
        print("    - business_type_restaurant")
        print("    - business_type_manufacturing")
        print("    - business_type_import_export")
        print("    - business_type_catering")
        print("  7. num_employees - Number of Employees")
        print("  8. delivery_radius - Delivery Radius (miles for US, km for others)")
        print("  9. has_refrigeration - Refrigeration Equipment (checkbox)")
        print("  10. certification_date - Food Safety Certification Date")
        print("  11. product_description - Product/Menu Description (multi-line)")
        print("  12. safety_procedures - Safety Procedures (multi-line)")

        print("\nThese forms are ready for LLM-powered translation testing.")
    else:
        print("❌ ERRORS: Some forms failed verification.")


if __name__ == "__main__":
    main()
