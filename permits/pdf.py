from io import BytesIO

import qrcode

from django.http import FileResponse

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from .models import Permit


def generate_permit_pdf(request, permit):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "PermitTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        spaceAfter=10,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        textColor=colors.white,
        backColor=colors.HexColor("#1f4e78"),
        borderPadding=5,
        spaceBefore=10,
        spaceAfter=5,
    )

    normal = styles["Normal"]

    elements = []

    elements.append(
        Paragraph(
            "PERMIT TO WORK",
            title_style,
        )
    )

    elements.append(
        Paragraph(
            f"<b>Permit Number:</b> {permit.permit_number}",
            normal,
        )
    )

    elements.append(
        Spacer(
            1,
            5,
        )
    )

    data = [
        [
            "Permit Type",
            permit.permit_type.name,
        ],
        [
            "Location",
            permit.location.name,
        ],
        [
            "Requester",
            str(permit.requester),
        ],
        [
            "Contractor",
            permit.contractor_name or "-",
        ],
        [
            "Work Start",
            permit.work_start.strftime(
                "%d-%m-%Y %H:%M"
            ),
        ],
        [
            "Work End",
            permit.work_end.strftime(
                "%d-%m-%Y %H:%M"
            ),
        ],
        [
            "Status",
            permit.get_status_display(),
        ],
    ]

    table = Table(
        data,
        colWidths=[
            45 * mm,
            125 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#eeeeee"),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    elements.append(table)

    elements.append(
        Paragraph(
            "WORK DETAILS",
            heading_style,
        )
    )

    elements.append(
        Paragraph(
            permit.work_description.replace(
                "\n",
                "<br/>",
            ),
            normal,
        )
    )

    elements.append(
        Paragraph(
            "WORKERS",
            heading_style,
        )
    )

    workers = permit.workers or "-"

    elements.append(
        Paragraph(
            workers.replace(
                "\n",
                "<br/>",
            ),
            normal,
        )
    )

    elements.append(
        Paragraph(
            "REQUIRED PPE",
            heading_style,
        )
    )

    ppe_data = [
        [
            "PPE",
            "Required",
            "Verified",
            "Remarks",
        ]
    ]

    for item in permit.ppe_items.select_related("ppe"):

        ppe_data.append(
            [
                item.ppe.name,
                "YES" if item.required else "NO",
                "YES" if item.verified else "NO",
                item.remarks or "-",
            ]
        )

    ppe_table = Table(
        ppe_data,
        colWidths=[
            65 * mm,
            25 * mm,
            25 * mm,
            55 * mm,
        ],
    )

    ppe_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#dddddd"),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    elements.append(ppe_table)

    elements.append(
        Paragraph(
            "SAFETY CONTROLS",
            heading_style,
        )
    )

    control_data = [
        [
            "Safety Control",
            "Required",
            "Verified",
            "Remarks",
        ]
    ]

    for item in permit.safety_controls.select_related(
        "safety_control"
    ):

        control_data.append(
            [
                item.safety_control.name,
                "YES" if item.required else "NO",
                "YES" if item.verified else "NO",
                item.remarks or "-",
            ]
        )

    control_table = Table(
        control_data,
        colWidths=[
            70 * mm,
            25 * mm,
            25 * mm,
            50 * mm,
        ],
    )

    control_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#dddddd"),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    elements.append(control_table)

    elements.append(
        Paragraph(
            "APPROVAL",
            heading_style,
        )
    )

    approval = [
        [
            "Approved By",
            str(permit.approved_by or "-"),
        ],
        [
            "Approved At",
            (
                permit.approved_at.strftime(
                    "%d-%m-%Y %H:%M"
                )
                if permit.approved_at
                else "-"
            ),
        ],
    ]

    approval_table = Table(
        approval,
        colWidths=[
            45 * mm,
            125 * mm,
        ],
    )

    approval_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#eeeeee"),
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "PADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
            ]
        )
    )

    elements.append(approval_table)

    # QR Code
    qr_data = (
        request.build_absolute_uri(
            f"/permits/{permit.pk}/"
        )
    )

    qr = qrcode.make(qr_data)

    qr_buffer = BytesIO()

    qr.save(
        qr_buffer,
        format="PNG",
    )

    qr_buffer.seek(0)

    from reportlab.platypus import Image

    elements.append(
        Spacer(
            1,
            10,
        )
    )

    elements.append(
        Image(
            qr_buffer,
            width=30 * mm,
            height=30 * mm,
        )
    )

    doc.build(elements)

    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f"{permit.permit_number}.pdf",
        content_type="application/pdf",
    )
