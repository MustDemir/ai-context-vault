#!/usr/bin/env python3
"""Generate black-and-white thesis diagrams using Pillow.

Outputs:
  1) 03_04_methoden_framework_overview_v02.png  (Methoden-Framework, aktualisiert)
  2) 05_02_architektur_ki-fabrik-analogie_v02.png (KI-Fabrik, 3-Phasen-Lifecycle)
"""

from PIL import Image, ImageDraw, ImageFont
import os, sys

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def get_font(size):
    """Return a TrueType font; fall back to default if nothing available."""
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def get_bold_font(size):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]:
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    return get_font(size)


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY_LIGHT = (240, 240, 240)
GRAY_MID = (200, 200, 200)
GRAY_DARK = (120, 120, 120)

def draw_rect(d, x, y, w, h, fill=WHITE, outline=BLACK, lw=2):
    d.rectangle([x, y, x+w, y+h], fill=fill, outline=outline, width=lw)

def draw_rounded_rect(d, x, y, w, h, r=12, fill=WHITE, outline=BLACK, lw=2):
    d.rounded_rectangle([x, y, x+w, y+h], radius=r, fill=fill, outline=outline, width=lw)

def center_text(d, text, x, y, w, font, fill=BLACK):
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    d.text((x + (w - tw) / 2, y), text, font=font, fill=fill)

