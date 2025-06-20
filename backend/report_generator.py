import json
import tempfile
import numpy as np
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, ListFlowable, ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch


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

def netcop_plots(mat_p, v):
    fig, axs = plt.subplots(2, 1, figsize=(16, 8), gridspec_kw={'height_ratios': [3, 1]})
    axs[0].matshow(mat_p, cmap='viridis')
    axs[1].boxplot(v, vert=False, widths=0.5)
    axs[0].set_title('NetCop Posteriors Matrix')
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
    value = float(value)
    return f"{value:.4f}" if isinstance(value, (float, int)) else "-"


def generate_individual_report(model, output_dir):
    model_name = Path(model["path"]).stem
    last_modified = model["last_modified"]
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results = model["detection_methods_used"]["results"]
    if not results:
        print("No results found for this model.")
        return False

    pdf_path = Path(output_dir or "./reports") / f"trojan_detection_report_{model_name}.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=A4)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Detected', fontSize=11, backColor=colors.pink))
    styles.add(ParagraphStyle(name='NotDetected', fontSize=11, backColor=colors.lightgreen))
    styles.add(ParagraphStyle(name='SectionHeader', fontSize=14, spaceAfter=12, textColor=colors.darkblue))
    styles.add(ParagraphStyle(name='SubHeader', fontSize=12, spaceAfter=6, textColor=colors.darkred))

    elements = []
    elements.append(Paragraph("Trojan Detection Report", styles['Title']))
    elements.append(Paragraph(f"<b>Model:</b> {model_name}", styles['Normal']))
    elements.append(Paragraph(f"<b>Metrics generation date:</b> {last_modified}", styles['Normal']))
    elements.append(Paragraph(f"<b>Report generation date:</b> {report_date}", styles['Normal']))
    elements.append(Spacer(1, 12))

    summary_items = []
    for method, result in results.items():
        detected = result[0]
        style = styles['Detected'] if detected else styles['NotDetected']
        summary_items.append(ListItem(Paragraph(f"{method.upper()}: {'Trojan Detected' if detected else 'Clean'}", style), leftIndent=10))

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

    if 'netcop' in results:
        fe = results['netcop'][1]
        elements.append(Paragraph("NetCop Analysis:", styles['SubHeader']))
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

        netcop_matrix_vis = netcop_plots(fe['mat_p'], fe['V'])
        elements.append(Image(netcop_matrix_vis, width = 8 * inch, height = 4 * inch))
        elements.append(Spacer(1, 12))

    doc.build(elements)
    print(f"Generated: {pdf_path}")
    return True


def generate_pdf_report(json_path="backend/database.json", output_dir="reports"):
    with open(json_path) as f:
        data = json.load(f)

    Path(output_dir).mkdir(exist_ok=True)
    for model in data['models']:
        generate_individual_report(model, output_dir)


if __name__ == "__main__":
    generate_pdf_report()