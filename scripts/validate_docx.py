#!/usr/bin/env python3
"""
Скрипт автоматичної валідації параметрів DOCX-документа на відповідність
правилам українського службового діловодства (ДСТУ 4163:2020 та відомчим інструкціям).

Використання:
    python validate_docx.py <шлях_до_файлу.docx> [--profile ordinary|president|minjust]
"""

import sys
import json
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

try:
    from docx import Document
    from docx.shared import Pt, Mm
    from docx.oxml.ns import qn
except ImportError:
    print("Помилка: бібліотека 'python-docx' не встановлена. Встановіть її через: pip install python-docx", file=sys.stderr)
    sys.exit(1)


def check_margins(section, tolerance_mm=2.0):
    expected = {
        'left_margin': 30.0,
        'right_margin': 10.0,
        'top_margin': 20.0,
        'bottom_margin': 20.0
    }
    results = {}
    for attr, target in expected.items():
        actual_val = getattr(section, attr)
        actual_mm = actual_val.mm if actual_val is not None else 0.0
        diff = abs(actual_mm - target)
        results[attr] = {
            'expected_mm': target,
            'actual_mm': round(actual_mm, 2),
            'passed': diff <= tolerance_mm
        }
    return results


def check_docx_compliance(docx_path: Path, profile: str = 'ordinary') -> dict:
    if not docx_path.exists():
        return {'status': 'error', 'message': f'Файл не знайдено: {docx_path}'}

    doc = Document(docx_path)
    report = {
        'file': str(docx_path),
        'profile': profile,
        'sections_count': len(doc.sections),
        'paragraphs_count': len(doc.paragraphs),
        'tables_count': len(doc.tables),
        'checks': {},
        'issues': []
    }

    # 1. Перевірка полів першої секції
    if doc.sections:
        margins_res = check_margins(doc.sections[0])
        report['checks']['margins'] = margins_res
        for k, v in margins_res.items():
            if not v['passed']:
                report['issues'].append(
                    f"Поле '{k}': очікувалось {v['expected_mm']} мм, фактично {v['actual_mm']} мм"
                )

    # Визначення цільових значень за профілем
    if profile == 'president':
        target_font_size = 16.0
        target_spacing = 1.5
    elif profile == 'minjust':
        target_font_size = 14.0
        target_spacing = 1.5
    else:
        target_font_size = None  # Дозволений діапазон 12-14 pt
        target_spacing = None    # Дозволено 1.0 - 1.5

    # 2. Аналіз абзаців
    font_issues = 0
    heading_dot_issues = 0
    quote_issues = 0

    for idx, p in enumerate(doc.paragraphs):
        text = p.text.strip()
        if not text:
            continue

        # Перевірка лапок: дозволені виключно “”
        disallowed_quotes = [q for q in ('«', '»', '"', '„') if q in text]
        if disallowed_quotes:
            quote_issues += 1
            if quote_issues <= 3:
                report['issues'].append(
                    f"Абзац {idx+1}: виявлено недозволені лапки {disallowed_quotes}. Необхідно використовувати виключно лапки “”"
                )

        # Перевірка шрифту та кеглю
        for r in p.runs:
            if r.font.name and r.font.name != 'Times New Roman':
                font_issues += 1
                if font_issues <= 3:
                    report['issues'].append(
                        f"Абзац {idx+1}: шрифт '{r.font.name}' замість 'Times New Roman'"
                    )
            if r.font.size is not None:
                pt_val = r.font.size.pt
                if profile in ('president', 'minjust'):
                    if abs(pt_val - target_font_size) > 0.5:
                        report['issues'].append(
                            f"Абзац {idx+1}: розмір шрифту {pt_val} pt не відповідає профілю {profile} ({target_font_size} pt)"
                        )
                else:
                    if pt_val < 8.0 or pt_val > 14.5:
                        report['issues'].append(
                            f"Абзац {idx+1}: розмір шрифту {pt_val} pt поза дозволеним діапазоном (12–14 pt для тексту, 8–12 pt для допоміжних елементів)"
                        )

        # Перевірка крапки в кінці заголовків
        if p.style and 'heading' in p.style.name.lower() or p.runs and all(r.bold for r in p.runs if r.text.strip()):
            if text.endswith('.') and not text.endswith('...'):
                heading_dot_issues += 1
                report['issues'].append(
                    f"Абзац {idx+1} (заголовок): виявлено крапку в кінці заголовка: '{text[:40]}...'"
                )

    report['checks']['font_family_compliance'] = (font_issues == 0)
    report['checks']['heading_syntax_compliance'] = (heading_dot_issues == 0)
    report['checks']['quotes_compliance'] = (quote_issues == 0)

    report['status'] = 'PASSED' if not report['issues'] else 'FAILED'
    return report


def main():
    parser = argparse.ArgumentParser(description="Валідація DOCX-документа за українськими нормами діловодства")
    parser.add_argument("file", help="Шлях до DOCX файлу")
    parser.add_argument("--profile", choices=['ordinary', 'president', 'minjust'], default='ordinary',
                        help="Профіль перевірки (ordinary, president, minjust)")
    parser.add_argument("--json", action="store_true", help="Вивести звіт у форматі JSON")

    args = parser.parse_args()
    report = check_docx_compliance(Path(args.file), profile=args.profile)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print(f"ЗВІТ ВАЛІДАЦІЇ: {report['file']}")
        print(f"Профіль: {report['profile']} | Статус: {report['status']}")
        print("=" * 60)
        if report['issues']:
            print(f"Знайдено невідповідностей: {len(report['issues'])}")
            for issue in report['issues']:
                print(f" [!] {issue}")
        else:
            print("[+] Усі базові геометричні та шрифтові перевірки успішно пройдено!")
        print("=" * 60)


if __name__ == "__main__":
    main()
