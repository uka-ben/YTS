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
</style>

<button id="shuffle-load">Shuffle + Load Players</button>

<div id="video-grid">
{''.join(html_blocks)}
</div>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
let YT_API_ready = false;
let qualityIntervals = new Map();
let durationTimeouts = new Map();
let activePlayers = new Map();
let videoDurations = new Map();

function onYouTubeIframeAPIReady() {{
    YT_API_ready = true;
    console.log("API Ready");
}}

function forceQuality(player, box) {{
    try {{
        const currentQuality = player.getPlaybackQuality();
        console.log("Current quality:", currentQuality);
        if (currentQuality !== 'tiny' && currentQuality !== 'small') {{
            player.setPlaybackQuality('tiny');
            console.log("Forced tiny quality");
        }}
    }} catch(e) {{
        console.log("Quality error:", e);
    }}
}}

function loadPlayer(box) {{
    if(box.classList.contains("loaded") || !YT_API_ready) return;

    const vid = box.dataset.video;
    const duration = Math.floor(Math.random()*(46-35+1))+35;
    videoDurations.set(box, duration);
    
    console.log("Loading video:", vid, "Duration:", duration + "s");

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
            vq: 'tiny',
            enablejsapi: 1,
            origin: window.location.origin
        }},
        events: {{
            onReady: (event) => {{
                console.log("Player ready:", vid);
                activePlayers.set(box, event.target);
                
                // Try to set quality immediately
                setTimeout(() => forceQuality(event.target, box), 500);
                setTimeout(() => forceQuality(event.target, box), 1000);
                setTimeout(() => forceQuality(event.target, box), 2000);
                
                /* Aggressive quality forcing */
                const qualityInterval = setInterval(() => {{
                    forceQuality(event.target, box);
                }}, 800);
                
                qualityIntervals.set(box, qualityInterval);
                
                /* Track state changes for duration */
                event.target.addEventListener('onStateChange', (stateEvent) => {{
                    const state = stateEvent.data;
                    console.log("State change:", vid, state);
                    
                    if (state === 1) {{ // PLAYING
                        console.log("Playing:", vid);
                        forceQuality(event.target, box);
                        
                        // Clear any existing timeout
                        if (durationTimeouts.has(box)) {{
                            clearTimeout(durationTimeouts.get(box));
                        }}
                        
                        // Set new timeout for duration
                        const dur = videoDurations.get(box);
                        console.log("Setting timeout for:", dur + "s");
                        
                        const timeout = setTimeout(() => {{
                            console.log("Duration reached, pausing:", vid);
                            const p = activePlayers.get(box);
                            if (p) {{
                                p.pauseVideo();
                                p.seekTo(0);
                            }}
                            durationTimeouts.delete(box);
                        }}, dur * 1000);
                        
                        durationTimeouts.set(box, timeout);
                    }}
                    
                    if (state === 0) {{ // ENDED
                        console.log("Ended naturally:", vid);
                        if (durationTimeouts.has(box)) {{
                            clearTimeout(durationTimeouts.get(box));
                            durationTimeouts.delete(box);
                        }}
                    }}
                }});
            }},
            onError: (error) => {{
                console.log("Error:", vid, error.data);
            }}
        }}
    }});
}}

document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", () => {{
        console.log("Clicked:", box.dataset.video);
        loadPlayer(box);
    }});
}});

document.getElementById("shuffle-load").onclick = () => {{
    console.log("Shuffling...");
    
    // Clean up
    for (let [box, interval] of qualityIntervals) {{
        clearInterval(interval);
    }}
    qualityIntervals.clear();
    
    for (let [box, timeout] of durationTimeouts) {{
        clearTimeout(timeout);
    }}
    durationTimeouts.clear();
    
    for (let [box, player] of activePlayers) {{
        try {{
            player.destroy();
        }} catch(e) {{}}
    }}
    activePlayers.clear();
    videoDurations.clear();
    
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
        setTimeout(() => {{
            loadPlayer(box);
        }}, delay);
        delay += randomDelay;
    }});
}};
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)