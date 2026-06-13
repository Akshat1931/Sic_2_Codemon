"""
modules/incident_manager.py - Manages the lifecycle of disaster incidents.
"""
from collections import deque
import csv
from models.incident import DisasterIncident
from algorithms.priority_queue import IncidentPriorityQueue

class IncidentManager:
    """
    Module A: Incident Management.
    Registers incidents, manages the priority heap and FIFO dispatch queues,
    and supports exporting status reports.
    """
    def __init__(self):
        self.incidents: list[DisasterIncident] = []
        self.priority_queue = IncidentPriorityQueue()
        self.dispatch_queue = deque()  # FIFO Queue for dispatching

    def register(self, incident: DisasterIncident):
        """Registers a new incident, validates it, and inserts it into the queues."""
        incident.validate()
        self.incidents.append(incident)
        self.priority_queue.push(incident)
        self.dispatch_queue.append(incident)

    def get_by_severity(self, severity_level: str) -> list[DisasterIncident]:
        """Filters registered incidents by severity level (Low, Medium, High, Critical)."""
        return [i for i in self.incidents if i.severity_level_str.lower() == severity_level.lower()]

    def export_report(self, filepath: str):
        """Exports the list of incidents to a CSV report file."""
        with open(filepath, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Incident ID", "Location ID", "Disaster Type", 
                "Severity Score", "Population Affected", "Reporter", 
                "Timestamp", "Status", "Assigned Shelter"
            ])
            for i in self.incidents:
                writer.writerow([
                    i.incident_id, i.location, i.disaster_type,
                    i.severity, i.population_affected, i.reporter,
                    i.timestamp, i.status, i.assigned_shelter or "None"
                ])

    def export_report_pdf(self, filepath: str):
        """Exports the list of incidents to a professional PDF report (Section 13 of PDF)."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
        except ImportError:
            # Fallback to txt report if reportlab is not installed
            fallback_path = filepath.replace(".pdf", "_fallback.txt")
            with open(fallback_path, "w", encoding="utf-8") as f:
                f.write("=== DISASTERSENSE EMERGENCY INCIDENT REPORT (FALLBACK) ===\n\n")
                for i in self.incidents:
                    f.write(
                        f"ID: {i.incident_id} | Location: {i.location} | Type: {i.disaster_type} | "
                        f"Severity: {i.severity_level_str} | Population: {i.population_affected:,} | Status: {i.status}\n"
                    )
            return

        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=20,
            textColor=colors.HexColor('#0f172a'),
            spaceAfter=12
        )
        subtitle_style = ParagraphStyle(
            'SubtitleStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=15
        )
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8,
            textColor=colors.HexColor('#334155')
        )
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=8,
            textColor=colors.white
        )

        elements = []
        elements.append(Paragraph("DISASTERSENSE EMERGENCY OPERATIONS REPORT", title_style))
        from datetime import datetime
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} | Classification: CONFIDENTIAL", subtitle_style))
        elements.append(Spacer(1, 10))

        data = [[
            Paragraph("Incident ID", header_style),
            Paragraph("Location ID", header_style),
            Paragraph("Disaster Type", header_style),
            Paragraph("Severity Level", header_style),
            Paragraph("Population", header_style),
            Paragraph("Status", header_style),
        ]]
        
        for i in self.incidents:
            data.append([
                Paragraph(i.incident_id, body_style),
                Paragraph(i.location, body_style),
                Paragraph(i.disaster_type, body_style),
                Paragraph(i.severity_level_str, body_style),
                Paragraph(f"{i.population_affected:,}", body_style),
                Paragraph(i.status, body_style),
            ])

        # Width of columns matching total width of letter size printable area (around 480 points)
        t = Table(data, colWidths=[70, 80, 80, 80, 90, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('TOPPADDING', (0, 0), (-1, 0), 6),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ]))
        
        elements.append(t)
        doc.build(elements)
