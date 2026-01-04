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
        """
        <style>
            body {
                user-select: none;
            }

            #container {
                display: flex;
                gap: 20px;
            }

            #left-palette, #right-palette {
                width: 150px;
                border: 2px solid #ccc;
                padding: 10px;
                background: #fafafa;
            }

            .palette-item {
                font-size: 32px;
                padding: 8px;
                margin: 6px 0;
                border: 1px solid #aaa;
                background: white;
                text-align: center;
                cursor: grab;
            }

            /* Make vertical dash shorter in the palette */
            .electron-item[data-label="|"] {
                font-size: 24px !important;
            }

            #canvas {
                width: 900px;
                height: 600px;
                border: 2px solid #ccc;
                position: relative;
                background: white;
                overflow: hidden;
            }

            .piece {
                position: absolute;
                font-size: 48px;
                cursor: grab;
            }

            /* Make vertical dash shorter on the canvas */
            .piece.vertical-dash {
                font-size: 24px !important;
            }

            .piece:active {
                cursor: grabbing;
            }
        </style>

        <div id="container">

            <!-- Left Palette -->
            <div id="left-palette">
                <h4>Atoms</h4>
                """ + atom_palette_html + """
                <h4>Bonds</h4>
                """ + bond_palette_html + """
            </div>

            <!-- Canvas -->
            <div id="canvas"></div>

            <!-- Right Palette -->
            <div id="right-palette">
                <h4>Electron Pairs</h4>
                """ + electron_palette_html + """
            </div>

        </div>

        <script>
            const canvas = document.getElementById("canvas");

            // Create a new piece on the canvas
            function createPiece(label, type, x, y) {
                const id = "piece-" + Math.random().toString(36).substr(2, 9);

                const el = document.createElement("div");
                el.className = "piece";
                el.id = id;
                el.style.left = x + "px";
                el.style.top = y + "px";
                el.textContent = label;

                // Tag vertical dash for smaller size
                if (label === "|") {
                    el.classList.add("vertical-dash");
                }

                canvas.appendChild(el);
                makeDraggable(el);

                sendUpdate(id, x, y, false, label, type);
            }

            // Drag from palette → create new piece
            document.querySelectorAll(".palette-item").forEach(item => {
                item.addEventListener("mousedown", e => {
                    createPiece(
                        item.dataset.label,
                        item.dataset.type,
                        50,
                        50
                    );
                });
            });

            // Make a piece draggable
            function makeDraggable(el) {
                let active = false;
                let offsetX = 0;
                let offsetY = 0;

                el.addEventListener("mousedown", startDrag);

                function startDrag(e) {
                    active = true;
                    const rect = el.getBoundingClientRect();
                    offsetX = e.clientX - rect.left;
                    offsetY = e.clientY - rect.top;

                    document.addEventListener("mousemove", drag);
                    document.addEventListener("mouseup", endDrag);
                }

                function drag(e) {
                    if (!active) return;

                    const parent = canvas.getBoundingClientRect();
                    const x = e.clientX - parent.left - offsetX;
                    const y = e.clientY - parent.top - offsetY;

                    el.style.left = x + "px";
                    el.style.top = y + "px";
                }

                function endDrag(e) {
                    if (!active) return;
                    active = false;

                    const parent = canvas.getBoundingClientRect();
                    const x = e.clientX - parent.left - offsetX;
                    const y = e.clientY - parent.top - offsetY;

                    sendUpdate(el.id, x, y, false);

                    document.removeEventListener("mousemove", drag);
                    document.removeEventListener("mouseup", endDrag);
                }
            }

            // Send updates to Streamlit
            function sendUpdate(id, x, y, deleted, label=null, type=null) {
                window.parent.postMessage(
                    {
                        "type": "streamlit:setComponentValue",
                        "value": {
                            id, x, y, deleted, label, type
                        }
                    },
                    "*"
                );
            }
        </script>
        """,
        height=750,
    )


# -----------------------------
#  RENDER TABS
# -----------------------------
with tab1:
    st.subheader("Organic Molecule Builder")
    render_builder(ORGANIC_ATOMS)

with tab2:
    st.subheader("Inorganic Molecule Builder")
    render_builder(INORGANIC_ATOMS)

# -----------------------------
#  RECEIVE JS UPDATES
# -----------------------------
event = st.experimental_get_query_params().get("streamlit_component_value")

if event:
    try:
        data = json.loads(event[0])
        pid = data["id"]

        if data.get("deleted"):
            if pid in st.session_state.pieces:
                del st.session_state.pieces[pid]
        else:
            st.session_state.pieces[pid] = {
                "x": data["x"],
                "y": data["y"],
                "label": data.get("label", st.session_state.pieces.get(pid, {}).get("label")),
                "type": data.get("type", st.session_state.pieces.get(pid, {}).get("type")),
            }
    except Exception:
        pass

st.write("### Current pieces on canvas:")
st.json(st.session_state.pieces)
