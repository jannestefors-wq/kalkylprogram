#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kalkylprogram Bygg & Entreprenad – v2
"""
import streamlit as st
import pandas as pd
import json, datetime, copy, io

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
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
st.set_page_config(page_title="Kalkylprogram – Bygg & Entreprenad",
                   page_icon="🏗", layout="wide",
                   initial_sidebar_state="expanded")

RADTYPER    = ["Material", "Arbete", "UE"]
ENHETER     = ["st","m","m²","m³","kg","ton","tim","pers","ls","rund"]
STATUS_LIST = ["Kalkyl","Offert","Pågående","Vunnen","Förlorad","Avslutad","Pausad"]
BYGGDEL_DEF = ["Badrum","Kök","Vägg","Etapp 1","Rivning","Snickeri",
               "Grund","Fasad","Tak","El","VVS","Övrigt"]
OMKKOSTNADER= ["Arbetsledning","Etablering","Administration",
               "Transporter","Garanti","Risk","Övrigt"]
BKI = {
    "Flerbostadshus":{"2018":175.2,"2019":180.1,"2020":183.5,"2021":192.4,
                      "2022":215.8,"2023":228.3,"2024":232.1,"2025":238.5,"2026":242.0},
    "Småhus":        {"2018":168.4,"2019":173.2,"2020":177.8,"2021":186.3,
                      "2022":208.9,"2023":221.7,"2024":225.4,"2025":231.0,"2026":234.5},
    "ROT/Ombyggnad": {"2018":171.3,"2019":176.5,"2020":180.2,"2021":189.1,
                      "2022":212.1,"2023":224.9,"2024":228.7,"2025":234.8,"2026":238.2},
}

# ──────────────────────────────────────────────────────────────
#  UTILITIES
# ──────────────────────────────────────────────────────────────
def sf(v, d=0.0):
    try: return float(str(v).replace(" ","").replace(",","."))
    except: return d

def kr(v):
    try: return f"{float(v):,.0f} kr".replace(","," ")
    except: return "0 kr"

def pct(v):
    try: return f"{float(v):.1f} %"
    except: return "0,0 %"

def empty_projekt():
    return {"projektnamn":"","projektnummer":"","kund":"","bestallar":"",
            "adress":"","datum":datetime.date.today().isoformat(),
            "kalkylansvarig":"","status":"Kalkyl","kommentar":"",
            "rader":[],"byggdelar":list(BYGGDEL_DEF),
            "omkostnader":{k:0.0 for k in OMKKOSTNADER},
            "paslag":{"Omkostnad %":10.0,"Risk %":5.0,"Vinst %":8.0,"Rabatt %":0.0}}

def empty_rad():
    return {"Radtyp":"Material","Benämning":"","Byggdel":"",
            "Mängd":0.0,"Enhet":"st","Timmar":0.0,
            "Á-pris":0.0,"Kostnad":0.0,"Påslag %":0.0,"Försäljning":0.0,
            "Leverantör":"","Kod":"","Kommentar":""}

def berakna(r):
    m=sf(r.get("Mängd",0)); t=sf(r.get("Timmar",0))
    a=sf(r.get("Á-pris",0)); p=sf(r.get("Påslag %",0))
    k=(t*a) if r.get("Radtyp")=="Arbete" else (m*a)
    r["Kostnad"]=round(k,2); r["Försäljning"]=round(k*(1+p/100),2); return r

def summera(proj):
    rader=proj.get("rader",[]); dir_k=sum(sf(r.get("Kostnad",0)) for r in rader)
    omk=proj.get("omkostnader",{}); omk_s=sum(sf(v) for v in omk.values())
    p=proj.get("paslag",{}); o=sf(p.get("Omkostnad %",0)); ri=sf(p.get("Risk %",0))
    v=sf(p.get("Vinst %",0)); d=sf(p.get("Rabatt %",0))
    omk_b=dir_k*o/100; ris_b=dir_k*ri/100; sjk=dir_k+omk_s+omk_b+ris_b
    vin_b=sjk*v/100; fp=sjk+vin_b; fp_n=fp-fp*d/100
    tb=fp_n-dir_k; mg=(tb/fp_n*100) if fp_n else 0
    return {"dir_k":dir_k,"omk_s":omk_s,"omk_b":omk_b,"ris_b":ris_b,
            "sjk":sjk,"vin_b":vin_b,"fp":fp_n,"tb":tb,"mg":mg}

def init():
    if "projekt" not in st.session_state: st.session_state.projekt=empty_projekt()
    if "prisbank" not in st.session_state: st.session_state.prisbank=[]
    if "mallar"   not in st.session_state: st.session_state.mallar=[]

# ──────────────────────────────────────────────────────────────
#  CSS
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp{background:#f4f6f9}
.block-container{padding-top:1rem;padding-bottom:1rem}
h1,h2,h3{color:#1a3a5c}
.section-hdr{background:#1a3a5c;color:white;padding:8px 14px;border-radius:6px;
             font-weight:600;margin-bottom:10px;font-size:1rem}
.info-box{background:white;border-left:4px solid #1a3a5c;padding:10px 14px;
          border-radius:4px;margin:6px 0}
div[data-testid="stMetricValue"]{font-size:1.3rem;font-weight:700;color:#1a3a5c}
div[data-testid="stMetricLabel"]{color:#6b7280;font-size:.85rem}
</style>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
#  SIDEBAR
# ──────────────────────────────────────────────────────────────
def sidebar():
    proj=st.session_state.projekt
    with st.sidebar:
        st.markdown("## 🏗 Kalkylprogram")
        st.caption("Bygg & Entreprenad  v2")
        st.divider()

        st.markdown("**Projekt**")
        if st.button("➕ Nytt projekt", use_container_width=True):
            st.session_state.projekt=empty_projekt(); st.rerun()

        up=st.file_uploader("📂 Öppna (.json)", type=["json"],
                             label_visibility="collapsed")
        if up:
            try:
                st.session_state.projekt=json.loads(up.read().decode()); st.rerun()
            except: st.error("Kunde inte öppna filen.")

        name=(proj.get("projektnamn","projekt") or "projekt").replace(" ","_")
        st.download_button("💾 Spara projekt",
            data=json.dumps(proj,ensure_ascii=False,indent=2).encode(),
            file_name=f"{name}.json", mime="application/json",
            use_container_width=True)

        st.divider()
        s=summera(proj)
        pname=proj.get("projektnamn","") or "—"
        st.markdown(f"**{pname}**")
        st.caption(proj.get("status",""))
        col1,col2=st.columns(2)
        col1.metric("Rader", len(proj.get("rader",[])))
        col2.metric("Marginal", pct(s["mg"]))
        st.metric("Försäljning", kr(s["fp"]))
        st.metric("TB", kr(s["tb"]))

# ──────────────────────────────────────────────────────────────
#  TAB START
# ──────────────────────────────────────────────────────────────
def tab_start():
    proj=st.session_state.projekt
    s=summera(proj)
    st.markdown('<div class="section-hdr">Projektöversikt</div>',unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Direkta kostnader", kr(s["dir_k"]))
    c2.metric("Försäljningspris",  kr(s["fp"]))
    c3.metric("Täckningsbidrag",   kr(s["tb"]))
    c4.metric("Marginal",          pct(s["mg"]))
    st.divider()
    l,r=st.columns(2)
    with l:
        st.markdown("**Projektinfo**")
        for k,v in [("Projektnamn",proj.get("projektnamn","–")),
                    ("Projektnr",  proj.get("projektnummer","–")),
                    ("Kund",       proj.get("kund","–")),
                    ("Status",     proj.get("status","–")),
                    ("Ansvarig",   proj.get("kalkylansvarig","–")),
                    ("Datum",      proj.get("datum","–"))]:
            st.markdown(f'<div class="info-box"><b>{k}:</b> {v}</div>',unsafe_allow_html=True)
    with r:
        st.markdown("**Ekonomi**")
        df=pd.DataFrame([
            ("Direkta kostnader",   f"{s['dir_k']:,.0f}"),
            ("Omkostnader",         f"{s['omk_s']:,.0f}"),
            ("Självkostnad",        f"{s['sjk']:,.0f}"),
            ("Försäljningspris",    f"{s['fp']:,.0f}"),
            ("TB",                  f"{s['tb']:,.0f}"),
            ("Marginal",            f"{s['mg']:.1f} %"),
        ], columns=["Post","kr"])
        st.dataframe(df,hide_index=True,use_container_width=True)

# ──────────────────────────────────────────────────────────────
#  TAB PROJEKT
# ──────────────────────────────────────────────────────────────
def tab_projekt():
    proj=st.session_state.projekt
    st.markdown('<div class="section-hdr">Projektinformation</div>',unsafe_allow_html=True)
    with st.form("proj"):
        c1,c2=st.columns(2)
        with c1:
            proj["projektnamn"]   =st.text_input("Projektnamn *",   proj.get("projektnamn",""))
            proj["projektnummer"] =st.text_input("Projektnummer",   proj.get("projektnummer",""))
            proj["kund"]          =st.text_input("Kund",            proj.get("kund",""))
            proj["bestallar"]     =st.text_input("Beställare",      proj.get("bestallar",""))
        with c2:
            proj["adress"]        =st.text_input("Adress",          proj.get("adress",""))
            proj["datum"]         =st.text_input("Datum",           proj.get("datum",""))
            proj["kalkylansvarig"]=st.text_input("Kalkylansvarig",  proj.get("kalkylansvarig",""))
            idx=STATUS_LIST.index(proj.get("status","Kalkyl")) if proj.get("status") in STATUS_LIST else 0
            proj["status"]        =st.selectbox("Status", STATUS_LIST, index=idx)
        proj["kommentar"]=st.text_area("Kommentar", proj.get("kommentar",""))
        if st.form_submit_button("💾 Spara", type="primary"):
            st.session_state.projekt=proj; st.success("Sparat.")
    st.divider()
    st.markdown("**Byggdelar** – en per rad")
    txt=st.text_area("","\n".join(proj.get("byggdelar",BYGGDEL_DEF)),height=180,
                     label_visibility="collapsed")
    if st.button("Uppdatera byggdelar"):
        proj["byggdelar"]=[b.strip() for b in txt.splitlines() if b.strip()]
        st.session_state.projekt=proj; st.success("Klart.")

# ──────────────────────────────────────────────────────────────
#  TAB KALKYL  (omdesignad)
# ──────────────────────────────────────────────────────────────
def tab_kalkyl():
    proj =st.session_state.projekt
    rader=proj.get("rader",[])
    bdlar=proj.get("byggdelar",BYGGDEL_DEF)
    pb   =st.session_state.prisbank

    st.markdown('<div class="section-hdr">Kalkyl</div>',unsafe_allow_html=True)

    # ── Lägg till rad – tre sätt ──────────────────────────────
    with st.expander("➕  Lägg till rad", expanded=len(rader)==0):
        mode=st.radio("Lägg till via:",
                      ["Prisbank","Tom rad","Kopiera från mall"],
                      horizontal=True, label_visibility="collapsed")

        if mode=="Prisbank":
            if not pb:
                st.info("Prisbanken är tom. Gå till fliken **Prisbank** för att lägga till artiklar.")
            else:
                c1,c2,c3,c4,c5=st.columns([3,1,1,1,1])
                sok=c1.text_input("Sök artikel", placeholder="Namn eller kod...",
                                  label_visibility="collapsed")
                träffar=[p for p in pb if not sok or sok.lower() in p.get("benamning","").lower()
                         or sok.lower() in p.get("kod","").lower()]
                if träffar:
                    vald=c1.selectbox("Artikel",[f"{p.get('kod','')+' – ' if p.get('kod') else ''}{p['benamning']} ({p.get('enhet','st')} | mat:{p.get('matpris',0):.0f} | arb:{p.get('arbpris',0):.0f})"
                                                  for p in träffar],
                                       label_visibility="collapsed")
                    idx_v=0
                    for i,p in enumerate(träffar):
                        lbl=f"{p.get('kod','')+' – ' if p.get('kod') else ''}{p['benamning']} ({p.get('enhet','st')} | mat:{p.get('matpris',0):.0f} | arb:{p.get('arbpris',0):.0f})"
                        if lbl==vald: idx_v=i; break
                    item=träffar[idx_v]
                    radtyp=c2.selectbox("Typ", RADTYPER, label_visibility="collapsed")
                    mangd=c3.number_input("Mängd",value=1.0,min_value=0.0,
                                          label_visibility="collapsed")
                    bdl=c4.selectbox("Byggdel",["–"]+bdlar,
                                      label_visibility="collapsed")
                    paslag=c5.number_input("Påslag %",value=0.0,min_value=0.0,
                                            label_visibility="collapsed")
                    if st.button("Lägg till i kalkyl ➜", type="primary"):
                        apris=sf(item.get("arbpris",0)) if radtyp=="Arbete" else sf(item.get("matpris",0))
                        ny=empty_rad()
                        ny.update({"Radtyp":radtyp,"Benämning":item["benamning"],
                                   "Kod":item.get("kod",""),"Enhet":item.get("enhet","st"),
                                   "Á-pris":apris,"Mängd":mangd,"Påslag %":paslag,
                                   "Byggdel":bdl if bdl!="–" else "",
                                   "Leverantör":item.get("leverantor","")})
                        if radtyp=="Arbete": ny["Timmar"]=mangd; ny["Mängd"]=0
                        berakna(ny)
                        proj["rader"].append(ny)
                        st.session_state.projekt=proj; st.rerun()
                else:
                    st.warning("Inga träffar i prisbanken.")

        elif mode=="Tom rad":
            with st.form("ny_rad"):
                c1,c2,c3=st.columns(3)
                typ =c1.selectbox("Typ",RADTYPER)
                ben =c1.text_input("Benämning *")
                bdl =c1.selectbox("Byggdel",["–"]+bdlar)
                enh =c2.selectbox("Enhet",ENHETER)
                mng =c2.number_input("Mängd",value=0.0,min_value=0.0)
                tim =c2.number_input("Timmar",value=0.0,min_value=0.0)
                apr =c3.number_input("Á-pris (kr)",value=0.0,min_value=0.0)
                pas =c3.number_input("Påslag %",value=0.0,min_value=0.0)
                lev =c3.text_input("Leverantör")
                if st.form_submit_button("Lägg till ➜", type="primary"):
                    if not ben: st.warning("Ange benämning.")
                    else:
                        ny={"Radtyp":typ,"Benämning":ben,"Byggdel":bdl if bdl!="–" else "",
                            "Mängd":mng,"Enhet":enh,"Timmar":tim,"Á-pris":apr,
                            "Påslag %":pas,"Leverantör":lev,"Kod":"","Kommentar":"",
                            "Kostnad":0.0,"Försäljning":0.0}
                        berakna(ny); proj["rader"].append(ny)
                        st.session_state.projekt=proj; st.rerun()

        else:  # Mall
            mallar=st.session_state.mallar
            if not mallar:
                st.info("Inga mallar sparade. Gå till fliken **Mallar**.")
            else:
                vald=st.selectbox("Välj mall",[m["namn"] for m in mallar])
                m=next((x for x in mallar if x["namn"]==vald),None)
                if m:
                    st.caption(f"{len(m.get('rader',[]))} rader i mallen")
                    if st.button(f"Lägg till '{vald}' ➜", type="primary"):
                        for r in m.get("rader",[]):
                            ny=copy.deepcopy(r); berakna(ny)
                            proj["rader"].append(ny)
                        st.session_state.projekt=proj; st.rerun()

    # ── Filter ───────────────────────────────────────────────
    fc1,fc2,fc3,fc4=st.columns([2,2,2,1])
    f_bdl=fc1.selectbox("Byggdel",["Alla"]+bdlar,label_visibility="visible")
    f_typ=fc2.selectbox("Typ",["Alla"]+RADTYPER,label_visibility="visible")
    f_sok=fc3.text_input("Sök",placeholder="Sök benämning...",label_visibility="visible")
    if fc4.button("✕ Rensa",use_container_width=True): st.rerun()

    visa=[r for r in rader
          if (f_bdl=="Alla" or r.get("Byggdel","")==f_bdl)
          and (f_typ=="Alla" or r.get("Radtyp","")==f_typ)
          and (not f_sok or f_sok.lower() in r.get("Benämning","").lower())]

    # ── Kalkylbord – smala kolumner ───────────────────────────
    if visa:
        df=pd.DataFrame(visa)
        # Ensure all columns exist
        for col in empty_rad():
            if col not in df.columns: df[col]=None

        edited=st.data_editor(
            df[["Radtyp","Benämning","Byggdel","Mängd","Enhet","Timmar",
                "Á-pris","Kostnad","Påslag %","Försäljning","Leverantör"]],
            column_config={
                "Radtyp":     st.column_config.SelectboxColumn("Typ",   options=RADTYPER,width=90),
                "Benämning":  st.column_config.TextColumn("Benämning",  width=220),
                "Byggdel":    st.column_config.SelectboxColumn("Byggdel",options=["–"]+bdlar,width=110),
                "Mängd":      st.column_config.NumberColumn("Mängd",    format="%.2f",width=80),
                "Enhet":      st.column_config.SelectboxColumn("Enhet", options=ENHETER,width=70),
                "Timmar":     st.column_config.NumberColumn("Tim",      format="%.1f",width=70),
                "Á-pris":     st.column_config.NumberColumn("Á-pris",   format="%.2f",width=90),
                "Kostnad":    st.column_config.NumberColumn("Kostnad",  format="%.0f",width=90,disabled=True),
                "Påslag %":   st.column_config.NumberColumn("Pål%",     format="%.1f",width=65),
                "Försäljning":st.column_config.NumberColumn("Försälj.", format="%.0f",width=90,disabled=True),
                "Leverantör": st.column_config.TextColumn("Leverantör", width=110),
            },
            use_container_width=True, hide_index=True,
            num_rows="dynamic", height=min(60+len(visa)*35, 500),
            key="kalkyl_ed"
        )

        c1,c2,c3=st.columns([2,1,1])
        if c1.button("✓  Beräkna & spara", type="primary"):
            ny_rader=[]
            for _,row in edited.iterrows():
                r=row.to_dict()
                if r.get("Byggdel")=="–": r["Byggdel"]=""
                berakna(r)
                ny_rader.append(r)
            if f_bdl=="Alla" and f_typ=="Alla" and not f_sok:
                proj["rader"]=ny_rader
            else:
                orig_ids={id(r):i for i,r in enumerate(rader)}
                other=[r for r in rader if r not in visa]
                proj["rader"]=other+ny_rader
            st.session_state.projekt=proj; st.success("Kalkyl sparad."); st.rerun()

        if c2.button("💾  Spara som mall"):
            namn=st.session_state.get("_mall_namn","")
            if visa:
                st.session_state["_visa_mall_input"]=True
        if st.session_state.get("_visa_mall_input"):
            namn=st.text_input("Mallnamn",key="mall_namn_inp")
            if st.button("Spara mall ➜"):
                if namn:
                    st.session_state.mallar.append(
                        {"namn":namn,"rader":copy.deepcopy(visa),
                         "skapad":datetime.date.today().isoformat()})
                    st.session_state["_visa_mall_input"]=False
                    st.success(f"Mall '{namn}' sparad."); st.rerun()
    else:
        st.info("Inga kalkylrader ännu. Lägg till rader via panelen ovan.")

    # ── Summering ─────────────────────────────────────────────
    if rader:
        st.divider()
        tot_k=sum(sf(r.get("Kostnad",0)) for r in rader)
        tot_f=sum(sf(r.get("Försäljning",0)) for r in rader)
        m1,m2,m3,m4=st.columns(4)
        m1.metric("Rader",len(rader))
        m2.metric("Direkta kostnader",kr(tot_k))
        m3.metric("Försäljning",kr(tot_f))
        m4.metric("TB",kr(tot_f-tot_k))

    # ── Export ────────────────────────────────────────────────
    if rader:
        with st.expander("📤 Exportera"):
            xc1,xc2=st.columns(2)
            if OPX_OK:
                buf=io.BytesIO(); _xl_kalkyl(proj,buf); buf.seek(0)
                xc1.download_button("📊 Excel-kalkyl",data=buf,
                    file_name=f"{name_safe(proj)}_kalkyl.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            if RL_OK:
                buf=io.BytesIO(); _pdf_kalkyl(proj,buf); buf.seek(0)
                xc2.download_button("📄 PDF-kalkyl",data=buf,
                    file_name=f"{name_safe(proj)}_kalkyl.pdf",
                    mime="application/pdf")

# ──────────────────────────────────────────────────────────────
#  TAB PRISBANK  (omdesignad)
# ──────────────────────────────────────────────────────────────
def tab_prisbank():
    st.markdown('<div class="section-hdr">Prisbank – artiklar & à-priser</div>',
                unsafe_allow_html=True)

    pb=st.session_state.prisbank

    # ── Tre sektioner ─────────────────────────────────────────
    t1,t2,t3=st.tabs(["📋  Alla artiklar","➕  Lägg till manuellt","📥  Importera Excel"])

    # ── 1. Visa och redigera alla priser ──────────────────────
    with t1:
        if not pb:
            st.info("Prisbanken är tom. Importera en prislista eller lägg till artiklar manuellt.")
        else:
            sok=st.text_input("🔍 Sök",placeholder="Namn, kod eller leverantör...")
            träffar=pb if not sok else [p for p in pb if
                sok.lower() in p.get("benamning","").lower() or
                sok.lower() in p.get("kod","").lower() or
                sok.lower() in p.get("leverantor","").lower()]

            st.caption(f"{len(träffar)} av {len(pb)} artiklar")

            df=pd.DataFrame(träffar if träffar else [{"kod":"","benamning":"","enhet":"st","matpris":0,"arbpris":0,"leverantor":""}])
            edited=st.data_editor(
                df,
                column_config={
                    "kod":        st.column_config.TextColumn("Kod",         width=80),
                    "benamning":  st.column_config.TextColumn("Benämning",   width=260),
                    "enhet":      st.column_config.SelectboxColumn("Enhet",  options=ENHETER,width=70),
                    "matpris":    st.column_config.NumberColumn("Mat-pris",  format="%.2f",width=110,
                                     help="Materialpris per enhet (kr)"),
                    "arbpris":    st.column_config.NumberColumn("Arb-pris",  format="%.2f",width=110,
                                     help="Arbetstid × timpris (kr per enhet)"),
                    "leverantor": st.column_config.TextColumn("Leverantör",  width=130),
                },
                use_container_width=True, hide_index=True,
                num_rows="dynamic", height=420, key="pb_ed"
            )
            c1,c2=st.columns([2,1])
            if c1.button("💾  Spara ändringar", type="primary"):
                ny=[r for r in edited.to_dict("records")
                    if r.get("benamning","").strip()]
                if not sok:
                    st.session_state.prisbank=ny
                else:
                    others=[p for p in pb if not any(
                        p.get("benamning")==t.get("benamning") for t in träffar)]
                    st.session_state.prisbank=others+ny
                st.success(f"Prisbank sparad – {len(st.session_state.prisbank)} artiklar.")
                st.rerun()

            buf=io.BytesIO()
            pd.DataFrame(st.session_state.prisbank).to_excel(buf,index=False)
            buf.seek(0)
            c2.download_button("⬇ Ladda ner Excel",data=buf,
                file_name="prisbank.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        # BKI
        st.divider()
        st.markdown("**BKI-indexomräkning**")
        bki_c1,bki_c2,bki_c3,bki_c4=st.columns(4)
        bki_typ=bki_c1.selectbox("Typ",list(BKI.keys()),key="bki_t")
        bki_bas=bki_c2.selectbox("Basår",list(BKI[bki_typ].keys()),index=2,key="bki_b")
        bki_ny =bki_c3.selectbox("Till år",list(BKI[bki_typ].keys()),index=7,key="bki_n")
        try:
            fak=BKI[bki_typ][bki_ny]/BKI[bki_typ][bki_bas]
            bki_c4.metric("Index-faktor",f"{fak:.4f}")
        except: pass
        if pb and st.button("Räkna om alla priser med faktorn"):
            try:
                for p in st.session_state.prisbank:
                    p["matpris"]=round(sf(p.get("matpris",0))*fak,2)
                    p["arbpris"]=round(sf(p.get("arbpris",0))*fak,2)
                st.success(f"Alla priser räknade om med faktor {fak:.4f}"); st.rerun()
            except: st.error("Fyll i BKI-inställningarna ovan.")

    # ── 2. Lägg till manuellt ─────────────────────────────────
    with t2:
        st.markdown("Lägg till en egen artikel med pris:")
        with st.form("ny_artikel"):
            c1,c2,c3=st.columns(3)
            kod =c1.text_input("Kod (valfri)")
            ben =c1.text_input("Benämning *")
            enh =c1.selectbox("Enhet",ENHETER)
            mat =c2.number_input("Materialpris (kr/enhet)",value=0.0,
                                  help="Pris per enhet för material")
            arb =c2.number_input("Arbetspris (kr/enhet)",value=0.0,
                                  help="Timkostnad × normtid per enhet")
            lev =c3.text_input("Leverantör/källa")
            komm=c3.text_area("Notering",height=80)
            if st.form_submit_button("➕ Lägg till i prisbank", type="primary"):
                if not ben: st.warning("Ange benämning.")
                else:
                    st.session_state.prisbank.append(
                        {"kod":kod,"benamning":ben,"enhet":enh,
                         "matpris":mat,"arbpris":arb,
                         "leverantor":lev,"notering":komm})
                    st.success(f"'{ben}' tillagd."); st.rerun()

    # ── 3. Importera Excel ────────────────────────────────────
    with t3:
        st.markdown("""
        **Importera prislista från Excel**

        Filen ska ha kolumner med:
        - **Kod** – artikelnummer (valfri)
        - **Benämning** – artikelns namn
        - **Enhet** – t.ex. st, m², tim
        - **Materialpris** – pris per enhet
        - **Arbetspris** – arbetstid × timpris per enhet

        Kolumnnamnen behöver inte vara exakta – programmet försöker matcha automatiskt.
        """)

        up=st.file_uploader("Välj Excel-fil (.xlsx/.xls)",type=["xlsx","xls"])
        if up:
            try:
                xl=pd.ExcelFile(up)
                sheet=xl.sheet_names[0]
                if len(xl.sheet_names)>1:
                    sheet=st.selectbox("Välj flik",xl.sheet_names)
                df=xl.parse(sheet)
                df.columns=[str(c).strip().lower() for c in df.columns]

                # Auto-map columns
                cm={}
                for col in df.columns:
                    if any(x in col for x in ["kod","code","nr","id"]): cm["kod"]=col
                    elif any(x in col for x in ["benäm","namn","desc","beskriv","text"]): cm["benamning"]=col
                    elif any(x in col for x in ["enh","unit"]): cm["enhet"]=col
                    elif any(x in col for x in ["mat","material","pris","kostnad"]) and "arb" not in col: cm["matpris"]=col
                    elif any(x in col for x in ["arb","arbete","lön","tim","work"]): cm["arbpris"]=col

                st.markdown(f"**Hittade kolumner:** {', '.join(df.columns.tolist())}")
                st.markdown("**Matchning:**")
                for k,v in cm.items():
                    st.markdown(f"- {k} → `{v}`")

                if "benamning" not in cm:
                    st.warning("Kunde inte hitta en kolumn för Benämning. Välj manuellt:")
                    cm["benamning"]=st.selectbox("Benämning-kolumn",df.columns.tolist())

                läge=st.radio("Importläge",
                              ["Lägg till (behåll befintliga)","Ersätt hela prisbanken"],
                              horizontal=True)

                if st.button("✅ Importera", type="primary"):
                    ny=[]
                    for _,row in df.iterrows():
                        item={"kod":  str(row.get(cm.get("kod",""),"")),
                              "benamning": str(row.get(cm["benamning"],"")),
                              "enhet":str(row.get(cm.get("enhet",""),"st")),
                              "matpris":float(row.get(cm.get("matpris",""),0) or 0),
                              "arbpris":float(row.get(cm.get("arbpris",""),0) or 0),
                              "leverantor":""}
                        if item["benamning"] and item["benamning"]!="nan":
                            ny.append(item)
                    if läge.startswith("Lägg"):
                        st.session_state.prisbank.extend(ny)
                    else:
                        st.session_state.prisbank=ny
                    st.success(f"✅ {len(ny)} artiklar importerade.")
                    st.rerun()
            except Exception as e:
                st.error(f"Importfel: {e}")

# ──────────────────────────────────────────────────────────────
#  TAB MALLAR
# ──────────────────────────────────────────────────────────────
def tab_mallar():
    st.markdown('<div class="section-hdr">Mallar</div>',unsafe_allow_html=True)
    mallar=st.session_state.mallar; proj=st.session_state.projekt
    l,r=st.columns([1,2])
    with l:
        st.markdown("**Spara kalkyl som mall**")
        namn=st.text_input("Mallnamn",placeholder="T.ex. Standardbadrum")
        if st.button("💾 Spara",type="primary"):
            if namn and proj.get("rader"):
                mallar.append({"namn":namn,"rader":copy.deepcopy(proj["rader"]),
                               "skapad":datetime.date.today().isoformat()})
                st.session_state.mallar=mallar; st.success(f"'{namn}' sparad."); st.rerun()
            else: st.warning("Kalkylen är tom eller inget namn angivet.")
        st.divider()
        if mallar:
            st.download_button("⬇ Exportera mallar",
                data=json.dumps(mallar,ensure_ascii=False,indent=2).encode(),
                file_name="mallar.json",mime="application/json",
                use_container_width=True)
        up=st.file_uploader("📥 Importera mallar",type=["json"],key="mi")
        if up:
            try:
                imp=json.loads(up.read()); st.session_state.mallar.extend(imp)
                st.success(f"{len(imp)} mallar importerade."); st.rerun()
            except: st.error("Ogiltigt format.")
    with r:
        if not mallar: st.info("Inga mallar sparade.")
        else:
            for i,m in enumerate(mallar):
                with st.expander(f"📑 {m['namn']}  ({len(m.get('rader',[]))} rader)  – {m.get('skapad','')}"):
                    df=pd.DataFrame(m.get("rader",[]))[["Radtyp","Benämning","Byggdel","Mängd","Á-pris","Kostnad"]]
                    st.dataframe(df,hide_index=True,use_container_width=True,height=180)
                    bc1,bc2=st.columns(2)
                    if bc1.button("➕ Lägg till i kalkyl",key=f"anv{i}",type="primary"):
                        for rad in m.get("rader",[]):
                            ny=copy.deepcopy(rad); berakna(ny)
                            proj["rader"].append(ny)
                        st.session_state.projekt=proj
                        st.success(f"{len(m['rader'])} rader tillagda."); st.rerun()
                    if bc2.button("🗑 Radera",key=f"del{i}"):
                        mallar.pop(i); st.session_state.mallar=mallar; st.rerun()

# ──────────────────────────────────────────────────────────────
#  TAB BYGGDELAR
# ──────────────────────────────────────────────────────────────
def tab_byggdelar():
    proj=st.session_state.projekt; rader=proj.get("rader",[])
    bdlar=proj.get("byggdelar",BYGGDEL_DEF)
    st.markdown('<div class="section-hdr">Byggdelar – summering</div>',unsafe_allow_html=True)
    totals={}
    for r in rader:
        bd=r.get("Byggdel","") or "(Utan byggdel)"
        if bd not in totals: totals[bd]={"n":0,"k":0.0,"f":0.0}
        totals[bd]["n"]+=1; totals[bd]["k"]+=sf(r.get("Kostnad",0))
        totals[bd]["f"]+=sf(r.get("Försäljning",0))
    rows=[]
    for bd in list(bdlar)+["(Utan byggdel)"]:
        t=totals.get(bd,{"n":0,"k":0.0,"f":0.0})
        tb_=t["f"]-t["k"]; mg=(tb_/t["f"]*100) if t["f"] else 0
        rows.append({"Byggdel":bd,"Rader":t["n"],"Kostnad":round(t["k"],0),
                     "Försäljning":round(t["f"],0),"TB":round(tb_,0),"Marginal %":round(mg,1)})
    all_k=sum(r["Kostnad"] for r in rows); all_f=sum(r["Försäljning"] for r in rows)
    tb_t=all_f-all_k; mg_t=(tb_t/all_f*100) if all_f else 0
    rows.append({"Byggdel":"▶ TOTALT","Rader":sum(r["Rader"] for r in rows),
                 "Kostnad":round(all_k,0),"Försäljning":round(all_f,0),
                 "TB":round(tb_t,0),"Marginal %":round(mg_t,1)})
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True,
        column_config={
            "Kostnad":    st.column_config.NumberColumn(format="%,.0f kr"),
            "Försäljning":st.column_config.NumberColumn(format="%,.0f kr"),
            "TB":         st.column_config.NumberColumn(format="%,.0f kr"),
            "Marginal %": st.column_config.NumberColumn(format="%.1f %%"),
        })
    st.divider()
    vald=st.selectbox("Visa rader för:",["–"]+list(bdlar)+["(Utan byggdel)"])
    if vald!="–":
        bd_rader=[r for r in rader if (r.get("Byggdel","") or "(Utan byggdel)")==vald]
        if bd_rader:
            st.dataframe(pd.DataFrame(bd_rader)[
                ["Radtyp","Benämning","Mängd","Enhet","Á-pris","Kostnad","Försäljning","Leverantör"]],
                hide_index=True,use_container_width=True)
        else: st.info(f"Inga rader för {vald}.")

# ──────────────────────────────────────────────────────────────
#  TAB SLUTSIDA
# ──────────────────────────────────────────────────────────────
def tab_slutsida():
    proj=st.session_state.projekt
    st.markdown('<div class="section-hdr">Slutsida – Ekonomi</div>',unsafe_allow_html=True)
    l,r=st.columns([1,1])
    with l:
        st.markdown("**Omkostnader (kr)**")
        omk=proj.get("omkostnader",{k:0.0 for k in OMKKOSTNADER})
        ny_omk={}
        for k in OMKKOSTNADER:
            ny_omk[k]=st.number_input(k,value=float(omk.get(k,0)),
                                       min_value=0.0,step=1000.0,key=f"o_{k}")
        proj["omkostnader"]=ny_omk
        st.divider()
        st.markdown("**Påslag (%)**")
        pas=proj.get("paslag",{"Omkostnad %":10.0,"Risk %":5.0,"Vinst %":8.0,"Rabatt %":0.0})
        ny_pas={}
        for k in ["Omkostnad %","Risk %","Vinst %","Rabatt %"]:
            ny_pas[k]=st.number_input(k,value=float(pas.get(k,0)),
                                       min_value=0.0,max_value=100.0,step=0.5,key=f"p_{k}")
        proj["paslag"]=ny_pas
        st.session_state.projekt=proj

    with r:
        s=summera(proj)
        st.markdown("**Resultat**")
        items=[("Direkta kostnader",s["dir_k"],False),
               ("Omkostnader (fasta)",s["omk_s"],False),
               ("Omkostnadspåslag",s["omk_b"],False),
               ("Riskpåslag",s["ris_b"],False),
               ("Självkostnad",s["sjk"],True),
               ("Vinst",s["vin_b"],False),
               ("Försäljningspris",s["fp"],True),
               ("Täckningsbidrag",s["tb"],True)]
        for lbl,val,bold in items:
            txt=f"**{lbl}:** &nbsp; **{val:,.0f} kr**" if bold else f"{lbl}: &nbsp; {val:,.0f} kr"
            st.markdown(txt,unsafe_allow_html=True)
        st.divider()
        m1,m2=st.columns(2)
        m1.metric("Försäljningspris",kr(s["fp"]))
        m2.metric("Marginal",pct(s["mg"]))
        st.divider()
        if OPX_OK:
            buf=io.BytesIO(); _xl_slutsida(proj,buf); buf.seek(0)
            st.download_button("📊 Excel-slutsida",data=buf,
                file_name=f"{name_safe(proj)}_slutsida.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        if RL_OK:
            buf=io.BytesIO(); _pdf_slutsida(proj,buf); buf.seek(0)
            st.download_button("📄 PDF-slutsida",data=buf,
                file_name=f"{name_safe(proj)}_slutsida.pdf",
                mime="application/pdf",use_container_width=True)

# ──────────────────────────────────────────────────────────────
#  EXPORT HELPERS
# ──────────────────────────────────────────────────────────────
def name_safe(proj): return (proj.get("projektnamn","projekt") or "projekt").replace(" ","_")

def _xl_kalkyl(proj,buf):
    wb=openpyxl.Workbook(); ws=wb.active; ws.title="Kalkyl"
    hdrs=["Typ","Benämning","Byggdel","Mängd","Enhet","Tim","Á-pris","Kostnad","Pål%","Försäljning","Leverantör"]
    ws.append(hdrs)
    for cell in ws[1]:
        cell.fill=PatternFill("solid",fgColor="1A3A5C"); cell.font=Font(color="FFFFFF",bold=True)
    for r in proj.get("rader",[]):
        ws.append([r.get("Radtyp",""),r.get("Benämning",""),r.get("Byggdel",""),
                   r.get("Mängd",0),r.get("Enhet",""),r.get("Timmar",0),
                   r.get("Á-pris",0),r.get("Kostnad",0),r.get("Påslag %",0),
                   r.get("Försäljning",0),r.get("Leverantör","")])
    for col,w in zip("ABCDEFGHIJK",[8,30,14,8,6,6,10,12,6,12,14]):
        ws.column_dimensions[col].width=w
    wb.save(buf)

def _xl_slutsida(proj,buf):
    wb=openpyxl.Workbook(); ws=wb.active; ws.title="Slutsida"
    s=summera(proj)
    ws["A1"]=proj.get("projektnamn",""); ws["A1"].font=Font(bold=True,size=13)
    ws.append([]); ws.append(["Post","Belopp (kr)"])
    for cell in ws[3]: cell.fill=PatternFill("solid",fgColor="1A3A5C"); cell.font=Font(color="FFFFFF",bold=True)
    for p,v in [("Direkta kostnader",s["dir_k"]),("Omkostnader",s["omk_s"]),
                ("Självkostnad",s["sjk"]),("Vinst",s["vin_b"]),
                ("Försäljningspris",s["fp"]),("TB",s["tb"]),("Marginal %",s["mg"])]:
        ws.append([p,round(v,2)])
    ws.column_dimensions["A"].width=28; ws.column_dimensions["B"].width=18
    wb.save(buf)

def _pdf_kalkyl(proj,buf):
    doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=15*mm,rightMargin=15*mm,
                          topMargin=20*mm,bottomMargin=20*mm)
    styles=getSampleStyleSheet(); els=[]
    els.append(Paragraph(f"Kalkyl – {proj.get('projektnamn','')}",styles["Title"]))
    els.append(Spacer(1,4*mm))
    rows=[["Typ","Benämning","Byggdel","Mängd","Enhet","Á-pris","Kostnad","Försälj."]]
    for r in proj.get("rader",[]):
        rows.append([r.get("Radtyp","")[:3],r.get("Benämning","")[:30],
                     r.get("Byggdel","")[:12],f"{r.get('Mängd',0):.1f}",
                     r.get("Enhet",""),f"{r.get('Á-pris',0):.0f}",
                     f"{r.get('Kostnad',0):.0f}",f"{r.get('Försäljning',0):.0f}"])
    t=Table(rows,colWidths=[25,90,50,22,20,38,40,40],repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),rl_colors.HexColor("#1A3A5C")),
        ("TEXTCOLOR",(0,0),(-1,0),rl_colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),7),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[rl_colors.HexColor("#EEF3F8"),rl_colors.white]),
        ("GRID",(0,0),(-1,-1),0.3,rl_colors.grey),
    ])); els.append(t); doc.build(els)

def _pdf_slutsida(proj,buf):
    doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=20*mm,rightMargin=20*mm,
                          topMargin=25*mm,bottomMargin=20*mm)
    styles=getSampleStyleSheet(); s=summera(proj); els=[]
    els.append(Paragraph(f"Kalkyl – {proj.get('projektnamn','')}",styles["Title"]))
    els.append(Spacer(1,8*mm))
    data=[["Post","Belopp"],
          ["Direkta kostnader",f"{s['dir_k']:,.0f} kr"],
          ["Självkostnad",f"{s['sjk']:,.0f} kr"],
          ["Försäljningspris",f"{s['fp']:,.0f} kr"],
          ["Täckningsbidrag",f"{s['tb']:,.0f} kr"],
          ["Marginal",f"{s['mg']:.2f} %"]]
    t=Table(data,colWidths=[120*mm,60*mm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),rl_colors.HexColor("#1A3A5C")),
        ("TEXTCOLOR",(0,0),(-1,0),rl_colors.white),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),11),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[rl_colors.HexColor("#EEF3F8"),rl_colors.white]),
        ("GRID",(0,0),(-1,-1),0.5,rl_colors.grey),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ])); els.append(t); doc.build(els)

# ──────────────────────────────────────────────────────────────
#  MAIN
# ──────────────────────────────────────────────────────────────
def main():
    init(); sidebar()
    t1,t2,t3,t4,t5,t6,t7=st.tabs([
        "🏠 Start","📋 Projekt","🔢 Kalkyl",
        "💰 Prisbank","📑 Mallar","🏗 Byggdelar","📊 Slutsida"])
    with t1: tab_start()
    with t2: tab_projekt()
    with t3: tab_kalkyl()
    with t4: tab_prisbank()
    with t5: tab_mallar()
    with t6: tab_byggdelar()
    with t7: tab_slutsida()

if __name__=="__main__": main()
