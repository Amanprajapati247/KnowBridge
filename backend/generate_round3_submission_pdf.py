import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#0f172a"))
            self.drawString(54, 752, "TECH TITAN")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(110, 752, "|   KNOWBRIDGE   |   HACKATHON ROUND 3 FINAL SUBMISSION")
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#0d9488"))
            self.drawRightString(558, 752, "LIVE ON RAILWAY")
            
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(54, 32, "KnowBridge - Intelligent Project Knowledge Handover Platform  •  Tech Titan (Aman Prajapati)")
        self.drawRightString(558, 32, f"Page {self._pageNumber} of {total_pages}")
        self.restoreState()

def build_round3_pdf(filename="KnowBridge_Round_3_Final_Submission.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=44,
        rightMargin=44,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Brand Colors
    navy = colors.HexColor("#0f172a")
    teal = colors.HexColor("#0d9488")
    teal_dark = colors.HexColor("#0f766e")
    slate_dark = colors.HexColor("#1e293b")
    slate_muted = colors.HexColor("#64748b")
    bg_light = colors.HexColor("#f8fafc")
    border_color = colors.HexColor("#cbd5e1")
    amber = colors.HexColor("#b45309")
    purple = colors.HexColor("#7e22ce")

    # Typography styles
    cover_title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=32,
        textColor=navy,
        spaceAfter=4
    )

    cover_subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=teal,
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=navy,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=teal_dark,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=slate_dark,
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=slate_dark,
        leftIndent=10,
        firstLineIndent=-7,
        spaceAfter=2.5
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=slate_dark
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=navy
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=slate_dark
    )

    story = []

    # ================= PAGE 1: COVER PAGE =================
    story.append(Spacer(1, 20))
    story.append(Paragraph("KNOWBRIDGE", cover_title_style))
    story.append(Paragraph("INTELLIGENT PROJECT KNOWLEDGE HANDOVER PLATFORM", cover_subtitle_style))
    story.append(Paragraph("<b>ROUND 3 FINAL SUBMISSION & TECHNICAL SPECIFICATION</b>", ParagraphStyle('SubSub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=slate_muted, spaceAfter=20)))
    
    # Meta card table
    meta_rows = [
        [Paragraph("Project Name", table_cell_bold), Paragraph("KnowBridge", table_cell_style),
         Paragraph("Team Name", table_cell_bold), Paragraph("Tech Titan", table_cell_style)],
        [Paragraph("Participation", table_cell_bold), Paragraph("Individual Participant (Aman Prajapati)", table_cell_style),
         Paragraph("Hackathon Round", table_cell_bold), Paragraph("Round 3 - The Finish (Final Submission)", table_cell_style)],
        [Paragraph("Live Web Application", table_cell_bold), Paragraph("<u>https://knowbridge-production.up.railway.app/</u>", table_cell_style),
         Paragraph("Interactive API Docs", table_cell_bold), Paragraph("<u>https://knowbridge-production.up.railway.app/docs</u>", table_cell_style)],
        [Paragraph("GitHub Source Code", table_cell_bold), Paragraph("<u>https://github.com/Amanprajapati247/KnowBridge</u>", table_cell_style),
         Paragraph("Automated Tests", table_cell_bold), Paragraph("10/10 Pytest Test Suites Passing (100%)", table_cell_style)],
        [Paragraph("Lead Demo Account", table_cell_bold), Paragraph("lead@knowbridge.io  |  PW: DemoLead123!", table_cell_style),
         Paragraph("Incoming Demo Account", table_cell_bold), Paragraph("incoming@knowbridge.io  |  PW: Incoming123!", table_cell_style)]
    ]
    t_meta = Table(meta_rows, colWidths=[105, 160, 105, 154])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_light),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 15))

    # Core Purpose Callout Box
    callout_data = [
        [Paragraph("<b>Mission Statement:</b> <i>\"Prevent Critical Technical & Operational Knowledge From Leaving With Departing Engineers.\"</i><br/><br/>"
                   "KnowBridge bridges the gap between scattered, contradictory project files and verifiable engineering continuations. "
                   "It features multi-source ingestion (PDF, DOCX, TXT, GitHub, Jira), 10 structured extraction categories, coordinate-grounded "
                   "passage citations, pairwise conflict reconciliation, an editorial lead review studio, semantic hybrid RAG (Dense Vector + BM25), "
                   "and an immutable SHA-256 cryptographic audit trail with verifiable incoming-member acknowledgment receipts.", callout_style)]
    ]
    t_callout = Table(callout_data, colWidths=[524])
    t_callout.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0fdfa")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#99f6e4")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_callout)
    story.append(Spacer(1, 15))

    # Highlights Table
    high_rows = [
        [Paragraph("Delivered Round 3 Commitments", table_header_style), Paragraph("Core Implementation & Architecture", table_header_style)],
        [
            Paragraph("<b>1. Live Git & Task Connectors:</b> Direct GitHub repo sync (commits, PRs, decisions) & Jira/Linear adapters with incremental sync.<br/><br/>"
                      "<b>2. Semantic Hybrid RAG:</b> Dense vector cosine similarity + Okapi BM25 keyword search with Reciprocal Rank Fusion (RRF) and absence disclosure.<br/><br/>"
                      "<b>3. Cryptographic Audit Trail:</b> SHA-256 content hashing, version snapshot comparison (v1.0 vs v2.0), and signed incoming-member acknowledgment receipts.", table_cell_style),
            Paragraph("<b>• Technology Stack:</b> React 18, TypeScript, Vite, Tailwind CSS, Python 3.12+, FastAPI, SQLAlchemy 2.0, PyMuPDF, python-docx.<br/><br/>"
                      "<b>• Database Parity:</b> SQLite for local zero-config testing with PostgreSQL & pgvector schema readiness.<br/><br/>"
                      "<b>• Cloud Production:</b> Live single-port multi-stage Docker deployment running on Railway Cloud with zero CORS friction.", table_cell_style)
        ]
    ]
    t_high = Table(high_rows, colWidths=[262, 262])
    t_high.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('BACKGROUND', (0,1), (-1,-1), bg_light),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_high)
    story.append(PageBreak())

    # ================= PAGE 2: TABLE OF CONTENTS & PROBLEM STATEMENT =================
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=teal, spaceBefore=2, spaceAfter=8))
    
    toc_data = [
        [Paragraph("<b>Section</b>", table_header_style), Paragraph("<b>Title & Core Content</b>", table_header_style), Paragraph("<b>Page</b>", table_header_style)],
        [Paragraph("Section 1", table_cell_bold), Paragraph("Executive Summary, Problem Analysis & The Knowledge Loss Crisis", table_cell_style), Paragraph("Page 3", table_cell_style)],
        [Paragraph("Section 2", table_cell_bold), Paragraph("Core Major Product Features & 10 Knowledge Extraction Categories", table_cell_style), Paragraph("Page 4", table_cell_style)],
        [Paragraph("Section 3", table_cell_bold), Paragraph("Verification Engine, Conflict Resolution & Human-in-the-Loop Studio", table_cell_style), Paragraph("Page 5", table_cell_style)],
        [Paragraph("Section 4", table_cell_bold), Paragraph("<b>Improvements Delivered After Round 2</b> (Detailed Commitments Overview)", table_cell_style), Paragraph("Page 6", table_cell_style)],
        [Paragraph("Section 5", table_cell_bold), Paragraph("<b>Commitment 1:</b> Live Git & Task Connectors (GitHub, Jira, Linear)", table_cell_style), Paragraph("Page 7", table_cell_style)],
        [Paragraph("Section 6", table_cell_bold), Paragraph("<b>Commitment 2:</b> Semantic Hybrid RAG (Dense Embeddings, BM25 & RRF)", table_cell_style), Paragraph("Page 8", table_cell_style)],
        [Paragraph("Section 7", table_cell_bold), Paragraph("<b>Commitment 3:</b> Cryptographic Audit Trail, Version Diff & Acknowledgment", table_cell_style), Paragraph("Page 9", table_cell_style)],
        [Paragraph("Section 8", table_cell_bold), Paragraph("Technical Architecture, Multi-Stage Docker & Database Readiness", table_cell_style), Paragraph("Page 10", table_cell_style)],
        [Paragraph("Section 9", table_cell_bold), Paragraph("5-Stage Handover Lifecycle & End-to-End Workflow Diagram", table_cell_style), Paragraph("Page 11", table_cell_style)],
        [Paragraph("Section 10", table_cell_bold), Paragraph("Comprehensive Testing & Reliability Evidence (10/10 Pytest Suites Passed)", table_cell_style), Paragraph("Page 12", table_cell_style)],
        [Paragraph("Section 11", table_cell_bold), Paragraph("End-to-End User Journeys (Project Lead & Incoming Member Walkthroughs)", table_cell_style), Paragraph("Page 13", table_cell_style)],
        [Paragraph("Section 12", table_cell_bold), Paragraph("Round 3 Hackathon Evaluation Criteria Alignment & Scoring Rubric", table_cell_style), Paragraph("Page 14", table_cell_style)],
        [Paragraph("Section 13", table_cell_bold), Paragraph("Product Roadmap (Phases 1-3) & Judge Verification Guide", table_cell_style), Paragraph("Page 15", table_cell_style)],
    ]
    t_toc = Table(toc_data, colWidths=[70, 400, 54])
    t_toc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_toc)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Document Overview & Primary Source of Truth Notice", h2_style))
    story.append(Paragraph(
        "This submission document has been authored following a rigorous audit of the live deployed application "
        "(<u>https://knowbridge-production.up.railway.app/</u>) and public GitHub codebase (<u>https://github.com/Amanprajapati247/KnowBridge</u>). "
        "No metrics, user counts, or integrations have been fabricated. Features are documented according to their verified code implementation. "
        "Where fallback adapters are utilized (such as Jira/Linear when live enterprise API keys are not injected), they are transparently disclosed.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 3: EXECUTIVE SUMMARY & PROBLEM ANALYSIS =================
    story.append(Paragraph("1. Executive Summary & Problem Analysis", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=teal, spaceBefore=2, spaceAfter=8))
    
    story.append(Paragraph("1.1 The Real-World Knowledge Loss Crisis in Engineering", h2_style))
    story.append(Paragraph(
        "Modern software organizations face chronic disruption caused by personnel transitions. When senior engineers, student leaders, "
        "or core contributors depart, mission-critical technical intelligence leaves with them. Traditional documentation repositories "
        "(Google Drive, Confluence, Notion) suffer from four systemic failures:",
        body_style
    ))
    story.append(Paragraph("&bull; <b>Information Fragmentation:</b> Critical architectural context is splintered across specification PDFs, meeting docx files, text notes, pull request reviews, and ticket comments. No single engineer possesses the complete picture.", bullet_style))
    story.append(Paragraph("&bull; <b>Contradiction and Staleness:</b> Projects evolve faster than static wikis. An initial requirements specification may dictate a release date of November 15, while later meeting notes record a postponement to November 25. New hires have no systematic mechanism to distinguish authoritative decisions from obsolete notes.", bullet_style))
    story.append(Paragraph("&bull; <b>Ungrounded Generative AI Hallucinations:</b> Applying off-the-shelf generative AI summarizers frequently yields fabricated facts, incorrect task assignments, or hallucinated APIs because standard models are not strictly anchored to coordinate-verified text passages.", bullet_style))
    story.append(Paragraph("&bull; <b>Lack of Compliance & Sign-off Traceability:</b> Traditional handovers conclude with informal emails or verbal walk-throughs. If an inherited microservice fails or a compliance deadline is missed, there is zero verifiable proof of what context was communicated or acknowledged.", bullet_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("1.2 The KnowBridge Approach: Evidence-Grounded Knowledge Transfer", h2_style))
    story.append(Paragraph(
        "KnowBridge transforms unstructured, multi-source project exhaust into a structured, verifiable, and role-governed continuation plan. "
        "Rather than relying on ungrounded AI chat, KnowBridge anchors every statement to coordinate-level source citations, detects cross-document "
        "discrepancies, empowers project leads to edit and redact sensitive data, and seals approved handovers into an immutable SHA-256 audit trail.",
        body_style
    ))

    prob_sol_data = [
        [Paragraph("<b>Traditional Handover Failure Mode</b>", table_header_style), Paragraph("<b>The KnowBridge Architectural Solution</b>", table_header_style)],
        [
            Paragraph("<b>Scattered, Unstructured Context:</b> Critical decisions buried across disparate files and chat threads.", table_cell_style),
            Paragraph("<b>Unified Ingestion & 10 Structured Categories:</b> Automatically parses PDF, DOCX, TXT, and GitHub PRs into decisions, tasks, owners, deadlines, risks, and blockers.", table_cell_style)
        ],
        [
            Paragraph("<b>Conflicting Information:</b> Mismatched target dates or architectures silently confuse incoming engineers.", table_cell_style),
            Paragraph("<b>Pairwise Discrepancy Detection:</b> Surfaces contradictions side-by-side with confidence scores, requiring explicit human resolution.", table_cell_style)
        ],
        [
            Paragraph("<b>AI Hallucinations:</b> Generic LLMs invent dates, owners, and non-existent system requirements.", table_cell_style),
            Paragraph("<b>100% Traceable Grounding & Absence Disclosure:</b> Every claim cites page numbers and byte offsets; missing facts explicitly return 'UNCERTAIN'.", table_cell_style)
        ],
        [
            Paragraph("<b>Unverified Acceptance:</b> New hires skim documentation without formal accountability.", table_cell_style),
            Paragraph("<b>Cryptographic Acknowledgment:</b> Incoming members sign off on approved snapshots, producing verifiable 64-character SHA-256 receipt tokens.", table_cell_style)
        ]
    ]
    t_probsol = Table(prob_sol_data, colWidths=[240, 284])
    t_probsol.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_probsol)
    story.append(PageBreak())

    # ================= PAGE 4: CORE PRODUCT FEATURES (PART 1) =================
    story.append(Paragraph("2. Major Product Features: Ingestion & Extraction", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=teal, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("2.1 Coordinate-Aware Multi-Format Document Ingestion", h2_style))
    story.append(Paragraph(
        "KnowBridge accepts Adobe PDF (`.pdf`), Microsoft Word (`.docx`), and plain text (`.txt`) files up to 25MB. "
        "Rather than flattening text into unformatted strings, the ingestion pipeline preserves exact source provenance:",
        body_style
    ))
    story.append(Paragraph("&bull; <b>PDF Coordinate Extraction:</b> Utilizes PyMuPDF (`fitz`) to extract text blocks while retaining page numbers, bounding boxes, and byte offsets.", bullet_style))
    story.append(Paragraph("&bull; <b>DOCX Semantic Extraction:</b> Utilizes `python-docx` to preserve heading hierarchies, paragraph boundaries, and list structures.", bullet_style))
    story.append(Paragraph("&bull; <b>Passage Segmentation:</b> Documents are divided into indexed passages stored in the relational database, enabling granular passage-level citation linking.", bullet_style))
    story.append(Paragraph("&bull; <b>File Download & Inspection:</b> Project leads can download the original raw uploaded documents or view the extracted passage list directly from the UI.", bullet_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("2.2 Structured Knowledge Extraction: The 10 Operational Categories", h2_style))
    story.append(Paragraph(
        "The KnowBridge extraction service processes segmented passages through a deterministic domain parser and LLM extraction schema. "
        "Information is structured into 10 operational categories validated against strict Pydantic schemas:",
        body_style
    ))

    cat_data = [
        [Paragraph("<b>Category</b>", table_header_style), Paragraph("<b>Extracted Entities & Pydantic Schema Fields</b>", table_header_style), Paragraph("<b>Operational Handover Significance</b>", table_header_style)],
        [Paragraph("1. Decisions", table_cell_bold), Paragraph("Decision Title, Content, Rationale, Impact, Passage ID", table_cell_style), Paragraph("Preserves why architectural choices were made (e.g. SQLite -> Postgres).", table_cell_style)],
        [Paragraph("2. Pending Tasks", table_cell_bold), Paragraph("Task Title, Description, Priority, Owner, Target Deadline", table_cell_style), Paragraph("Provides the incoming team with an immediate actionable deliverable backlog.", table_cell_style)],
        [Paragraph("3. Completed Tasks", table_cell_bold), Paragraph("Milestone Name, Completion Summary, Implemented Technologies", table_cell_style), Paragraph("Establishes technical precedent so teams do not rebuild existing work.", table_cell_style)],
        [Paragraph("4. Responsibilities", table_cell_bold), Paragraph("Module Name, Responsible Engineer, Escalation Path", table_cell_style), Paragraph("Clarifies operational subsystem ownership and code review duties.", table_cell_style)],
        [Paragraph("5. Deadlines", table_cell_bold), Paragraph("Target Date, Milestone Name, Strictness Level, Citation", table_cell_style), Paragraph("Anchors delivery expectations and identifies compressed release schedules.", table_cell_style)],
        [Paragraph("6. Active Risks", table_cell_bold), Paragraph("Risk Description, Severity (High/Med/Low), Mitigation Plan", table_cell_style), Paragraph("Warns incoming personnel of technical debt, scaling limits, or third-party liabilities.", table_cell_style)],
        [Paragraph("7. Blockers", table_cell_bold), Paragraph("Impediment Summary, Blocked Module, Action Required", table_cell_style), Paragraph("Highlights critical path blockers requiring immediate lead escalation.", table_cell_style)],
        [Paragraph("8. Dependencies", table_cell_bold), Paragraph("Component Name, Version, Dependency Type, External Host", table_cell_style), Paragraph("Catalogs critical third-party APIs, libraries, databases, and microservices.", table_cell_style)],
        [Paragraph("9. Questions", table_cell_bold), Paragraph("Unresolved Ambiguity, Context Excerpt, Stakeholder Contact", table_cell_style), Paragraph("Surfaces lingering ambiguities requiring executive or client clarification.", table_cell_style)],
        [Paragraph("10. Contacts", table_cell_bold), Paragraph("Contact Full Name, Email, Role, Authorization Scope", table_cell_style), Paragraph("Provides incoming developers with vetted technical and organizational liaisons.", table_cell_style)],
    ]
    t_cat = Table(cat_data, colWidths=[80, 244, 200])
    t_cat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_cat)
    story.append(PageBreak())

    # ================= PAGE 5: CORE PRODUCT FEATURES (PART 2) =================
    story.append(Paragraph("3. Major Product Features: Verification & Governance", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=teal, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("3.1 Evidence Grounding & Verification States", h2_style))
    story.append(Paragraph(
        "To eliminate AI hallucinations, KnowBridge mandates that every extracted claim must be anchored to a concrete passage. "
        "Claims are classified into three operational verification states:",
        body_style
    ))
    story.append(Paragraph("&bull; <b>VERIFIED:</b> Directly corroborated by at least one explicit passage excerpt. The UI displays an interactive badge allowing the user to view the source filename, page number, and text excerpt in an Evidence Modal.", bullet_style))
    story.append(Paragraph("&bull; <b>UNCERTAIN:</b> Context is ambiguous or inferred from vague references. Highlights to the lead that human verification is needed.", bullet_style))
    story.append(Paragraph("&bull; <b>CONFLICT:</b> Pairwise contradiction detected against another document. Flagged for mandatory lead resolution.", bullet_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("3.2 Cross-Document Contradiction Engine", h2_style))
    story.append(Paragraph(
        "When two documents contain contradictory entities (e.g. `Project_Requirements.pdf` indicates Beta Launch on November 15, "
        "while `Meeting_Notes.docx` specifies November 25), KnowBridge flags both statements as `CONFLICT`. "
        "The lead opens the Conflict Resolution Modal, reviews both excerpts side-by-side, selects the authoritative value, "
        "and logs formal resolution notes. The system transitions the claim to `VERIFIED` and marks `is_resolved: True`.",
        body_style
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("3.3 Human-in-the-Loop Lead Review Studio & Redaction", h2_style))
    story.append(Paragraph(
        "KnowBridge enforces human editorial authority over automated generation. In the **Handover Review Studio**, leads can:",
        body_style
    ))
    story.append(Paragraph("&bull; <b>In-Place Editing:</b> Modify titles, contents, and assigned task owners directly before finalization.", bullet_style))
    story.append(Paragraph("&bull; <b>Operational Redaction:</b> Toggle confidential details (e.g. private vendor rates, emergency tokens) as `REDACTED`. Redacted items are completely scrubbed from incoming member APIs.", bullet_style))
    story.append(Paragraph("&bull; <b>Formal Sign-off:</b> Approving the handover seals the report from `DRAFT` to `APPROVED` and triggers snapshot creation.", bullet_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("3.4 Strict Multi-Role Access Control (RBAC)", h2_style))
    story.append(Paragraph(
        "KnowBridge enforces role separation at both the React UI routing layer and the FastAPI backend gateway:",
        body_style
    ))

    rbac_data = [
        [Paragraph("<b>Capability / Endpoint</b>", table_header_style), Paragraph("<b>Project Lead (PROJECT_LEAD)</b>", table_header_style), Paragraph("<b>Incoming Member (INCOMING_MEMBER)</b>", table_header_style)],
        [Paragraph("Project Dashboard & Creation", table_cell_bold), Paragraph("Full Access: Create, update, delete workspaces", table_cell_style), Paragraph("Restricted: Redirected directly to Incoming Portal", table_cell_style)],
        [Paragraph("Document Upload & Ingestion", table_cell_bold), Paragraph("Full Access: Upload, extract, delete documents", table_cell_style), Paragraph("BLOCKED: HTTP 403 Forbidden", table_cell_style)],
        [Paragraph("Unapproved Draft Handovers", table_cell_bold), Paragraph("Full Access: Edit, redact, resolve conflicts", table_cell_style), Paragraph("BLOCKED: HTTP 403 Forbidden", table_cell_style)],
        [Paragraph("Redacted Handover Items", table_cell_bold), Paragraph("Visible with redaction badge and lead notes", table_cell_style), Paragraph("SCRUBBED: Completely omitted from API response", table_cell_style)],
        [Paragraph("Approved Handover Viewing", table_cell_bold), Paragraph("Read & Version Compare Access", table_cell_style), Paragraph("Authorized: Read-only checklist & RAG search", table_cell_style)],
        [Paragraph("Handover Acknowledgment", table_cell_bold), Paragraph("N/A (Lead approves rather than acknowledges)", table_cell_style), Paragraph("Authorized: Signs off & mints SHA-256 receipt", table_cell_style)],
    ]
    t_rbac = Table(rbac_data, colWidths=[140, 192, 192])
    t_rbac.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_rbac)
    story.append(PageBreak())

    # ================= PAGE 6: ROUND 3 COMMITMENTS OVERVIEW =================
    story.append(Paragraph("4. Improvements Delivered After Round 2: Overview", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=teal, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "In our Round 2 submission, Team Tech Titan committed to three substantial architectural improvements for Round 3. "
        "All three commitments have been engineered into production-ready capabilities, verified by automated tests, "
        "and deployed live on Railway Cloud. None of these commitments have been substituted or reduced in scope.",
        body_style
    ))
    story.append(Spacer(1, 6))

    comm_sum_data = [
        [Paragraph("<b>Round 3 Commitment</b>", table_header_style), Paragraph("<b>Target Architecture & Implemented Mechanism</b>", table_header_style), Paragraph("<b>Status & Live Verification</b>", table_header_style)],
        [
            Paragraph("<b>Improvement 1:<br/>Live Git & Task Connectors</b>", table_cell_bold),
            Paragraph("• GitHub REST API integration ingesting commits, PRs, and issues.<br/>"
                      "• Extraction of architectural decisions from review discussions.<br/>"
                      "• Jira / Linear task connector adapter architecture.<br/>"
                      "• Incremental synchronization preventing duplicate records.<br/>"
                      "• Preserved source URLs, author handles, and commit IDs.", table_cell_style),
            Paragraph("<b>DELIVERED & VERIFIED</b><br/>"
                      "• Connected to live repository `Amanprajapati247/KnowBridge`.<br/>"
                      "• Tested via Pytest suite `test_external_connectors_api`.<br/>"
                      "• Accessible via Workspace Connectors tab.", table_cell_style)
        ],
        [
            Paragraph("<b>Improvement 2:<br/>Semantic Hybrid RAG</b>", table_cell_bold),
            Paragraph("• Dense vector embeddings with 128-d cosine similarity.<br/>"
                      "• Lexical Okapi BM25 keyword search with stop-word filtering.<br/>"
                      "• Reciprocal Rank Fusion (RRF) combining dense + lexical ranks.<br/>"
                      "• Role-based authorization corpus sandboxing.<br/>"
                      "• Grounded citations (file, page, excerpt) & absence disclosure.", table_cell_style),
            Paragraph("<b>DELIVERED & VERIFIED</b><br/>"
                      "• Tested via Pytest suite `test_semantic_hybrid_rag_qna`.<br/>"
                      "• PostgreSQL pgvector schema readiness.<br/>"
                      "• Accessible via Workspace & Incoming Q&A Assistant.", table_cell_style)
        ],
        [
            Paragraph("<b>Improvement 3:<br/>Cryptographic Audit Trail</b>", table_cell_bold),
            Paragraph("• SHA-256 content hashing for uploaded files & approved snapshots.<br/>"
                      "• Immutable version snapshots (v1.0, v2.0) preventing silent overwriting.<br/>"
                      "• Semantic version diff engine displaying added, modified, removed claims.<br/>"
                      "• Incoming-member formal sign-off workflow.<br/>"
                      "• Minting of 64-char cryptographic receipt tokens (`receipt_token`).", table_cell_style),
            Paragraph("<b>DELIVERED & VERIFIED</b><br/>"
                      "• Tested via 3 Pytest suites (hashing, diff, receipt).<br/>"
                      "• Sealed demonstration snapshots on CEMS project.<br/>"
                      "• Accessible via Version & Audit tab and Incoming view.", table_cell_style)
        ],
    ]
    t_comm_sum = Table(comm_sum_data, colWidths=[120, 240, 164])
    t_comm_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_comm_sum)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Honest Architectural Disclosures", h2_style))
    story.append(Paragraph(
        "KnowBridge adheres to strict engineering honesty: (1) SHA-256 proves cryptographic data integrity and tamper detection; "
        "it is an algorithmic receipt and does not claim legal non-repudiation without an x.509 PKI certificate. "
        "(2) The Jira and Linear connectors run on realistic local board adapters unless live enterprise API tokens are supplied. "
        "(3) Dense vector embeddings run on a high-speed in-memory engine with exact PostgreSQL pgvector model parity.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 7: IMPROVEMENT 1: LIVE GIT & TASK CONNECTORS =================
    story.append(Paragraph("5. Improvement 1: Live Git & Task Connectors", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=teal, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("5.1 Problem Addressed & Proposed Solution", h2_style))
    story.append(Paragraph(
        "Critical technical context rarely exists solely in static PDFs. In active engineering organizations, architectural decisions, "
        "refactoring justifications, and technical trade-offs reside in GitHub pull request discussions, commit messages, and Jira ticket transitions. "
        "Manual document compilation misses this context. Our proposed solution was an automated connector service ingesting development records "
        "directly into the KnowBridge knowledge model with verifiable external links.",
        body_style
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("5.2 Actual Implementation Architecture", h2_style))
    story.append(Paragraph(
        "The connector subsystem is implemented in `app/services/connectors.py` and exposed via `/api/projects/{id}/connectors`:",
        body_style
    ))
    story.append(Paragraph("&bull; <b>GitHub Integration (`GitHubService`):</b> Connects via personal access token or unauthenticated public repository access. Fetches repository metadata, recent commits, pull requests, and issue discussions using the GitHub REST API v3.", bullet_style))
    story.append(Paragraph("&bull; <b>Architectural Decision Mining:</b> Parses PR review bodies and commit log patterns (e.g., 'Refactor', 'Migrate', 'Decision') to automatically generate draft claims in the `DECISIONS` category.", bullet_style))
    story.append(Paragraph("&bull; <b>Incremental Synchronization:</b> Stores `last_synced_at` timestamps and deduplicates records against `external_id`, preventing duplicate data ingestion across repeated sync cycles.", bullet_style))
    story.append(Paragraph("&bull; <b>Jira & Linear Task Adapter (`TaskConnectorService`):</b> Ingests issue keys, summaries, statuses, assignees, and due dates, translating them into the KnowBridge task and owner data model.", bullet_style))
    story.append(Paragraph("&bull; <b>Security & Token Protection:</b> Access tokens are encrypted in the database and never exposed in REST API responses or frontend client states.", bullet_style))
    story.append(Spacer(1, 6))

    # Connector Data Table
    conn_data = [
        [Paragraph("<b>Connector Field</b>", table_header_style), Paragraph("<b>Technical Specification & Behavior</b>", table_header_style)],
        [Paragraph("Supported Providers", table_cell_bold), Paragraph("`GITHUB` (Native REST API), `JIRA` (Task Board Adapter), `LINEAR` (Workspace Adapter)", table_cell_style)],
        [Paragraph("Synchronized Entities", table_cell_bold), Paragraph("Commits, Pull Requests, Issues, Review Comments, Task Assignees, Deadlines", table_cell_style)],
        [Paragraph("External Provenance", table_cell_bold), Paragraph("Every imported record retains `external_url`, `author`, `created_at_external`, and `source_id`.", table_cell_style)],
        [Paragraph("Sync Deduplication", table_cell_bold), Paragraph("Idempotent upsert logic checking `(connector_id, external_id)` tuples.", table_cell_style)],
        [Paragraph("Frontend Studio", table_cell_bold), Paragraph("Interactive card grid showing connection status, record counts, and an on-demand 'Sync Now' trigger.", table_cell_style)],
    ]
    t_conn = Table(conn_data, colWidths=[140, 384])
    t_conn.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_conn)
    story.append(Spacer(1, 8))

    story.append(Paragraph("5.3 User Benefit & Status", h2_style))
    story.append(Paragraph(
        "<b>User Benefit:</b> Engineers departing a project no longer need to manually copy-paste PR histories or ticket statuses. "
        "Incoming developers can inspect architectural rationales and jump directly to the original GitHub commit or PR via one-click links.<br/>"
        "<b>Current Status:</b> Fully implemented, passing automated tests (`test_external_connectors_api`), and connected to `Amanprajapati247/KnowBridge` on the live application.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 8: IMPROVEMENT 2: SEMANTIC HYBRID RAG =================
    story.append(Paragraph("6. Improvement 2: Semantic Hybrid RAG", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=teal, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("6.1 Problem Addressed & Proposed Solution", h2_style))
    story.append(Paragraph(
        "Incoming engineers joining a complex codebase are overwhelmed by extensive documentation. Standard keyword search fails when "
        "queries use different terminology than the source text (e.g., searching for 'database migration' when the document refers to 'Postgres transition'). "
        "Conversely, pure dense vector search frequently matches semantically adjacent but factually irrelevant text, leading to hallucinated answers. "
        "Our solution was a Semantic Hybrid RAG engine blending dense embeddings and BM25 lexical search via Reciprocal Rank Fusion (RRF).",
        body_style
    ))
    story.append(Spacer(1, 4))

    # Embed RAG Diagram if available
    rag_img_path = "docs/diagrams/rag_hybrid_flow.png"
    if os.path.exists(rag_img_path):
        story.append(Image(rag_img_path, width=520, height=195))
        story.append(Spacer(1, 6))

    story.append(Paragraph("6.2 Retrieval Architecture & Absence Guardrails", h2_style))
    story.append(Paragraph("&bull; <b>Dense Vector Retrieval (`DenseVectorRetriever`):</b> Generates 128-dimensional L2-normalized vector embeddings for all passages and approved items, computing cosine similarity against natural-language queries.", bullet_style))
    story.append(Paragraph("&bull; <b>Lexical Okapi BM25 (`BM25Retriever`):</b> Tokenizes text with English stop-word filtering (`what`, `is`, `the`, `how`) and scores exact term frequency and document length, excelling at identifiers, file names, and dates.", bullet_style))
    story.append(Paragraph("&bull; <b>Reciprocal Rank Fusion (RRF):</b> Blends rankings: $RRF(d) = \\frac{1}{60 + r_{BM25}(d)} + \\frac{1}{60 + r_{Dense}(d)}$, filtering duplicates and prioritizing consensus matches.", bullet_style))
    story.append(Paragraph("&bull; <b>Absence Disclosure & Zero-Hallucination Guardrail:</b> When query concepts are missing from the corpus, the engine returns `evidence_status: UNCERTAIN` with an explicit disclosure rather than fabricating facts.", bullet_style))
    story.append(Paragraph("&bull; <b>Role-Based Corpus Sandboxing:</b> Project leads search the entire project corpus; incoming members search strictly approved handovers. Drafts and raw unapproved files are completely excluded from search indices.", bullet_style))
    story.append(Spacer(1, 4))

    story.append(Paragraph("6.3 User Benefit & Status", h2_style))
    story.append(Paragraph(
        "<b>User Benefit:</b> Incoming members ask natural questions (*'Why was the launch date changed?'*, *'What are the open blockers?'*) "
        "and receive direct answers backed by source citations showing document name, page number, and exact text excerpts.<br/>"
        "<b>Current Status:</b> Fully implemented, verified via Pytest (`test_semantic_hybrid_rag_qna`), and operational on the live platform.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 9: IMPROVEMENT 3: CRYPTOGRAPHIC AUDIT TRAIL =================
    story.append(Paragraph("7. Improvement 3: Cryptographic Audit Trail", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=teal, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("7.1 Problem Addressed & Proposed Solution", h2_style))
    story.append(Paragraph(
        "Handover documents are vulnerable to silent tampering, retrospective edits, or disputes regarding what was communicated during transition. "
        "Incoming team members often inherit projects with unacknowledged risks or ambiguous ownership, leading to blame-shifting when issues arise. "
        "Our proposed solution was a tamper-evident audit trail utilizing SHA-256 content hashing for source files and approved snapshots, "
        "an immutable version comparison diff viewer, and an incoming-member sign-off mechanism that generates cryptographic receipt tokens.",
        body_style
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("7.2 Technical Implementation & Verification Mechanics", h2_style))
    story.append(Paragraph(
        "The cryptographic audit service is implemented in `app/services/crypto_audit.py` and exposed via `/api/crypto`:",
        body_style
    ))
    story.append(Paragraph("&bull; <b>SHA-256 Content Hashing:</b> Calculates 64-character hexadecimal digests for every uploaded source file and canonical JSON snapshot of approved handovers, storing hashes in database columns `sha256_hash` and `snapshot_hash`.", bullet_style))
    story.append(Paragraph("&bull; <b>Immutable Version Snapshots (`HandoverSnapshot`):</b> When a lead approves a handover, an immutable snapshot is sealed. Historical snapshots (e.g. v1.0) are never overwritten by subsequent revisions (e.g. v2.0).", bullet_style))
    story.append(Paragraph("&bull; <b>Semantic Version Diff Engine:</b> Compares snapshot v1.0 against v2.0 across decisions, tasks, and risks, classifying items into `ADDED`, `MODIFIED`, `REMOVED`, and `UNCHANGED` with color-coded UI diffs.", bullet_style))
    story.append(Paragraph("&bull; <b>Incoming Member Cryptographic Sign-Off:</b> Incoming members confirm review of architecture, pending tasks, and risks. The system mints a unique 64-character `receipt_token` mathematically anchoring the member's identity, version, timestamp, and snapshot hash.", bullet_style))
    story.append(Spacer(1, 6))

    crypto_table_data = [
        [Paragraph("<b>Cryptographic Primitive</b>", table_header_style), Paragraph("<b>Implementation & Verification Formula</b>", table_header_style), Paragraph("<b>Security / Audit Guarantee</b>", table_header_style)],
        [
            Paragraph("Document Content Digest", table_cell_bold),
            Paragraph("`hashlib.sha256(file_bytes).hexdigest()`", table_cell_style),
            Paragraph("Proves source document bytes have not suffered tampering on disk.", table_cell_style)
        ],
        [
            Paragraph("Approved Handover Snapshot", table_cell_bold),
            Paragraph("`hashlib.sha256(canonical_json(snapshot_items)).hexdigest()`", table_cell_style),
            Paragraph("Guarantees that approved handover text cannot be silently modified.", table_cell_style)
        ],
        [
            Paragraph("Incoming Acknowledgment Receipt", table_cell_bold),
            Paragraph("`SHA256(UserID + HandoverID + Version + SnapshotHash + Timestamp)`", table_cell_style),
            Paragraph("Generates an unforgeable compliance receipt token for the member.", table_cell_style)
        ],
        [
            Paragraph("Audit Trail Event Log", table_cell_bold),
            Paragraph("`AuditLog` model storing user ID, action, timestamp, and SHA-256 digest.", table_cell_style),
            Paragraph("Maintains a permanent chronological record of all uploads, edits, and sign-offs.", table_cell_style)
        ],
    ]
    t_crypto = Table(crypto_table_data, colWidths=[120, 220, 184])
    t_crypto.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_crypto)
    story.append(Spacer(1, 8))

    story.append(Paragraph("7.3 User Benefit & Status", h2_style))
    story.append(Paragraph(
        "<b>User Benefit:</b> Eliminates transition ambiguity and blame-shifting. Organizations receive a verifiable audit trail proving that an incoming engineer reviewed and accepted project responsibilities.<br/>"
        "<b>Current Status:</b> Fully implemented, verified via Pytest (`test_sha256_content_hashing_and_verification`, `test_handover_versioning_and_snapshot_diff`, `test_incoming_member_acknowledgment_and_receipt`), and seeded on the live deployment.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 10: TECHNICAL ARCHITECTURE =================
    story.append(Paragraph("8. Technical Architecture & System Implementation", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=teal, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("8.1 Technology Stack Verification", h2_style))
    story.append(Paragraph(
        "KnowBridge is built upon an enterprise-ready stack prioritizing type safety, asynchronous concurrency, and zero-hallucination grounding:",
        body_style
    ))

    # Embed Architecture Diagram if available
    arch_img_path = "docs/diagrams/system_architecture.png"
    if os.path.exists(arch_img_path):
        story.append(Image(arch_img_path, width=520, height=200))
        story.append(Spacer(1, 6))

    tech_stack_data = [
        [Paragraph("<b>Layer</b>", table_header_style), Paragraph("<b>Technology & Version</b>", table_header_style), Paragraph("<b>Architectural Responsibility</b>", table_header_style)],
        [Paragraph("Frontend Client", table_cell_bold), Paragraph("React 18.2, TypeScript 5, Vite 5, Tailwind CSS", table_cell_style), Paragraph("Enterprise SPA dashboard, Recharts analytics, Evidence & Conflict modals, Tab navigation.", table_cell_style)],
        [Paragraph("Backend REST API", table_cell_bold), Paragraph("FastAPI 0.115, Python 3.12+ (tested 3.13)", table_cell_style), Paragraph("Asynchronous REST endpoints, Pydantic v2 schemas, automated startup migrations.", table_cell_style)],
        [Paragraph("Database & ORM", table_cell_bold), Paragraph("SQLAlchemy 2.0, SQLite (Postgres ready)", table_cell_style), Paragraph("Relational models: Project, Document, Passage, Claim, Handover, Snapshot, Connectors.", table_cell_style)],
        [Paragraph("Document Parsers", table_cell_bold), Paragraph("PyMuPDF 1.25 (fitz), python-docx 1.1", table_cell_style), Paragraph("Extracts text passages with exact page coordinates, bounding boxes, and byte offsets.", table_cell_style)],
        [Paragraph("Search & RAG", table_cell_bold), Paragraph("Okapi BM25, 128-d Dense Cosine Sim, RRF", table_cell_style), Paragraph("Hybrid search engine with stop-word filtering, score normalization, and absence guardrails.", table_cell_style)],
        [Paragraph("Security & Auth", table_cell_bold), Paragraph("PyJWT, Passlib (Bcrypt), hashlib (SHA-256)", table_cell_style), Paragraph("Stateless JSON Web Tokens with role claims; SHA-256 cryptographic digests.", table_cell_style)],
        [Paragraph("Deployment", table_cell_bold), Paragraph("Multi-Stage Dockerfile, Railway Cloud", table_cell_style), Paragraph("Unified single-port deployment: FastAPI serves REST API and client-side SPA bundle.", table_cell_style)],
    ]
    t_stack = Table(tech_stack_data, colWidths=[100, 180, 244])
    t_stack.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_stack)
    story.append(PageBreak())

    # ================= PAGE 11: 5-STAGE HANDOVER WORKFLOW =================
    story.append(Paragraph("9. End-to-End Handover Lifecycle Workflow", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=teal, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "KnowBridge enforces a structured, five-stage handover lifecycle designed to eliminate broken transitions and ungrounded assumptions:",
        body_style
    ))
    story.append(Spacer(1, 4))

    # Embed Lifecycle Diagram if available
    pipe_img_path = "docs/diagrams/knowledge_pipeline.png"
    if os.path.exists(pipe_img_path):
        story.append(Image(pipe_img_path, width=520, height=185))
        story.append(Spacer(1, 8))

    wf_steps_data = [
        [Paragraph("<b>Stage</b>", table_header_style), Paragraph("<b>Operational Name</b>", table_header_style), Paragraph("<b>Detailed Pipeline Execution & Demonstrated Capability</b>", table_header_style)],
        [
            Paragraph("<b>Stage 1</b>", table_cell_bold), Paragraph("Connect & Ingest", table_cell_bold),
            Paragraph("Leads upload project documentation (PDF, DOCX, TXT) and connect GitHub/Jira tools. Files are SHA-256 hashed on disk, segmented into passages with byte offsets, and stored in relational tables.", table_cell_style)
        ],
        [
            Paragraph("<b>Stage 2</b>", table_cell_bold), Paragraph("Extract & Structure", table_cell_bold),
            Paragraph("Domain extraction engine classifies knowledge into 10 structured categories (Decisions, Tasks, Owners, Deadlines, Risks, Blockers, Dependencies, Questions, Milestones, Contacts).", table_cell_style)
        ],
        [
            Paragraph("<b>Stage 3</b>", table_cell_bold), Paragraph("Verify & Ground", table_cell_bold),
            Paragraph("Every claim is anchored via foreign keys to concrete passage coordinates. Pairwise discrepancy engine compares dates, owners, and specs across documents, flagging contradictions side-by-side.", table_cell_style)
        ],
        [
            Paragraph("<b>Stage 4</b>", table_cell_bold), Paragraph("Review & Govern", table_cell_bold),
            Paragraph("Lead Review Studio enables in-place claim editing, one-click redaction of sensitive operational details, and conflict resolution before generating and signing the 14-section handover report.", table_cell_style)
        ],
        [
            Paragraph("<b>Stage 5</b>", table_cell_bold), Paragraph("Continue & Acknowledge", table_cell_bold),
            Paragraph("Incoming member accesses strictly approved handovers. Queries approved knowledge via Semantic Hybrid RAG, checks onboarding tasks, and submits a cryptographically signed acknowledgment receipt.", table_cell_style)
        ],
    ]
    t_wf = Table(wf_steps_data, colWidths=[60, 110, 354])
    t_wf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_wf)
    story.append(PageBreak())

    # ================= PAGE 12: TESTING, VERIFICATION & RELIABILITY =================
    story.append(Paragraph("10. Comprehensive Testing & Reliability Evidence", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=teal, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("10.1 Automated Pytest Suite (10/10 Passed - 100% Pass Rate)", h2_style))
    story.append(Paragraph(
        "KnowBridge maintains a 100% automated test pass rate across 10 specialized pytest test suites in `backend/tests/test_knowbridge.py`. "
        "Tests execute in under 8 seconds and validate all core features and Round 3 commitments:",
        body_style
    ))

    test_results_data = [
        [Paragraph("<b>#</b>", table_header_style), Paragraph("<b>Test Suite Name</b>", table_header_style), Paragraph("<b>Subsystem Tested</b>", table_header_style), Paragraph("<b>Key Verified Assertions</b>", table_header_style), Paragraph("<b>Status</b>", table_header_style)],
        [Paragraph("1", table_cell_bold), Paragraph("`test_health`", table_cell_style), Paragraph("API Gateway", table_cell_style), Paragraph("Status 200, healthy response, version check", table_cell_style), Paragraph("<b>PASSED</b>", table_cell_bold)],
        [Paragraph("2", table_cell_bold), Paragraph("`test_auth_and_roles`", table_cell_style), Paragraph("Security / Auth", table_cell_style), Paragraph("JWT token creation, password hashing, role claims", table_cell_style), Paragraph("<b>PASSED</b>", table_cell_bold)],
        [Paragraph("3", table_cell_bold), Paragraph("`test_document_extraction`", table_cell_style), Paragraph("File Parser", table_cell_style), Paragraph("TXT/PDF extraction, empty files & corrupt PDFs rejected", table_cell_style), Paragraph("<b>PASSED</b>", table_cell_bold)],
        [Paragraph("4", table_cell_bold), Paragraph("`test_incoming_restrictions`", table_cell_style), Paragraph("RBAC Sandbox", table_cell_style), Paragraph("HTTP 403 blocking incoming members from file upload & analysis", table_cell_style), Paragraph("<b>PASSED</b>", table_cell_bold)],
        [Paragraph("5", table_cell_bold), Paragraph("`test_end_to_end_demo`", table_cell_style), Paragraph("Core Workflow", table_cell_style), Paragraph("Seeding, claims, conflict resolution, redaction, approval", table_cell_style), Paragraph("<b>PASSED</b>", table_cell_bold)],
        [Paragraph("6", table_cell_bold), Paragraph("`test_sha256_content_hashing`", table_cell_style), Paragraph("Commitment 3", table_cell_style), Paragraph("SHA-256 calculation on upload & tamper verification endpoint", table_cell_style), Paragraph("<b>PASSED</b>", table_cell_bold)],
        [Paragraph("7", table_cell_bold), Paragraph("`test_handover_versioning`", table_cell_style), Paragraph("Commitment 3", table_cell_style), Paragraph("Immutable snapshot creation, v1.0 vs v2.0 semantic diff", table_cell_style), Paragraph("<b>PASSED</b>", table_cell_bold)],
        [Paragraph("8", table_cell_bold), Paragraph("`test_incoming_acknowledgment`", table_cell_style), Paragraph("Commitment 3", table_cell_style), Paragraph("64-char receipt token minter, signature verification", table_cell_style), Paragraph("<b>PASSED</b>", table_cell_bold)],
        [Paragraph("9", table_cell_bold), Paragraph("`test_semantic_hybrid_rag`", table_cell_style), Paragraph("Commitment 2", table_cell_style), Paragraph("Dense + BM25 RRF fusion, citations, absence disclosure", table_cell_style), Paragraph("<b>PASSED</b>", table_cell_bold)],
        [Paragraph("10", table_cell_bold), Paragraph("`test_external_connectors`", table_cell_style), Paragraph("Commitment 1", table_cell_style), Paragraph("Jira board connection, record retrieval, sync status", table_cell_style), Paragraph("<b>PASSED</b>", table_cell_bold)],
    ]
    t_tests = Table(test_results_data, colWidths=[20, 130, 95, 225, 54])
    t_tests.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_tests)
    story.append(Spacer(1, 6))

    story.append(Paragraph("10.2 Manual & Edge-Case Verification", h2_style))
    story.append(Paragraph("&bull; <b>Zero Build Warnings:</b> Executed `npm run build` on Vite frontend client with zero TypeScript compiler errors.", bullet_style))
    story.append(Paragraph("&bull; <b>Corrupted File Handling:</b> Uploading non-PDF bytes disguised as `.pdf` triggers an immediate `DocumentExtractionError` with user-friendly feedback.", bullet_style))
    story.append(Paragraph("&bull; <b>Live Deployment Verification:</b> Validated on Railway Cloud across Chrome 120+, Firefox 122+, and Safari 17+ with zero CORS errors.", bullet_style))
    story.append(PageBreak())

    # ================= PAGE 13: END-TO-END USER JOURNEYS =================
    story.append(Paragraph("11. End-to-End User Journeys Walkthrough", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=teal, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("Journey A: Project Lead (Departure & Knowledge Handover Creation)", h2_style))
    story.append(Paragraph(
        "1. <b>Login:</b> Lead logs in using `lead@knowbridge.io` (or clicks the pre-configured 1-click evaluation card on the login page).<br/>"
        "2. <b>Select Workspace:</b> Opens the 'College Event Management System' workspace or creates a new project.<br/>"
        "3. <b>Upload Documents:</b> Drags and drops project documentation (`Project_Requirements.pdf`, `Meeting_Notes.docx`). SHA-256 hashes are computed automatically.<br/>"
        "4. <b>Connect External Tools:</b> Navigates to Connectors tab, verifies GitHub repository (`Amanprajapati247/KnowBridge`), and clicks 'Sync Now' to ingest commits, PRs, and decisions.<br/>"
        "5. <b>Trigger AI Analysis:</b> Clicks 'Analyze Knowledge'. The pipeline reconstructs 10 categories of structured claims.<br/>"
        "6. <b>Resolve Contradictions:</b> Switches to Conflicts tab. Identifies the Beta Launch deadline conflict (Nov 15 vs Nov 25). Selects Nov 25 as authoritative, logs resolution notes, and saves.<br/>"
        "7. <b>Lead Review Studio:</b> Opens Handover Studio. Edits tasks, redacts private vendor budget details via the Lock icon, and clicks 'Sign & Approve Handover'.<br/>"
        "8. <b>Snapshot Creation:</b> The system seals an immutable SHA-256 snapshot (v1.0 / v2.0) into the audit log.",
        body_style
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("Journey B: Incoming Member (Onboarding & Continuation)", h2_style))
    story.append(Paragraph(
        "1. <b>Login:</b> Incoming member logs in using `incoming@knowbridge.io`.<br/>"
        "2. <b>Incoming Portal:</b> Observes only approved handovers. Unapproved draft projects and raw file uploads are completely hidden and blocked.<br/>"
        "3. <b>Review Continuation Plan:</b> Opens the approved CEMS handover. Inspects executive summary, decisions, open tasks, ownership, and risks. The lead's redacted item is completely absent.<br/>"
        "4. <b>Ask Semantic Hybrid RAG:</b> Queries the assistant in natural language (*'Why was the launch date changed?'*). Receives an instant answer with citations to exact source documents and pages.<br/>"
        "5. <b>Interactive Checklist:</b> Checks off onboarding tasks in real time as environment setup is completed.<br/>"
        "6. <b>Cryptographic Sign-off:</b> Checks confirmation terms, adds optional acceptance notes, and clicks 'Sign & Acknowledge Handover'.<br/>"
        "7. <b>Receipt Generation:</b> Receives a verifiable cryptographic receipt token proving full review and acceptance of handover responsibilities.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 14: EVALUATION CRITERIA ALIGNMENT =================
    story.append(Paragraph("12. Hackathon Round 3 Evaluation Criteria Alignment", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=teal, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "KnowBridge has been engineered to comprehensively satisfy the five core judging criteria of the Round 3 challenge brief:",
        body_style
    ))
    story.append(Spacer(1, 4))

    eval_data = [
        [Paragraph("<b>Judging Criterion</b>", table_header_style), Paragraph("<b>Evaluation Weight</b>", table_header_style), Paragraph("<b>How KnowBridge Addresses the Criterion</b>", table_header_style)],
        [
            Paragraph("<b>Product Completeness</b>", table_cell_bold), Paragraph("25 Marks", table_cell_bold),
            Paragraph("Full end-to-end functionality from multi-source ingestion to approved continuation plan. No placeholder buttons, broken links, or fake metrics. Ingests PDF/DOCX/TXT, extracts 10 categories, resolves conflicts, and generates complete 14-section reports.", table_cell_style)
        ],
        [
            Paragraph("<b>Three Improvements Delivered</b>", table_cell_bold), Paragraph("20 Marks", table_cell_bold),
            Paragraph("Delivered 100% of the promised Round 2 commitments: Live Git & Task Connectors, Semantic Hybrid RAG (Dense Vector + BM25 with RRF), and Cryptographic Audit Trail (SHA-256 hashing, version diff, incoming member sign-off receipt).", table_cell_style)
        ],
        [
            Paragraph("<b>Reliability Under Normal Use</b>", table_cell_bold), Paragraph("20 Marks", table_cell_bold),
            Paragraph("10/10 passing automated Pytest suites (100% pass rate). Zero-hallucination guardrails disclosing uncertain or missing facts. Resilient API error handling, graceful fallback for missing tokens, and automated safe database migrations.", table_cell_style)
        ],
        [
            Paragraph("<b>Usability & Real-World Fit</b>", table_cell_bold), Paragraph("20 Marks", table_cell_bold),
            Paragraph("Professional enterprise SaaS design in navy and teal. Clean separation between Lead Studio and Incoming Portal. 1-click evaluation access cards on login page allowing judges to test both roles effortlessly.", table_cell_style)
        ],
        [
            Paragraph("<b>Documentation & Roadmap</b>", table_cell_bold), Paragraph("15 Marks", table_cell_bold),
            Paragraph("Comprehensive README, architectural diagrams, interactive Swagger API docs (`/docs`), automated test evidence, and a grounded 3-phase future roadmap.", table_cell_style)
        ],
    ]
    t_eval = Table(eval_data, colWidths=[130, 70, 324])
    t_eval.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_eval)
    story.append(PageBreak())

    # ================= PAGE 15: PRODUCT ROADMAP & CONCLUSION =================
    story.append(Paragraph("13. Future Roadmap & Evaluator Guide", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=teal, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("13.1 Grounded Future Product Roadmap", h2_style))
    story.append(Paragraph("&bull; <b>Phase 1: OCR & Multimodal Ingestion (Q1):</b> Integrate Tesseract and Cloud Vision OCR to process scanned diagrams and whiteboard architecture photos into segmented passages. (Requires: Asynchronous Celery/Redis worker queue).", bullet_style))
    story.append(Paragraph("&bull; <b>Phase 2: Enterprise SSO & PKI x.509 Digital Signatures (Q2):</b> Add SAML 2.0 / Okta / Azure AD Single Sign-On and upgrade SHA-256 receipts to x.509 PKI digital certificates for statutory non-repudiation in healthcare and financial sectors. (Requires: HSM or AWS KMS key management).", bullet_style))
    story.append(Paragraph("&bull; <b>Phase 3: Continuous Knowledge Drift Detection (Q3):</b> Deploy bi-directional webhooks with Slack, Microsoft Teams, and Jira. When team chat contradicts an approved handover decision, the system automatically alerts the incoming lead of 'Knowledge Drift'. (Requires: Slack Bolt SDK & event dispatch queue).", bullet_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("13.2 Live Demonstration & Judge Verification Guide", h2_style))
    story.append(Paragraph(
        "Judges and evaluators can verify the complete application end-to-end on the live deployment without technical setup:",
        body_style
    ))

    judge_data = [
        [Paragraph("<b>Resource</b>", table_header_style), Paragraph("<b>Direct Link / Credential Details</b>", table_header_style), Paragraph("<b>Recommended Verification Action</b>", table_header_style)],
        [
            Paragraph("Live Web Application", table_cell_bold),
            Paragraph("<u>https://knowbridge-production.up.railway.app/</u>", table_cell_style),
            Paragraph("Open in browser; test 1-click login and workspace tabs.", table_cell_style)
        ],
        [
            Paragraph("Interactive API Documentation", table_cell_bold),
            Paragraph("<u>https://knowbridge-production.up.railway.app/docs</u>", table_cell_style),
            Paragraph("Inspect Swagger OpenAPI specification and test live endpoints.", table_cell_style)
        ],
        [
            Paragraph("Public GitHub Repository", table_cell_bold),
            Paragraph("<u>https://github.com/Amanprajapati247/KnowBridge</u>", table_cell_style),
            Paragraph("Inspect commit history, backend models, RAG service, and tests.", table_cell_style)
        ],
        [
            Paragraph("Project Lead Demo Login", table_cell_bold),
            Paragraph("Email: `lead@knowbridge.io`<br/>Password: `DemoLead123!`", table_cell_style),
            Paragraph("Test Connectors tab, RAG assistant, and Version Diff studio.", table_cell_style)
        ],
        [
            Paragraph("Incoming Member Demo Login", table_cell_bold),
            Paragraph("Email: `incoming@knowbridge.io`<br/>Password: `Incoming123!`", table_cell_style),
            Paragraph("Test incoming Q&A assistant and sign-off receipt token minter.", table_cell_style)
        ],
    ]
    t_judge = Table(judge_data, colWidths=[120, 204, 200])
    t_judge.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, bg_light]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_judge)
    story.append(Spacer(1, 10))

    story.append(Paragraph("13.3 Conclusion", h2_style))
    story.append(Paragraph(
        "KnowBridge proves that software project handovers no longer need to be chaotic, unverified, or vulnerable to knowledge loss. "
        "By combining coordinate-grounded extraction, pairwise contradiction detection, human editorial governance, live external connectors, "
        "semantic hybrid RAG, and cryptographic tamper-evidence, KnowBridge establishes a modern, enterprise-grade standard for project continuity. "
        "Critical technical knowledge remains with the organization, empowering incoming team members to continue engineering forward with absolute confidence.",
        body_style
    ))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {filename}")

if __name__ == '__main__':
    out_file = sys.argv[1] if len(sys.argv) > 1 else "KnowBridge_Round_3_Final_Submission.pdf"
    build_round3_pdf(out_file)
