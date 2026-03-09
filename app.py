import streamlit as st

st.set_page_config(page_title="Compact YouTube Grid", layout="wide")

# --- Video IDs ---
video_id = "JZYnS6ypa2g"
video_ids = [video_id]*100  # 100 videos

# --- Generate video blocks ---
blocks = []
for i, vid in enumerate(video_ids):
    blocks.append(f"""
    <div class="video-box" id="player{i}" data-video="{vid}" data-index="{i}" 
         style="cursor:pointer;">
        <img src="https://i.ytimg.com/vi_webp/{vid}/mqdefault.webp" 
             loading="lazy"
             style="width:100%;aspect-ratio:16/9;border-radius:2px;">
    </div>
    """)

# --- HTML + JS ---
html = f"""
<div style="margin-bottom:8px;">
<button id="play-all" style="padding:6px 12px;font-size:12px;cursor:pointer;">
Play All Sequentially
</button>
</div>

<div id="video-grid" style="
background:#000;
padding:6px;
display:grid;
grid-template-columns:repeat(auto-fit,minmax(60px,1fr));
gap:4px;
max-height:90vh;
overflow-y:auto;">
{''.join(blocks)}
</div>

<style>
.video-box:hover {{
    transform: scale(1.1);
    transition: transform 0.2s;
}}
.fade-out {{
    opacity: 0;
    transition: opacity 0.5s ease;
}}
</style>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
let players = {{}};
let timers = {{}};

function randomStopTime() {{
    return Math.floor(Math.random()*(45-35+1))+35;
}}

function onYouTubeIframeAPIReady() {{
    document.querySelectorAll(".video-box").forEach(box=>{{
        let vid = box.dataset.video;
        let idx = box.dataset.index;
        box.addEventListener("click",()=>loadVideo(idx,vid));
    }});
}}

function loadVideo(index, video) {{
    if(players[index]) {{
        players[index].playVideo();
        return;
    }}
    players[index] = new YT.Player("player"+index,{{
        videoId: video,
        playerVars: {{
            autoplay:0,
            playsinline:1,
            rel:0,
            modestbranding:1,
            vq:"tiny",
            controls:1
        }},
        events: {{
            'onStateChange': function(e){{
                if(e.data === YT.PlayerState.PLAYING){{
                    clearTimeout(timers[index]);
                    let stopTime = randomStopTime();
                    timers[index] = setTimeout(()=>{{
                        players[index].stopVideo();
                        players[index].destroy();
                        delete players[index];
                        let box = document.getElementById("player"+index);
                        box.classList.add("fade-out");
                        setTimeout(()=>{{ box.remove() }}, 500);
                    }}, stopTime*1000);
                }}
            }}
        }}
    }});
}}

document.getElementById("play-all").addEventListener("click", async ()=>{{
    const boxes = document.querySelectorAll(".video-box");
    for(let i=0;i<boxes.length;i++){{ 
        let vid = boxes[i].dataset.video;
        loadVideo(i, vid);
        let delay = Math.floor(Math.random()*(5000-2000+1))+2000;
        await new Promise(r=>setTimeout(r, delay));
    }}
}});
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)