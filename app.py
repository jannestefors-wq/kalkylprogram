#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kalkylprogram Bygg & Entreprenad – Streamlit-version
"""

import streamlit as st
import pandas as pd
import json
import datetime
import copy
import io

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    OPX_OK = True
except ImportError:
    OPX_OK = False

try:
    from reportlab.lib import colors as rl_colors
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    RL_OK = True
except ImportError:
    RL_OK = False

# ──────────────────────────────────────────────────────────────
#  CONFIG & CONSTANTS
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kalkylprogram – Bygg & Entreprenad",
    page_icon="🏗",
    layout="wide",
    initial_sidebar_state="expanded",
)

RADTYPER    = ["Material", "Arbete", "UE"]
ENHETER     = ["st", "m", "m²", "m³", "kg", "ton", "tim", "pers", "ls", "rund"]
STATUS_LIST = ["Kalkyl", "Offert", "Pågående", "Vunnen", "Förlorad", "Avslutad", "Pausad"]
BYGGDEL_DEF = ["Badrum", "Kök", "Vägg", "Etapp 1", "Rivning", "Snickeri",
               "Grund", "Fasad", "Tak", "El", "VVS", "Övrigt"]
OMKKOSTNADER = ["Arbetsledning", "Etablering", "Administration",
                "Transporter", "Garanti", "Risk", "Övrigt"]
BKI = {
    "Flerbostadshus": {"2018":175.2,"2019":180.1,"2020":183.5,"2021":192.4,
                       "2022":215.8,"2023":228.3,"2024":232.1,"2025":238.5,"2026":242.0},
    "Småhus":         {"2018":168.4,"2019":173.2,"2020":177.8,"2021":186.3,
                       "2022":208.9,"2023":221.7,"2024":225.4,"2025":231.0,"2026":234.5},
    "ROT/Ombyggnad":  {"2018":171.3,"2019":176.5,"2020":180.2,"2021":189.1,
                       "2022":212.1,"2023":224.9,"2024":228.7,"2025":234.8,"2026":238.2},
}

# ──────────────────────────────────────────────────────────────
#  UTILITIES
# ──────────────────────────────────────────────────────────────
def sfloat(v, d=0.0):
    try:
        return float(str(v).replace(" ", "").replace(",", "."))
    except:
        return d

def fmt_kr(v):
    try:
        return f"{float(v):,.0f} kr".replace(",", " ")
    except:
        return "0 kr"

def fmt_pct(v):
    try:
        return f"{float(v):.1f} %"
    except:
        return "0,0 %"

def empty_projekt():
    return {
        "projektnamn": "", "projektnummer": "", "kund": "", "bestallar": "",
        "adress": "", "datum": datetime.date.today().isoformat(),
        "kalkylansvarig": "", "status": "Kalkyl", "kommentar": "",
        "rader": [], "byggdelar": list(BYGGDEL_DEF),
        "omkostnader": {k: 0.0 for k in OMKKOSTNADER},
        "paslag": {"Omkostnad %": 10.0, "Risk %": 5.0, "Vinst %": 8.0, "Rabatt %": 0.0},
    }

def empty_rad(byggdel=""):
    return {
        "Radtyp": "Material", "Kod": "", "Benämning": "", "Beskrivning": "",
        "Byggdel": byggdel, "Mängd": 0.0, "Enhet": "st", "Timmar": 0.0,
        "Á-pris": 0.0, "Kostnad": 0.0, "Påslag %": 0.0,
        "Försäljning": 0.0, "Leverantör": "", "Kommentar": "",
    }

def berakna_rad(rad):
    typ = rad.get("Radtyp", "Material")
    m   = sfloat(rad.get("Mängd", 0))
    t   = sfloat(rad.get("Timmar", 0))
    a   = sfloat(rad.get("Á-pris", 0))
    p   = sfloat(rad.get("Påslag %", 0))
    k   = (t * a) if typ == "Arbete" else (m * a)
    rad["Kostnad"]     = round(k, 2)
    rad["Försäljning"] = round(k * (1 + p / 100), 2)
    return rad

def berakna_alla(rader):
    return [berakna_rad(r) for r in rader]

def summera(projekt):
    rader = projekt.get("rader", [])
    dir_k = sum(sfloat(r.get("Kostnad", 0)) for r in rader)
    omk   = projekt.get("omkostnader", {})
    omk_s = sum(sfloat(v) for v in omk.values())
    p     = projekt.get("paslag", {})
    o_pct = sfloat(p.get("Omkostnad %", 0))
    r_pct = sfloat(p.get("Risk %", 0))
    v_pct = sfloat(p.get("Vinst %", 0))
    d_pct = sfloat(p.get("Rabatt %", 0))
    omk_b = dir_k * o_pct / 100
    ris_b = dir_k * r_pct / 100
    sjk   = dir_k + omk_s + omk_b + ris_b
    vin_b = sjk * v_pct / 100
    fp    = sjk + vin_b
    rab   = fp * d_pct / 100
    fp_n  = fp - rab
    tb    = fp_n - dir_k
    mg    = (tb / fp_n * 100) if fp_n else 0
    return {"dir_k": dir_k, "omk_s": omk_s, "omk_b": omk_b, "ris_b": ris_b,
            "sjk": sjk, "vin_b": vin_b, "fp": fp_n, "tb": tb, "mg": mg}

def rader_till_df(rader):
    if not rader:
        return pd.DataFrame(columns=list(empty_rad().keys()))
    return pd.DataFrame(rader)

def df_till_rader(df):
    rader = df.to_dict("records")
    return [berakna_rad(r) for r in rader]

# ──────────────────────────────────────────────────────────────
#  SESSION STATE
# ──────────────────────────────────────────────────────────────
def init_state():
    if "projekt" not in st.session_state:
        st.session_state.projekt = empty_projekt()
    if "prisbank" not in st.session_state:
        st.session_state.prisbank = []
    if "mallar" not in st.session_state:
        st.session_state.mallar = []

# ──────────────────────────────────────────────────────────────
#  CSS
# ──────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    .stApp { background: #f4f6f9; }
    .block-container { padding-top: 1.5rem; }
    .metric-card {
        background: white; border-radius: 8px; padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 8px;
    }
    .section-header {
        background: #1a3a5c; color: white; padding: 8px 16px;
        border-radius: 6px; margin-bottom: 12px; font-weight: 600;
    }
    .highlight { color: #1a3a5c; font-weight: 700; }
    div[data-testid="stMetricValue"] { font-size: 1.4rem; }
    </style>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
#  SIDEBAR
# ──────────────────────────────────────────────────────────────
def render_sidebar():
    proj = st.session_state.projekt
    with st.sidebar:
        st.markdown("### 🏗 Kalkylprogram")
        st.caption("Bygg & Entreprenad")
        st.divider()

        # Save / Load
        st.markdown("**Projekt**")
        if st.button("➕  Nytt projekt", use_container_width=True):
            st.session_state.projekt = empty_projekt()
            st.rerun()

        uploaded = st.file_uploader("📂  Öppna projekt (.json)", type=["json"],
                                     label_visibility="collapsed")
        if uploaded:
            try:
                data = json.loads(uploaded.read().decode("utf-8"))
                st.session_state.projekt = data
                st.success("Projekt öppnat!")
                st.rerun()
            except Exception as e:
                st.error(f"Fel: {e}")

        # Download project
        proj_json = json.dumps(proj, ensure_ascii=False, indent=2)
        name = proj.get("projektnamn", "projekt").replace(" ", "_") or "projekt"
        st.download_button("💾  Spara projekt",
                           data=proj_json.encode("utf-8"),
                           file_name=f"{name}.json",
                           mime="application/json",
                           use_container_width=True)

        st.divider()
        s = summera(proj)
        st.markdown("**Snabbsummering**")
        st.metric("Försäljning", fmt_kr(s["fp"]))
        st.metric("TB", fmt_kr(s["tb"]))
        st.metric("Marginal", fmt_pct(s["mg"]))
        st.caption(f"{len(proj.get('rader', []))} kalkylrader")

# ──────────────────────────────────────────────────────────────
#  TAB: START
# ──────────────────────────────────────────────────────────────
def tab_start():
    proj = st.session_state.projekt
    s    = summera(proj)

    st.markdown('<div class="section-header">Projektöversikt</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Direkta kostnader", fmt_kr(s["dir_k"]))
    col2.metric("Försäljningspris",  fmt_kr(s["fp"]))
    col3.metric("Täckningsbidrag",   fmt_kr(s["tb"]))
    col4.metric("Marginal",          fmt_pct(s["mg"]))

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Projektinformation**")
        info = {
            "Projektnamn":    proj.get("projektnamn", "–"),
            "Projektnummer":  proj.get("projektnummer", "–"),
            "Kund":           proj.get("kund", "–"),
            "Status":         proj.get("status", "–"),
            "Datum":          proj.get("datum", "–"),
            "Ansvarig":       proj.get("kalkylansvarig", "–"),
        }
        for k, v in info.items():
            st.markdown(f"**{k}:** {v}")

    with c2:
        st.markdown("**Ekonomisk summering**")
        rows = [
            ("Direkta kostnader",    s["dir_k"]),
            ("Omkostnader (fasta)",  s["omk_s"]),
            ("Omkostnadspåslag",     s["omk_b"]),
            ("Riskpåslag",           s["ris_b"]),
            ("Självkostnad",         s["sjk"]),
            ("Vinst",                s["vin_b"]),
            ("Försäljningspris",     s["fp"]),
            ("TB",                   s["tb"]),
        ]
        df = pd.DataFrame(rows, columns=["Post", "Belopp (kr)"])
        df["Belopp (kr)"] = df["Belopp (kr)"].apply(lambda x: f"{x:,.0f}".replace(",", " "))
        st.dataframe(df, hide_index=True, use_container_width=True)

# ──────────────────────────────────────────────────────────────
#  TAB: PROJEKT
# ──────────────────────────────────────────────────────────────
def tab_projekt():
    proj = st.session_state.projekt
    st.markdown('<div class="section-header">Projektinformation</div>', unsafe_allow_html=True)

    with st.form("projekt_form"):
        c1, c2 = st.columns(2)
        with c1:
            proj["projektnamn"]   = st.text_input("Projektnamn",    proj.get("projektnamn",""))
            proj["projektnummer"] = st.text_input("Projektnummer",  proj.get("projektnummer",""))
            proj["kund"]          = st.text_input("Kund",           proj.get("kund",""))
            proj["bestallar"]     = st.text_input("Beställare",     proj.get("bestallar",""))
        with c2:
            proj["adress"]        = st.text_input("Adress",         proj.get("adress",""))
            proj["datum"]         = st.text_input("Datum",          proj.get("datum", datetime.date.today().isoformat()))
            proj["kalkylansvarig"]= st.text_input("Kalkylansvarig", proj.get("kalkylansvarig",""))
            proj["status"]        = st.selectbox("Status",          STATUS_LIST,
                                                  index=STATUS_LIST.index(proj.get("status","Kalkyl"))
                                                  if proj.get("status") in STATUS_LIST else 0)
        proj["kommentar"] = st.text_area("Kommentar", proj.get("kommentar",""), height=100)

        if st.form_submit_button("💾  Spara projektinfo", type="primary"):
            st.session_state.projekt = proj
            st.success("Projektinfo sparad.")

    st.divider()
    st.markdown("**Byggdelar**")
    bdl_text = st.text_area("Hantera byggdelar (en per rad)",
                             "\n".join(proj.get("byggdelar", BYGGDEL_DEF)),
                             height=200)
    if st.button("Uppdatera byggdelar"):
        proj["byggdelar"] = [b.strip() for b in bdl_text.splitlines() if b.strip()]
        st.session_state.projekt = proj
        st.success("Byggdelar uppdaterade.")

# ──────────────────────────────────────────────────────────────
#  TAB: KALKYL
# ──────────────────────────────────────────────────────────────
def tab_kalkyl():
    proj    = st.session_state.projekt
    rader   = proj.get("rader", [])
    bdlar   = proj.get("byggdelar", BYGGDEL_DEF)

    st.markdown('<div class="section-header">Kalkyl</div>', unsafe_allow_html=True)

    # Controls
    c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 2])
    with c1:
        if st.button("➕  Ny rad", use_container_width=True, type="primary"):
            ny = empty_rad()
            proj["rader"].append(ny)
            st.session_state.projekt = proj
            st.rerun()
    with c2:
        filter_bdl = st.selectbox("Filtrera byggdel", ["Alla"] + bdlar,
                                   label_visibility="collapsed")
    with c3:
        filter_typ = st.selectbox("Filtrera typ", ["Alla"] + RADTYPER,
                                   label_visibility="collapsed")
    with c4:
        filter_sok = st.text_input("Sök benämning", placeholder="Sök...",
                                    label_visibility="collapsed")
    with c5:
        if st.button("🗑  Rensa filter", use_container_width=True):
            st.rerun()

    # Filter
    visa_rader = rader
    if filter_bdl != "Alla":
        visa_rader = [r for r in visa_rader if r.get("Byggdel","") == filter_bdl]
    if filter_typ != "Alla":
        visa_rader = [r for r in visa_rader if r.get("Radtyp","") == filter_typ]
    if filter_sok:
        q = filter_sok.lower()
        visa_rader = [r for r in visa_rader if q in r.get("Benämning","").lower()
                      or q in r.get("Kod","").lower()]

    # Data editor
    if visa_rader:
        df = pd.DataFrame(visa_rader)
    else:
        df = pd.DataFrame([empty_rad()])
        df = df.iloc[0:0]  # empty

    col_config = {
        "Radtyp":    st.column_config.SelectboxColumn("Typ",      options=RADTYPER, width="small"),
        "Kod":       st.column_config.TextColumn("Kod",           width="small"),
        "Benämning": st.column_config.TextColumn("Benämning",     width="large"),
        "Byggdel":   st.column_config.SelectboxColumn("Byggdel",  options=bdlar, width="medium"),
        "Mängd":     st.column_config.NumberColumn("Mängd",       format="%.2f", width="small"),
        "Enhet":     st.column_config.SelectboxColumn("Enhet",    options=ENHETER, width="small"),
        "Timmar":    st.column_config.NumberColumn("Tim",         format="%.1f", width="small"),
        "Á-pris":    st.column_config.NumberColumn("Á-pris",      format="%.2f", width="small"),
        "Kostnad":   st.column_config.NumberColumn("Kostnad",     format="%.2f", width="small",
                                                   disabled=True),
        "Påslag %":  st.column_config.NumberColumn("Pål%",        format="%.1f", width="small"),
        "Försäljning": st.column_config.NumberColumn("Försälj.",  format="%.2f", width="small",
                                                    disabled=True),
        "Leverantör": st.column_config.TextColumn("Leverantör",   width="medium"),
        "Kommentar":  st.column_config.TextColumn("Kommentar",    width="medium"),
        "Beskrivning": st.column_config.TextColumn("Beskrivning", width="medium"),
    }

    edited_df = st.data_editor(
        df,
        column_config=col_config,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        height=420,
        key="kalkyl_editor",
    )

    if st.button("✓  Beräkna & spara kalkyl", type="primary"):
        ny_rader = df_till_rader(edited_df)
        if filter_bdl == "Alla" and filter_typ == "Alla" and not filter_sok:
            proj["rader"] = ny_rader
        else:
            # Merge back – replace filtered rows, keep others
            filtered_ids = {id(r) for r in visa_rader}
            andra = [r for r in rader if r not in visa_rader]
            proj["rader"] = andra + ny_rader
        st.session_state.projekt = proj
        st.success(f"Sparat {len(proj['rader'])} rader.")
        st.rerun()

    # Summary
    st.divider()
    tot_k = sum(sfloat(r.get("Kostnad",0)) for r in proj.get("rader",[]))
    tot_f = sum(sfloat(r.get("Försäljning",0)) for r in proj.get("rader",[]))
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Rader totalt", len(proj.get("rader",[])))
    c2.metric("Direkta kostnader", fmt_kr(tot_k))
    c3.metric("Försäljning", fmt_kr(tot_f))
    c4.metric("TB", fmt_kr(tot_f - tot_k))

    # Export
    st.divider()
    ec1, ec2 = st.columns(2)
    with ec1:
        if OPX_OK and st.button("📊  Ladda ner Excel"):
            buf = io.BytesIO()
            _export_excel_kalkyl(proj, buf)
            buf.seek(0)
            st.download_button("⬇  Hämta Excel-kalkyl",
                               data=buf,
                               file_name=f"{proj.get('projektnamn','kalkyl')}_kalkyl.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with ec2:
        if RL_OK and st.button("📄  Ladda ner PDF"):
            buf = io.BytesIO()
            _export_pdf_kalkyl(proj, buf)
            buf.seek(0)
            st.download_button("⬇  Hämta PDF-kalkyl",
                               data=buf,
                               file_name=f"{proj.get('projektnamn','kalkyl')}_kalkyl.pdf",
                               mime="application/pdf")

# ──────────────────────────────────────────────────────────────
#  TAB: PRISBANK
# ──────────────────────────────────────────────────────────────
def tab_prisbank():
    st.markdown('<div class="section-header">Prisbank</div>', unsafe_allow_html=True)

    pb = st.session_state.prisbank

    c1, c2 = st.columns([3, 1])
    with c1:
        uploaded = st.file_uploader("📥  Importera Excel-prislista",
                                     type=["xlsx", "xls"],
                                     label_visibility="visible")
        if uploaded:
            try:
                df = pd.read_excel(uploaded)
                df.columns = [str(c).strip().lower() for c in df.columns]
                colmap = {}
                for col in df.columns:
                    if any(x in col for x in ["kod","code","nr"]): colmap["kod"]=col
                    elif any(x in col for x in ["benäm","namn","desc","beskr"]): colmap["benamning"]=col
                    elif any(x in col for x in ["enh","unit"]): colmap["enhet"]=col
                    elif any(x in col for x in ["mat","material"]): colmap["matpris"]=col
                    elif any(x in col for x in ["arb","arbete","tim"]): colmap["arbpris"]=col
                if "benamning" not in colmap:
                    cols = list(df.columns)
                    for i,k in enumerate(["kod","benamning","enhet","matpris","arbpris"]):
                        if i < len(cols): colmap[k] = cols[i]
                ny = []
                for _, row in df.iterrows():
                    item = {
                        "kod":      str(row.get(colmap.get("kod",""),"")),
                        "benamning":str(row.get(colmap.get("benamning",""),"")),
                        "enhet":    str(row.get(colmap.get("enhet",""),"st")),
                        "matpris":  float(row.get(colmap.get("matpris",""),0) or 0),
                        "arbpris":  float(row.get(colmap.get("arbpris",""),0) or 0),
                    }
                    if item["benamning"] and item["benamning"] != "nan":
                        ny.append(item)
                st.session_state.prisbank.extend(ny)
                st.success(f"{len(ny)} artiklar importerade.")
            except Exception as e:
                st.error(f"Importfel: {e}")

    with c2:
        st.markdown("**BKI-index**")
        bki_typ = st.selectbox("Byggnadstyp", list(BKI.keys()), key="bki_typ")
        bki_bas = st.selectbox("Basår",   list(BKI[bki_typ].keys()), index=2, key="bki_bas")
        bki_nytt= st.selectbox("Till år", list(BKI[bki_typ].keys()), index=7, key="bki_nytt")
        try:
            faktor = BKI[bki_typ][bki_nytt] / BKI[bki_typ][bki_bas]
            st.metric("Index-faktor", f"{faktor:.4f}")
            st.caption(f"{bki_bas} → {bki_nytt}")
        except:
            pass

    st.divider()
    sok = st.text_input("🔍  Sök i prisbank", placeholder="Artikel eller kod...")
    if pb:
        df_pb = pd.DataFrame(pb)
        if sok:
            df_pb = df_pb[df_pb.apply(
                lambda r: sok.lower() in str(r.get("benamning","")).lower()
                       or sok.lower() in str(r.get("kod","")).lower(), axis=1)]
        st.dataframe(df_pb, use_container_width=True, hide_index=True, height=300)

        st.markdown("**Lägg till i kalkyl**")
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            benlist = [f"{r.get('kod','')} – {r.get('benamning','')}" for r in pb]
            vald    = st.selectbox("Välj artikel", benlist, key="pb_select")
        with c2:
            mangd   = st.number_input("Mängd", value=1.0, min_value=0.0, key="pb_mangd")
        with c3:
            bdl     = st.selectbox("Byggdel",
                                    st.session_state.projekt.get("byggdelar", BYGGDEL_DEF),
                                    key="pb_bdl")
        if st.button("➕  Lägg till i kalkyl", type="primary"):
            idx = benlist.index(vald)
            item = pb[idx]
            ny = empty_rad(bdl)
            ny["Kod"]       = item.get("kod","")
            ny["Benämning"] = item.get("benamning","")
            ny["Enhet"]     = item.get("enhet","st")
            ny["Á-pris"]    = float(item.get("matpris",0) or 0)
            ny["Mängd"]     = mangd
            berakna_rad(ny)
            st.session_state.projekt["rader"].append(ny)
            st.success(f"'{ny['Benämning']}' lagt till i kalkyl.")
    else:
        st.info("Prisbanken är tom. Importera en Excel-prislista ovan.")

        with st.expander("Lägg till artikel manuellt"):
            with st.form("ny_artikel"):
                ac1, ac2, ac3, ac4, ac5 = st.columns(5)
                a_kod  = ac1.text_input("Kod")
                a_ben  = ac2.text_input("Benämning")
                a_enh  = ac3.text_input("Enhet", "st")
                a_mat  = ac4.number_input("Materialpris", 0.0)
                a_arb  = ac5.number_input("Arbetspris", 0.0)
                if st.form_submit_button("Spara artikel"):
                    st.session_state.prisbank.append({
                        "kod": a_kod, "benamning": a_ben,
                        "enhet": a_enh, "matpris": a_mat, "arbpris": a_arb
                    })
                    st.success("Artikel sparad.")
                    st.rerun()

# ──────────────────────────────────────────────────────────────
#  TAB: MALLAR
# ──────────────────────────────────────────────────────────────
def tab_mallar():
    st.markdown('<div class="section-header">Mallar</div>', unsafe_allow_html=True)

    mallar = st.session_state.mallar
    proj   = st.session_state.projekt

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("**Spara nuvarande kalkyl som mall**")
        mall_namn = st.text_input("Mallnamn", placeholder="T.ex. Standardbadrum")
        if st.button("💾  Spara som mall", type="primary"):
            if mall_namn and proj.get("rader"):
                mallar.append({
                    "namn": mall_namn,
                    "rader": copy.deepcopy(proj["rader"]),
                    "skapad": datetime.date.today().isoformat()
                })
                st.session_state.mallar = mallar
                st.success(f"Mall '{mall_namn}' sparad ({len(proj['rader'])} rader).")
            else:
                st.warning("Ange mallnamn och se till att kalkyl innehåller rader.")

    with c2:
        if mallar:
            st.markdown("**Sparade mallar**")
            for i, m in enumerate(mallar):
                with st.expander(f"📑  {m['namn']}  ({len(m.get('rader',[]))} rader)"):
                    df = pd.DataFrame(m.get("rader",[]))[["Radtyp","Kod","Benämning","Byggdel","Mängd","Á-pris","Kostnad"]]
                    st.dataframe(df, hide_index=True, use_container_width=True)
                    bc1, bc2 = st.columns(2)
                    if bc1.button("➕  Lägg till i kalkyl", key=f"anvand_{i}"):
                        for r in m.get("rader",[]):
                            ny = copy.deepcopy(r)
                            berakna_rad(ny)
                            proj["rader"].append(ny)
                        st.session_state.projekt = proj
                        st.success(f"{len(m['rader'])} rader tillagda från mall '{m['namn']}'.")
                        st.rerun()
                    if bc2.button("🗑  Radera mall", key=f"radera_{i}"):
                        mallar.pop(i)
                        st.session_state.mallar = mallar
                        st.rerun()
        else:
            st.info("Inga mallar sparade ännu.")

        # Download/upload mallar
        st.divider()
        if mallar:
            st.download_button("⬇  Exportera mallar (.json)",
                               data=json.dumps(mallar, ensure_ascii=False, indent=2).encode(),
                               file_name="mallar.json", mime="application/json")
        up = st.file_uploader("📥  Importera mallar (.json)", type=["json"], key="mall_import")
        if up:
            try:
                imported = json.loads(up.read().decode("utf-8"))
                st.session_state.mallar.extend(imported)
                st.success(f"{len(imported)} mallar importerade.")
                st.rerun()
            except Exception as e:
                st.error(str(e))

# ──────────────────────────────────────────────────────────────
#  TAB: BYGGDELAR
# ──────────────────────────────────────────────────────────────
def tab_byggdelar():
    proj  = st.session_state.projekt
    rader = proj.get("rader", [])
    bdlar = proj.get("byggdelar", BYGGDEL_DEF)

    st.markdown('<div class="section-header">Byggdelar</div>', unsafe_allow_html=True)

    totals = {}
    for r in rader:
        bd = r.get("Byggdel","") or "(Utan byggdel)"
        if bd not in totals: totals[bd] = {"n":0,"k":0.0,"f":0.0}
        totals[bd]["n"] += 1
        totals[bd]["k"] += sfloat(r.get("Kostnad",0))
        totals[bd]["f"] += sfloat(r.get("Försäljning",0))

    alla_bdl = list(bdlar) + ["(Utan byggdel)"]
    rows = []
    for bd in alla_bdl:
        t  = totals.get(bd, {"n":0,"k":0.0,"f":0.0})
        tb_= t["f"] - t["k"]
        mg = (tb_/t["f"]*100) if t["f"] else 0
        rows.append({"Byggdel":bd,"Rader":t["n"],
                     "Kostnad":round(t["k"],0),"Försäljning":round(t["f"],0),
                     "TB":round(tb_,0),"Marginal %":round(mg,1)})
    # Totals
    all_k = sum(r["Kostnad"] for r in rows)
    all_f = sum(r["Försäljning"] for r in rows)
    tb_tot= all_f - all_k
    mg_tot= (tb_tot/all_f*100) if all_f else 0
    rows.append({"Byggdel":"TOTALT","Rader":sum(r["Rader"] for r in rows),
                 "Kostnad":round(all_k,0),"Försäljning":round(all_f,0),
                 "TB":round(tb_tot,0),"Marginal %":round(mg_tot,1)})

    df = pd.DataFrame(rows)
    st.dataframe(df, hide_index=True, use_container_width=True,
                 column_config={
                     "Kostnad":     st.column_config.NumberColumn(format="%,.0f kr"),
                     "Försäljning": st.column_config.NumberColumn(format="%,.0f kr"),
                     "TB":          st.column_config.NumberColumn(format="%,.0f kr"),
                     "Marginal %":  st.column_config.NumberColumn(format="%.1f %%"),
                 })

    st.divider()
    vald_bd = st.selectbox("Visa rader för byggdel",
                            ["Välj..."] + alla_bdl)
    if vald_bd != "Välj...":
        rad_bd = [r for r in rader if (r.get("Byggdel","") or "(Utan byggdel)") == vald_bd]
        if rad_bd:
            st.dataframe(pd.DataFrame(rad_bd)[["Radtyp","Kod","Benämning","Mängd","Enhet","Á-pris","Kostnad","Försäljning","Leverantör"]],
                         hide_index=True, use_container_width=True)
        else:
            st.info(f"Inga rader för {vald_bd}.")

# ──────────────────────────────────────────────────────────────
#  TAB: SLUTSIDA
# ──────────────────────────────────────────────────────────────
def tab_slutsida():
    proj = st.session_state.projekt
    st.markdown('<div class="section-header">Slutsida – Ekonomi</div>', unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("**Omkostnader (kr)**")
        omk = proj.get("omkostnader", {k:0.0 for k in OMKKOSTNADER})
        ny_omk = {}
        for k in OMKKOSTNADER:
            ny_omk[k] = st.number_input(k, value=float(omk.get(k,0)),
                                         min_value=0.0, step=1000.0, key=f"omk_{k}")
        proj["omkostnader"] = ny_omk

        st.divider()
        st.markdown("**Påslag (%)**")
        pas = proj.get("paslag", {"Omkostnad %":10.0,"Risk %":5.0,"Vinst %":8.0,"Rabatt %":0.0})
        ny_pas = {}
        for k in ["Omkostnad %","Risk %","Vinst %","Rabatt %"]:
            ny_pas[k] = st.number_input(k, value=float(pas.get(k,0)),
                                         min_value=0.0, max_value=100.0,
                                         step=0.5, key=f"pas_{k}")
        proj["paslag"] = ny_pas
        st.session_state.projekt = proj

    with c2:
        s = summera(proj)
        st.markdown("**Resultat**")

        items = [
            ("Direkta kostnader",    s["dir_k"],  False),
            ("Omkostnader (fasta)",  s["omk_s"],  False),
            ("Omkostnadspåslag",     s["omk_b"],  False),
            ("Riskpåslag",           s["ris_b"],  False),
            ("",                     None,         True),  # divider
            ("Självkostnad",         s["sjk"],    True),
            ("Vinst",                s["vin_b"],  False),
            ("",                     None,         True),
            ("Försäljningspris",     s["fp"],     True),
            ("Täckningsbidrag (TB)", s["tb"],     True),
        ]
        for label, val, bold in items:
            if val is None:
                st.divider()
                continue
            suffix = " kr"
            txt = f"**{label}:** {fmt_kr(val)}" if bold else f"{label}: {fmt_kr(val)}"
            st.markdown(txt)

        st.divider()
        m1, m2 = st.columns(2)
        m1.metric("Försäljningspris", fmt_kr(s["fp"]))
        m2.metric("Marginal", fmt_pct(s["mg"]))

        st.divider()
        if OPX_OK:
            buf = io.BytesIO()
            _export_excel_slutsida(proj, buf)
            buf.seek(0)
            st.download_button("📊  Ladda ner Excel-slutsida",
                               data=buf,
                               file_name=f"{proj.get('projektnamn','slutsida')}_slutsida.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)
        if RL_OK:
            buf = io.BytesIO()
            _export_pdf_slutsida(proj, buf)
            buf.seek(0)
            st.download_button("📄  Ladda ner PDF-slutsida",
                               data=buf,
                               file_name=f"{proj.get('projektnamn','slutsida')}_slutsida.pdf",
                               mime="application/pdf",
                               use_container_width=True)

# ──────────────────────────────────────────────────────────────
#  EXPORT HELPERS
# ──────────────────────────────────────────────────────────────
def _export_excel_kalkyl(proj, buf):
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Kalkyl"
    hdrs = ["Typ","Kod","Benämning","Byggdel","Mängd","Enh","Tim","Á-pris","Kostnad","Pål%","Försäljning","Leverantör"]
    ws.append(hdrs)
    hdr_fill = PatternFill("solid", fgColor="1A3A5C")
    for cell in ws[1]:
        cell.fill = hdr_fill; cell.font = Font(color="FFFFFF",bold=True)
    for r in proj.get("rader",[]):
        ws.append([r.get("Radtyp",""),r.get("Kod",""),r.get("Benämning",""),r.get("Byggdel",""),
                   r.get("Mängd",0),r.get("Enhet",""),r.get("Timmar",0),r.get("Á-pris",0),
                   r.get("Kostnad",0),r.get("Påslag %",0),r.get("Försäljning",0),r.get("Leverantör","")])
    wb.save(buf)

def _export_excel_slutsida(proj, buf):
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Slutsida"
    s = summera(proj)
    ws["A1"] = proj.get("projektnamn",""); ws["A1"].font = Font(bold=True,size=13)
    ws.append([])
    ws.append(["Post","Belopp (kr)"])
    hdr_fill = PatternFill("solid", fgColor="1A3A5C")
    for cell in ws[3]: cell.fill=hdr_fill; cell.font=Font(color="FFFFFF",bold=True)
    for post, val in [
        ("Direkta kostnader",s["dir_k"]),("Omkostnader",s["omk_s"]),
        ("Omkostnadspåslag",s["omk_b"]),("Riskpåslag",s["ris_b"]),
        ("Självkostnad",s["sjk"]),("Vinst",s["vin_b"]),
        ("Försäljningspris",s["fp"]),("TB",s["tb"]),("Marginal %",s["mg"])
    ]: ws.append([post, round(val,2)])
    ws.column_dimensions["A"].width=28; ws.column_dimensions["B"].width=18
    wb.save(buf)

def _export_pdf_kalkyl(proj, buf):
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=15*mm, rightMargin=15*mm, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet(); elements = []
    elements.append(Paragraph(f"Kalkyl – {proj.get('projektnamn','')} ({proj.get('projektnummer','')})", styles["Title"]))
    elements.append(Spacer(1,5*mm))
    hdrs = [["Typ","Kod","Benämning","Byggdel","Mängd","Enh","Á-pris","Kostnad","Försälj."]]
    rows = hdrs[:]
    for r in proj.get("rader",[]):
        rows.append([r.get("Radtyp","")[:3],r.get("Kod","")[:8],r.get("Benämning","")[:28],
                     r.get("Byggdel","")[:14],f"{r.get('Mängd',0):.1f}",r.get("Enhet",""),
                     f"{r.get('Á-pris',0):.0f}",f"{r.get('Kostnad',0):.0f}",f"{r.get('Försäljning',0):.0f}"])
    t = Table(rows, colWidths=[25,25,85,50,22,18,38,40,42], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),rl_colors.HexColor("#1A3A5C")),
        ("TEXTCOLOR",(0,0),(-1,0),rl_colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),7),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[rl_colors.HexColor("#EEF3F8"),rl_colors.white]),
        ("GRID",(0,0),(-1,-1),0.3,rl_colors.grey),
    ]))
    elements.append(t)
    doc.build(elements)

def _export_pdf_slutsida(proj, buf):
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm, topMargin=25*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet(); elements = []
    s = summera(proj)
    elements.append(Paragraph(f"Kalkyl – {proj.get('projektnamn','')}", styles["Title"]))
    elements.append(Spacer(1,8*mm))
    data = [["Post","Belopp"],
            ["Direkta kostnader",f"{s['dir_k']:,.0f} kr"],
            ["Omkostnader",f"{s['omk_s']:,.0f} kr"],
            ["Självkostnad",f"{s['sjk']:,.0f} kr"],
            ["Försäljningspris",f"{s['fp']:,.0f} kr"],
            ["Täckningsbidrag",f"{s['tb']:,.0f} kr"],
            ["Marginal",f"{s['mg']:.2f} %"]]
    t = Table(data, colWidths=[120*mm,60*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),rl_colors.HexColor("#1A3A5C")),
        ("TEXTCOLOR",(0,0),(-1,0),rl_colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),11),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[rl_colors.HexColor("#EEF3F8"),rl_colors.white]),
        ("GRID",(0,0),(-1,-1),0.5,rl_colors.grey),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))
    elements.append(t)
    doc.build(elements)

# ──────────────────────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────────────────────
def main():
    init_state()
    inject_css()
    render_sidebar()

    t1,t2,t3,t4,t5,t6,t7 = st.tabs([
        "🏠  Start",
        "📋  Projekt",
        "🔢  Kalkyl",
        "💰  Prisbank",
        "📑  Mallar",
        "🏗  Byggdelar",
        "📊  Slutsida",
    ])
    with t1: tab_start()
    with t2: tab_projekt()
    with t3: tab_kalkyl()
    with t4: tab_prisbank()
    with t5: tab_mallar()
    with t6: tab_byggdelar()
    with t7: tab_slutsida()

if __name__ == "__main__":
    main()
