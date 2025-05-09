!pip install reportlab

import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                Table, TableStyle, PageBreak, ListFlowable, ListItem)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import tempfile


def entropy_histogram(entropy_dict, title="Entropy Histogram"):
    entropies = [v['entropy'] for v in entropy_dict.values()]
    fig, ax = plt.subplots()
    ax.hist(entropies, bins=30, color='steelblue', edgecolor='black')
    ax.set_title(title)
    ax.set_xlabel("Entropy")
    ax.set_ylabel("Frequency")
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.tight_layout()
    plt.savefig(temp.name)
    plt.close(fig)
    return temp.name


def poisoned_count_chart(entropy_dict):
    poisoned = sum(1 for v in entropy_dict.values() if v['poisoned'])
    clean = len(entropy_dict) - poisoned
    fig, ax = plt.subplots()
    ax.pie([clean, poisoned], labels=['Clean', 'Poisoned'], autopct='%1.1f%%', colors=['lightgreen', 'red'])
    ax.set_title("Clean vs Poisoned Images")
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.tight_layout()
    plt.savefig(temp.name)
    plt.close(fig)
    return temp.name


def strip_entropy_stats(entropy_dict):
    values = [v['entropy'] for v in entropy_dict.values()]
    if not values:
        return [['Metric', 'Value']]
    stats = [
        ['Metric', 'Value'],
        ['Min Entropy', f"{min(values):.4f}"],
        ['Max Entropy', f"{max(values):.4f}"],
        ['Mean Entropy', f"{np.mean(values):.4f}"],
        ['Median Entropy', f"{np.median(values):.4f}"]
    ]
    return stats


def safe_format(value):
    return f"{value:.4f}" if isinstance(value, (float, int)) else "-"


def generate_individual_report(model, output_dir, report_date):
    model_name = Path(model["path"]).stem
    last_modified = model["last_modified"]
    results = model["detection_methods_used"]["results"]
    if not results:
        return

    pdf_path = Path(output_dir) / f"trojan_detection_report_{model_name}.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Detected', fontSize=11, backColor=colors.pink))
    styles.add(ParagraphStyle(name='NotDetected', fontSize=11, backColor=colors.lightgreen))
    styles.add(ParagraphStyle(name='SectionHeader', fontSize=14, spaceAfter=12, textColor=colors.darkblue))
    styles.add(ParagraphStyle(name='SubHeader', fontSize=12, spaceAfter=6, textColor=colors.darkred))

    elements = []
    elements.append(Paragraph("Trojan Detection Report", styles['Title']))
    elements.append(Paragraph(f"<b>Model:</b> {model_name}", styles['Normal']))
    elements.append(Paragraph(f"<b>Last Modified:</b> {last_modified}", styles['Normal']))
    elements.append(Paragraph(f"<b>Generated:</b> {report_date}", styles['Normal']))
    elements.append(Spacer(1, 12))

    summary_items = []
    for method, result in results.items():
        detected = result[0]
        style = styles['Detected'] if detected else styles['NotDetected']
        summary_items.append(ListItem(Paragraph(f"{method.upper()}: {'Detected' if detected else 'Clean'}", style), leftIndent=10))

    elements.append(Paragraph("Detection Summary:", styles['SubHeader']))
    elements.append(ListFlowable(summary_items, bulletType='bullet'))
    elements.append(Spacer(1, 12))

    if 'strip' in results:
        strip_data = results['strip'][1]
        entropy_img = entropy_histogram(strip_data, title=f"Entropy Distribution – {model_name}")
        poisoned_img = poisoned_count_chart(strip_data)
        entropy_stats = strip_entropy_stats(strip_data)

        elements.append(Paragraph("STRIP Analysis:", styles['SubHeader']))
        elements.append(Paragraph("This analysis shows how entropy varies across inputs. Lower entropy can indicate poisoning.", styles['Normal']))
        elements.append(Image(entropy_img, width=5.5 * inch, height=3 * inch))
        elements.append(Image(poisoned_img, width=4.5 * inch, height=3.5 * inch))
        stats_table = Table(entropy_stats, hAlign='LEFT')
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 12))

    if 'free_eagle' in results:
        fe = results['free_eagle'][1]
        elements.append(Paragraph("Free Eagle Analysis:", styles['SubHeader']))
        elements.append(Paragraph("Statistical thresholds and activation patterns are used to identify potential backdoors.", styles['Normal']))
        stats = [
            ['Metric', 'Value'],
            ['m_trojaned', safe_format(fe.get('m_trojaned'))],
            ['Lower Bound', safe_format(fe.get('lower_bound'))],
            ['Upper Bound', safe_format(fe.get('upper_bound'))]
        ]
        table = Table(stats, hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

    doc.build(elements)
    print(f"Generated: {pdf_path}")


def generate_pdf_report(json_path="backend/database.json", output_dir="reports"):
    with open(json_path) as f:
        data = json.load(f)

    Path(output_dir).mkdir(exist_ok=True)
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for model in data['models']:
        generate_individual_report(model, output_dir, report_date)


if __name__ == "__main__":
    generate_pdf_report()
