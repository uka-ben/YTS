import streamlit as st
import random

st.set_page_config(page_title="YouTube Grid - Random Features", layout="wide")

# Video list
video_id = "JZYnS6ypa2g"
video_ids = [video_id]*20  # repeat 20 times; can increase

# Generate HTML blocks for grid
blocks = []
for idx, vid in enumerate(video_ids):
    blocks.append(f"""
    <div class="video-box" id="player{idx}" data-video="{vid}" data-index="{idx}">
        <img src="https://i.ytimg.com/vi_webp/{vid}/mqdefault.webp" loading="lazy">
    </div>
    """)

html = f"""
<div style="margin-bottom:6px;">
<button id="load-all">Load All Sequentially</button>
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
  position:relative;
}}

.video-box img {{
  width:100%;
  height:100%;
  object-fit:cover;
  border-radius:2px;
}}

.loaded {{
  opacity:0.6;  /* visual indicator when loaded */
  transition: opacity 0.3s;
}}

.fade-out {{
  opacity:0;
  transition: opacity 0.5s;
}}
</style>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
let players = {{}};
let timers = {{}};

function randomStopTime(){{
    return Math.floor(Math.random()*(45-35+1))+35; // 35–45 seconds
}}

// Add click to manually play video
function onYouTubeIframeAPIReady(){{
    document.querySelectorAll(".video-box").forEach(box => {{
        let vid = box.dataset.video;
        let idx = box.dataset.index;
        box.addEventListener("click", () => {{
            if(players[idx]) return;

            players[idx] = new YT.Player("player"+idx, {{
                width:"100%",
                height:"100%",
                videoId:vid,
                playerVars:{{
                    autoplay:0,  // NO autoplay
                    playsinline:1,
                    rel:0,
                    vq:"tiny",
                    controls:1
                }},
                events:{{
                    'onStateChange': function(e){{
                        if(e.data === YT.PlayerState.PLAYING){{
                            clearTimeout(timers[idx]);
                            let stop = randomStopTime();
                            timers[idx] = setTimeout(()=>{{
                                players[idx].stopVideo();
                                players[idx].destroy();
                                delete players[idx];
                                let boxEl = document.getElementById("player"+idx);
                                boxEl.classList.add("fade-out");
                                setTimeout(()=>{{ boxEl.remove() }},500);
                            }}, stop*1000);
                        }}
                    }}
                }}
            }});
        }});
    }});
}}

// "Load All" button: random order + random delay
document.getElementById("load-all").addEventListener("click", async () => {{
    let boxes = Array.from(document.querySelectorAll(".video-box"));
    while(boxes.length > 0){{
        let idx = Math.floor(Math.random()*boxes.length); // pick random box
        boxes[idx].classList.add("loaded");  // mark loaded
        boxes.splice(idx,1);
        await new Promise(r => setTimeout(r, Math.floor(Math.random()*(500-200+1))+200)); // random delay 200–500ms
    }}
}});
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)