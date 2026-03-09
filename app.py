import streamlit as st

st.set_page_config(page_title="Compact YouTube Grid", layout="wide")

video_id = "JZYnS6ypa2g"
video_ids = [video_id]*100

blocks = []

for i, vid in enumerate(video_ids):
    blocks.append("""
    <div class="video-box" id="player{0}" data-video="{1}" data-index="{0}">
        <img src="https://i.ytimg.com/vi_webp/{1}/mqdefault.webp" loading="lazy">
    </div>
    """.format(i, vid))

html = """
<div style="margin-bottom:6px;">
<button id="load-all">Load All Sequentially</button>
</div>

<div id="video-grid">
{blocks}
</div>

<style>

#video-grid {{
background:#000;
padding:6px;
display:grid;
grid-template-columns:repeat(auto-fit,minmax(60px,1fr));
gap:4px;
max-height:90vh;
overflow-y:auto;
}}

.video-box {{
width:100%;
aspect-ratio:16/9;
cursor:pointer;
}}

.video-box img {{
width:100%;
height:100%;
object-fit:cover;
border-radius:2px;
}}

.video-box iframe {{
width:100% !important;
height:100% !important;
border:0;
}}

.video-box.loaded {{
outline: 2px solid #0f0; /* optional visual to show loaded */
}}

.fade-out {{
opacity:0;
transition:opacity 0.5s;
}}

</style>

<script src="https://www.youtube.com/iframe_api"></script>

<script>

let players = {{}};
let timers = {{}};

function randomStopTime(){{
    return Math.floor(Math.random()*(45-35+1))+35;
}}

// Add click handlers to each box (user-initiated play)
function onYouTubeIframeAPIReady(){{
    document.querySelectorAll(".video-box").forEach(box => {{
        let vid = box.dataset.video;
        let idx = box.dataset.index;
        box.addEventListener("click", () => loadVideo(idx, vid));
    }});
}}

// Load video on user click, stop after random seconds
function loadVideo(index, video){{
    if(players[index]) return;

    players[index] = new YT.Player("player"+index, {{
        width:"100%",
        height:"100%",
        videoId:video,
        playerVars:{{
            autoplay:0,  // IMPORTANT: do not autoplay
            playsinline:1,
            rel:0,
            vq:"tiny",
            controls:1
        }},
        events:{{
            'onStateChange': function(e){{
                if(e.data === YT.PlayerState.PLAYING){{
                    clearTimeout(timers[index]);
                    let stop = randomStopTime();
                    timers[index] = setTimeout(()=>{{
                        players[index].stopVideo();
                        players[index].destroy();
                        delete players[index];
                        let box = document.getElementById("player"+index);
                        box.classList.add("fade-out");
                        setTimeout(()=>{{ box.remove() }},500);
                    }}, stop*1000);
                }}
            }}
        }}
    }});
}}

// Sequential "Load All" button: marks each box as loaded, no autoplay
document.getElementById("load-all").addEventListener("click", async ()=>{{
    const boxes = document.querySelectorAll(".video-box");
    for(let i=0;i<boxes.length;i++) {{
        boxes[i].classList.add("loaded");  // optional visual
        // random delay to simulate sequential loading
        await new Promise(r => setTimeout(r, Math.floor(Math.random()*(500-200+1))+200));
    }}
}});

</script>
""".format(blocks="".join(blocks))

st.components.v1.html(html, height=900, scrolling=True)