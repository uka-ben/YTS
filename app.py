import streamlit as st
import random

st.set_page_config(page_title="Random Load YouTube Grid", layout="wide")

# Video list
video_id = "JZYnS6ypa2g"
video_ids = [video_id]*20  # example 20 videos, can increase

# Shuffle order for random loading
shuffled_indices = list(range(len(video_ids)))
random.shuffle(shuffled_indices)

blocks = []

for i in shuffled_indices:
    vid = video_ids[i]
    blocks.append(f"""
    <div class="video-box" id="player{i}" data-video="{vid}" data-index="{i}">
        <img src="https://i.ytimg.com/vi_webp/{vid}/mqdefault.webp" loading="lazy">
    </div>
    """)

html = f"""
<div style="margin-bottom:6px;">
<button id="load-all">Play All Sequentially</button>
</div>

<div id="video-grid">
{''.join(blocks)}
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

.loaded {{
opacity:0.6;
}}

</style>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
let players = {{}};
let timers = {{}};

function randomStopTime(){{
    return Math.floor(Math.random()*(45-35+1))+35;
}}

// Click handler: user must click to play
function onYouTubeIframeAPIReady(){{
    document.querySelectorAll(".video-box").forEach(box => {{
        let vid = box.dataset.video;
        let idx = box.dataset.index;
        box.addEventListener("click", () => loadVideo(idx, vid));
    }});
}}

// Load video but do NOT autoplay
function loadVideo(index, video){{
    if(players[index]) return;

    players[index] = new YT.Player("player"+index, {{
        width:"100%",
        height:"100%",
        videoId:video,
        playerVars:{{
            autoplay:0,
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

// Load All button: mark boxes as "loaded" in random order
document.getElementById("load-all").addEventListener("click", async () => {{
    const boxes = Array.from(document.querySelectorAll(".video-box"));
    while(boxes.length > 0){{
        let idx = Math.floor(Math.random()*boxes.length);
        boxes[idx].classList.add("loaded");  // optional visual
        boxes.splice(idx,1);
        await new Promise(r => setTimeout(r, Math.floor(Math.random()*(500-200+1))+200));
    }}
}});
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)