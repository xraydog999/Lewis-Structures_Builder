import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="Molecule Builder", layout="wide")

st.title("🧪 Molecule Builder (Organic & Inorganic)")
st.write("Use the tabs to switch between Organic and Inorganic builders.")

# -----------------------------
#  PALETTES
# -----------------------------

ORGANIC_ATOMS = ["H", "C", "N", "O", "F", "Cl"]
INORGANIC_ATOMS = ["H", "C", "N", "O", "F", "Cl", "S", "P"]

BONDS = ["-", "=", "≡"]

ELECTRON_PAIRS = [
    {"label": "|", "desc": "Vertical dash"},
    {"label": "••", "desc": "Horizontal electron pair"},
    {"label": ":", "desc": "Vertical electron pair"},
]

# -----------------------------
#  SESSION STATE
# -----------------------------
if "pieces" not in st.session_state:
    st.session_state.pieces = {}

# -----------------------------
#  TABS
# -----------------------------
tab1, tab2 = st.tabs(["Organic Builder", "Inorganic Builder"])

def render_builder(atom_list):
    """Renders the full HTML/JS builder with the given atom palette."""

    atom_palette_html = "".join(
        f'<div class="palette-item" data-label="{a}" data-type="atom">{a}</div>'
        for a in atom_list
    )

    bond_palette_html = "".join(
        f'<div class="palette-item" data-label="{b}" data-type="bond">{b}</div>'
        for b in BONDS
    )

    electron_palette_html = "".join(
        f'<div class="palette-item electron-item" data-label="{e["label"]}" data-type="electron">{e["label"]}</div>'
        for e in ELECTRON_PAIRS
    )

    components.html(
        f"""
        <style>
            body {{
                user-select: none;
            }}

            #container {{
                display: flex;
                gap: 20px;
            }}

            #left-palette, #right-palette {{
                width: 150px;
                border: 2px solid #ccc;
                padding: 10px;
                background: #fafafa;
            }}

            .palette-item {{
                font-size: 32px;
                padding: 8px;
                margin: 6px 0;
                border: 1px solid #aaa;
                background: white;
                text-align: center;
                cursor: grab;
            }}

            /* Make vertical dash shorter in the palette */
            .electron-item[data-label="|"] {{
                font-size: 24px !important;
            }}

            #canvas {{
                width: 900px;
                height: 600px;
                border: 2px solid #ccc;
                position: relative;
                background: white;
                overflow: hidden;
            }}

            .piece {{
                position: absolute;
                font-size: 48px;
                cursor: grab;
            }}

            /* Make vertical dash shorter on the canvas */
            .piece.vertical-dash {{
                font-size: 24px !important;
            }}

            .piece:active {{
                cursor: grabbing;
            }}
        </style>

        <div id="container">

            <!-- Left Palette -->
            <div id="left-palette">
                <h4>Atoms</h4>
                {atom_palette_html}

                <h4>Bonds</h4>
                {bond_palette_html}
            </div>

            <!-- Canvas -->
            <div id="canvas"></div>

            <!-- Right Palette -->
            <div id="right-palette">
                <h4>Electron Pairs</h4>
                {electron_palette_html}
            </div>

