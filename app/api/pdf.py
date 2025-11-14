"""PDF summary endpoint for domain account summaries (G17)."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from app.db.session import get_db
from app.db.models import Company, DomainSignal, LeadScore
from app.core.normalizer import normalize_domain
from app.core.priority import calculate_priority_score


router = APIRouter(prefix="/leads", tags=["pdf"])


@router.get("/{domain}/summary.pdf")
async def get_pdf_summary(domain: str, db: Session = Depends(get_db)):
    """
    Generate a PDF summary for a domain.

    Includes:
    - Provider information
    - SPF/DKIM/DMARC status
    - Expiry date
    - Signals (MX, nameservers)
    - Migration Score, Priority Score
    - Risks (no SPF, no DKIM, DMARC none)

    Args:
        domain: Domain name (will be normalized)
        db: Database session

    Returns:
        PDF file download

    Raises:
        404: If domain not found or not scanned
        400: If domain is invalid
    """
    # Normalize domain
    normalized_domain = normalize_domain(domain)

    if not normalized_domain:
        raise HTTPException(status_code=400, detail="Invalid domain format")

    # Query domain data
    query = """
        SELECT 
            c.id AS company_id,
            c.canonical_name,
            c.domain,
            c.provider,
            c.country,
            ds.spf,
            ds.dkim,
            ds.dmarc_policy,
            ds.mx_root,
            ds.registrar,
            ds.expires_at,
            ds.nameservers,
            ds.scan_status,
            ds.scanned_at,
            ls.readiness_score,
            ls.segment,
            ls.reason
        FROM companies c
        LEFT JOIN domain_signals ds ON c.domain = ds.domain
        LEFT JOIN lead_scores ls ON c.domain = ls.domain
        WHERE c.domain = :domain
    """

    try:
        result = db.execute(text(query), {"domain": normalized_domain})
        row = result.fetchone()

        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"Domain {normalized_domain} not found. Please ingest the domain first using /ingest/domain",
            )

        # Check if domain has been scanned
        if row.readiness_score is None:
            raise HTTPException(
                status_code=404,
                detail=f"Domain {normalized_domain} has not been scanned yet. Please use /scan/domain first.",
            )

        # Calculate priority score
        priority_score = calculate_priority_score(row.segment, row.readiness_score)

        # Generate PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch
        )

        # Container for the 'Flowable' objects
        elements = []

        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1a1a1a"),
            spaceAfter=30,
            alignment=TA_CENTER,
        )

        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=14,
            textColor=colors.HexColor("#2c3e50"),
            spaceAfter=12,
            spaceBefore=12,
        )

        # Title
        elements.append(Paragraph("Domain Account Summary", title_style))
        elements.append(Spacer(1, 0.2 * inch))

        # Domain Information
        elements.append(Paragraph("Domain Information", heading_style))
        domain_data = [
            ["Domain:", normalized_domain],
            ["Company:", row.canonical_name or "N/A"],
            ["Provider:", row.provider or "Unknown"],
            ["Country:", row.country or "N/A"],
        ]
        domain_table = Table(domain_data, colWidths=[2 * inch, 4 * inch])
        domain_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ecf0f1")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        elements.append(domain_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Security Status
        elements.append(Paragraph("Security Status", heading_style))
        security_data = [
            ["SPF:", "Yes" if row.spf else "No"],
            ["DKIM:", "Yes" if row.dkim else "No"],
            ["DMARC Policy:", row.dmarc_policy or "None"],
        ]
        security_table = Table(security_data, colWidths=[2 * inch, 4 * inch])
        security_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ecf0f1")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        elements.append(security_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Scores
        elements.append(Paragraph("Scores", heading_style))
        scores_data = [
            ["Readiness Score:", f"{row.readiness_score}/100"],
            ["Segment:", row.segment or "N/A"],
            ["Priority Score:", f"{priority_score}/6" if priority_score else "N/A"],
        ]
        scores_table = Table(scores_data, colWidths=[2 * inch, 4 * inch])
        scores_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ecf0f1")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        elements.append(scores_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Signals
        elements.append(Paragraph("Signals", heading_style))
        signals_data = [
            ["MX Root:", row.mx_root or "N/A"],
            ["Registrar:", row.registrar or "N/A"],
            ["Expires At:", str(row.expires_at) if row.expires_at else "N/A"],
            ["Nameservers:", ", ".join(row.nameservers) if row.nameservers else "N/A"],
        ]
        signals_table = Table(signals_data, colWidths=[2 * inch, 4 * inch])
        signals_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ecf0f1")),
                    ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ]
            )
        )
        elements.append(signals_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Risks
        risks = []
        if row.spf is False:
            risks.append("No SPF record")
        if row.dkim is False:
            risks.append("No DKIM record")
        if row.dmarc_policy == "none" or not row.dmarc_policy:
            risks.append("DMARC policy is 'none'")

        if risks:
            elements.append(Paragraph("Risks", heading_style))
            for risk in risks:
                elements.append(Paragraph(f"• {risk}", styles["Normal"]))
            elements.append(Spacer(1, 0.2 * inch))

        # Reason
        if row.reason:
            elements.append(Paragraph("Analysis", heading_style))
            elements.append(Paragraph(row.reason, styles["Normal"]))
            elements.append(Spacer(1, 0.2 * inch))

        # Footer
        elements.append(Spacer(1, 0.3 * inch))
        elements.append(
            Paragraph(
                f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                ParagraphStyle(
                    "Footer",
                    parent=styles["Normal"],
                    fontSize=8,
                    textColor=colors.grey,
                    alignment=TA_CENTER,
                ),
            )
        )

        # Build PDF
        doc.build(elements)
        buffer.seek(0)

        # Return PDF
        return Response(
            content=buffer.read(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={normalized_domain}_summary.pdf"
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
