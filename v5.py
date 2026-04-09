import streamlit as st

st.set_page_config(layout="wide")

video_id = "dIbenqerI3g"
video_ids = [video_id] * 20

html_blocks = []

for vid in video_ids:
    html_blocks.append(f"""
<div class="video-box" data-video="{vid}">
    <img src="https://i.ytimg.com/vi_webp/{vid}/mqdefault.webp"
         loading="lazy"
         class="thumb">
</div>
""")

html = f"""
<style>
#video-grid {{
background:#000;
padding:20px;
display:grid;
grid-template-columns:repeat(auto-fill,minmax(160px,1fr));
gap:8px;
}}
.video-box {{
cursor:pointer;
aspect-ratio:16/9;
position:relative;
transition:opacity 1s;
}}
.thumb {{
width:100%;
height:100%;
object-fit:cover;
border-radius:6px;
}}
iframe {{
width:100%;
height:100%;
border:none;
border-radius:6px;
}}
button {{
padding:10px 20px;
font-size:16px;
cursor:pointer;
margin-bottom:10px;
}}
</style>

<button id="shuffle-load">Shuffle + Load Players</button>

<div id="video-grid">
{''.join(html_blocks)}
</div>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
let YT_API_ready = false;
let qualityIntervals = new Map();
let activePlayers = new Map();

function onYouTubeIframeAPIReady() {{
    YT_API_ready = true;
}}

function loadPlayer(box) {{
    if(box.classList.contains("loaded") || !YT_API_ready) return;

    const vid = box.dataset.video;
    const duration = Math.floor(Math.random()*(46-35+1))+35;

    box.innerHTML = '';
    box.classList.add("loaded");

    const playerDiv = document.createElement("div");
    box.appendChild(playerDiv);

    const player = new YT.Player(playerDiv, {{
        height: '100%',
        width: '100%',
        videoId: vid,
        playerVars: {{
            autoplay: 0,
            controls: 1,
            rel: 0,
            modestbranding: 1,
            playsinline: 1,
            vq: 'tiny'
        }},
        events: {{
            onReady: (event) => {{
                activePlayers.set(box, event.target);
                
                /* Force 144p every second */
                const qualityInterval = setInterval(() => {{
                    try {{
                        event.target.setPlaybackQuality('tiny');
                    }} catch(e){{}}
                }}, 1000);
                
                qualityIntervals.set(box, qualityInterval);
                
                /* Click to play */
                box.addEventListener("click", () => {{
                    event.target.playVideo();
                    
                    /* Pause and reset after duration - preserves buffer */
                    setTimeout(() => {{
                        event.target.pauseVideo();
                        event.target.seekTo(0);
                    }}, duration * 1000);
                }});
            }}
        }}
    }});
}}

document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", () => loadPlayer(box));
}});

document.getElementById("shuffle-load").onclick = () => {{
    /* Clean up intervals and players */
    for (let [box, interval] of qualityIntervals) {{
        clearInterval(interval);
    }}
    qualityIntervals.clear();
    
    for (let [box, player] of activePlayers) {{
        try {{
            player.destroy();
        }} catch(e) {{}}
    }}
    activePlayers.clear();
    
    let grid = document.getElementById("video-grid");
    let boxes = [...grid.children];

    /* shuffle grid */
    for(let i = boxes.length - 1; i > 0; i--) {{
        let j = Math.floor(Math.random() * (i + 1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }}
    boxes.forEach(b => grid.appendChild(b));

    /* Reset boxes */
    boxes.forEach(b => {{
        b.innerHTML = `<img src="https://i.ytimg.com/vi_webp/${{b.dataset.video}}/mqdefault.webp" loading="lazy" class="thumb">`;
        b.classList.remove('loaded');
        b.style.opacity = '1';
    }});

    /* sequential loading with 1–5s random delay */
    let delay = 0;
    boxes.forEach(box => {{
        let randomDelay = 1000 + Math.random() * 4000;
        setTimeout(() => {{
            loadPlayer(box);
        }}, delay);
        delay += randomDelay;
    }});
}};
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)