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

KATEGORIER = ["Mark","Betong","Murning","Trä & stål","Isolering",
              "Tak","Puts","Målning","Beläggning","Sakvaror","Övrigt"]

DEFAULT_PRISBANK = [
    # MARK
    {"kod":"BC","benamning":"Maskinschakt källare klass A","enhet":"m³","matpris":472,"arbpris":0,"leverantor":"BK 2025","kategori":"Mark"},
    {"kod":"BC","benamning":"Maskinschakt källare klass B","enhet":"m³","matpris":504,"arbpris":0,"leverantor":"BK 2025","kategori":"Mark"},
    {"kod":"BC","benamning":"Maskinschakt källare klass C","enhet":"m³","matpris":530,"arbpris":0,"leverantor":"BK 2025","kategori":"Mark"},
    {"kod":"BC","benamning":"Schakt yttre rörgravar klass A","enhet":"m³","matpris":530,"arbpris":0,"leverantor":"BK 2025","kategori":"Mark"},
    {"kod":"BC","benamning":"Schakt yttre rörgravar klass B","enhet":"m³","matpris":562,"arbpris":0,"leverantor":"BK 2025","kategori":"Mark"},
    {"kod":"BC","benamning":"Grovplanering med schaktmaskin","enhet":"m²","matpris":106,"arbpris":0,"leverantor":"BK 2025","kategori":"Mark"},
    {"kod":"BC","benamning":"Fyllnad klass A schaktmaskin","enhet":"m³","matpris":176,"arbpris":0,"leverantor":"BK 2025","kategori":"Mark"},
    {"kod":"BC","benamning":"Fyllnad klass B C D schaktmaskin","enhet":"m³","matpris":228,"arbpris":0,"leverantor":"BK 2025","kategori":"Mark"},
    {"kod":"BC","benamning":"Asfalt 60Ab 8t exkl underarbete","enhet":"m²","matpris":530,"arbpris":0,"leverantor":"BK 2025","kategori":"Mark"},
    {"kod":"BC","benamning":"Asfalt 80Ab 12t exkl underarbete","enhet":"m²","matpris":600,"arbpris":0,"leverantor":"BK 2025","kategori":"Mark"},
    {"kod":"BC","benamning":"Grus slitlager 50mm","enhet":"m²","matpris":106,"arbpris":0,"leverantor":"BK 2025","kategori":"Mark"},
    {"kod":"BC","benamning":"Dräneringsrör PEH ø90","enhet":"m","matpris":176,"arbpris":0,"leverantor":"BK 2025","kategori":"Mark"},
    {"kod":"BC","benamning":"Dräneringsrör PEH ø110","enhet":"m","matpris":207,"arbpris":0,"leverantor":"BK 2025","kategori":"Mark"},
    {"kod":"BC","benamning":"Dräneringsrör PEH ø175","enhet":"m","matpris":266,"arbpris":0,"leverantor":"BK 2025","kategori":"Mark"},
    {"kod":"BC","benamning":"Gångbaneplattor betong 350x350x50mm","enhet":"m²","matpris":975,"arbpris":0,"leverantor":"BK 2025","kategori":"Mark"},
    # BETONG
    {"kod":"ES","benamning":"Betong C20/25 gjutning i hus","enhet":"m³","matpris":2778,"arbpris":446,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ES","benamning":"Betong C25/30 gjutning i hus","enhet":"m³","matpris":2835,"arbpris":446,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ES","benamning":"Betong C25/30 VT gjutning i hus","enhet":"m³","matpris":2993,"arbpris":446,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ES","benamning":"Betong C28/35 gjutning i hus","enhet":"m³","matpris":2989,"arbpris":495,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ESB","benamning":"Form väggar råplan 25mm","enhet":"m²","matpris":735,"arbpris":396,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ESB","benamning":"Form väggar gles","enhet":"m²","matpris":646,"arbpris":327,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ESB","benamning":"Form bjälklag 23mm råplan","enhet":"m²","matpris":600,"arbpris":297,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ESB","benamning":"Form pelare balkformar 23mm råplan","enhet":"m²","matpris":972,"arbpris":594,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ESC","benamning":"Armering B500 ø6mm","enhet":"kg","matpris":50,"arbpris":20,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ESC","benamning":"Armering B500 ø8-12mm","enhet":"kg","matpris":37,"arbpris":20,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ESC","benamning":"Armering B500 ø16-25mm","enhet":"kg","matpris":33,"arbpris":15,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ESC","benamning":"Armeringsnät 5150","enhet":"m²","matpris":68,"arbpris":20,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ESE","benamning":"Undergolv betong C25/30 50mm","enhet":"m²","matpris":174,"arbpris":50,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ESE","benamning":"Undergolv betong C25/30 100mm","enhet":"m²","matpris":285,"arbpris":54,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ESE","benamning":"Betonggolv helgjutet 70mm","enhet":"m²","matpris":282,"arbpris":99,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ESE","benamning":"Betonggolv helgjutet 100mm","enhet":"m²","matpris":343,"arbpris":99,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ESE","benamning":"Stålglättat golv 50mm","enhet":"m²","matpris":318,"arbpris":153,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ESE","benamning":"Stålglättat golv 60mm","enhet":"m²","matpris":345,"arbpris":158,"leverantor":"BK 2025","kategori":"Betong"},
    {"kod":"ESE","benamning":"Platsgjuten betongtrappa b=1000 per steg","enhet":"st","matpris":3126,"arbpris":1589,"leverantor":"BK 2025","kategori":"Betong"},
    # MURNING
    {"kod":"FSE","benamning":"Lättbetongblock mellanvägg 50mm","enhet":"m²","matpris":861,"arbpris":297,"leverantor":"BK 2025","kategori":"Murning"},
    {"kod":"FSE","benamning":"Lättbetongblock mellanvägg 70mm","enhet":"m²","matpris":921,"arbpris":297,"leverantor":"BK 2025","kategori":"Murning"},
    {"kod":"FSE","benamning":"Lättbetongblock mellanvägg 100mm","enhet":"m²","matpris":1063,"arbpris":297,"leverantor":"BK 2025","kategori":"Murning"},
    {"kod":"FSE","benamning":"Murblock yttervägg 150mm","enhet":"m²","matpris":1386,"arbpris":322,"leverantor":"BK 2025","kategori":"Murning"},
    {"kod":"FSE","benamning":"Murblock yttervägg 200mm","enhet":"m²","matpris":1768,"arbpris":322,"leverantor":"BK 2025","kategori":"Murning"},
    {"kod":"FSE","benamning":"Murblock yttervägg 250mm","enhet":"m²","matpris":2044,"arbpris":322,"leverantor":"BK 2025","kategori":"Murning"},
    {"kod":"FSF.2","benamning":"Lättklinker isolerblock 290x190x590mm","enhet":"m²","matpris":1898,"arbpris":257,"leverantor":"BK 2025","kategori":"Murning"},
    {"kod":"FSF.2","benamning":"Lättklinkerbetong 70x190x590mm","enhet":"m²","matpris":870,"arbpris":297,"leverantor":"BK 2025","kategori":"Murning"},
    {"kod":"FSF.2","benamning":"Lättklinkerbetong 125x198x498mm","enhet":"m²","matpris":1171,"arbpris":322,"leverantor":"BK 2025","kategori":"Murning"},
    {"kod":"FSG.2","benamning":"Tegel halvstens vägg puts","enhet":"m²","matpris":1583,"arbpris":371,"leverantor":"BK 2025","kategori":"Murning"},
    {"kod":"FSG.2","benamning":"Tegel helstens vägg puts","enhet":"m²","matpris":2967,"arbpris":599,"leverantor":"BK 2025","kategori":"Murning"},
    {"kod":"FSG.2","benamning":"Fasadmurning halvstens röd tegel","enhet":"m²","matpris":2594,"arbpris":545,"leverantor":"BK 2025","kategori":"Murning"},
    # TRÄ & STÅL
    {"kod":"HSD.11","benamning":"Regel virke 45x95 Ö-virke","enhet":"m","matpris":118,"arbpris":59,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.11","benamning":"Regel virke 45x120 Ö-virke","enhet":"m","matpris":127,"arbpris":59,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.11","benamning":"Regel virke 45x145 Ö-virke","enhet":"m","matpris":137,"arbpris":64,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.11","benamning":"Innerväggsregel 45x95 c600","enhet":"m²","matpris":243,"arbpris":94,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.11","benamning":"Innerväggsregel 45x120 c600","enhet":"m²","matpris":315,"arbpris":94,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.11","benamning":"Innerväggsregel 45x145 c600","enhet":"m²","matpris":332,"arbpris":99,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.11","benamning":"Ytterväggsregel 45x170 c600","enhet":"m²","matpris":344,"arbpris":94,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.12","benamning":"Bjälkar 45x145 c600 bjälklag","enhet":"m²","matpris":256,"arbpris":79,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.12","benamning":"Bjälkar 45x195 c600 bjälklag","enhet":"m²","matpris":322,"arbpris":89,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.12","benamning":"Bjälkar 45x220 c600 bjälklag","enhet":"m²","matpris":345,"arbpris":89,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.131","benamning":"Takstol fackverkstol c900 spw 8-12m","enhet":"m²","matpris":338,"arbpris":74,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.131","benamning":"Takstol fackverkstol c750 spw 15m","enhet":"m²","matpris":488,"arbpris":74,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.133","benamning":"Inbrädning yttertak 17mm råspontad","enhet":"m²","matpris":274,"arbpris":89,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.133","benamning":"Inbrädning yttertak 19mm råspontad","enhet":"m²","matpris":309,"arbpris":89,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.16","benamning":"Fasadpanel lockläkt 22x170","enhet":"m²","matpris":787,"arbpris":332,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.16","benamning":"Fasadpanel dubbelfasspont 22x145","enhet":"m²","matpris":576,"arbpris":193,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.17","benamning":"Panel inomhus 15mm granpanel","enhet":"m²","matpris":625,"arbpris":218,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.17","benamning":"Panel inomhus 22mm granpanel","enhet":"m²","matpris":768,"arbpris":218,"leverantor":"BK 2025","kategori":"Trä & stål"},
    {"kod":"HSD.12","benamning":"Golvreglar 45x70 c600","enhet":"m²","matpris":445,"arbpris":94,"leverantor":"BK 2025","kategori":"Trä & stål"},
    # ISOLERING
    {"kod":"IBE","benamning":"Mineralull yttervägg 70mm KL0.037","enhet":"m²","matpris":101,"arbpris":30,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBE","benamning":"Mineralull yttervägg 95mm KL0.037","enhet":"m²","matpris":120,"arbpris":30,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBE","benamning":"Mineralull yttervägg 120mm KL0.037","enhet":"m²","matpris":144,"arbpris":35,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBE","benamning":"Mineralull yttervägg 145mm KL0.037","enhet":"m²","matpris":165,"arbpris":35,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBE","benamning":"Mineralull yttervägg 170mm KL0.037","enhet":"m²","matpris":183,"arbpris":35,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBE","benamning":"Cellplast yttervägg 50mm","enhet":"m²","matpris":122,"arbpris":35,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBE","benamning":"Cellplast yttervägg 100mm","enhet":"m²","matpris":203,"arbpris":35,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBF","benamning":"Mineralull bjälklag 70mm KL0.036","enhet":"m²","matpris":135,"arbpris":35,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBF","benamning":"Mineralull bjälklag 120mm KL0.036","enhet":"m²","matpris":191,"arbpris":40,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBF","benamning":"Mineralull bjälklag 145mm KL0.036","enhet":"m²","matpris":209,"arbpris":40,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBG","benamning":"PIR-isolering tak/bjälklag 50mm","enhet":"m²","matpris":460,"arbpris":45,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBG","benamning":"PIR-isolering tak/bjälklag 100mm","enhet":"m²","matpris":767,"arbpris":45,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBG","benamning":"PIR-isolering tak/bjälklag 150mm","enhet":"m²","matpris":1001,"arbpris":50,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBG","benamning":"Takskiva stenull hård 80mm","enhet":"m²","matpris":564,"arbpris":59,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBG","benamning":"Takskiva stenull hård 100mm","enhet":"m²","matpris":655,"arbpris":59,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBC","benamning":"Markskiva cellplast 50mm","enhet":"m²","matpris":137,"arbpris":30,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBC","benamning":"Markskiva cellplast 100mm","enhet":"m²","matpris":222,"arbpris":30,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBC","benamning":"Sockelelement 75mm","enhet":"m","matpris":511,"arbpris":149,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBC","benamning":"Sockelelement 100mm","enhet":"m","matpris":629,"arbpris":149,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBF","benamning":"Lösull sprutad t400","enhet":"m²","matpris":192,"arbpris":0,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBF","benamning":"Lösull sprutad t500","enhet":"m²","matpris":240,"arbpris":0,"leverantor":"BK 2025","kategori":"Isolering"},
    {"kod":"IBF","benamning":"Ekofiber sprutad t400","enhet":"m²","matpris":300,"arbpris":0,"leverantor":"BK 2025","kategori":"Isolering"},
    # PUTS
    {"kod":"LBS","benamning":"Slamning vanlig invändig","enhet":"m²","matpris":141,"arbpris":84,"leverantor":"BK 2025","kategori":"Puts"},
    {"kod":"LBS","benamning":"Slätputs invändigt 6mm","enhet":"m²","matpris":371,"arbpris":153,"leverantor":"BK 2025","kategori":"Puts"},
    {"kod":"LBS","benamning":"Sockelputs stålslipat","enhet":"m²","matpris":617,"arbpris":307,"leverantor":"BK 2025","kategori":"Puts"},
    {"kod":"LBS","benamning":"Grundning + stänkputs utvändigt","enhet":"m²","matpris":271,"arbpris":0,"leverantor":"BK 2025","kategori":"Puts"},
    {"kod":"LBS","benamning":"Grundning + grovputs + stänkputs fin","enhet":"m²","matpris":625,"arbpris":0,"leverantor":"BK 2025","kategori":"Puts"},
    {"kod":"LBS","benamning":"Ädelputsfasad inkl stålnät","enhet":"m²","matpris":1280,"arbpris":0,"leverantor":"BK 2025","kategori":"Puts"},
    {"kod":"LBS","benamning":"Putsställning vägg/takyta","enhet":"m²","matpris":132,"arbpris":45,"leverantor":"BK 2025","kategori":"Puts"},
    # MÅLNING
    {"kod":"LCS","benamning":"Kalkfärg slät putsyta","enhet":"m²","matpris":70,"arbpris":0,"leverantor":"BK 2025","kategori":"Målning"},
    {"kod":"LCS","benamning":"Latexfärg på puts","enhet":"m²","matpris":79,"arbpris":0,"leverantor":"BK 2025","kategori":"Målning"},
    {"kod":"LCS","benamning":"Silikatfärg slät putsyta","enhet":"m²","matpris":90,"arbpris":0,"leverantor":"BK 2025","kategori":"Målning"},
    {"kod":"LCS","benamning":"Sandspacklingputs","enhet":"m²","matpris":47,"arbpris":0,"leverantor":"BK 2025","kategori":"Målning"},
    {"kod":"LCS","benamning":"Lackfärg bredd ≤30cm","enhet":"m","matpris":81,"arbpris":0,"leverantor":"BK 2025","kategori":"Målning"},
    {"kod":"LCS","benamning":"Tapetsering putsyta spruts","enhet":"m²","matpris":162,"arbpris":0,"leverantor":"BK 2025","kategori":"Målning"},
    {"kod":"LCS","benamning":"Glasfiberväv inkl målning puts","enhet":"m²","matpris":239,"arbpris":0,"leverantor":"BK 2025","kategori":"Målning"},
    {"kod":"LCS","benamning":"Glasfiberväv inkl målning skivor","enhet":"m²","matpris":240,"arbpris":0,"leverantor":"BK 2025","kategori":"Målning"},
    {"kod":"LCS","benamning":"Målning golv betong","enhet":"m²","matpris":150,"arbpris":0,"leverantor":"BK 2025","kategori":"Målning"},
    {"kod":"LCS","benamning":"Tapetsering betong/lättbetong","enhet":"m²","matpris":145,"arbpris":0,"leverantor":"BK 2025","kategori":"Målning"},
    {"kod":"LCS","benamning":"Målning nybyggnad villa per m³ BV","enhet":"m³","matpris":312,"arbpris":0,"leverantor":"BK 2025","kategori":"Målning"},
    {"kod":"LCS","benamning":"Målning nybyggnad flerbostadshus per m³","enhet":"m³","matpris":324,"arbpris":0,"leverantor":"BK 2025","kategori":"Målning"},
    # TAK
    {"kod":"JSD.1","benamning":"Tegelpannor lertegel normalformat","enhet":"m²","matpris":645,"arbpris":198,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.1","benamning":"Tegelpannor betong normalformat","enhet":"m²","matpris":520,"arbpris":178,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.1","benamning":"Tegelpannor lertegel enkupigt","enhet":"m²","matpris":780,"arbpris":218,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.2","benamning":"Stålplåt profilerad takplåt 0.5mm","enhet":"m²","matpris":395,"arbpris":148,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.2","benamning":"Stålplåt profilerad takplåt 0.6mm","enhet":"m²","matpris":440,"arbpris":148,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.2","benamning":"Falsad stålplåt stående serafimfals","enhet":"m²","matpris":625,"arbpris":218,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.3","benamning":"Papp 2-lagers fiberreinforcerad","enhet":"m²","matpris":335,"arbpris":99,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.3","benamning":"Papp 3-lagers bitumenpapp","enhet":"m²","matpris":490,"arbpris":138,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.3","benamning":"Takduk EPDM 1.5mm","enhet":"m²","matpris":565,"arbpris":148,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.4","benamning":"Asfaltssingel standard","enhet":"m²","matpris":285,"arbpris":89,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.4","benamning":"Asfaltssingel laminerad 30 år","enhet":"m²","matpris":360,"arbpris":89,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.5","benamning":"Takränna PVC ø125mm","enhet":"m","matpris":178,"arbpris":74,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.5","benamning":"Takränna plåt ø125mm","enhet":"m","matpris":245,"arbpris":89,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.5","benamning":"Stuprör PVC ø90mm","enhet":"m","matpris":132,"arbpris":59,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.5","benamning":"Stuprör plåt ø87mm","enhet":"m","matpris":198,"arbpris":74,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.6","benamning":"Takfönster standard 55x98cm","enhet":"st","matpris":6800,"arbpris":1485,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.6","benamning":"Takfönster standard 78x118cm","enhet":"st","matpris":8950,"arbpris":1980,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.7","benamning":"Snörasskydd stål per m","enhet":"m","matpris":385,"arbpris":99,"leverantor":"BK 2025","kategori":"Tak"},
    {"kod":"JSD.7","benamning":"Taksäkerhetsutrustning gångbrygga m","enhet":"m","matpris":1250,"arbpris":198,"leverantor":"BK 2025","kategori":"Tak"},
    # BELÄGGNING
    {"kod":"NSS.1","benamning":"Klinker 150x150 stengodsklinker","enhet":"m²","matpris":895,"arbpris":396,"leverantor":"BK 2025","kategori":"Beläggning"},
    {"kod":"NSS.1","benamning":"Klinker 200x200 stengodsklinker","enhet":"m²","matpris":825,"arbpris":347,"leverantor":"BK 2025","kategori":"Beläggning"},
    {"kod":"NSS.1","benamning":"Klinker 300x300 stengodsklinker","enhet":"m²","matpris":780,"arbpris":297,"leverantor":"BK 2025","kategori":"Beläggning"},
    {"kod":"NSS.1","benamning":"Klinker 600x600 stengodsklinker","enhet":"m²","matpris":1050,"arbpris":297,"leverantor":"BK 2025","kategori":"Beläggning"},
    {"kod":"NSS.2","benamning":"Parkett massiv 22mm ek","enhet":"m²","matpris":1380,"arbpris":198,"leverantor":"BK 2025","kategori":"Beläggning"},
    {"kod":"NSS.2","benamning":"Parkett 3-stav 14mm ek","enhet":"m²","matpris":980,"arbpris":178,"leverantor":"BK 2025","kategori":"Beläggning"},
    {"kod":"NSS.2","benamning":"Laminat 8mm AC4","enhet":"m²","matpris":485,"arbpris":148,"leverantor":"BK 2025","kategori":"Beläggning"},
    {"kod":"NSS.2","benamning":"Laminat 12mm AC5","enhet":"m²","matpris":595,"arbpris":148,"leverantor":"BK 2025","kategori":"Beläggning"},
    {"kod":"NSS.3","benamning":"PVC-planka 5mm LVT","enhet":"m²","matpris":545,"arbpris":99,"leverantor":"BK 2025","kategori":"Beläggning"},
    {"kod":"NSS.3","benamning":"Linoleum 2.5mm på golv","enhet":"m²","matpris":465,"arbpris":148,"leverantor":"BK 2025","kategori":"Beläggning"},
    {"kod":"NSS.3","benamning":"Plastmatta homogen 2mm","enhet":"m²","matpris":385,"arbpris":138,"leverantor":"BK 2025","kategori":"Beläggning"},
    {"kod":"NSS.4","benamning":"Matta heltäckningsmatta enkel","enhet":"m²","matpris":495,"arbpris":99,"leverantor":"BK 2025","kategori":"Beläggning"},
    {"kod":"NSS.5","benamning":"Undergolv avjämning 10mm","enhet":"m²","matpris":148,"arbpris":59,"leverantor":"BK 2025","kategori":"Beläggning"},
    {"kod":"NSS.5","benamning":"Undergolv avjämning 20mm","enhet":"m²","matpris":218,"arbpris":69,"leverantor":"BK 2025","kategori":"Beläggning"},
    {"kod":"NSS.5","benamning":"Spånskiva golvskiva 22mm","enhet":"m²","matpris":198,"arbpris":74,"leverantor":"BK 2025","kategori":"Beläggning"},
    {"kod":"NSS.5","benamning":"Golvvärme el i gjutning","enhet":"m²","matpris":745,"arbpris":148,"leverantor":"BK 2025","kategori":"Beläggning"},
    # SAKVAROR
    {"kod":"PSB","benamning":"Innerdörr massiv ek 9x21 komplett","enhet":"st","matpris":5800,"arbpris":990,"leverantor":"BK 2025","kategori":"Sakvaror"},
    {"kod":"PSB","benamning":"Innerdörr mdf 9x21 komplett","enhet":"st","matpris":3200,"arbpris":742,"leverantor":"BK 2025","kategori":"Sakvaror"},
    {"kod":"PSB","benamning":"Ytterdörr stål isolerad 9x21","enhet":"st","matpris":12500,"arbpris":1980,"leverantor":"BK 2025","kategori":"Sakvaror"},
    {"kod":"PSB","benamning":"Ytterdörr trä 9x21 komplett","enhet":"st","matpris":18500,"arbpris":1980,"leverantor":"BK 2025","kategori":"Sakvaror"},
    {"kod":"PSC","benamning":"Fönster trä/alu 10x12 2-glas","enhet":"st","matpris":8900,"arbpris":1485,"leverantor":"BK 2025","kategori":"Sakvaror"},
    {"kod":"PSC","benamning":"Fönster trä/alu 12x14 2-glas","enhet":"st","matpris":11500,"arbpris":1980,"leverantor":"BK 2025","kategori":"Sakvaror"},
    {"kod":"PSC","benamning":"Fönster trä/alu 10x12 3-glas","enhet":"st","matpris":10800,"arbpris":1485,"leverantor":"BK 2025","kategori":"Sakvaror"},
    {"kod":"PSC","benamning":"Fönster PVC 10x12 2-glas","enhet":"st","matpris":6500,"arbpris":1485,"leverantor":"BK 2025","kategori":"Sakvaror"},
    {"kod":"PSD","benamning":"Köksstomme IKEA standard m² stomme","enhet":"m²","matpris":4500,"arbpris":990,"leverantor":"BK 2025","kategori":"Sakvaror"},
    {"kod":"PSD","benamning":"Diskbänk rostfri 1200mm","enhet":"st","matpris":3800,"arbpris":495,"leverantor":"BK 2025","kategori":"Sakvaror"},
    {"kod":"PSD","benamning":"Badrumspaket enkel (tvättst+wc+dusch)","enhet":"st","matpris":28000,"arbpris":9900,"leverantor":"BK 2025","kategori":"Sakvaror"},
    {"kod":"PSE","benamning":"Trappa rak trä enkel 2700mm","enhet":"st","matpris":22000,"arbpris":4950,"leverantor":"BK 2025","kategori":"Sakvaror"},
    {"kod":"PSE","benamning":"Trappa rak ek 2700mm","enhet":"st","matpris":38000,"arbpris":4950,"leverantor":"BK 2025","kategori":"Sakvaror"},
    {"kod":"PSF","benamning":"Tätskikt badrum vattentät duk","enhet":"m²","matpris":485,"arbpris":198,"leverantor":"BK 2025","kategori":"Sakvaror"},
    {"kod":"PSF","benamning":"Tätskikt badrum flytspackel","enhet":"m²","matpris":198,"arbpris":99,"leverantor":"BK 2025","kategori":"Sakvaror"},
]

EXEMPELPROJEKT = [{'projektnamn': 'Badrumsrenovering Ringvägen 12', 'projektnummer': '2025-001', 'kund': 'Anders & Maria Lindström', 'bestallar': 'Anders Lindström', 'adress': 'Ringvägen 12, 123 45 Huddinge', 'datum': '2025-03-01', 'kalkylansvarig': 'Jan Stefors', 'status': 'Offert', 'kommentar': 'Badrumsrenovering ca 7m². Befintlig badkar byts mot dusch. Ny klinker golv och vägg. ROT-avdrag tillämpas.', 'byggdelar': ['Rivning', 'Tätskikt', 'Klinker', 'VVS', 'El', 'Övrigt'], 'omkostnader': {'Arbetsledning': 4500.0, 'Etablering': 2000.0, 'Administration': 1500.0, 'Transporter': 2500.0, 'Garanti': 0.0, 'Risk': 0.0, 'Övrigt': 0.0}, 'paslag': {'Omkostnad %': 10.0, 'Risk %': 5.0, 'Vinst %': 8.0, 'Rabatt %': 0.0}, 'rader': [{'Radtyp': 'UE', 'Benämning': 'Rivning befintligt badrum inkl borttransport', 'Byggdel': 'Rivning', 'Mängd': 1.0, 'Enhet': 'ls', 'Timmar': 0.0, 'Á-pris': 18500, 'Påslag %': 0.0, 'Kostnad': 18500.0, 'Försäljning': 18500.0, 'Leverantör': 'UE Rivning AB', 'Kod': '', 'Kommentar': 'Fast pris inkl container'}, {'Radtyp': 'Material', 'Benämning': 'Undergolv betong C25/30 50mm', 'Byggdel': 'Tätskikt', 'Mängd': 7.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 174, 'Påslag %': 0.0, 'Kostnad': 1218.0, 'Försäljning': 1218.0, 'Leverantör': 'BK 2025', 'Kod': 'ESE', 'Kommentar': ''}, {'Radtyp': 'Arbete', 'Benämning': 'Gjutning undergolv', 'Byggdel': 'Tätskikt', 'Mängd': 0.0, 'Enhet': 'tim', 'Timmar': 6.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 3570.0, 'Försäljning': 3570.0, 'Leverantör': 'Eget', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Tätskikt badrum vattentät duk', 'Byggdel': 'Tätskikt', 'Mängd': 14.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 485, 'Påslag %': 0.0, 'Kostnad': 6790.0, 'Försäljning': 6790.0, 'Leverantör': 'BK 2025', 'Kod': 'PSF', 'Kommentar': 'Golv + väggar 1m upp'}, {'Radtyp': 'Arbete', 'Benämning': 'Montering tätskikt', 'Byggdel': 'Tätskikt', 'Mängd': 0.0, 'Enhet': 'tim', 'Timmar': 10.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 5950.0, 'Försäljning': 5950.0, 'Leverantör': 'Eget', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Klinker 300x300 stengodsklinker', 'Byggdel': 'Klinker', 'Mängd': 7.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 780, 'Påslag %': 0.0, 'Kostnad': 5460.0, 'Försäljning': 5460.0, 'Leverantör': 'BK 2025', 'Kod': 'NSS.1', 'Kommentar': 'Golvklinker halkfri R11'}, {'Radtyp': 'Arbete', 'Benämning': 'Läggning klinker golv inkl fogning', 'Byggdel': 'Klinker', 'Mängd': 0.0, 'Enhet': 'tim', 'Timmar': 12.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 7140.0, 'Försäljning': 7140.0, 'Leverantör': 'Eget', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Klinker 200x200 stengodsklinker', 'Byggdel': 'Klinker', 'Mängd': 22.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 825, 'Påslag %': 0.0, 'Kostnad': 18150.0, 'Försäljning': 18150.0, 'Leverantör': 'BK 2025', 'Kod': 'NSS.1', 'Kommentar': 'Väggklinker vit 200x200'}, {'Radtyp': 'Arbete', 'Benämning': 'Läggning klinker vägg inkl fogning', 'Byggdel': 'Klinker', 'Mängd': 0.0, 'Enhet': 'tim', 'Timmar': 28.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 16660.0, 'Försäljning': 16660.0, 'Leverantör': 'Eget', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'UE', 'Benämning': 'VVS komplett: dusch, wc, tvättställ, rör', 'Byggdel': 'VVS', 'Mängd': 1.0, 'Enhet': 'ls', 'Timmar': 0.0, 'Á-pris': 38500, 'Påslag %': 0.0, 'Kostnad': 38500.0, 'Försäljning': 38500.0, 'Leverantör': 'VVS Proffs AB', 'Kod': '', 'Kommentar': 'Fast pris inkl material'}, {'Radtyp': 'UE', 'Benämning': 'El: belysning, golvvärme, ventilationsfläkt', 'Byggdel': 'El', 'Mängd': 1.0, 'Enhet': 'ls', 'Timmar': 0.0, 'Á-pris': 12500, 'Påslag %': 0.0, 'Kostnad': 12500.0, 'Försäljning': 12500.0, 'Leverantör': 'EL-service', 'Kod': '', 'Kommentar': 'Fast pris inkl material'}, {'Radtyp': 'Material', 'Benämning': 'Spegel + badrumsskåp', 'Byggdel': 'Övrigt', 'Mängd': 1.0, 'Enhet': 'st', 'Timmar': 0.0, 'Á-pris': 3800, 'Påslag %': 0.0, 'Kostnad': 3800.0, 'Försäljning': 3800.0, 'Leverantör': 'IKEA', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'Arbete', 'Benämning': 'Montering, slutsnickeri och städning', 'Byggdel': 'Övrigt', 'Mängd': 0.0, 'Enhet': 'tim', 'Timmar': 8.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 4760.0, 'Försäljning': 4760.0, 'Leverantör': 'Eget', 'Kod': '', 'Kommentar': ''}]}, {'projektnamn': 'Tillbyggnad Villa Björkgatan 5', 'projektnummer': '2025-002', 'kund': 'Familjen Svensson', 'bestallar': 'Petra Svensson', 'adress': 'Björkgatan 5, 702 28 Örebro', 'datum': '2025-04-15', 'kalkylansvarig': 'Jan Stefors', 'status': 'Kalkyl', 'kommentar': 'Tillbyggnad av befintlig villa, plan 1. Ca 30m² nya boarea. Inkl grund, stomme, tak, fasad och invändigt. Bygglov beviljat 2025-02-10.', 'byggdelar': ['Grund', 'Stomme', 'Tak', 'Fasad', 'Isolering', 'Invändigt', 'El & VVS'], 'omkostnader': {'Arbetsledning': 15000.0, 'Etablering': 8000.0, 'Administration': 5000.0, 'Transporter': 6000.0, 'Garanti': 3000.0, 'Risk': 0.0, 'Övrigt': 2000.0}, 'paslag': {'Omkostnad %': 12.0, 'Risk %': 5.0, 'Vinst %': 10.0, 'Rabatt %': 0.0}, 'rader': [{'Radtyp': 'Material', 'Benämning': 'Maskinschakt källare klass A', 'Byggdel': 'Grund', 'Mängd': 35.0, 'Enhet': 'm³', 'Timmar': 0.0, 'Á-pris': 472, 'Påslag %': 0.0, 'Kostnad': 16520.0, 'Försäljning': 16520.0, 'Leverantör': 'BK 2025', 'Kod': 'BC', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Markskiva cellplast 100mm', 'Byggdel': 'Grund', 'Mängd': 30.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 222, 'Påslag %': 0.0, 'Kostnad': 6660.0, 'Försäljning': 6660.0, 'Leverantör': 'BK 2025', 'Kod': 'IBC', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Betong C25/30 gjutning i hus', 'Byggdel': 'Grund', 'Mängd': 6.0, 'Enhet': 'm³', 'Timmar': 0.0, 'Á-pris': 2835, 'Påslag %': 0.0, 'Kostnad': 17010.0, 'Försäljning': 17010.0, 'Leverantör': 'BK 2025', 'Kod': 'ES', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Armering B500 ø8-12mm', 'Byggdel': 'Grund', 'Mängd': 280.0, 'Enhet': 'kg', 'Timmar': 0.0, 'Á-pris': 37, 'Påslag %': 0.0, 'Kostnad': 10360.0, 'Försäljning': 10360.0, 'Leverantör': 'BK 2025', 'Kod': 'ESC', 'Kommentar': ''}, {'Radtyp': 'Arbete', 'Benämning': 'Gjutning grund inkl form', 'Byggdel': 'Grund', 'Mängd': 0.0, 'Enhet': 'tim', 'Timmar': 24.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 14280.0, 'Försäljning': 14280.0, 'Leverantör': 'Eget', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Ytterväggsregel 45x170 c600', 'Byggdel': 'Stomme', 'Mängd': 55.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 344, 'Påslag %': 0.0, 'Kostnad': 18920.0, 'Försäljning': 18920.0, 'Leverantör': 'BK 2025', 'Kod': 'HSD.11', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Bjälkar 45x195 c600 bjälklag', 'Byggdel': 'Stomme', 'Mängd': 30.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 322, 'Påslag %': 0.0, 'Kostnad': 9660.0, 'Försäljning': 9660.0, 'Leverantör': 'BK 2025', 'Kod': 'HSD.12', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Innerväggsregel 45x95 c600', 'Byggdel': 'Stomme', 'Mängd': 18.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 243, 'Påslag %': 0.0, 'Kostnad': 4374.0, 'Försäljning': 4374.0, 'Leverantör': 'BK 2025', 'Kod': 'HSD.11', 'Kommentar': ''}, {'Radtyp': 'Arbete', 'Benämning': 'Resning och montering stomme', 'Byggdel': 'Stomme', 'Mängd': 0.0, 'Enhet': 'tim', 'Timmar': 40.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 23800.0, 'Försäljning': 23800.0, 'Leverantör': 'Eget', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Takstol fackverkstol c900 spw 8-12m', 'Byggdel': 'Tak', 'Mängd': 30.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 338, 'Påslag %': 0.0, 'Kostnad': 10140.0, 'Försäljning': 10140.0, 'Leverantör': 'BK 2025', 'Kod': 'HSD.131', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Inbrädning yttertak 19mm råspontad', 'Byggdel': 'Tak', 'Mängd': 33.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 309, 'Påslag %': 0.0, 'Kostnad': 10197.0, 'Försäljning': 10197.0, 'Leverantör': 'BK 2025', 'Kod': 'HSD.133', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Tegelpannor betong normalformat', 'Byggdel': 'Tak', 'Mängd': 33.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 520, 'Påslag %': 0.0, 'Kostnad': 17160.0, 'Försäljning': 17160.0, 'Leverantör': 'BK 2025', 'Kod': 'JSD.1', 'Kommentar': ''}, {'Radtyp': 'Arbete', 'Benämning': 'Takläggning', 'Byggdel': 'Tak', 'Mängd': 0.0, 'Enhet': 'tim', 'Timmar': 20.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 11900.0, 'Försäljning': 11900.0, 'Leverantör': 'Eget', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Takränna plåt ø125mm', 'Byggdel': 'Tak', 'Mängd': 8.0, 'Enhet': 'm', 'Timmar': 0.0, 'Á-pris': 245, 'Påslag %': 0.0, 'Kostnad': 1960.0, 'Försäljning': 1960.0, 'Leverantör': 'BK 2025', 'Kod': 'JSD.5', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Stuprör plåt ø87mm', 'Byggdel': 'Tak', 'Mängd': 5.0, 'Enhet': 'm', 'Timmar': 0.0, 'Á-pris': 198, 'Påslag %': 0.0, 'Kostnad': 990.0, 'Försäljning': 990.0, 'Leverantör': 'BK 2025', 'Kod': 'JSD.5', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Mineralull yttervägg 145mm KL0.037', 'Byggdel': 'Fasad', 'Mängd': 55.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 165, 'Påslag %': 0.0, 'Kostnad': 9075.0, 'Försäljning': 9075.0, 'Leverantör': 'BK 2025', 'Kod': 'IBE', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Fasadpanel lockläkt 22x170', 'Byggdel': 'Fasad', 'Mängd': 55.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 787, 'Påslag %': 0.0, 'Kostnad': 43285.0, 'Försäljning': 43285.0, 'Leverantör': 'BK 2025', 'Kod': 'HSD.16', 'Kommentar': ''}, {'Radtyp': 'Arbete', 'Benämning': 'Montering fasad inkl isolering', 'Byggdel': 'Fasad', 'Mängd': 0.0, 'Enhet': 'tim', 'Timmar': 36.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 21420.0, 'Försäljning': 21420.0, 'Leverantör': 'Eget', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Fönster trä/alu 10x12 3-glas', 'Byggdel': 'Fasad', 'Mängd': 3.0, 'Enhet': 'st', 'Timmar': 0.0, 'Á-pris': 10800, 'Påslag %': 0.0, 'Kostnad': 32400.0, 'Försäljning': 32400.0, 'Leverantör': 'BK 2025', 'Kod': 'PSC', 'Kommentar': ''}, {'Radtyp': 'Arbete', 'Benämning': 'Montering fönster', 'Byggdel': 'Fasad', 'Mängd': 0.0, 'Enhet': 'tim', 'Timmar': 9.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 5355.0, 'Försäljning': 5355.0, 'Leverantör': 'Eget', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Ytterdörr stål isolerad 9x21', 'Byggdel': 'Fasad', 'Mängd': 1.0, 'Enhet': 'st', 'Timmar': 0.0, 'Á-pris': 12500, 'Påslag %': 0.0, 'Kostnad': 12500.0, 'Försäljning': 12500.0, 'Leverantör': 'BK 2025', 'Kod': 'PSB', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Mineralull bjälklag 145mm KL0.036', 'Byggdel': 'Isolering', 'Mängd': 30.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 209, 'Påslag %': 0.0, 'Kostnad': 6270.0, 'Försäljning': 6270.0, 'Leverantör': 'BK 2025', 'Kod': 'IBF', 'Kommentar': ''}, {'Radtyp': 'Arbete', 'Benämning': 'Isolering invändig inkl ångspärr', 'Byggdel': 'Isolering', 'Mängd': 0.0, 'Enhet': 'tim', 'Timmar': 16.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 9520.0, 'Försäljning': 9520.0, 'Leverantör': 'Eget', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Spånskiva golvskiva 22mm', 'Byggdel': 'Invändigt', 'Mängd': 30.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 198, 'Påslag %': 0.0, 'Kostnad': 5940.0, 'Försäljning': 5940.0, 'Leverantör': 'BK 2025', 'Kod': 'NSS.5', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Laminat 12mm AC5', 'Byggdel': 'Invändigt', 'Mängd': 28.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 16660.0, 'Försäljning': 16660.0, 'Leverantör': 'BK 2025', 'Kod': 'NSS.2', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Innerdörr mdf 9x21 komplett', 'Byggdel': 'Invändigt', 'Mängd': 2.0, 'Enhet': 'st', 'Timmar': 0.0, 'Á-pris': 3200, 'Påslag %': 0.0, 'Kostnad': 6400.0, 'Försäljning': 6400.0, 'Leverantör': 'BK 2025', 'Kod': 'PSB', 'Kommentar': ''}, {'Radtyp': 'Arbete', 'Benämning': 'Invändig finish, lister, målning', 'Byggdel': 'Invändigt', 'Mängd': 0.0, 'Enhet': 'tim', 'Timmar': 32.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 19040.0, 'Försäljning': 19040.0, 'Leverantör': 'Eget', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'UE', 'Benämning': 'El: komplett ny elinstallation', 'Byggdel': 'El & VVS', 'Mängd': 1.0, 'Enhet': 'ls', 'Timmar': 0.0, 'Á-pris': 28000, 'Påslag %': 0.0, 'Kostnad': 28000.0, 'Försäljning': 28000.0, 'Leverantör': 'EL AB', 'Kod': '', 'Kommentar': 'Fast pris inkl material'}, {'Radtyp': 'UE', 'Benämning': 'VVS: radiator, rör, koppling', 'Byggdel': 'El & VVS', 'Mängd': 1.0, 'Enhet': 'ls', 'Timmar': 0.0, 'Á-pris': 22000, 'Påslag %': 0.0, 'Kostnad': 22000.0, 'Försäljning': 22000.0, 'Leverantör': 'VVS AB', 'Kod': '', 'Kommentar': 'Fast pris inkl material'}]}, {'projektnamn': 'Fasadrenovering Solhemsgatan 14-18', 'projektnummer': '2025-003', 'kund': 'Brf Solhem', 'bestallar': 'Styrelsen Brf Solhem', 'adress': 'Solhemsgatan 14-18, 163 41 Spånga', 'datum': '2025-05-01', 'kalkylansvarig': 'Jan Stefors', 'status': 'Kalkyl', 'kommentar': 'Fasadrenovering 3 huskroppar. Byte av puts, tilläggsisolering 70mm, ny ädelputs och fönsterbyte. Ca 1 200m² fasad. Upphandlas som totalentreprenad.', 'byggdelar': ['Ställning', 'Rivning', 'Isolering', 'Puts', 'Fönster', 'Målning', 'Mark'], 'omkostnader': {'Arbetsledning': 45000.0, 'Etablering': 25000.0, 'Administration': 18000.0, 'Transporter': 12000.0, 'Garanti': 15000.0, 'Risk': 0.0, 'Övrigt': 5000.0}, 'paslag': {'Omkostnad %': 12.0, 'Risk %': 6.0, 'Vinst %': 9.0, 'Rabatt %': 2.0}, 'rader': [{'Radtyp': 'UE', 'Benämning': 'Fasadställning hyra 3 mån inkl montage', 'Byggdel': 'Ställning', 'Mängd': 1200.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 185, 'Påslag %': 0.0, 'Kostnad': 222000.0, 'Försäljning': 222000.0, 'Leverantör': 'Ställnings AB', 'Kod': '', 'Kommentar': 'Inkl montering och demontering'}, {'Radtyp': 'UE', 'Benämning': 'Borthuggning befintlig puts klass B', 'Byggdel': 'Rivning', 'Mängd': 1200.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 148, 'Påslag %': 0.0, 'Kostnad': 177600.0, 'Försäljning': 177600.0, 'Leverantör': 'Rivning AB', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'UE', 'Benämning': 'Borttransport rivmassor container', 'Byggdel': 'Rivning', 'Mängd': 1.0, 'Enhet': 'ls', 'Timmar': 0.0, 'Á-pris': 42000, 'Påslag %': 0.0, 'Kostnad': 42000.0, 'Försäljning': 42000.0, 'Leverantör': 'Rivning AB', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Mineralull yttervägg 70mm KL0.037', 'Byggdel': 'Isolering', 'Mängd': 1200.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 101, 'Påslag %': 0.0, 'Kostnad': 121200.0, 'Försäljning': 121200.0, 'Leverantör': 'BK 2025', 'Kod': 'IBE', 'Kommentar': ''}, {'Radtyp': 'Arbete', 'Benämning': 'Montering mineralull inkl mekaniska fästen', 'Byggdel': 'Isolering', 'Mängd': 0.0, 'Enhet': 'tim', 'Timmar': 180.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 107100.0, 'Försäljning': 107100.0, 'Leverantör': 'Eget', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Grundning + stänkputs utvändigt', 'Byggdel': 'Puts', 'Mängd': 1200.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 271, 'Påslag %': 0.0, 'Kostnad': 325200.0, 'Försäljning': 325200.0, 'Leverantör': 'BK 2025', 'Kod': 'LBS', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Grundning + grovputs + stänkputs fin', 'Byggdel': 'Puts', 'Mängd': 1200.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 625, 'Påslag %': 0.0, 'Kostnad': 750000.0, 'Försäljning': 750000.0, 'Leverantör': 'BK 2025', 'Kod': 'LBS', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Ädelputsfasad inkl stålnät', 'Byggdel': 'Puts', 'Mängd': 1200.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 1280, 'Påslag %': 0.0, 'Kostnad': 1536000.0, 'Försäljning': 1536000.0, 'Leverantör': 'BK 2025', 'Kod': 'LBS', 'Kommentar': ''}, {'Radtyp': 'Arbete', 'Benämning': 'Puts och ytbehandling fasad', 'Byggdel': 'Puts', 'Mängd': 0.0, 'Enhet': 'tim', 'Timmar': 200.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 119000.0, 'Försäljning': 119000.0, 'Leverantör': 'Eget', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Fönster trä/alu 10x12 2-glas', 'Byggdel': 'Fönster', 'Mängd': 48.0, 'Enhet': 'st', 'Timmar': 0.0, 'Á-pris': 8900, 'Påslag %': 0.0, 'Kostnad': 427200.0, 'Försäljning': 427200.0, 'Leverantör': 'BK 2025', 'Kod': 'PSC', 'Kommentar': 'Lägenheter'}, {'Radtyp': 'Material', 'Benämning': 'Fönster trä/alu 12x14 2-glas', 'Byggdel': 'Fönster', 'Mängd': 12.0, 'Enhet': 'st', 'Timmar': 0.0, 'Á-pris': 11500, 'Påslag %': 0.0, 'Kostnad': 138000.0, 'Försäljning': 138000.0, 'Leverantör': 'BK 2025', 'Kod': 'PSC', 'Kommentar': 'Trapphus och gavlar'}, {'Radtyp': 'Arbete', 'Benämning': 'Montering fönster inkl tätning', 'Byggdel': 'Fönster', 'Mängd': 0.0, 'Enhet': 'tim', 'Timmar': 120.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 71400.0, 'Försäljning': 71400.0, 'Leverantör': 'Eget', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Silikatfärg slät putsyta', 'Byggdel': 'Målning', 'Mängd': 1200.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 90, 'Påslag %': 0.0, 'Kostnad': 108000.0, 'Försäljning': 108000.0, 'Leverantör': 'BK 2025', 'Kod': 'LCS', 'Kommentar': '2 strykningar'}, {'Radtyp': 'Arbete', 'Benämning': 'Målning fasad', 'Byggdel': 'Målning', 'Mängd': 0.0, 'Enhet': 'tim', 'Timmar': 160.0, 'Á-pris': 595, 'Påslag %': 0.0, 'Kostnad': 95200.0, 'Försäljning': 95200.0, 'Leverantör': 'Eget', 'Kod': '', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Sockelputs stålslipat', 'Byggdel': 'Målning', 'Mängd': 120.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 617, 'Påslag %': 0.0, 'Kostnad': 74040.0, 'Försäljning': 74040.0, 'Leverantör': 'BK 2025', 'Kod': 'LBS', 'Kommentar': ''}, {'Radtyp': 'Material', 'Benämning': 'Gångbaneplattor betong 350x350x50mm', 'Byggdel': 'Mark', 'Mängd': 85.0, 'Enhet': 'm²', 'Timmar': 0.0, 'Á-pris': 975, 'Påslag %': 0.0, 'Kostnad': 82875.0, 'Försäljning': 82875.0, 'Leverantör': 'BK 2025', 'Kod': 'BC', 'Kommentar': 'Reparation efter ställning'}, {'Radtyp': 'UE', 'Benämning': 'Slutbesiktning och dokumentation', 'Byggdel': 'Mark', 'Mängd': 1.0, 'Enhet': 'ls', 'Timmar': 0.0, 'Á-pris': 18500, 'Påslag %': 0.0, 'Kostnad': 18500.0, 'Försäljning': 18500.0, 'Leverantör': 'Besiktnings AB', 'Kod': '', 'Kommentar': ''}]}]

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

def sync_active():
    """Spara aktivt projekt tillbaka till projektlistan."""
    idx  = st.session_state.get("aktivt_idx", 0)
    lista= st.session_state.get("projekt_lista", [])
    if lista and idx < len(lista):
        lista[idx] = st.session_state.projekt

def init():
    if "projekt_lista" not in st.session_state:
        st.session_state.projekt_lista = copy.deepcopy(EXEMPELPROJEKT)
        st.session_state.aktivt_idx    = 0
        st.session_state.projekt       = copy.deepcopy(EXEMPELPROJEKT[0])
    if "prisbank" not in st.session_state: st.session_state.prisbank=list(DEFAULT_PRISBANK)
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
/* ── Flikar – tydligare ── */
.stTabs [data-baseweb="tab-list"]{gap:4px;border-bottom:2px solid #1a3a5c;padding-bottom:0}
.stTabs [data-baseweb="tab"]{background:#e8edf4;border-radius:6px 6px 0 0;
    padding:8px 16px;font-weight:600;font-size:.92rem;color:#1a3a5c;border:none}
.stTabs [aria-selected="true"]{background:#1a3a5c !important;color:white !important}
/* ── Utskrift ── */
@media print{
  section[data-testid="stSidebar"]{display:none}
  .stTabs [data-baseweb="tab-list"]{display:none}
  .block-container{padding:0}
  button,footer{display:none}
}
</style>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
#  SIDEBAR
# ──────────────────────────────────────────────────────────────
def sidebar():
    sync_active()
    proj =st.session_state.projekt
    lista=st.session_state.projekt_lista
    akt  =st.session_state.get("aktivt_idx",0)

    with st.sidebar:
        st.markdown("## 🏗 Kalkylprogram")
        st.caption("Bygg & Entreprenad  v2")
        st.divider()

        # ── Projektlista ──────────────────────────────────────
        st.markdown("**Projekt**")
        namn_lista=[p.get("projektnamn","") or f"Projekt {i+1}"
                    for i,p in enumerate(lista)]
        valt=st.selectbox("Välj projekt",namn_lista,index=akt,
                          label_visibility="collapsed")
        ny_idx=namn_lista.index(valt)
        if ny_idx!=akt:
            lista[akt]=copy.deepcopy(proj)
            st.session_state.projekt_lista=lista
            st.session_state.aktivt_idx=ny_idx
            st.session_state.projekt=copy.deepcopy(lista[ny_idx])
            st.rerun()

        c1,c2=st.columns(2)
        if c1.button("➕ Nytt",use_container_width=True):
            lista[akt]=copy.deepcopy(proj)
            ny=empty_projekt()
            lista.append(ny)
            st.session_state.projekt_lista=lista
            st.session_state.aktivt_idx=len(lista)-1
            st.session_state.projekt=ny
            st.rerun()
        if c2.button("🗑 Ta bort",use_container_width=True):
            if len(lista)>1:
                lista.pop(akt)
                ny_akt=min(akt,len(lista)-1)
                st.session_state.projekt_lista=lista
                st.session_state.aktivt_idx=ny_akt
                st.session_state.projekt=copy.deepcopy(lista[ny_akt])
                st.rerun()
            else:
                st.session_state.projekt=empty_projekt()
                lista[0]=st.session_state.projekt
                st.rerun()

        # ── Fil-operationer ───────────────────────────────────
        up=st.file_uploader("📂 Öppna (.json)", type=["json"],
                             label_visibility="collapsed")
        if up:
            try:
                imp=json.loads(up.read().decode())
                lista[akt]=copy.deepcopy(proj)
                lista.append(imp)
                st.session_state.projekt_lista=lista
                st.session_state.aktivt_idx=len(lista)-1
                st.session_state.projekt=imp
                st.rerun()
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
        st.caption(f"{proj.get('status','')}  ·  {len(lista)} projekt totalt")
        col1,col2=st.columns(2)
        col1.metric("Rader", len(proj.get("rader",[])))
        col2.metric("Marginal", pct(s["mg"]))
        st.metric("Försäljning", kr(s["fp"]))
        st.metric("TB", kr(s["tb"]))
        st.divider()
        st.markdown("""
<a href="javascript:window.print()" style="
  display:block;text-align:center;background:#1a3a5c;color:white;
  padding:8px 0;border-radius:6px;font-weight:600;font-size:.9rem;
  text-decoration:none;margin-top:4px">
  🖨 Skriv ut / Spara PDF
</a>""", unsafe_allow_html=True)

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
                st.caption("💡 Priser från **Prisbank** (BK 2025 + egna). Mat-pris = komplett á-pris inkl arbete. Välj Typ=UE för underentreprenörsarbeten.")
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
                "Á-pris","Kostnad","Påslag %","Försäljning"]],
            column_config={
                "Radtyp":     st.column_config.SelectboxColumn("Typ",    options=RADTYPER,width="small"),
                "Benämning":  st.column_config.TextColumn("Benämning",   width="medium"),
                "Byggdel":    st.column_config.SelectboxColumn("Byggdel",options=["–"]+bdlar,width="small"),
                "Mängd":      st.column_config.NumberColumn("Mängd",     format="%.2f",width="small"),
                "Enhet":      st.column_config.SelectboxColumn("Enhet",  options=ENHETER,width="small"),
                "Timmar":     st.column_config.NumberColumn("Tim",       format="%.1f",width="small"),
                "Á-pris":     st.column_config.NumberColumn("Á-pris",    format="%.0f",width="small"),
                "Kostnad":    st.column_config.NumberColumn("Kostnad",   format="%.0f",width="small",disabled=True),
                "Påslag %":   st.column_config.NumberColumn("Pål%",      format="%.1f",width="small"),
                "Försäljning":st.column_config.NumberColumn("Försälj.",  format="%.0f",width="small",disabled=True),
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
            if st.button("🔄 Återställ BK 2025 standardpriser", type="primary"):
                st.session_state.prisbank=list(DEFAULT_PRISBANK); st.rerun()
        else:
            fc1,fc2=st.columns([2,1])
            sok=fc1.text_input("🔍 Sök",placeholder="Namn eller kod...",label_visibility="collapsed")
            kat=fc2.selectbox("Kategori",["Alla"]+KATEGORIER,label_visibility="collapsed")
            träffar=[p for p in pb if
                (not sok or sok.lower() in p.get("benamning","").lower() or sok.lower() in p.get("kod","").lower())
                and (kat=="Alla" or p.get("kategori","")==kat)]

            st.caption(f"📋 {len(träffar)} av {len(pb)} artiklar  |  Källa: BK 2025 (Byggmästarnas Kostnadskalkylator)")

            # Ensure kategori field exists
            for p in pb:
                if "kategori" not in p: p["kategori"]="Övrigt"

            df=pd.DataFrame(träffar if träffar else [{"kod":"","benamning":"","enhet":"st","matpris":0,"arbpris":0,"leverantor":"BK 2025","kategori":"Övrigt"}])
            cols_show=["kategori","kod","benamning","enhet","matpris","arbpris","leverantor"]
            for c in cols_show:
                if c not in df.columns: df[c]=""
            edited=st.data_editor(
                df[cols_show],
                column_config={
                    "kategori":   st.column_config.SelectboxColumn("Kategori",  options=KATEGORIER,width="small"),
                    "kod":        st.column_config.TextColumn("Kod",            width="small"),
                    "benamning":  st.column_config.TextColumn("Benämning",      width="medium"),
                    "enhet":      st.column_config.SelectboxColumn("Enhet",     options=ENHETER,width="small"),
                    "matpris":    st.column_config.NumberColumn("Mat-pris",     format="%.0f",width="small",
                                     help="Komplett á-pris enl BK 2025 (material+arbete). Används som UE- eller materialpris."),
                    "arbpris":    st.column_config.NumberColumn("Arb-pris",     format="%.0f",width="small",
                                     help="Uppskattad arbetskostnad kr/enhet (tim × 495 kr)"),
                    "leverantor": st.column_config.TextColumn("Källa",          width="small"),
                },
                use_container_width=True, hide_index=True,
                num_rows="dynamic", height=400, key="pb_ed"
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
        st.markdown("**Lägg till egen artikel:**")
        st.caption("Mat-pris = komplett á-pris (material+arbete) för UE/material. Arb-pris = om du vill särskilja enbart arbetskostnaden.")
        with st.form("ny_artikel"):
            c1,c2,c3=st.columns(3)
            kat =c1.selectbox("Kategori",KATEGORIER)
            kod =c1.text_input("Kod (valfri)")
            ben =c1.text_input("Benämning *")
            enh =c1.selectbox("Enhet",ENHETER)
            mat =c2.number_input("Mat-pris (kr/enhet)",value=0.0,
                                  help="Komplett á-pris inkl material och arbete")
            arb =c2.number_input("Arb-pris (kr/enhet)",value=0.0,
                                  help="Enbart arbetskostnad per enhet")
            lev =c3.text_input("Källa/leverantör")
            komm=c3.text_area("Notering",height=80)
            if st.form_submit_button("➕ Lägg till i prisbank", type="primary"):
                if not ben: st.warning("Ange benämning.")
                else:
                    st.session_state.prisbank.append(
                        {"kod":kod,"benamning":ben,"enhet":enh,
                         "matpris":mat,"arbpris":arb,
                         "leverantor":lev,"kategori":kat,"notering":komm})
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
