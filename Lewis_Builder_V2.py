import streamlit as st
import streamlit.components.v1 as components
import uuid
import json

st.set_page_config(page_title="Molecule Builder", layout="wide")

st.title("🧪 Free‑Form Molecule Builder")
st.write("Drag atoms and bonds from the palette onto the canvas to build any molecule you like.")

# Session state for pieces on the canvas
if "pieces" not in st.session_state:
    st.session_state.pieces = {}

# Palette items
PALETTE = [
    {"label": "H", "type": "atom"},
    {"label": "C", "type": "atom"},
    {"label": "N", "type": "atom"},
    {"label": "O", "type": "atom"},
    {"label": "F", "type": "atom"},
    {"label": "Cl", "type": "atom"},
    {"label": "S", "type": "atom"},
    {"label": "P", "type": "atom"},
    {"label": "-", "type": "bond"},
    {"label": "=", "type": "bond"},
    {"label": "≡", "type": "bond"},
    {"label": "••", "type": "lone"},
]

# HTML + JS component
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

        #palette {{
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

        .piece:active {{
            cursor: grabbing;
        }}

        .delete-btn {{
            position: absolute;
            top: -10px;
            right: -10px;
            background: red;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 14px;
            text-align: center;
            line-height: 20px;
            cursor: pointer;
        }}
    </style>

    <div id="container">

        <!-- Palette -->
        <div id="palette">
            <h4>Palette</h4>
            {"".join(
                f'<div class="palette-item" data-label="{item["label"]}" data-type="{item["type"]}">{item["label"]}</div>'
                for item in PALETTE
            )}
        </div>

        <!-- Canvas -->
        <div id="canvas"></div>

    </div>

    <script>
        const canvas = document.getElementById("canvas");

        // Create a new piece on the canvas
        function createPiece(label, type, x, y) {{
            const id = "piece-" + Math.random().toString(36).substr(2, 9);

            const el = document.createElement("div");
            el.className = "piece";
            el.id = id;
            el.style.left = x + "px";
            el.style.top = y + "px";
            el.textContent = label;

            // Delete button
            const del = document.createElement("div");
            del.className = "delete-btn";
            del.textContent = "×";
            del.onclick = () => {{
                el.remove();
                sendUpdate(id, null, null, true);
            }};
            el.appendChild(del);

            canvas.appendChild(el);

            makeDraggable(el);

            sendUpdate(id, x, y, false, label, type);
        }}

        // Drag from palette → create new piece
        document.querySelectorAll(".palette-item").forEach(item => {{
            item.addEventListener("mousedown", e => {{
                const rect = canvas.getBoundingClientRect();
                createPiece(
                    item.dataset.label,
                    item.dataset.type,
                    50,
                    50
                );
            }});
        }});

        // Make a piece draggable
        function makeDraggable(el) {{
            let active = false;
            let offsetX = 0;
            let offsetY = 0;

            el.addEventListener("mousedown", startDrag);

            function startDrag(e) {{
                if (e.target.classList.contains("delete-btn")) return;

                active = true;
                const rect = el.getBoundingClientRect();
                offsetX = e.clientX - rect.left;
                offsetY = e.clientY - rect.top;

                document.addEventListener("mousemove", drag);
                document.addEventListener("mouseup", endDrag);
            }}

            function drag(e) {{
                if (!active) return;

                const parent = canvas.getBoundingClientRect();
                const x = e.clientX - parent.left - offsetX;
                const y = e.clientY - parent.top - offsetY;

                el.style.left = x + "px";
                el.style.top = y + "px";
            }}

            function endDrag(e) {{
                if (!active) return;
                active = false;

                const parent = canvas.getBoundingClientRect();
                const x = e.clientX - parent.left - offsetX;
                const y = e.clientY - parent.top - offsetY;

                sendUpdate(el.id, x, y, false);

                document.removeEventListener("mousemove", drag);
                document.removeEventListener("mouseup", endDrag);
            }}
        }}

        // Send updates to Streamlit
        function sendUpdate(id, x, y, deleted, label=null, type=null) {{
            window.parent.postMessage(
                {{
                    "type": "streamlit:setComponentValue",
                    "value": {{
                        id, x, y, deleted, label, type
                    }}
                }},
                "*"
            );
        }}
    </script>
    """,
    height=700,
)

# Receive updates from JS
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