def wrap_center_text(d, text, x, y, w, font, fill=BLACK, line_spacing=4):
    """Word-wrap text centred in a box."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = d.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > w - 16:
            if current:
                lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    cy = y
    for line in lines:
        bbox = d.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        d.text((x + (w - tw) / 2, cy), line, font=font, fill=fill)
        cy += th + line_spacing
    return cy

def draw_arrow_down(d, cx, y1, y2, lw=2):
    d.line([(cx, y1), (cx, y2)], fill=BLACK, width=lw)
    d.polygon([(cx-8, y2-12), (cx+8, y2-12), (cx, y2)], fill=BLACK)

def draw_arrow_right(d, x1, cy, x2, lw=2):
    d.line([(x1, cy), (x2, cy)], fill=BLACK, width=lw)
    d.polygon([(x2-12, cy-8), (x2-12, cy+8), (x2, cy)], fill=BLACK)

# ============================================================================
# DIAGRAM 1: Methoden-Framework v02
# ============================================================================
def generate_methoden_framework(out_path):
    W, H = 2600, 1950
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    ft_title = get_bold_font(36)
    ft_sub = get_bold_font(26)
    ft_body = get_font(21)
    ft_small = get_font(18)
    ft_label = get_bold_font(21)

    # --- Title ---
    center_text(d, "Methoden-Framework: Forschungsmethode + Technische Konstruktionsmethoden", 0, 25, W, ft_title)
    center_text(d, "(aktualisiert — v02, schwarz-weiss)", 0, 70, W, ft_body, fill=GRAY_DARK)

    # ===== EBENE 1: Forschungsmethode =====
    e1_y = 110
    e1_h = 270
    draw_rect(d, 50, e1_y, W-100, e1_h, fill=GRAY_LIGHT, outline=BLACK, lw=3)
    d.text((80, e1_y+12), "EBENE 1: FORSCHUNGSMETHODE — Wie wird die Masterarbeit durchgefuehrt?", font=ft_sub, fill=BLACK)

    # Three DSR frameworks
    fw_w = 720
    fw_h = 160
    fw_y = e1_y + 60
    fw_gap = 50
    fw_x_start = (W - (3 * fw_w + 2 * fw_gap)) // 2
    frameworks = [
        ("DSR nach Hevner (2004)", "IS Research Framework\n3 Zyklen: Relevance, Design, Rigor"),
        ("DSRM nach Peffers (2007)", "6-Schritte-Prozessmodell\nproblem-centered initiation"),
        ("DSR Grid nach vom Brocke\n& Maedche (2019)", "Systematische Abdeckung\naller DSR-Dimensionen"),
    ]
    for i, (title, desc) in enumerate(frameworks):
        fx = fw_x_start + i * (fw_w + fw_gap)
        draw_rounded_rect(d, fx, fw_y, fw_w, fw_h, fill=WHITE)
        d.text((fx+20, fw_y+15), title, font=ft_label, fill=BLACK)
        d.text((fx+20, fw_y+65), desc, font=ft_body, fill=GRAY_DARK)

    # Scope note
    d.text((fw_x_start, fw_y + fw_h + 20), "Scope: Deployment- und Inference-Zyklus  |  n >= 4 Expert Reviews  |  2 Iterationen  |  NIST AI RMF (Rigor)", font=ft_body, fill=BLACK)

    # Arrow down
    draw_arrow_down(d, W//2, e1_y + e1_h, e1_y + e1_h + 40)

    # ===== EBENE 2: Technische Konstruktionsmethoden =====
    e2_y = e1_y + e1_h + 50
    col_w = 570
    col_gap = 35
    col_x_start = (W - (4 * col_w + 3 * col_gap)) // 2
    col_h = 720
    col_y = e2_y + 55
    e2_h = col_h + 80
    draw_rect(d, 50, e2_y, W-100, e2_h, fill=GRAY_LIGHT, outline=BLACK, lw=3)
    d.text((80, e2_y+12), "EBENE 2: TECHNISCHE KONSTRUKTIONSMETHODEN — Womit wird das Artefakt gebaut?", font=ft_sub, fill=BLACK)

    saeulen = [
        {
            "title": "S1: ARCHITEKTURENTWURF",
            "subtitle": "Entwurf: Schichten-/Komponentenmodell",
            "methoden": [
                "Referenzmodellierung (Entwurfsmuster)",
                "Cloud-native Architekturprinzipien",
                "Modularitaet & Loose Coupling",
                "Infrastructure-as-Code (IaC)",
            ],
            "output": "Komponenten, alle Phasen\n(DATA ... MODEL ... DEPLOY ... PROD)",
            "policy": "Pol: Strukturierung | Ansatz",
        },
        {
            "title": "S2: QUALITY-GATE-FRAMEWORK",
            "subtitle": "Kernlogik: Gate-Systematik (USP)",
            "methoden": [
                "Template-basierte Gate-Spezifikation",
                "Dimensionale Parametrisierung",
                "Pruefung: Evidenz → Entscheidung",
                "Evidence-driven Decision Logic",
            ],
            "output": "Gate Template (USP):\nTrigger | Kriterien | Evidenzartefakte\nEntscheidung | Verantwortlichkeit\nAudit Trail | Waiver-Regelung",
            "policy": "Pol: Cluster-basiert",
        },
        {
            "title": "S3: PIPELINE-INTEGRATION",
            "subtitle": "Einbettung: Automatisierte Pipeline\nmit Gates",
            "methoden": [
                "CI/CD/CT-Plattform (GitHub Actions)",
                "GitOps/ArgoCD Continuous Deployment",
                "Policy-as-Code (OPA/Rego)",
                "Automatisierter Gate Check",
            ],
            "output": "Ergebnis: Automatisierter\nPipeline-Fluss mit\nGate-Checkpoints pro Phase",
            "policy": "Pol: Stage | EVAL | DEPLOY | PROD",
        },
        {
            "title": "S4: COMPLIANCE-OP.",
            "subtitle": "Governance: EU AI Act als\nAudit Trail (USP)",
            "methoden": [
                "Regulatory-to-Technical Mapping",
                "Policy-as-Code (Art. 9-15)",
                "Continuous Compliance Monitoring",
                "Accountability-by-Design",
            ],
            "output": "Policy Engine (Compliance)\n→ Evidence Store\nAI Act: Art. 9-15 | Immutable Log\nEvidence Store (USP)",
            "policy": "Pol: Regulatorisch | Technisch\n| Strategisch",
        },
    ]

    for i, s in enumerate(saeulen):
        cx = col_x_start + i * (col_w + col_gap)
        draw_rect(d, cx, col_y, col_w, col_h, fill=WHITE, outline=BLACK, lw=2)

        # Title bar
        draw_rect(d, cx, col_y, col_w, 48, fill=GRAY_MID, outline=BLACK, lw=2)
        center_text(d, s["title"], cx, col_y+12, col_w, ft_label)

        # Subtitle
        sy = col_y + 60
        for line in s["subtitle"].split("\n"):
            d.text((cx+15, sy), line, font=ft_body, fill=GRAY_DARK)
            sy += 28

        # Methoden
        d.text((cx+15, sy + 10), "Methoden:", font=ft_label, fill=BLACK)
        my = sy + 40
        for m in s["methoden"]:
            d.text((cx+25, my), f"- {m}", font=ft_small, fill=BLACK)
            my += 30

        # Separator
        d.line([(cx+15, my+15), (cx+col_w-15, my+15)], fill=GRAY_MID, width=1)

        # Output
        d.text((cx+15, my+28), "Output:", font=ft_label, fill=BLACK)
        oy = my + 55
        for line in s["output"].split("\n"):
            d.text((cx+20, oy), line, font=ft_small, fill=BLACK)
            oy += 28

        # Policy
        d.line([(cx+15, oy+15), (cx+col_w-15, oy+15)], fill=GRAY_MID, width=1)
        py = oy + 25
        for line in s["policy"].split("\n"):
            d.text((cx+15, py), line, font=ft_small, fill=GRAY_DARK)
            py += 25

    # --- Bottom: Blueprint-Kette ---
    bp_y = col_y + col_h + 40
    draw_rect(d, 80, bp_y, W-160, 140, fill=WHITE, outline=BLACK, lw=2)
    d.text((110, bp_y+12), "ZUSAMMENFUEHRUNG — Blueprint-Ableitungskette (Kap. 4 + Kap. 5):", font=ft_label, fill=BLACK)
    chain = "EU AI Act (Art. 9-15) --> Funktionale Transformation --> Kontrollmechanismen --> Lifecycle (3 Phasen)"
    d.text((110, bp_y+48), chain, font=ft_body, fill=BLACK)
    chain2 = "--> Governance-Konsolidierung (NIST) --> Requirements-Katalog --> Design-Prinzipien"
    d.text((110, bp_y+78), chain2, font=ft_body, fill=BLACK)
    chain3 = "--> Quality Gates --> Referenzarchitektur --> PoC"
    d.text((110, bp_y+108), chain3, font=ft_body, fill=BLACK)

    # --- Legend ---
    leg_y = bp_y + 160
    items = ["S1 (Architektur)", "S2 (Gate-Framework, USP)", "S3 (Pipeline)", "S4 (Compliance, USP)"]
    d.text((80, leg_y), "Saeulen:", font=ft_label, fill=BLACK)
    lx = 220
    for item in items:
        draw_rounded_rect(d, lx, leg_y-4, 260, 32, r=8, fill=GRAY_LIGHT, outline=BLACK, lw=1)
        d.text((lx+12, leg_y+1), item, font=ft_small, fill=BLACK)
        lx += 285

    d.text((lx + 40, leg_y+1), "Artefakttyp: Model + Method + Instantiation", font=ft_small, fill=GRAY_DARK)

    # Footer
    d.text((80, H-40), "Basis: Hevner et al. (2004), Peffers et al. (2007), vom Brocke & Maedche (2019)  |  NIST AI RMF (2023)  |  EU AI Act (VO 2024/1689)", font=ft_small, fill=GRAY_DARK)

    img.save(out_path, "PNG", dpi=(300, 300))
    print(f"  -> {out_path}  ({W}x{H})")


# ============================================================================
# DIAGRAM 2: KI-Fabrik-Analogie v02 (3-Phasen-Lifecycle)
# ============================================================================
def generate_ki_fabrik(out_path):
    W, H = 2600, 2050
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    ft_title = get_bold_font(36)
    ft_sub = get_bold_font(26)
    ft_body = get_font(21)
    ft_small = get_font(18)
    ft_label = get_bold_font(21)
    ft_large = get_bold_font(28)

    # --- Title ---
    center_text(d, "Die KI-Fabrik — Referenzarchitektur als Analogie (v02)", 0, 25, W, ft_title)
    center_text(d, "Enterprise-Referenzarchitektur fuer GenAI | Quality Gates | EU AI Act | CI/CD/CT-Pipeline", 0, 72, W, ft_body, fill=GRAY_DARK)
    center_text(d, "Scope: Deployment- und Inference-Zyklus (3-Phasen-Lifecycle)", 0, 100, W, ft_body, fill=BLACK)

    # ===== AUTOMATISCHES FLIESSBAND (Pipeline) =====
    band_y = 145
    draw_rect(d, 50, band_y, W-100, 65, fill=GRAY_LIGHT, outline=BLACK, lw=2)
    center_text(d, "AUTOMATISCHES FLIESSBAND (CI/CD/CT-Pipeline)", 50, band_y+18, W-100, ft_sub)

    # ===== 3 HALLEN (Phasen) =====
    hall_y = 245
    hall_h = 380
    hall_gap = 50

    phases = [
        {
            "name": "PHASE 1",
            "label": "PRE-DEPLOYMENT",
            "icon": "[ Vorbereitung ]",
            "w": 700,
            "items": [
                "Model Registry & Versionierung",
                "Pre-Deployment Validation",
                "Prompt Testing, Red-Teaming",
                "Safety & Toxicity Checks",
                "Halluzinations-Rate pruefen",
                "Risk Classification (Art. 6 AI Act)",
                "Business-Impact-Assessment",
                "Technische Dokumentation (Art. 11)",
            ],
        },
        {
            "name": "PHASE 2",
            "label": "DEPLOYMENT",
            "icon": "[ Bereitstellung ]",
            "w": 780,
            "items": [
                "Staging Environment Validation",
                "Canary / Blue-Green Deployment",
                "GitOps (ArgoCD) Promotion",
                "OPA/Rego Policy Checks",
                "Post-Deployment Gate (Smoke Tests)",
                "Supply-Chain-Security (SBOM)",
                "Transparenzpflicht (Art. 13)",
                "Menschliche Aufsicht (Art. 14)",
                "Daten-Governance (Art. 10)",
            ],
        },
        {
            "name": "PHASE 3",
            "label": "OPERATION",
            "icon": "[ Betrieb & Inference ]",
            "w": 820,
            "items": [
                "Inference Serving (vLLM, API)",
                "Latency SLO Monitoring",
                "Retrieval Precision (RAG)",
                "Continuous Evaluation (DeepEval)",
                "Drift Detection & Alerting",
                "Protokollierung (Art. 12 AI Act)",
                "Robustheit (Art. 15 AI Act)",
                "Risikomanagement (Art. 9 AI Act)",
                "Continuous Compliance Monitoring",
            ],
        },
    ]

    # Center all 3 phases
    total_pw = sum(p["w"] for p in phases) + hall_gap * 2
    px = (W - total_pw) // 2

    for phase in phases:
        pw = phase["w"]
        # Phase box
        draw_rect(d, px, hall_y, pw, hall_h, fill=WHITE, outline=BLACK, lw=2)
        # Header
        draw_rect(d, px, hall_y, pw, 55, fill=GRAY_MID, outline=BLACK, lw=2)
        center_text(d, f'{phase["name"]}: {phase["label"]}', px, hall_y+5, pw, ft_label)
        center_text(d, phase["icon"], px, hall_y+30, pw, ft_small, fill=GRAY_DARK)

        # Items
        iy = hall_y + 70
        for item in phase["items"]:
            d.text((px+20, iy), f"- {item}", font=ft_small, fill=BLACK)
            iy += 32

        # Arrow between phases
        if phase != phases[-1]:
            ax = px + pw + 2
            draw_arrow_right(d, ax, hall_y + hall_h//2, ax + hall_gap - 4)

        px += pw + hall_gap

    # ===== QUALITY GATES (3 Checklisten) =====
    qg_y = hall_y + hall_h + 55
    center_text(d, "Jeder Phasenuebergang hat 3 Checklisten (Quality Gates):", 0, qg_y, W, ft_sub)

    qg_y += 45
    qg_w = 720
    qg_h = 280
    qg_gap = 50
    cx_start = (W - (3*qg_w + 2*qg_gap)) // 2

    checklists = [
        {
            "role": "Checkliste 1: DER MANAGER",
            "gate": "Strategisches Gate (Lifecycle Governance)",
            "items": [
                "Phase-Transition-Approval erteilt?",
                "Freigabe lt. Unternehmensrichtlinien?",
                "Risk-Budget & IT-Ressourcen genehmigt?",
                "Business-Impact bewertet?",
            ],
        },
        {
            "role": "Checkliste 2: DER INGENIEUR",
            "gate": "Technisches Gate (Qualitaetssicherung)",
            "items": [
                "Halluzinations-Rate unter Schwellwert?",
                "Performance & Latenz OK? (SLOs)",
                "Retrieval-Precision akzeptabel? (RAG)",
                "Safety Evaluation (Prompt Injection, Toxicity)?",
            ],
        },
        {
            "role": "Checkliste 3: DER INSPEKTOR",
            "gate": "Compliance Gate (EU AI Act)",
            "items": [
                "Risikomanagement vorhanden? (Art. 9)",
                "Daten-Governance validiert? (Art. 10)",
                "Techn. Dokumentation vollstaendig? (Art. 11)",
                "Transparenz & Human Oversight? (Art. 13, 14)",
            ],
        },
    ]

    for i, cl in enumerate(checklists):
        cx = cx_start + i * (qg_w + qg_gap)
        draw_rounded_rect(d, cx, qg_y, qg_w, qg_h, r=12, fill=WHITE, outline=BLACK, lw=2)

        # Role header
        draw_rounded_rect(d, cx, qg_y, qg_w, 42, r=12, fill=GRAY_MID, outline=BLACK, lw=2)
        center_text(d, cl["role"], cx, qg_y+9, qg_w, ft_label)

        # Gate type
        d.text((cx+20, qg_y+55), cl["gate"], font=ft_body, fill=GRAY_DARK)

        # Items
        iy = qg_y + 90
        for item in cl["items"]:
            d.text((cx+25, iy), f"[ ] {item}", font=ft_small, fill=BLACK)
            iy += 35

    # ===== GATE DECISION =====
    gd_y = qg_y + qg_h + 40
    draw_rect(d, 150, gd_y, W-300, 80, fill=GRAY_LIGHT, outline=BLACK, lw=2)
    center_text(d, "ALLE 3 Checklisten PASS --> Weiter zur naechsten Phase  |  EINE Checkliste FAIL --> Zurueck zur Nachbesserung",
                150, gd_y+10, W-300, ft_body)
    center_text(d, "Checklisten sind als Policy-as-Code (OPA/Rego) programmiert --> Pruefung laeuft automatisch auf dem Fliessband",
                150, gd_y+45, W-300, ft_small, fill=GRAY_DARK)

    # ===== EVIDENCE STORE =====
    ev_y = gd_y + 100
    draw_rect(d, 150, ev_y, W-300, 130, fill=WHITE, outline=BLACK, lw=3)
    center_text(d, "DAS FABRIK-ARCHIV (Evidence Store + Audit Trail)", 150, ev_y+8, W-300, ft_sub)

    # Evidence items in a row
    ev_items = [
        "Welches Modell?",
        "Welche Version?",
        "Welche Regeln?",
        "Welches Ergebnis?",
        "Wer hat geprueft?",
        "Beweis wo?",
    ]
    ev_box_w = 310
    ev_gap = 20
    total_ev = len(ev_items) * ev_box_w + (len(ev_items)-1) * ev_gap
    eix = 150 + ((W-300) - total_ev) // 2
    for item in ev_items:
        draw_rounded_rect(d, eix, ev_y+48, ev_box_w, 42, r=8, fill=GRAY_LIGHT, outline=BLACK, lw=1)
        center_text(d, item, eix, ev_y+57, ev_box_w, ft_small)
        eix += ev_box_w + ev_gap

    center_text(d, "Jede Gate-Entscheidung wird automatisch protokolliert — lueckenlos, unveraenderlich, nachvollziehbar.",
                150, ev_y+100, W-300, ft_small, fill=GRAY_DARK)

    # ===== AUDITOR =====
    au_y = ev_y + 150
    au_w = W - 500
    au_x = (W - au_w) // 2
    draw_rounded_rect(d, au_x, au_y, au_w, 55, r=10, fill=GRAY_LIGHT, outline=BLACK, lw=2)
    center_text(d, "Wenn der Auditor (EU-Behoerde) kommt: Archiv oeffnen --> Lueckenloser Nachweis was wann geprueft wurde",
                au_x, au_y+15, au_w, ft_body)

    # ===== Lifecycle note =====
    d.text((80, H-70), "3-Phasen-Lifecycle: Pre-Deployment | Deployment | Operation  (Training/Data-Engineering explizit ausgeschlossen — MD9/MD13)", font=ft_small, fill=GRAY_DARK)
    d.text((80, H-40), "Basis: EU AI Act (VO 2024/1689) Art. 9-15  |  NIST AI RMF (2023)  |  Hevner et al. (2004)  |  Accountability-by-Design", font=ft_small, fill=GRAY_DARK)

    img.save(out_path, "PNG", dpi=(300, 300))
    print(f"  -> {out_path}  ({W}x{H})")


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    out1 = os.path.join(repo, "03_forschungsdesign_methodik", "images", "final",
                        "03_04_methoden_framework_overview_v02.png")
    out2 = os.path.join(repo, "05_referenzarchitektur_RQ2", "05_02_architekturuebersicht",
                        "images", "final", "05_02_architektur_ki-fabrik-analogie_v02.png")

    print("Generating diagrams (black-and-white) ...")
    generate_methoden_framework(out1)
    generate_ki_fabrik(out2)
    print("Done.")
