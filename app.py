import streamlit as st
import hashlib
import json
import os, re
from datetime import datetime, timedelta
from fpdf import FPDF
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="MedChain",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
<style>
    :root {
        --primary:   #0f172a;
        --primary-d: #020617;
        --green:     #15803d;
        --red:       #991b1b;
        --amber:     #b45309;
        --nurse:     #4338ca;
        --auth:      #b45309;
        --bg:        #0f172a;
        --border:    #475569;
        --txt:       #f8fafc;
        --sub:       #cbd5e1;
    }
    .main, .stApp, .reportview-container { background: #0f172a; }

    /* ---- HEADER ---- */
    .header-container {
        background: linear-gradient(135deg,#111827 0%,#1f2937 100%);
        padding: 36px 30px; border-radius: 15px; color: #f8fafc;
        margin-bottom: 28px; box-shadow: 0 10px 30px rgba(15,23,42,.18);
        text-align: center;
    }
    .header-container h1 { font-size: 2.4em; margin:0; font-weight:700; color: #f8fafc; }
    .header-container p  { font-size: 1.1em; margin:8px 0 0; color: #cbd5e1; opacity:.95; }
    .hero-header {
        background-image: url('https://thumbs.dreamstime.com/b/modern-hospital-building-illuminated-night-wide-tiled-entrance-clear-dark-blue-sky-urban-setting-angle-view-420258658.jpg?w=1200');
        background-size: 140%;
        background-position: center center;
        min-height: 260px;
        padding: 48px 30px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        text-align: left;
    }
    .hero-caption {
        background: rgba(15,23,42,0.38);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(255,255,255,0.16);
        border-radius: 18px;
        padding: 28px 30px;
        max-width: 620px;
        box-shadow: 0 18px 40px rgba(0,0,0,0.24);
    }

    /* role-coloured headers */
    .header-nurse  { background: linear-gradient(135deg,#4338ca,#312e81)!important; }
    .header-auth   { background: linear-gradient(135deg,#92400e,#7c2d12)!important; }

    /* ---- CARDS ---- */
    .card {
        background:#111827; padding:22px; border-radius:12px;
        border-left:5px solid var(--primary);
        box-shadow:0 4px 15px rgba(0,0,0,.28); margin-bottom:18px;
        transition:all .3s;
    }
    .card:hover { box-shadow:0 8px 25px rgba(0,0,0,.18); transform:translateY(-2px); }
    .card-nurse  { border-left-color: var(--nurse)!important; background: #c7d2fe!important; }
    .card-nurse strong, .card-nurse p, .card-nurse h3, .card-nurse code { color: #312e81!important; }
    .card-auth   { border-left-color: var(--auth)!important; }
    .card-green  { border-left-color: var(--green)!important; }
    .card-red    { border-left-color: var(--red)!important; }

    /* ---- BUTTONS ---- */
    .stButton > button {
        background: linear-gradient(135deg,#0b3d91,#1e40af);
        color:#fff; border:none; border-radius:8px; padding:11px 26px;
        font-weight:800; font-size:1em; transition:all .3s;
        box-shadow:0 4px 12px rgba(0,0,0,.32);
    }
    .stButton > button:hover {
        transform:translateY(-2px);
        box-shadow:0 6px 20px rgba(0,0,0,.5);
        background: linear-gradient(135deg,#09326c,#1d4ed8);
    }

    /* ---- BADGES ---- */
    .badge {
        display:inline-block; padding:5px 13px; border-radius:20px;
        font-weight:600; font-size:.85em;
    }
    .badge-active   { background:#d4f4dd; color:#007c41; }
    .badge-inactive { background:#4b5563; color:#f8fafc; }
    .badge-nurse    { background:#4338ca; color:#f8fafc; }
    .badge-auth     { background:#b45309; color:#f8fafc; }
    .badge-pending  { background:#c2410c; color:#f8fafc; }

    /* ---- STAT BOXES ---- */
    .stat-box {
        background:#111827; border-radius:12px; padding:20px;
        text-align:center; box-shadow:0 4px 12px rgba(0,0,0,.16);
    }
    .stat-val  { font-size:2.2em; font-weight:700; color:#f8fafc; }
    .stat-lbl  { font-size:.95em; color:#cbd5e1; margin-top:6px; }

    /* ---- SIDEBAR ---- */
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0b1229 0%, #1a2d5d 60%, #0f172a 100%); }
    section[data-testid="stSidebar"] * { color:#e2e8f0!important; }
    section[data-testid="stSidebar"] .stButton>button {
        background: linear-gradient(135deg,#4f46e5,#2563eb);
        color:#fff!important; border:none; border-radius:14px; padding:12px 18px;
        font-weight:800; box-shadow:0 8px 20px rgba(37,99,235,.35);
    }
    section[data-testid="stSidebar"] .stButton>button:hover {
        background: linear-gradient(135deg,#4338ca,#1d4ed8);
    }
    section[data-testid="stSidebar"] hr { border-color: rgba(147,197,253,0.22); }
    .sidebar-panel {
        background: rgba(15,23,42,0.92);
        border:1px solid rgba(96,165,250,0.24);
        border-radius: 22px;
        padding: 22px 20px;
        margin-bottom: 18px;
        box-shadow: 0 18px 45px rgba(15,23,42,.28);
    }
    .sidebar-panel h3 { margin:0 0 12px; color:#93c5fd; font-size:1.18rem; }
    .sidebar-panel p, .sidebar-panel div { color:#dbeafe; margin: 6px 0; line-height:1.5; }
    .sidebar-panel strong { color:#eff6ff; }

    /* ---- TABS ---- */
    .stTabs [data-baseweb="tab-list"] { gap:16px; border-bottom:2px solid var(--border); }
    .stTabs [data-baseweb="tab"] {
        padding:10px 22px; font-weight:600; border-radius:8px 8px 0 0;
        background:transparent; color:#e2e8f0;
    }
    .stTabs [aria-selected="true"] { background:#0f172a; color:#f8fafc; border-bottom:3px solid #0f172a; }

    h2 { font-weight:600; border-bottom:2px solid #475569; padding-bottom:8px; margin-bottom:14px; }
    /* Ensure Streamlit-rendered markdown headings are dark for readability */
    .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #f8fafc !important;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#   CONSTANTS & PERSISTENCE
# ─────────────────────────────────────────────
USER_FILE   = "users.json"
LEDGER_FILE = "medical_ledger.json"
KEYS_DIR    = "user_keys"
UPLOAD_DIR  = "patient_uploads"  # NEW: Folder for physical file storage

# Ensure storage directories exist
os.makedirs(KEYS_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True) 

ROLE_PREFIXES = {
    "DOCTOR":    "DOC",
    "PATIENT":   "PT",
    "NURSE":     "NRS",
    "AUTHORITY": "AUTH",
}
ROLE_STORES = {
    "DOCTOR":    "DOCTORS",
    "PATIENT":   "PATIENTS",
    "NURSE":     "NURSES",
    "AUTHORITY": "AUTHORITIES",
}

# ─────────────────────────────────────────────
#   SECURITY UTILITIES
# ─────────────────────────────────────────────
def get_salted_hash(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()
    h = hashlib.sha256((password + salt).encode()).hexdigest()
    return h, salt

class RSAKeyManager:
    @staticmethod
    def generate_keypair():
        pk = rsa.generate_private_key(65537, 2048, default_backend())
        return pk, pk.public_key()

    @staticmethod
    def serialize_private_key(k):
        pem = k.private_bytes(serialization.Encoding.PEM,
                              serialization.PrivateFormat.PKCS8,
                              serialization.NoEncryption())
        return base64.b64encode(pem).decode()

    @staticmethod
    def serialize_public_key(k):
        pem = k.public_bytes(serialization.Encoding.PEM,
                             serialization.PublicFormat.SubjectPublicKeyInfo)
        return base64.b64encode(pem).decode()

    @staticmethod
    def deserialize_private_key(s):
        return serialization.load_pem_private_key(
            base64.b64decode(s.encode()), password=None, backend=default_backend())

    @staticmethod
    def deserialize_public_key(s):
        return serialization.load_pem_public_key(base64.b64decode(s.encode()),
                                                  backend=default_backend())

class ProxyReEncryption:
    @staticmethod
    def generate_aes_key():
        return os.urandom(32)

    @staticmethod
    def encrypt_aes_key(aes_key, public_key):
        enc = public_key.encrypt(aes_key,
            padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),
                         algorithm=hashes.SHA256(), label=None))
        return base64.b64encode(enc).decode()

    @staticmethod
    def decrypt_aes_key(encrypted_key, private_key):
        return private_key.decrypt(base64.b64decode(encrypted_key.encode()),
            padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),
                         algorithm=hashes.SHA256(), label=None))

    @staticmethod
    def generate_reencryption_key(patient_private_key, doctor_public_key):
        seed = os.urandom(32)
        enc_seed = doctor_public_key.encrypt(seed,
            padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),
                         algorithm=hashes.SHA256(), label=None))
        return {
            "seed": base64.b64encode(seed).decode(),
            "encrypted_seed": base64.b64encode(enc_seed).decode(),
            "type": "rsa_pre"
        }

# ─────────────────────────────────────────────
#   USER DATABASE
# ─────────────────────────────────────────────
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def load_users():
    default = {
        "DOCTORS": {}, "PATIENTS": {}, "NURSES": {}, "AUTHORITIES": {},
        "COUNTERS": {"DOCTOR": 1, "PATIENT": 1, "NURSE": 1, "AUTHORITY": 1}
    }
    if not os.path.exists(USER_FILE):
        return default
    with open(USER_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return default

    # migrate old files
    for key in ["NURSES", "AUTHORITIES"]:
        if key not in data:
            data[key] = {}
    if "COUNTERS" not in data:
        data["COUNTERS"] = {
            "DOCTOR":    len(data.get("DOCTORS", {})) + 1,
            "PATIENT":   len(data.get("PATIENTS", {})) + 1,
            "NURSE":     len(data.get("NURSES", {})) + 1,
            "AUTHORITY": len(data.get("AUTHORITIES", {})) + 1,
        }
    for role in ["NURSE", "AUTHORITY"]:
        if role not in data["COUNTERS"]:
            data["COUNTERS"][role] = len(data.get(ROLE_STORES[role], {})) + 1
    save_users(data)
    return data

def generate_next_id(db, role):
    count = db["COUNTERS"].get(role, 1)
    prefix = ROLE_PREFIXES[role]
    new_id = f"{prefix}-{count:03d}"
    return new_id, count

# ─────────────────────────────────────────────
#   BLOCKCHAIN
# ─────────────────────────────────────────────
class MedicalBlockchain:
    def __init__(self):
        self.chain = []
        self.load_data()

    def load_data(self):
        if os.path.exists(LEDGER_FILE):
            with open(LEDGER_FILE) as f:
                try:
                    self.chain = json.load(f)
                except json.JSONDecodeError:
                    self.create_block({"info": "Genesis Block"}, "0")
        else:
            self.create_block({"info": "Genesis Block"}, "0")

    def save_to_disk(self):
        with open(LEDGER_FILE, "w") as f:
            json.dump(self.chain, f, indent=4)

    def hash_block(self, block):
        copy = {k: v for k, v in block.items() if k != "hash"}
        return hashlib.sha256(json.dumps(copy, sort_keys=True).encode()).hexdigest()

    def create_block(self, data, prev_hash):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": data,
            "previous_hash": prev_hash,
        }
        block["hash"] = self.hash_block(block)
        self.chain.append(block)
        self.save_to_disk()
        return block

    # ── permission helpers ──
    def _parse_timestamp(self, timestamp):
        if isinstance(timestamp, str):
            return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        return timestamp

    def has_regular_access(self, patient_id, doctor_id):
        for i, block in enumerate(self.chain):
            d = block["data"]
            if d.get("op") == "GRANT_ACCESS" and d.get("patient") == patient_id and d.get("doctor") == doctor_id:
                revoked = any(
                    b["data"].get("op") == "REVOKE_ACCESS"
                    and b["data"].get("patient") == patient_id
                    and b["data"].get("doctor") == doctor_id
                    for b in self.chain[i + 1:]
                )
                if not revoked:
                    return True
        return False

    def has_emergency_access(self, patient_id, doctor_id):
        now = datetime.now()
        for i, block in enumerate(self.chain):
            d = block["data"]
            if d.get("op") == "EMERGENCY_ACCESS" and d.get("patient") == patient_id and d.get("doctor") == doctor_id:
                expires_at = self._parse_timestamp(d.get("expires_at", "1970-01-01 00:00:00"))
                if expires_at < now:
                    continue
                revoked = any(
                    b["data"].get("op") == "REVOKE_ACCESS"
                    and b["data"].get("patient") == patient_id
                    and b["data"].get("doctor") == doctor_id
                    for b in self.chain[i + 1:]
                )
                if not revoked:
                    return True
        return False

    def check_permission(self, patient_id, doctor_id):
        return self.has_regular_access(patient_id, doctor_id) or self.has_emergency_access(patient_id, doctor_id)

    def get_active_emergency_accesses(self, patient_id=None):
        active = []
        now = datetime.now()
        for i, block in enumerate(self.chain):
            d = block["data"]
            if d.get("op") != "EMERGENCY_ACCESS":
                continue
            if patient_id and d.get("patient") != patient_id:
                continue
            expires_at = self._parse_timestamp(d.get("expires_at", "1970-01-01 00:00:00"))
            if expires_at < now:
                continue
            revoked = any(
                b["data"].get("op") == "REVOKE_ACCESS"
                and b["data"].get("patient") == d.get("patient")
                and b["data"].get("doctor") == d.get("doctor")
                for b in self.chain[i + 1:]
            )
            if not revoked:
                active.append(block)
        return active

    def get_emergency_audit_log(self, patient_id=None, doctor_id=None):
        audit = []
        for block in self.chain:
            d = block["data"]
            if d.get("op") not in {"EMERGENCY_ACCESS", "REVOKE_ACCESS"}:
                continue
            if patient_id and d.get("patient") != patient_id:
                continue
            if doctor_id and d.get("doctor") != doctor_id:
                continue
            audit.append(block)
        return audit

    def get_emergency_access_info(self, patient_id, doctor_id):
        for block in reversed(self.chain):
            d = block["data"]
            if d.get("op") == "EMERGENCY_ACCESS" and d.get("patient") == patient_id and d.get("doctor") == doctor_id:
                expires_at = self._parse_timestamp(d.get("expires_at", "1970-01-01 00:00:00"))
                if expires_at < datetime.now():
                    return None
                revoked = any(
                    b["data"].get("op") == "REVOKE_ACCESS"
                    and b["data"].get("patient") == patient_id
                    and b["data"].get("doctor") == doctor_id
                    for b in self.chain[self.chain.index(block) + 1:]
                )
                if not revoked:
                    return block
        return None

    def get_reencryption_key(self, patient_id, doctor_id):
        for block in reversed(self.chain):
            d = block["data"]
            if (d.get("op") == "GRANT_ACCESS"
                    and d.get("patient") == patient_id
                    and d.get("doctor") == doctor_id
                    and "reencryption_key" in d):
                return d["reencryption_key"]
        return None

    # ── nurse assignment helpers ──
    def get_nurse_patient(self, nurse_id):
        assigned = None
        for block in self.chain:
            d = block["data"]
            if d.get("op") == "ASSIGN_NURSE" and d.get("nurse") == nurse_id:
                assigned = d["patient"]
            if d.get("op") == "RELEASE_NURSE" and d.get("nurse") == nurse_id:
                assigned = None
        return assigned

    def get_patient_nurse(self, patient_id):
        assigned = None
        for block in self.chain:
            d = block["data"]
            if d.get("op") == "ASSIGN_NURSE" and d.get("patient") == patient_id:
                assigned = d["nurse"]
            if d.get("op") == "RELEASE_NURSE" and d.get("patient") == patient_id:
                assigned = None
        return assigned

    def get_available_nurses(self, nurses_db):
        return [nid for nid in nurses_db if self.get_nurse_patient(nid) is None]

    def auto_assign_nurse(self, patient_id, nurses_db):
        if self.get_patient_nurse(patient_id):
            return self.get_patient_nurse(patient_id)
        available = self.get_available_nurses(nurses_db)
        if not available:
            return None
        nurse_id = available[0]
        self.create_block(
            {"op": "ASSIGN_NURSE", "nurse": nurse_id, "patient": patient_id},
            self.chain[-1]["hash"]
        )
        return nurse_id

    def get_nurse_notes(self, patient_id):
        return [b for b in self.chain if b["data"].get("op") == "NURSE_NOTE"
                and b["data"].get("patient") == patient_id]

    def all_records_for_authority(self):
        return [b for b in self.chain if b["data"].get("op") == "DIAGNOSIS"]

    def all_uploads(self):
        return [b for b in self.chain if b["data"].get("op") == "UPLOAD_RECORD"]


# ─────────────────────────────────────────────
#   PDF GENERATOR
# ─────────────────────────────────────────────
def _safe(text):
    replacements = {
        '\u2014': '-', '\u2013': '-', '\u2012': '-',   
        '\u2018': "'", '\u2019': "'",                   
        '\u201c': '"', '\u201d': '"',                   
        '\u2026': '...', '\u2022': '*', '\u00b7': '*',  
        '\u00a0': ' ',                                   
    }
    for ch, repl in replacements.items():
        text = text.replace(ch, repl)
    return text.encode('latin-1', errors='replace').decode('latin-1')

def create_pdf(doctor, date, patient_id, condition, rx):
    doctor    = _safe(str(doctor))
    date      = _safe(str(date))
    patient_id= _safe(str(patient_id))
    condition = _safe(str(condition))
    rx        = _safe(str(rx))
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=18)

    W = 210  

    pdf.set_fill_color(10, 45, 100)
    pdf.rect(0, 0, W, 42, 'F')

    pdf.set_xy(0, 8)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 22)
    pdf.cell(W, 10, "MedChain", align='C', ln=1)

    pdf.set_font("Arial", 'I', 9)
    pdf.set_text_color(180, 210, 255)
    pdf.cell(W, 6, "Secure Blockchain Medical Records  |  Official Prescription Document", align='C', ln=1)

    pdf.set_fill_color(212, 175, 55)
    pdf.rect(0, 42, W, 1.5, 'F')

    pdf.set_fill_color(240, 245, 255)
    pdf.rect(0, 43.5, W, 14, 'F')
    pdf.set_xy(0, 45)
    pdf.set_text_color(10, 45, 100)
    pdf.set_font("Arial", 'B', 13)
    pdf.cell(W, 8, "OFFICIAL MEDICAL PRESCRIPTION", align='C', ln=1)

    pdf.ln(6)

    margin   = 15
    box_gap  = 6
    box_w    = (W - 2 * margin - box_gap) / 2
    box_y    = pdf.get_y()
    box_h    = 28

    pdf.set_fill_color(235, 242, 255)
    pdf.set_draw_color(10, 45, 100)
    pdf.set_line_width(0.4)
    pdf.rect(margin, box_y, box_w, box_h, 'FD')

    pdf.set_xy(margin + 4, box_y + 4)
    pdf.set_font("Arial", 'B', 7.5)
    pdf.set_text_color(10, 45, 100)
    pdf.cell(box_w - 8, 5, "PRESCRIBING PHYSICIAN", ln=1)

    pdf.set_xy(margin + 4, box_y + 10)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(15, 30, 70)
    pdf.cell(box_w - 8, 6, f"Dr. {doctor}", ln=1)

    pdf.set_xy(margin + 4, box_y + 18)
    pdf.set_font("Arial", '', 8.5)
    pdf.set_text_color(80, 100, 140)
    pdf.cell(box_w - 8, 5, f"MedChain Registered Physician", ln=1)

    rx_box_x = margin + box_w + box_gap
    pdf.set_fill_color(235, 242, 255)
    pdf.rect(rx_box_x, box_y, box_w, box_h, 'FD')

    pdf.set_xy(rx_box_x + 4, box_y + 4)
    pdf.set_font("Arial", 'B', 7.5)
    pdf.set_text_color(10, 45, 100)
    pdf.cell(box_w - 8, 5, "PATIENT DETAILS", ln=1)

    pdf.set_xy(rx_box_x + 4, box_y + 10)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(15, 30, 70)
    pdf.cell(box_w - 8, 6, f"ID: {patient_id}", ln=1)

    pdf.set_xy(rx_box_x + 4, box_y + 18)
    pdf.set_font("Arial", '', 8.5)
    pdf.set_text_color(80, 100, 140)
    pdf.cell(box_w - 8, 5, f"Date Issued: {date}", ln=1)

    pdf.ln(box_h + 6)

    sec_y = pdf.get_y()
    pdf.set_fill_color(10, 45, 100)
    pdf.set_draw_color(10, 45, 100)
    pdf.rect(margin, sec_y, 40, 7, 'F')
    pdf.set_xy(margin, sec_y)
    pdf.set_font("Arial", 'B', 8)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(40, 7, "  DIAGNOSIS", ln=0)

    pdf.set_xy(margin, sec_y + 9)
    pdf.set_fill_color(252, 252, 255)
    pdf.set_draw_color(190, 205, 235)
    pdf.set_line_width(0.3)
    diag_lines = condition if condition else "N/A"
    diag_h = max(14, 8 + len(condition) // 60 * 6)
    pdf.rect(margin, sec_y + 9, W - 2 * margin, diag_h, 'FD')
    pdf.set_xy(margin + 4, sec_y + 13)
    pdf.set_font("Arial", '', 10.5)
    pdf.set_text_color(20, 30, 60)
    pdf.multi_cell(W - 2 * margin - 8, 6, diag_lines)

    pdf.ln(diag_h - 4)

    sec_y2 = pdf.get_y()
    pdf.set_fill_color(0, 130, 100)
    pdf.rect(margin, sec_y2, 55, 7, 'F')
    pdf.set_xy(margin, sec_y2)
    pdf.set_font("Arial", 'B', 8)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(55, 7, "  MEDICATIONS & TREATMENT", ln=0)

    pdf.set_xy(margin, sec_y2 + 9)
    pdf.set_fill_color(248, 255, 252)
    pdf.set_draw_color(180, 225, 210)
    rx_h = max(30, 12 + len(rx) // 55 * 6)
    pdf.rect(margin, sec_y2 + 9, W - 2 * margin, rx_h, 'FD')

    pdf.set_xy(margin + 4, sec_y2 + 14)
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(20, 40, 30)
    for line in rx.split('\n'):
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue
        if pdf.get_x() != margin + 4:
            pdf.set_x(margin + 4)
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(0, 130, 100)
        pdf.cell(6, 6, chr(149), ln=0)
        pdf.set_font("Arial", '', 10)
        pdf.set_text_color(20, 40, 30)
        pdf.multi_cell(W - 2 * margin - 14, 6, line)

    pdf.ln(rx_h - 8)

    sig_y = pdf.get_y() + 4
    pdf.set_draw_color(10, 45, 100)
    pdf.set_line_width(0.4)
    pdf.line(margin, sig_y + 18, margin + 65, sig_y + 18)
    pdf.set_xy(margin, sig_y + 20)
    pdf.set_font("Arial", 'I', 8.5)
    pdf.set_text_color(100, 115, 145)
    pdf.cell(70, 5, f"Dr. {doctor}  -  Authorized Signature")

    pdf.set_fill_color(10, 45, 100)
    stamp_x = W - margin - 52
    pdf.rect(stamp_x, sig_y + 4, 52, 18, 'F')
    pdf.set_xy(stamp_x, sig_y + 7)
    pdf.set_font("Arial", 'B', 7)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(52, 5, "BLOCKCHAIN VERIFIED", align='C', ln=1)
    pdf.set_xy(stamp_x, sig_y + 13)
    pdf.set_font("Arial", '', 6.5)
    pdf.set_text_color(180, 210, 255)
    pdf.cell(52, 5, "SHA-256 | RSA-2048 Secured", align='C')

    footer_y = 282
    pdf.set_fill_color(10, 45, 100)
    pdf.rect(0, footer_y, W, 0.8, 'F')
    pdf.set_xy(0, footer_y + 2)
    pdf.set_font("Arial", 'I', 7)
    pdf.set_text_color(130, 145, 170)
    pdf.cell(W, 4, "This prescription is cryptographically secured on the MedChain blockchain. Tampering invalidates this document.", align='C', ln=1)
    pdf.cell(W, 4, f"Generated: {date}  |  MedChain  |  Confidential Medical Record", align='C')

    return pdf.output(dest='S').encode('latin-1')


SYMPTOM_PATTERNS = [
    ("fever cough fatigue body ache", "Influenza-like illness", "Recommend rest, fluids, and symptomatic relief. Monitor for worsening respiratory distress."),
    ("fever cough fatigue", "Viral respiratory infection", "Recommend rest, fluids, and monitoring. Consider follow-up if symptoms worsen."),
    ("chest pain shortness of breath nausea sweating", "Possible acute coronary syndrome", "Recommend immediate cardiac evaluation and urgent medical attention."),
    ("chest pain shortness of breath", "Possible cardiac or respiratory emergency", "Evaluate immediately. Consider ECG and urgent referral."),
    ("abdominal pain nausea vomiting diarrhea", "Gastroenteritis", "Recommend hydration, electrolyte support, and light food. Evaluate for infection or food intolerance."),
    ("abdominal pain nausea vomiting", "Gastrointestinal upset", "Recommend hydration and a light diet. Evaluate for food poisoning or infection."),
    ("headache dizziness nausea", "Migraine or dehydration", "Recommend rest, hydration, and pain management. Monitor for visual changes."),
    ("headache blurred vision nausea", "Possible hypertensive crisis", "Recommend urgent blood pressure evaluation and emergency care."),
    ("joint pain swelling stiffness", "Possible arthritis or inflammatory condition", "Recommend anti-inflammatory support and follow-up examination."),
    ("joint pain fever rash", "Possible autoimmune flare", "Recommend anti-inflammatory treatment and specialist evaluation."),
    ("sore throat fever swollen glands", "Upper respiratory infection", "Recommend throat rest, fluids, and monitoring for bacterial infection."),
    ("runny nose sneezing itchy eyes", "Allergic rhinitis", "Recommend antihistamines, nasal irrigation, and trigger avoidance."),
    ("rash itching swelling", "Allergic reaction", "Recommend antihistamines and avoidance of trigger. Monitor for worsening symptoms."),
    ("rash pain redness fever", "Possible cellulitis", "Recommend medical review and possible antibiotic therapy."),
    ("blood in urine back pain", "Possible urinary tract infection", "Recommend urine test, hydration, and follow-up treatment."),
    ("frequent urination burning sensation", "Urinary tract infection", "Recommend urine test and hydration. Consider antibiotic evaluation if infection is confirmed."),
    ("high fever stiff neck confusion", "Serious infection such as meningitis", "Recommend immediate emergency evaluation."),
    ("shortness of breath wheezing chest tightness", "Asthma exacerbation", "Recommend bronchodilator use and monitoring. Seek urgent care if breathing difficulty worsens."),
    ("dry mouth thirst frequent urination", "Possible diabetes", "Recommend blood glucose testing and dietary review."),
    ("dizziness lightheaded fainting", "Orthostatic hypotension or dehydration", "Recommend hydration, rest, and follow-up evaluation."),
    ("leg swelling pain redness", "Possible deep vein thrombosis", "Recommend urgent medical assessment and vascular evaluation."),
    ("tremor anxiety sweating heart palpitations", "Panic attack or hyperthyroid symptoms", "Recommend calming measures, monitoring, and follow-up evaluation."),
    ("confusion memory loss mood changes", "Possible cognitive impairment", "Recommend neurological assessment and monitoring."),
    ("persistent cough blood sputum", "Possible bronchitis or pneumonia", "Recommend chest imaging, cough management, and medical review."),
    ("ear pain hearing loss fever", "Otitis media", "Recommend ear examination and symptomatic relief. Consider antibiotics if bacterial infection is suspected."),
    ("fatigue night sweats weight loss", "Possible chronic infection or malignancy", "Recommend urgent clinical evaluation and further testing."),
    ("severe abdominal pain radiating to back", "Possible pancreatitis", "Recommend immediate evaluation and pancreatic enzyme testing."),
    ("sudden weakness slurred speech facial droop", "Possible stroke", "Recommend emergency evaluation and immediate transport to a stroke center."),
]


def normalize_text(text):
    return re.sub(r"[^a-z0-9 ]", " ", (text or "").lower())


def keyword_overlap(text, pattern):
    words = set(normalize_text(text).split())
    return len(words & set(pattern.split()))


def find_best_symptom_matches(text, top_n=3):
    scored = []
    for pattern, diagnosis, advice in SYMPTOM_PATTERNS:
        score = keyword_overlap(text, pattern)
        if score > 0:
            scored.append((score, pattern, diagnosis, advice))
    scored.sort(key=lambda item: (-item[0], -len(item[1])))
    return scored[:top_n]


def generate_ai_chat_response(message):
    prompt = normalize_text(message)
    if not prompt.strip():
        return "Please describe the patient's symptoms, including duration, location, and severity."

    words = set(prompt.split())
    if len(words) < 4:
        return "Tell me a bit more about the symptoms. For example, include pain location, fever, duration, or breathing issues."

    matches = find_best_symptom_matches(message)
    if not matches:
        follow_up = []
        if any(keyword in prompt for keyword in ["pain", "ache", "discomfort"]):
            follow_up.append("Is there fever, swelling, red skin, or stiffness?")
        if any(keyword in prompt for keyword in ["breath", "cough", "wheeze"]):
            follow_up.append("Is there chest tightness, rapid breathing, or blood in sputum?")
        if any(keyword in prompt for keyword in ["stomach", "abdomen", "nausea"]):
            follow_up.append("Does the pain radiate to the back or get worse after eating?")
        if not follow_up:
            follow_up.append("Please add information about temperature, pain location, and how long the symptoms have lasted.")
        return "I don't have a strong match yet. " + " ".join(follow_up)

    response_lines = ["I found the following likely conditions based on the symptoms you described:"]
    for score, pattern, diagnosis, advice in matches:
        response_lines.append(f"- **{diagnosis}** (matched: {pattern})")
        response_lines.append(f"  - Advice: {advice}")
    response_lines.append("\nIf needed, you can ask me for a differential diagnosis, red-flag symptoms, or next steps for treatment.")
    return "\n".join(response_lines)


def handle_ai_chat_send():
    message = st.session_state.get("ai_chat_input", "").strip()
    if not message:
        return
    st.session_state.ai_chat_history.append({"role": "user", "content": message})
    reply = generate_ai_chat_response(message)
    st.session_state.ai_chat_history.append({"role": "assistant", "content": reply})
    st.session_state.ai_chat_input = ""


def handle_ai_chat_reset():
    st.session_state.ai_chat_history = [
        {
            "role": "assistant",
            "content": "Hello! I am your clinical assistant. Describe the patient's symptoms, and I will help identify possible diagnoses and treatment guidance."
        }
    ]
    st.session_state.ai_chat_input = ""


def suggest_diagnosis(symptoms):
    suggestions = []
    for pattern, diagnosis, advice in SYMPTOM_PATTERNS:
        if all(keyword in symptoms.lower() for keyword in pattern.split()):
            suggestions.append({
                "diagnosis": diagnosis,
                "advice": advice,
                "pattern": pattern,
            })
    if not suggestions:
        best_score = 0
        best_suggestions = []
        symptom_words = set(normalize_text(symptoms).split())
        for pattern, diagnosis, advice in SYMPTOM_PATTERNS:
            keywords = set(pattern.split())
            score = len(symptom_words & keywords)
            if score > best_score:
                best_score = score
                best_suggestions = [{
                    "diagnosis": diagnosis,
                    "advice": advice,
                    "pattern": pattern,
                }]
            elif score == best_score and score > 0:
                best_suggestions.append({
                    "diagnosis": diagnosis,
                    "advice": advice,
                    "pattern": pattern,
                })
        suggestions = best_suggestions
    return suggestions[:3]


# ─────────────────────────────────────────────
#   APP INIT
# ─────────────────────────────────────────────
if 'bc' not in st.session_state:
    st.session_state.bc = MedicalBlockchain()
if 'user' not in st.session_state:
    st.session_state.user = None

users_db = load_users()
bc: MedicalBlockchain = st.session_state.bc

def render_header(title, subtitle, extra_class=""):
    st.markdown(f"""
    <div class="header-container hero-header {extra_class}">
        <div class="hero-caption">
            <h1>🏥 MedChain</h1>
            <p>{title} · {subtitle}</p>
        </div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
#   AUTH PAGE
# ══════════════════════════════════════════════
if not st.session_state.user:
    st.markdown("""
    <div class="header-container hero-header">
        <div class="hero-caption">
            <h1>🏥 MedChain</h1>
            <p>Secure Medical Records · 4-Role Blockchain System</p>
        </div>
    </div>""", unsafe_allow_html=True)

    col_login, col_reg = st.columns(2)

    with col_login:
        st.markdown("<h2 style='color:#bfdbfe; font-weight:800;'>🔑 Sign In</h2>", unsafe_allow_html=True)
        login_role = st.selectbox("Role", ["DOCTOR", "PATIENT", "NURSE", "AUTHORITY"], key="lr")
        store = ROLE_STORES[login_role]
        u_id  = st.text_input("User ID", placeholder=f"{ROLE_PREFIXES[login_role]}-001")
        u_pw  = st.text_input("Password", type="password")

        if st.button("Sign In", use_container_width=True):
            rec = users_db[store].get(u_id)
            if rec:
                h, _ = get_salted_hash(u_pw, rec["salt"])
                if h == rec["pw_hash"]:
                    st.session_state.user = {"id": u_id, "name": rec["name"], "role": login_role}
                    st.success("✅ Welcome!")
                    st.rerun()
                else:
                    st.error("❌ Wrong password.")
            else:
                st.error("❌ User ID not found.")

    with col_reg:
        st.markdown("<h2 style='color:#bfdbfe; font-weight:800'>📝 Create Account</h2>", unsafe_allow_html=True)
        new_role = st.selectbox("Role", ["DOCTOR", "PATIENT", "NURSE", "AUTHORITY"], key="nr")
        new_name = st.text_input("Full Name", placeholder="Jane Doe")
        new_pw   = st.text_input("Password", type="password", placeholder="Min 6 characters", key="npw")

        if st.button("Register", use_container_width=True):
            if not new_name or not new_pw:
                st.warning("All fields required.")
            elif len(new_pw) < 6:
                st.warning("Password must be ≥ 6 characters.")
            else:
                store      = ROLE_STORES[new_role]
                new_id, cnt = generate_next_id(users_db, new_role)
                pw_hash, salt = get_salted_hash(new_pw)

                record: dict = {"name": new_name, "pw_hash": pw_hash, "salt": salt}

                if new_role in ("DOCTOR", "PATIENT"):
                    priv, pub = RSAKeyManager.generate_keypair()
                    record["public_key"]  = RSAKeyManager.serialize_public_key(pub)
                    record["private_key"] = RSAKeyManager.serialize_private_key(priv)

                users_db[store][new_id] = record
                users_db["COUNTERS"][new_role] = cnt + 1
                save_users(users_db)

                if new_role == "PATIENT" and users_db["NURSES"]:
                    nid = bc.auto_assign_nurse(new_id, users_db["NURSES"])
                    if nid:
                        nurse_name = users_db["NURSES"][nid]["name"]
                        st.info(f"🩺 Nurse **{nurse_name}** ({nid}) auto-assigned to you.")

                st.success(f"✅ Account created! Your ID: **{new_id}**")
                if new_role in ("DOCTOR", "PATIENT"):
                    st.info("🔐 RSA-2048 encryption keys generated.")


# ══════════════════════════════════════════════
#   DASHBOARDS
# ══════════════════════════════════════════════
else:
    u = st.session_state.user
    role = u["role"]

    role_icons = {"DOCTOR": "👨‍⚕️", "PATIENT": "🧑‍⚕️", "NURSE": "💉", "AUTHORITY": "🏛️"}
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-panel">
            <h3>{role_icons.get(role,'👤')} Profile</h3>
            <div><strong>Name:</strong> {u['name']}</div>
            <div><strong>ID:</strong> {u['id']}</div>
            <div><strong>Role:</strong> {role}</div>
        </div>""", unsafe_allow_html=True)

        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # ════════════════════════════════════════
    #   DOCTOR DASHBOARD
    # ════════════════════════════════════════
    if role == "DOCTOR":
        render_header(f"Dr. {u['name']}", "Physician Terminal")
        tab_rx, tab_view, tab_mypts = st.tabs(["✍️ Write Prescription", "🔍 View Patient History", "👥 My Patients"])

        with tab_rx:
            with st.form("rx_form"):
                st.markdown("#### 📋 New Medical Record")
                c1, c2 = st.columns(2)
                with c1: p_id = st.text_input("Patient ID", placeholder="PT-001")
                with c2: diag = st.text_input("Diagnosis", placeholder="e.g., Hypertension")
                meds = st.text_area("Prescription Details", placeholder="Medications and notes…", height=120)

                if st.form_submit_button("💾 Save & Secure", use_container_width=True):
                    if bc.check_permission(p_id, u["id"]):
                        integrity = hashlib.sha256(f"{diag}|{meds}".encode()).hexdigest()
                        bc.create_block({
                            "op": "DIAGNOSIS", "doctor": u["id"], "doctor_name": u["name"],
                            "patient": p_id, "condition": diag, "rx": meds,
                            "sha256_hash": integrity, "encrypted": False
                        }, bc.chain[-1]["hash"])
                        st.success("✅ Record secured on blockchain!")
                    else:
                        st.error("❌ Access Denied: Patient has not authorized you yet.")

            with st.expander("🤖 AI Symptom Chat Assistant", expanded=True):
                st.markdown(
                    "<div style='color:#f8fafc;font-weight:600;margin-bottom:10px;'>Use this chat assistant to analyze symptoms, suggest likely diagnoses, and recommend next steps.</div>",
                    unsafe_allow_html=True
                )
                if "ai_chat_history" not in st.session_state:
                    st.session_state.ai_chat_history = [
                        {
                            "role": "assistant",
                            "content": "Hello! I am your clinical assistant. Describe the patient's symptoms, and I will help identify possible diagnoses and treatment guidance."
                        }
                    ]

                for msg in st.session_state.ai_chat_history:
                    if msg["role"] == "assistant":
                        st.markdown(
                            f"<div style='background:#111827;color:#e2e8f0;border-radius:12px;padding:14px;margin-bottom:10px;line-height:1.5;'><strong style='color:#60a5fa;'>AI:</strong> {msg['content']}</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"<div style='background:#1f2937;color:#e2e8f0;border-radius:12px;padding:14px;margin-bottom:10px;line-height:1.5;'><strong style='color:#c7d2fe;'>You:</strong> {msg['content']}</div>",
                            unsafe_allow_html=True
                        )

                if "ai_chat_input" not in st.session_state:
                    st.session_state.ai_chat_input = ""

                ai_input = st.text_area(
                    "Ask the assistant about symptoms or management",
                    key="ai_chat_input",
                    height=120,
                    placeholder="e.g. Patient has fever, cough, mild chest tightness, and fatigue for 3 days."
                )

                c1, c2 = st.columns([3, 1])
                with c1:
                    st.button(
                        "Send to AI",
                        key="ai_chat_send",
                        use_container_width=True,
                        on_click=handle_ai_chat_send,
                    )
                with c2:
                    st.button(
                        "Reset chat",
                        key="ai_chat_reset",
                        use_container_width=True,
                        on_click=handle_ai_chat_reset,
                    )

                st.markdown("**Tip:** Ask clinical follow-up questions such as `What are red flags?`, `What should I monitor?`, or `What is the likely diagnosis?`")

        with tab_view:
            st.markdown("#### 🔍 Search Patient Records")
            search_p = st.text_input("Patient ID (e.g., PT-001)", key="doc_search")
            if st.button("Fetch Records", use_container_width=True, key="doc_fetch"):
                if not search_p:
                    st.warning("Enter a Patient ID.")
                elif bc.check_permission(search_p, u["id"]):
                    st.success(f"✅ Access granted for {search_p}")
                    if bc.has_emergency_access(search_p, u["id"]) and not bc.has_regular_access(search_p, u["id"]):
                        st.warning("🚨 Emergency break-glass access active for this patient.")
                    st.divider()

                    uploads = [b for b in bc.chain if b["data"].get("op") == "UPLOAD_RECORD" and b["data"].get("patient") == search_p]
                    prescriptions = [b for b in bc.chain if b["data"].get("op") == "DIAGNOSIS" and b["data"].get("patient") == search_p]
                    nurse_notes = bc.get_nurse_notes(search_p)

                    col_u, col_p = st.columns(2)

                    with col_u:
                        st.markdown("### 📤 Patient Uploads")
                        if not uploads:
                            st.info("No files uploaded by patient.")
                        for b in reversed(uploads):
                            d = b["data"]
                            with st.container(border=True):
                                st.markdown(f"**{d.get('file_name','File')}**")
                                st.caption(f"📅 {d.get('timestamp','')}")
                                
                                # NEW LOCAL STORAGE FETCH
                                file_path = d.get("file_path")
                                if file_path and os.path.exists(file_path):
                                    with open(file_path, "rb") as f:
                                        file_bytes = f.read()
                                    st.download_button("📥 Download", file_bytes,
                                                       d["file_name"], d.get("mime_type","application/octet-stream"),
                                                       key=f"dl_{b['hash']}", use_container_width=True)
                                else:
                                    st.error("File missing from server storage.")

                    with col_p:
                        st.markdown("### 📜 Past Diagnoses")
                        if not prescriptions:
                            st.info("No diagnoses yet.")
                        for b in reversed(prescriptions):
                            d = b["data"]
                            with st.container(border=True):
                                st.markdown(f"**Dr. {d.get('doctor_name','?')}**")
                                st.caption(f"📅 {b['timestamp']}")
                                st.markdown(f"**Condition:** {d.get('condition','N/A')}")
                                st.markdown(f"**Rx:** {d.get('rx','N/A')}")

                    if nurse_notes:
                        st.divider()
                        st.markdown("### 💉 Nurse Treatment Notes")
                        for b in reversed(nurse_notes):
                            d = b["data"]
                            with st.container(border=True):
                                st.markdown(f"**Nurse {d.get('nurse_name','?')}** (`{d.get('nurse','')}`)  ·  📅 {b['timestamp']}")
                                st.write(d.get("note", ""))
                else:
                    st.error("❌ Access Denied: Patient has not authorized you.")

        with tab_mypts:
            st.markdown("### 👥 My Patient List")
            st.caption("All patients who have granted you access to their records.")

            my_patients = {}
            for i, block in enumerate(bc.chain):
                d = block["data"]
                if d.get("op") == "GRANT_ACCESS" and d.get("doctor") == u["id"]:
                    pid = d["patient"]
                    revoked = any(
                        b2["data"].get("op") == "REVOKE_ACCESS"
                        and b2["data"].get("patient") == pid
                        and b2["data"].get("doctor") == u["id"]
                        for b2 in bc.chain[i+1:]
                    )
                    if not revoked:
                        my_patients[pid] = block["timestamp"]

            if not my_patients:
                st.info("No patients have granted you access yet.")
            else:
                search_q = st.text_input("🔍 Search by Patient ID or Name", placeholder="Type name or ID…", key="mypts_search")

                filtered = {}
                for pid, granted_ts in my_patients.items():
                    pinfo = users_db["PATIENTS"].get(pid, {})
                    name  = pinfo.get("name", "")
                    if search_q.lower() in pid.lower() or search_q.lower() in name.lower():
                        filtered[pid] = (granted_ts, pinfo)

                st.caption(f"Showing {len(filtered)} of {len(my_patients)} patient(s)")
                st.divider()

                for pid, (granted_ts, pinfo) in filtered.items():
                    nurse_id    = bc.get_patient_nurse(pid)
                    nurse_name  = users_db["NURSES"].get(nurse_id, {}).get("name", "None") if nurse_id else "None"
                    diag_blocks = [b for b in bc.chain if b["data"].get("op") == "DIAGNOSIS"
                                   and b["data"].get("patient") == pid
                                   and b["data"].get("doctor") == u["id"]]
                    uploads     = [b for b in bc.chain if b["data"].get("op") == "UPLOAD_RECORD"
                                   and b["data"].get("patient") == pid]

                    with st.expander(f"🧑‍⚕️  {pinfo.get('name','?')}   ·   `{pid}`   ·   {len(diag_blocks)} prescription(s)  ·  {len(uploads)} upload(s)", expanded=False):
                        col_info, col_stats = st.columns([3, 1])

                        with col_info:
                            st.markdown(f"**Patient Name:** {pinfo.get('name','?')}")
                            st.markdown(f"**Patient ID:** `{pid}`")
                            st.markdown(f"**Access Granted:** {granted_ts}")
                            st.markdown(f"**Assigned Nurse:** 💉 {nurse_name}" + (f" (`{nurse_id}`)" if nurse_id else ""))

                        with col_stats:
                            st.metric("My Prescriptions", len(diag_blocks))
                            st.metric("Patient Uploads", len(uploads))

                        st.divider()

                        sub_rx, sub_uploads = st.tabs(["📜 My Prescriptions", "📁 Patient's Previous Records"])

                        with sub_rx:
                            if not diag_blocks:
                                st.info("You haven't written any prescriptions for this patient yet.")
                            for b in reversed(diag_blocks):
                                d = b["data"]
                                with st.container(border=True):
                                    st.caption(f"📅 {b['timestamp']}")
                                    st.markdown(f"**Condition:** {d.get('condition','N/A')}")
                                    st.markdown(f"**Rx:** {d.get('rx','N/A')}")
                                    pdf = create_pdf(u["name"], b["timestamp"], pid,
                                                     d.get("condition","N/A"), d.get("rx","N/A"))
                                    st.download_button("📥 Download PDF", pdf,
                                                       f"Rx_{pid}_{b['index']}.pdf",
                                                       "application/pdf",
                                                       key=f"mypt_pdf_{b['hash']}")

                        with sub_uploads:
                            if not uploads:
                                st.info("This patient has not uploaded any previous records.")
                            for b in reversed(uploads):
                                d = b["data"]
                                with st.container(border=True):
                                    col_a, col_b = st.columns([3, 1])
                                    with col_a:
                                        st.markdown(f"**📄 {d.get('file_name','Unknown')}**")
                                        st.caption(f"📅 Uploaded: {d.get('timestamp','')}  ·  Type: {d.get('mime_type','')}")
                                    with col_b:
                                        # NEW LOCAL STORAGE FETCH
                                        file_path = d.get("file_path")
                                        if file_path and os.path.exists(file_path):
                                            with open(file_path, "rb") as f:
                                                file_bytes = f.read()
                                            st.download_button("📥 Download",
                                                               file_bytes,
                                                               d["file_name"],
                                                               d.get("mime_type","application/octet-stream"),
                                                               key=f"mypt_dl_{b['hash']}",
                                                               use_container_width=True)
                                        else:
                                            st.error("File missing.")

    # ════════════════════════════════════════
    #   PATIENT DASHBOARD
    # ════════════════════════════════════════
    elif role == "PATIENT":
        render_header(u["name"], "Health Records Portal")

        patient_record = users_db["PATIENTS"].get(u["id"])

        if "private_key" not in patient_record:
            priv, pub = RSAKeyManager.generate_keypair()
            patient_record["public_key"]  = RSAKeyManager.serialize_public_key(pub)
            patient_record["private_key"] = RSAKeyManager.serialize_private_key(priv)
            users_db["PATIENTS"][u["id"]] = patient_record
            save_users(users_db)
            st.rerun()

        assigned_nurse_id = bc.get_patient_nurse(u["id"])
        if not assigned_nurse_id and users_db["NURSES"]:
            assigned_nurse_id = bc.auto_assign_nurse(u["id"], users_db["NURSES"])

        patient_priv = RSAKeyManager.deserialize_private_key(patient_record["private_key"])
        patient_pub  = RSAKeyManager.deserialize_public_key(patient_record["public_key"])

        if assigned_nurse_id:
            nurse_info = users_db["NURSES"].get(assigned_nurse_id, {})
            st.markdown(f"""
            <div style="background: linear-gradient(135deg,#1e40af,#4338ca); border-left:5px solid #60a5fa; border-radius:16px;
                        padding:20px 24px; margin-bottom:18px; display:flex; align-items:center; gap:14px; color:#eff6ff; box-shadow:0 14px 30px rgba(15,23,42,0.32);">
                <span style="font-size:1.7em;">💉</span>
                <div>
                    <div style="font-size:0.85em; color:#bfdbfe; font-weight:700; letter-spacing:.08em; text-transform:uppercase; margin-bottom:4px;">Your Assigned Nurse</div>
                    <div style="font-size:1.2em; font-weight:800; color:#fff;">{nurse_info.get('name','?')}</div>
                    <div style="font-size:0.9em; color:#c7d2fe; margin-top:4px;">ID: <code style="background:rgba(255,255,255,0.12); padding:2px 8px; border-radius:6px; color:#f8fafc;">{assigned_nurse_id}</code>
                    &nbsp;<span style="background:#2563eb; color:#fff; padding:4px 12px; border-radius:16px; font-size:0.78em; font-weight:700;">Currently Treating You</span></div>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div style="background:#111827; border-left:5px solid #b91c1c; border-radius:12px; padding:16px 22px; margin-bottom:18px; color:#f8fafc; font-weight:600;">⚠️ No nurse assigned yet. Please wait for a nurse to become available.</div>', unsafe_allow_html=True)

        tab_rec, tab_upload, tab_perm = st.tabs(
            ["📜 My Records", "📤 Upload Records", "🔐 Doctor Access"])

        with tab_rec:
            st.markdown("### 📜 Your Medical Records")
            prescriptions = [b for b in bc.chain if b["data"].get("op") == "DIAGNOSIS"
                             and b["data"].get("patient") == u["id"]]
            if not prescriptions:
                st.info("No records yet. Your doctor will add them.")
            for b in reversed(prescriptions):
                d = b["data"]
                with st.container(border=True):
                    ca, cb = st.columns([4, 1])
                    with ca:
                        st.markdown(f"### 👨‍⚕️ {d.get('doctor_name','?')}")
                        st.caption(f"📅 {b['timestamp']}")
                        st.markdown(f"**Diagnosis:** {d.get('condition','N/A')}")
                        st.markdown(f"**Treatment:** {d.get('rx','N/A')}")
                    with cb:
                        pdf = create_pdf(d.get('doctor_name','N/A'), b['timestamp'],
                                         u['id'], d.get('condition','N/A'), d.get('rx','N/A'))
                        st.download_button("📥 PDF", pdf, f"Record_{b['index']}.pdf",
                                           "application/pdf", use_container_width=True)

        with tab_upload:
            st.markdown("### 📤 Upload Health Records")
            st.caption("Upload past lab results, X-rays, or reports. They will be saved to the local server storage and secured on the blockchain.")
            uploaded = st.file_uploader("PDF, JPG, or PNG", type=["pdf","png","jpg","jpeg"])
            if uploaded and st.button("🔒 Secure & Upload", use_container_width=True):
                
                # NEW LOCAL STORAGE UPLOAD LOGIC
                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                timestamp_bc = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Create a clean, timestamped file name
                safe_filename = f"{u['id']}_{timestamp_str}_{uploaded.name.replace(' ', '_')}"
                file_path = os.path.join(UPLOAD_DIR, safe_filename)

                # Save the physical file to the hard drive
                with open(file_path, "wb") as f:
                    f.write(uploaded.getbuffer())

                # Secure the PATH in the blockchain ledger instead of Base64
                bc.create_block({
                    "op": "UPLOAD_RECORD", "patient": u["id"],
                    "file_name": uploaded.name, "mime_type": uploaded.type,
                    "file_path": file_path,  # Storing the path reference
                    "timestamp": timestamp_bc
                }, bc.chain[-1]["hash"])
                
                st.success(f"✅ Document secured! File saved locally as `{safe_filename}`")

        with tab_perm:
            st.markdown("### 🔐 Manage Doctor Access")

            granted = {}
            for i, block in enumerate(bc.chain):
                d = block["data"]
                if d.get("op") == "GRANT_ACCESS" and d.get("patient") == u["id"]:
                    doc_id = d["doctor"]
                    revoked = any(
                        b2["data"].get("op") == "REVOKE_ACCESS"
                        and b2["data"].get("patient") == u["id"]
                        and b2["data"].get("doctor") == doc_id
                        for b2 in bc.chain[i+1:]
                    )
                    if not revoked:
                        granted[doc_id] = block["timestamp"]

            st.markdown("#### ✅ Active Permissions")
            if granted:
                c1, c2 = st.columns(2)
                c1.metric("Total Doctors", len(granted))
                c2.metric("Status", "🟢 Active")
                st.divider()
                for doc_id, ts in sorted(granted.items()):
                    info = users_db["DOCTORS"].get(doc_id)
                    if info:
                        with st.container(border=True):
                            cl, cr = st.columns([4, 1])
                            with cl:
                                st.markdown(f"### 👨‍⚕️ {info['name']}")
                                st.caption(f"ID: `{doc_id}` · Granted: {ts}")
                                st.markdown('<span class="badge badge-active">🟢 Active</span>', unsafe_allow_html=True)
                            with cr:
                                if st.button("🔒 Revoke", key=f"rev_{doc_id}", use_container_width=True):
                                    bc.create_block({"op": "REVOKE_ACCESS", "patient": u["id"], "doctor": doc_id},
                                                    bc.chain[-1]["hash"])
                                    st.rerun()
            else:
                st.info("No doctors have access yet.")

            emergency_overrides = bc.get_active_emergency_accesses(u["id"])
            if emergency_overrides:
                st.markdown("#### ⚠️ Active Emergency Overrides")
                for block in emergency_overrides:
                    d = block["data"]
                    st.markdown(f"- **Doctor:** `{d.get('doctor')}`  ·  Expires: {d.get('expires_at')}  ·  Reason: {d.get('reason')}")

            audit_log = bc.get_emergency_audit_log(u["id"])
            st.markdown("#### 🧾 Emergency Audit History")
            if not audit_log:
                st.info("No emergency override events have been recorded for your account.")
            else:
                for block in reversed(audit_log[-10:]):
                    d = block["data"]
                    if d.get("op") == "EMERGENCY_ACCESS":
                        st.markdown(f"- **Granted** to `{d.get('doctor')}` by `{d.get('authority')}` on {block.get('timestamp')} · expires {d.get('expires_at')} · reason: {d.get('reason')}")
                    else:
                        st.markdown(f"- **Revoked** for `{d.get('doctor')}` by `{d.get('revoked_by', 'unknown')}` on {block.get('timestamp')} · reason: {d.get('revoked_reason', 'N/A')}")

            st.divider()
            st.markdown("#### ➕ Grant New Access")
            available_docs = {f"{v['name']} ({k})": k
                              for k, v in users_db["DOCTORS"].items() if k not in granted}
            if available_docs:
                sel = st.selectbox("Select Doctor", list(available_docs.keys()))
                target = available_docs[sel]
                if st.button("✅ Grant Access", use_container_width=True):
                    doc_info = users_db["DOCTORS"][target]
                    if "public_key" not in doc_info:
                        priv, pub = RSAKeyManager.generate_keypair()
                        doc_info["public_key"]  = RSAKeyManager.serialize_public_key(pub)
                        doc_info["private_key"] = RSAKeyManager.serialize_private_key(priv)
                        users_db["DOCTORS"][target] = doc_info
                        save_users(users_db)
                    doc_pub = RSAKeyManager.deserialize_public_key(doc_info["public_key"])
                    re_key  = ProxyReEncryption.generate_reencryption_key(patient_priv, doc_pub)
                    bc.create_block({"op": "GRANT_ACCESS", "patient": u["id"], "doctor": target,
                                     "reencryption_key": re_key}, bc.chain[-1]["hash"])
                    st.success(f"✅ Access granted to {sel}!")
                    st.rerun()
            else:
                st.info("All registered doctors already have access.")

    # ════════════════════════════════════════
    #   NURSE DASHBOARD
    # ════════════════════════════════════════
    elif role == "NURSE":
        render_header(f"Nurse {u['name']}", "Treatment Assistant", "header-nurse")

        assigned_patient = bc.get_nurse_patient(u["id"])

        if not assigned_patient:
            st.markdown("""
            <div class="card card-nurse">
                <h3>💤 Currently Unassigned</h3>
                <p>You are <strong>available</strong>. You will be automatically assigned to the next
                registered patient who needs a nurse.</p>
            </div>""", unsafe_allow_html=True)

            st.markdown("### 📊 Your Statistics")
            served = set()
            for block in bc.chain:
                d = block["data"]
                if d.get("op") == "ASSIGN_NURSE" and d.get("nurse") == u["id"]:
                    served.add(d["patient"])
            st.metric("Total Patients Served", len(served))

        else:
            patient_info = users_db["PATIENTS"].get(assigned_patient, {})
            st.markdown(f"""
            <div class="card card-nurse">
                <h3>💉 Currently Treating</h3>
                <p><strong>Patient Name:</strong> {patient_info.get('name','Unknown')}</p>
                <p><strong>Patient ID:</strong> <code>{assigned_patient}</code></p>
                <p><span class="badge badge-nurse">Active Assignment</span></p>
            </div>""", unsafe_allow_html=True)

            tab_notes, tab_vitals, tab_history = st.tabs(
                ["📝 Add Treatment Note", "📋 Patient Summary", "📜 All My Notes"])

            with tab_notes:
                st.markdown("### 📝 Add Treatment Note")
                st.caption("Notes are visible to the patient's authorized doctors. You cannot see diagnosis details.")
                note_text = st.text_area("Treatment Note / Observation",
                                         placeholder="e.g., Patient administered 500mg paracetamol at 10:00 AM. Blood pressure checked: 120/80. Patient resting comfortably.",
                                         height=160)
                if st.button("💾 Save Note to Blockchain", use_container_width=True):
                    if note_text.strip():
                        bc.create_block({
                            "op": "NURSE_NOTE",
                            "nurse": u["id"],
                            "nurse_name": u["name"],
                            "patient": assigned_patient,
                            "note": note_text.strip(),
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }, bc.chain[-1]["hash"])
                        st.success("✅ Note saved to blockchain!")
                    else:
                        st.warning("Please write a note before saving.")

            with tab_vitals:
                st.markdown("### 📋 Patient Overview")
                st.info("🔒 As a nurse, you can see patient identity and your own notes, but **not** medical diagnoses or prescriptions.")

                with st.container(border=True):
                    st.markdown(f"**Patient Name:** {patient_info.get('name','Unknown')}")
                    st.markdown(f"**Patient ID:** `{assigned_patient}`")
                    st.markdown(f"**Assigned Nurse:** {u['name']} (`{u['id']}`)")

                    authorized_doctors = []
                    for block in bc.chain:
                        d = block["data"]
                        if d.get("op") == "GRANT_ACCESS" and d.get("patient") == assigned_patient:
                            doc_id = d["doctor"]
                            revoked = any(
                                b2["data"].get("op") == "REVOKE_ACCESS"
                                and b2["data"].get("patient") == assigned_patient
                                and b2["data"].get("doctor") == doc_id
                                for b2 in bc.chain[bc.chain.index(block)+1:]
                            )
                            if not revoked and doc_id not in authorized_doctors:
                                authorized_doctors.append(doc_id)

                    if authorized_doctors:
                        st.markdown(f"**Authorized Doctors:** " +
                                    ", ".join(f"Dr. {users_db['DOCTORS'].get(d,{}).get('name','?')} (`{d}`)"
                                              for d in authorized_doctors))
                    else:
                        st.caption("No doctors authorized yet.")

            with tab_history:
                st.markdown("### 📜 Your Notes for This Patient")
                notes = bc.get_nurse_notes(assigned_patient)
                my_notes = [b for b in notes if b["data"].get("nurse") == u["id"]]
                if not my_notes:
                    st.info("You haven't added any notes yet.")
                for b in reversed(my_notes):
                    d = b["data"]
                    with st.container(border=True):
                        st.caption(f"📅 {b['timestamp']}")
                        st.write(d.get("note", ""))

    # ════════════════════════════════════════
    #   HOSPITAL AUTHORITY DASHBOARD
    # ════════════════════════════════════════
    elif role == "AUTHORITY":
        render_header(u["name"], "Hospital Authority — Full System Access", "header-auth")

        st.markdown("### 📊 System Overview")
        total_docs   = len(users_db["DOCTORS"])
        total_pts    = len(users_db["PATIENTS"])
        total_nurses = len(users_db["NURSES"])
        total_auths  = len(users_db["AUTHORITIES"])
        
        cols = st.columns(4)
        stats = [
            ("👨‍⚕️ Doctors", total_docs, "#0066cc"),
            ("🧑‍⚕️ Patients", total_pts, "#00aa66"),
            ("💉 Nurses", total_nurses, "#7c3aed"),
            ("🏛️ Authorities", total_auths, "#b45309"),
        ]
        for col, (label, val, color) in zip(cols, stats):
            col.markdown(f"""
            <div class="stat-box">
                <div class="stat-val" style="color:{color}">{val}</div>
                <div class="stat-lbl">{label}</div>
            </div>""", unsafe_allow_html=True)

        st.divider()

        tab_nurses, tab_patients, tab_doctors, tab_records, tab_emergency, tab_chain, tab_backup = st.tabs([
            "💉 Nurse Management", "🧑‍⚕️ Patients", "👨‍⚕️ Doctors",
            "📜 All Records", "🚨 Emergency Access", "⛓️ Blockchain", "💾 Data Backup"
        ])

        # ─── Nurse Management ───
        with tab_nurses:
            st.markdown("### 💉 Nurse Assignment Dashboard")

            c1, c2 = st.columns([1,1])
            with c1:
                assigned_nurses  = [nid for nid in users_db["NURSES"] if bc.get_nurse_patient(nid)]
                available_nurses = [nid for nid in users_db["NURSES"] if not bc.get_nurse_patient(nid)]
                st.metric("Nurses On Duty", len(assigned_nurses))
                st.metric("Nurses Available", len(available_nurses))

            st.divider()
            st.markdown("#### 🗂️ All Nurses")

            if not users_db["NURSES"]:
                st.info("No nurses registered yet.")
            else:
                for nid, ninfo in users_db["NURSES"].items():
                    patient_id = bc.get_nurse_patient(nid)
                    with st.container(border=True):
                        cl, cr = st.columns([4, 1])
                        with cl:
                            st.markdown(f"### 💉 {ninfo['name']}")
                            st.caption(f"ID: `{nid}`")
                            if patient_id:
                                pname = users_db["PATIENTS"].get(patient_id, {}).get("name", "?")
                                st.markdown(f"**Assigned to:** {pname} (`{patient_id}`)")
                                st.markdown('<span class="badge badge-nurse">🟣 On Duty</span>', unsafe_allow_html=True)
                            else:
                                st.markdown("**Status:** Available")
                                st.markdown('<span class="badge badge-active">🟢 Available</span>', unsafe_allow_html=True)
                        with cr:
                            if patient_id:
                                if st.button("🔓 Release", key=f"rel_{nid}", use_container_width=True):
                                    bc.create_block(
                                        {"op": "RELEASE_NURSE", "nurse": nid, "patient": patient_id,
                                         "released_by": u["id"]},
                                        bc.chain[-1]["hash"]
                                    )
                                    st.success(f"✅ {ninfo['name']} released from {patient_id}")
                                    st.rerun()

            st.divider()
            st.markdown("#### ➕ Manual Nurse Assignment")
            if available_nurses and users_db["PATIENTS"]:
                nurse_opts = {f"{users_db['NURSES'][nid]['name']} ({nid})": nid for nid in available_nurses}
                unassigned_pts = [pid for pid in users_db["PATIENTS"] if not bc.get_patient_nurse(pid)]
                if unassigned_pts:
                    pt_opts = {f"{users_db['PATIENTS'][pid]['name']} ({pid})": pid for pid in unassigned_pts}
                    ca, cb, cc = st.columns([2,2,1])
                    with ca: sel_n = st.selectbox("Nurse", list(nurse_opts.keys()), key="man_nurse")
                    with cb: sel_p = st.selectbox("Patient", list(pt_opts.keys()), key="man_pt")
                    with cc:
                        st.write("")
                        st.write("")
                        if st.button("Assign", use_container_width=True, key="manual_assign"):
                            nid = nurse_opts[sel_n]
                            pid = pt_opts[sel_p]
                            bc.create_block({"op": "ASSIGN_NURSE", "nurse": nid, "patient": pid,
                                             "assigned_by": u["id"]}, bc.chain[-1]["hash"])
                            st.success(f"✅ {sel_n} assigned to {sel_p}!")
                            st.rerun()
                else:
                    st.info("All patients already have a nurse assigned.")
            else:
                st.info("Need both available nurses and unassigned patients for manual assignment.")

        # ─── Patients tab ───
        with tab_patients:
            st.markdown("### 🧑‍⚕️ All Patients")
            if not users_db["PATIENTS"]:
                st.info("No patients registered yet.")
            else:
                for pid, pinfo in users_db["PATIENTS"].items():
                    nurse_id = bc.get_patient_nurse(pid)
                    nurse_name = users_db["NURSES"].get(nurse_id, {}).get("name", "None") if nurse_id else "Unassigned"
                    doc_grants = sum(1 for b in bc.chain
                                     if b["data"].get("op") == "GRANT_ACCESS"
                                     and b["data"].get("patient") == pid)
                    diag_count = sum(1 for b in bc.chain
                                     if b["data"].get("op") == "DIAGNOSIS"
                                     and b["data"].get("patient") == pid)
                    with st.container(border=True):
                        c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
                        with c1:
                            st.markdown(f"**{pinfo['name']}** ·  `{pid}`")
                            nurse_badge = "badge-nurse" if nurse_id else "badge-inactive"
                            st.markdown(f'<span class="badge {nurse_badge}">💉 {nurse_name}</span>',
                                        unsafe_allow_html=True)
                        with c2: st.caption(f"Authorized Doctors: {doc_grants}")
                        with c3: st.metric("Records", diag_count)
                        with c4:
                            if not nurse_id and users_db["NURSES"]:
                                if st.button("Auto-Assign Nurse", key=f"aa_{pid}", use_container_width=True):
                                    nid = bc.auto_assign_nurse(pid, users_db["NURSES"])
                                    if nid:
                                        st.success(f"Assigned {users_db['NURSES'][nid]['name']}!")
                                        st.rerun()
                                    else:
                                        st.error("No nurses available.")

        # ─── Doctors tab ───
        with tab_doctors:
            st.markdown("### 👨‍⚕️ All Doctors")
            if not users_db["DOCTORS"]:
                st.info("No doctors registered yet.")
            for did, dinfo in users_db["DOCTORS"].items():
                diag_count = sum(1 for b in bc.chain
                                 if b["data"].get("op") == "DIAGNOSIS"
                                 and b["data"].get("doctor") == did)
                pt_count = len(set(b["data"]["patient"] for b in bc.chain
                                   if b["data"].get("op") == "GRANT_ACCESS"
                                   and b["data"].get("doctor") == did))
                with st.container(border=True):
                    c1, c2, c3 = st.columns([4, 1, 1])
                    with c1:
                        st.markdown(f"**Dr. {dinfo['name']}** · `{did}`")
                        st.markdown('<span class="badge badge-active">🟢 Active</span>', unsafe_allow_html=True)
                    with c2: st.metric("Prescriptions", diag_count)
                    with c3: st.metric("Patients", pt_count)

        # ─── All Records tab ───
        with tab_records:
            st.markdown("### 📜 All Medical Records (Authority View)")
            all_diag = [b for b in bc.chain if b["data"].get("op") == "DIAGNOSIS"]
            all_uploads = [b for b in bc.chain if b["data"].get("op") == "UPLOAD_RECORD"]
            all_notes = [b for b in bc.chain if b["data"].get("op") == "NURSE_NOTE"]

            sub1, sub2, sub3 = st.tabs(["🩺 Diagnoses", "📤 Uploads", "💉 Nurse Notes"])

            with sub1:
                if not all_diag:
                    st.info("No diagnoses on record.")
                for b in reversed(all_diag):
                    d = b["data"]
                    with st.container(border=True):
                        st.markdown(f"**Dr. {d.get('doctor_name','?')}** → Patient `{d.get('patient','?')}`  ·  📅 {b['timestamp']}")
                        st.markdown(f"**Condition:** {d.get('condition','N/A')}  ·  **Rx:** {d.get('rx','N/A')}")

            with sub2:
                st.info("🔒 File contents are private — only authorized doctors can download patient uploads.")
                if not all_uploads:
                    st.info("No uploads on record.")
                for b in reversed(all_uploads):
                    d = b["data"]
                    with st.container(border=True):
                        st.markdown(f"Patient `{d.get('patient','?')}` uploaded **{d.get('file_name','?')}**")
                        # UPDATED AUTHORITY VIEW to show local storage reference
                        st.caption(f"📅 {d.get('timestamp','')}  ·  Type: {d.get('mime_type','unknown')}  ·  🗂️ Stored at: `{d.get('file_path', 'unknown')}`")

            with sub3:
                if not all_notes:
                    st.info("No nurse notes on record.")
                for b in reversed(all_notes):
                    d = b["data"]
                    with st.container(border=True):
                        st.markdown(f"**{d.get('nurse_name','?')}** → Patient `{d.get('patient','?')}`  ·  📅 {b['timestamp']}")
                        st.write(d.get("note",""))

        # ─── Emergency Access tab ───
        with tab_emergency:
            st.markdown("### 🚨 Emergency Break-Glass Access")
            st.info("Use this only when a patient cannot grant consent and immediate doctor access is required. Every break-glass event is logged and expires automatically.")

            patients = [f"{p['name']} ({pid})" for pid, p in users_db["PATIENTS"].items()]
            doctors = [f"Dr. {d['name']} ({did})" for did, d in users_db["DOCTORS"].items()]

            if not patients or not doctors:
                st.warning("Need both registered patients and doctors to grant emergency access.")
            else:
                p_sel = st.selectbox("Select Patient", patients, key="emerg_pt")
                d_sel = st.selectbox("Select Doctor", doctors, key="emerg_doc")
                reason = st.text_area("Reason for Emergency Access", height=100,
                                      placeholder="e.g. Patient unconscious, immediate life-saving treatment required.")
                duration = st.selectbox("Access Duration", ["4 hours", "8 hours", "24 hours", "48 hours"], key="emerg_dur")
                dur_map = {"4 hours": 4, "8 hours": 8, "24 hours": 24, "48 hours": 48}

                if st.button("Grant Emergency Access", use_container_width=True):
                    pid = p_sel.split("(")[-1].strip(")")
                    did = d_sel.split("(")[-1].strip(")")
                    if not reason.strip():
                        st.warning("Please provide a reason for the emergency override.")
                    else:
                        expires = datetime.now() + timedelta(hours=dur_map[duration])
                        bc.create_block({
                            "op": "EMERGENCY_ACCESS",
                            "patient": pid,
                            "doctor": did,
                            "authority": u["id"],
                            "reason": reason.strip(),
                            "duration_hours": dur_map[duration],
                            "expires_at": expires.strftime("%Y-%m-%d %H:%M:%S"),
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }, bc.chain[-1]["hash"])
                        st.success(f"✅ Emergency access granted to {d_sel} for {duration}.")
                        st.rerun()

            st.divider()
            st.markdown("#### 🔎 Active Emergency Overrides")
            active_overrides = bc.get_active_emergency_accesses()
            if not active_overrides:
                st.info("No active emergency break-glass overrides.")
            else:
                for block in active_overrides:
                    data = block["data"]
                    with st.container(border=True):
                        st.markdown(f"**Patient:** `{data.get('patient')}`  ·  **Doctor:** `{data.get('doctor')}`")
                        st.markdown(f"**Granted by:** `{data.get('authority')}`  ·  Expires: {data.get('expires_at')}")
                        st.markdown(f"**Reason:** {data.get('reason')}")
                        if st.button("Revoke Emergency Access", key=f"revoke_emerg_{block['hash']}", use_container_width=True):
                            bc.create_block({
                                "op": "REVOKE_ACCESS",
                                "patient": data.get('patient'),
                                "doctor": data.get('doctor'),
                                "revoked_by": u["id"],
                                "revoked_reason": "Authority revocation"
                            }, bc.chain[-1]["hash"])
                            st.success("✅ Emergency override revoked.")
                            st.rerun()

            st.divider()
            st.markdown("#### 🧾 Emergency Audit Log")
            audit_log = bc.get_emergency_audit_log()
            if not audit_log:
                st.info("No emergency override events have been recorded yet.")
            else:
                for block in reversed(audit_log[-25:]):
                    data = block["data"]
                    event_type = data.get("op")
                    with st.container(border=True):
                        if event_type == "EMERGENCY_ACCESS":
                            st.markdown(f"**[GRANTED]** `{data.get('patient')}` → `{data.get('doctor')}`")
                            st.markdown(f"**By:** `{data.get('authority')}`  ·  Expires: {data.get('expires_at')}")
                            st.markdown(f"**Reason:** {data.get('reason')}")
                        else:
                            st.markdown(f"**[REVOKED]** `{data.get('patient')}` → `{data.get('doctor')}`")
                            st.markdown(f"**By:** `{data.get('revoked_by', 'unknown')}`  ·  Reason: {data.get('revoked_reason', 'N/A')}")
                        st.caption(f"Recorded: {block.get('timestamp')}")

        # ─── Blockchain tab ───
        with tab_chain:
            st.markdown("### ⛓️ Full Blockchain Ledger")
            st.metric("Total Blocks", len(bc.chain))
            st.divider()
            for block in reversed(bc.chain):
                op = block["data"].get("op","—")
                with st.expander(f"Block #{block['index']}  ·  {op}  ·  {block['timestamp']}"):
                    st.json(block)
                    
        # ─── Data Backup tab ───
        with tab_backup:
            st.markdown("### 💾 Local Device Backup")
            st.info(f"Your uploaded files (PDFs, Images) are physically saved on your server inside the `{UPLOAD_DIR}` folder. You can download the JSON ledgers below.")

            col1, col2 = st.columns(2)
            
            with col1:
                with st.container(border=True):
                    st.markdown("#### ⛓️ Blockchain Ledger")
                    st.caption("Contains all patient records, diagnoses, file path references, and nurse notes.")
                    if os.path.exists(LEDGER_FILE):
                        with open(LEDGER_FILE, "rb") as f:
                            ledger_data = f.read()
                        
                        st.download_button(
                            label="📥 Download medical_ledger.json",
                            data=ledger_data,
                            file_name=f"medical_ledger_backup_{datetime.now().strftime('%Y%m%d')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    else:
                        st.warning("Ledger file not found on server.")

            with col2:
                with st.container(border=True):
                    st.markdown("#### 👥 User Database")
                    st.caption("Contains all registered Doctors, Patients, Nurses, Authorities, and passwords.")
                    if os.path.exists(USER_FILE):
                        with open(USER_FILE, "rb") as f:
                            user_data = f.read()
                        
                        st.download_button(
                            label="📥 Download users.json",
                            data=user_data,
                            file_name=f"users_backup_{datetime.now().strftime('%Y%m%d')}.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    else:
                        st.warning("User file not found on server.")