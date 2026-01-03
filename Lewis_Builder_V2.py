import streamlit as st
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="NH₃ Builder", layout="wide")

st.title("🧪 Build Molecules with Bonds & Lone Pairs")
st.write("Drag atoms, bonds, and electron pairs to assemble Lewis structures.")

# Initialize positions
if "pieces" not in st.session_state:
    st.session_state.pieces = {
        "N": {"x": 350, "y": 150},
        "H1": {"x": 100, "y": 50},
        "H2": {"x": 600, "y": 50},
        "H3": {"x": 350, "y": 300},

        # Original bonds
        "bond1": {"x": 250, "y": 150},
        "bond2": {"x": 450, "y": 150},
        "bond3": {"x": 350, "y": 225},
        "lone": {"x": 350, "y": 75},

        # New palette items
        "vdash": {"x": 700, "y": 50},
        "dots_h": {"x": 700, "y": 150},
        "dots_v": {"x": 700, "y": 250},

        "dbl_h": {"x": 700, "y": 350},
        "dbl_v": {"x": 750, "y": 350},

        "tpl_h": {"x": 700, "y": 420},
        "tpl_v": {"x": 750, "y": 420},
    }

components.html(
    """
    <style>
        #drag-area {
            width: 900px;
            height: 550px;
            border: 2px solid #ccc;
            position: relative;
            background: white;
            user-select: none;
            overflow: hidden;
        }

        .piece {
            position: absolute;
            font-size: 70px;
            cursor: grab;
            transition: box-shadow 0.15s ease, transform 0.15s ease;
        }

        .piece:active {
            cursor: grabbing;
        }

        .glow {
            box-shadow: 0 0 18px 4px rgba(0, 150, 255, 0.7);
            transform: scale(1.05);
        }

        .lonepair {
            font-size: 40px;
        }

        .bondv {
            font-size: 70px;
            line-height: 50px;
        }

        .double_v {
            font-size: 70px;
            line-height: 40px;
        }

        .triple_v {
            font-size: 70px;
            line-height: 30px;
        }
    </style>

    <div id="drag-area">

        <!-- Atoms -->
        <div id="N" class="piece" style="left:350px; top:150px;">N</div>
        <div id="H1" class="piece" style="left:100px; top:50px;">H</div>
        <div id="H2" class="piece" style="left:600px; top:50px;">H</div>
        <div id="H3" class="piece" style="left:350px; top:300px;">H</div>

        <!-- Original bonds -->
        <div id="bond1" class="piece" style="left:250px; top:150px;">-</div>
        <div id="bond2" class="piece" style="left:450px; top:150px;">-</div>
        <div id="bond3" class="piece bondv" style="left:350px; top:225px;">|</div>

        <!-- Lone pair -->
        <div id="lone" class="piece lonepair" style="left:350px; top:75px;">••</div>

        <!-- New palette items -->
        <div id="vdash" class="piece bondv" style="left:700px; top:50px;">|</div>

        <div id="dots_h" class="piece lonepair" style="left:700px; top:150px;">••</div>
        <div id="dots_v" class="piece lonepair" style="left:700px; top:250px;">•<br>•</div>

        <!-- Double bonds -->
        <div id="dbl_h" class="piece" style="left:700px; top:350px;">=</div>
        <div id="dbl_v" class="piece double_v" style="left:750px; top:350px;">|<br>|</div>

        <!-- Triple bonds -->
        <div id="tpl_h" class="piece" style="left:700px; top:420px;">≡</div>
        <div id="tpl_v" class="piece triple_v" style="left:750px; top:420px;">|<br>|<br>|</div>

    </div>

    <script>
        const pieces = [
            "N","H1","H2","H3",
            "bond1","bond2","bond3","lone",
            "vdash","dots_h","dots_v",
            "dbl_h","dbl_v",
            "tpl_h","tpl_v"
        ];

        let active = null;
        let offsetX = 0;
        let offsetY = 0;

        const targets = {
            "N": {x:350, y:150},
            "H1": {x:250, y:150},
            "H2": {x:450, y:150},
            "H3": {x:350, y:260},
            "bond1": {x:300, y:150},
            "bond2": {x:400, y:150},
            "bond3": {x:350, y:200},
            "lone": {x:350, y:80},

            "vdash": {x:700, y:50},
            "dots_h": {x:700, y:150},
            "dots_v": {x:700, y:250},

            "dbl_h": {x:700, y:350},
            "dbl_v": {x:750, y:350},

            "tpl_h": {x:700, y:420},
            "tpl_v": {x:750, y:420}
        };

        const snapDistance = 40;

        pieces.forEach(id => {
            const el = document.getElementById(id);

            el.addEventListener("mousedown", startDrag);
            el.addEventListener("touchstart", startDrag);

            function startDrag(e) {
                active = el;
                const rect = el.getBoundingClientRect();
                const clientX = e.touches ? e.touches[0].clientX : e.clientX;
                const clientY = e.touches ? e.touches[0].clientY : e.clientY;
                offsetX = clientX - rect.left;
                offsetY = clientY - rect.top;

                document.addEventListener("mousemove", drag);
                document.addEventListener("mouseup", endDrag);
                document.addEventListener("touchmove", drag);
                document.addEventListener("touchend", endDrag);
            }

            function drag(e) {
                if (!active) return;

                const clientX = e.touches ? e.touches[0].clientX : e.clientX;
                const clientY = e.touches ? e.touches[0].clientY : e.clientY;

                const x = clientX - offsetX;
                const y = clientY - offsetY;

                active.style.left = x + "px";
                active.style.top = y + "px";

                const t = targets[active.id];
                const dx = t.x - x;
                const dy = t.y - y;
                const dist = Math.sqrt(dx*dx + dy*dy);

                if (dist < snapDistance * 1.5) {
                    active.classList.add("glow");
                } else {
                    active.classList.remove("glow");
                }
            }

            function endDrag() {
                if (!active) return;

                const rect = active.getBoundingClientRect();
                const parent = document.getElementById("drag-area").getBoundingClientRect();

                let x = rect.left - parent.left;
                let y = rect.top - parent.top;

                const t = targets[active.id];
                const dx = t.x - x;
                const dy = t.y - y;
                const dist = Math.sqrt(dx*dx + dy*dy);

                if (dist < snapDistance) {
                    x = t.x;
                    y = t.y;
                    active.style.left = x + "px";
                    active.style.top = y + "px";
                }

                active.classList.remove("glow");

                const payload = { id: active.id, x: x, y: y };

                window.parent.postMessage(
                    { "type": "streamlit:setComponentValue", "value": payload },
                    "*"
                );

                active = null;

                document.removeEventListener("mousemove", drag);
                document.removeEventListener("mouseup", endDrag);
                document.removeEventListener("touchmove", drag);
                document.removeEventListener("touchend", endDrag);
            }
        });
    </script>
    """,
    height=600,
)

# Receive JS → Python updates
event = st.experimental_get_query_params().get("streamlit_component_value")

if event:
    try:
        data = json.loads(event[0])
        if data["id"] in st.session_state.pieces:
            st.session_state.pieces[data["id"]]["x"] = data["x"]
            st.session_state.pieces[data["id"]]["y"] = data["y"]
    except Exception:
        pass
