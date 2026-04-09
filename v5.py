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
.video-box iframe {{
width:100%;
height:100%;
border:none;
border-radius:6px;
position:absolute;
top:0;
left:0;
}}
button {{
padding:10px 20px;
font-size:16px;
cursor:pointer;
margin-bottom:10px;
}}
.replay-indicator {{
position:absolute;
bottom:8px;
right:8px;
background:rgba(0,0,0,0.7);
color:#4CAF50;
padding:4px 8px;
border-radius:4px;
font-size:12px;
z-index:10;
pointer-events:none;
}}
</style>

<button id="shuffle-load">Shuffle + Load Players</button>

<div id="video-grid">
{''.join(html_blocks)}
</div>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
let YT_API_ready = false;
let activePlayers = new Map();
let playerTimeouts = new Map();
let qualityIntervals = new Map();
let hasPlayed = new Map();

function onYouTubeIframeAPIReady() {{
    YT_API_ready = true;
    console.log("API Ready");
}}

function loadPlayer(box) {{
    if(box.classList.contains("loaded") || !YT_API_ready) return;

    const vid = box.dataset.video;
    const duration = Math.floor(Math.random()*(46-35+1))+35;
    
    console.log("Loading " + vid + " with duration " + duration + "s");

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
                hasPlayed.set(box, false);
                console.log("Player ready: " + vid);
            }},
            onStateChange: (event) => {{
                const state = event.data;
                const player = event.target;
                
                if (state === 1) {{ // PLAYING
                    console.log("Playing: " + vid);
                    
                    // Force 144p immediately when playing starts
                    setTimeout(() => {{
                        try {{
                            player.setPlaybackQuality('tiny');
                            console.log("Quality forced to tiny");
                        }} catch(e){{}}
                    }}, 200);
                    
                    // Keep forcing quality every 2 seconds
                    if (qualityIntervals.has(box)) {{
                        clearInterval(qualityIntervals.get(box));
                    }}
                    const interval = setInterval(() => {{
                        try {{
                            player.setPlaybackQuality('tiny');
                        }} catch(e){{}}
                    }}, 2000);
                    qualityIntervals.set(box, interval);
                    
                    // Only set duration timeout on FIRST play
                    if (!hasPlayed.get(box)) {{
                        hasPlayed.set(box, true);
                        
                        // Clear any existing timeout
                        if (playerTimeouts.has(box)) {{
                            clearTimeout(playerTimeouts.get(box));
                        }}
                        
                        // Set timeout to pause and reset after duration
                        const timeout = setTimeout(() => {{
                            console.log("Duration reached: " + duration + "s");
                            const p = activePlayers.get(box);
                            if (p) {{
                                p.pauseVideo();
                                p.seekTo(0);
                                clearInterval(qualityIntervals.get(box));
                                qualityIntervals.delete(box);
                                
                                const indicator = document.createElement('div');
                                indicator.className = 'replay-indicator';
                                indicator.textContent = '↻ Ready to replay (no data)';
                                box.appendChild(indicator);
                                setTimeout(() => indicator.remove(), 3000);
                            }}
                        }}, duration * 1000);
                        
                        playerTimeouts.set(box, timeout);
                    }}
                }}
                
                if (state === 2) {{ // PAUSED
                    clearInterval(qualityIntervals.get(box));
                    qualityIntervals.delete(box);
                }}
                
                if (state === 0) {{ // ENDED
                    clearInterval(qualityIntervals.get(box));
                    qualityIntervals.delete(box);
                }}
            }}
        }}
    }});
    
    // Click handler
    box.addEventListener("click", () => {{
        const player = activePlayers.get(box);
        if (player) {{
            console.log("Click - playing video");
            player.playVideo();
        }}
    }});
}}

document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", () => loadPlayer(box));
}});

document.getElementById("shuffle-load").onclick = () => {{
    // Clean up everything
    for (let [box, interval] of qualityIntervals) {{
        clearInterval(interval);
    }}
    qualityIntervals.clear();
    
    for (let [box, timeout] of playerTimeouts) {{
        clearTimeout(timeout);
    }}
    playerTimeouts.clear();
    
    for (let [box, player] of activePlayers) {{
        try {{
            player.destroy();
        }} catch(e) {{}}
    }}
    activePlayers.clear();
    hasPlayed.clear();
    
    let grid = document.getElementById("video-grid");
    let boxes = [...grid.children];

    // Shuffle
    for(let i = boxes.length - 1; i > 0; i--) {{
        let j = Math.floor(Math.random() * (i + 1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }}
    boxes.forEach(b => grid.appendChild(b));

    // Reset
    boxes.forEach(b => {{
        b.innerHTML = `<img src="https://i.ytimg.com/vi_webp/${{b.dataset.video}}/mqdefault.webp" loading="lazy" class="thumb">`;
        b.classList.remove('loaded');
        b.style.opacity = '1';
    }});

    // Load sequentially
    let delay = 0;
    boxes.forEach(box => {{
        let randomDelay = 1000 + Math.random() * 4000;
        setTimeout(() => loadPlayer(box), delay);
        delay += randomDelay;
    }});
}};
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)