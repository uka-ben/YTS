import streamlit as st

st.set_page_config(layout="wide")

video_id = "ZYcZ_nBLG6Y"
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

function onYouTubeIframeAPIReady() {{
    YT_API_ready = true;
}}

function loadPlayer(box) {{
    if(box.classList.contains("loaded") || !YT_API_ready) return;

    const vid = box.dataset.video;
    const boxId = 'box_' + Math.random().toString(36).substr(2, 9); // Unique ID for this box
    console.log(`Loading video for ${{boxId}}`);

    // Mixed start strategy
    let start;
    if(Math.random() < 0.7){{
        start = 0;
    }} else {{
        start = Math.floor(Math.random() * 200);
    }}

    const targetDuration = Math.floor(Math.random()*(46-35+1)) + 35;
    const end = start + targetDuration;

    box.innerHTML = '';
    box.classList.add("loaded");
    box.setAttribute('data-box-id', boxId); // Tag the box with unique ID

    const playerDiv = document.createElement("div");
    playerDiv.setAttribute('data-player-id', boxId); // Tag player div
    box.appendChild(playerDiv);

    // Create unique tracking variables for THIS video only
    let actualPlayedTime = 0;
    let qualityInterval = null;
    let playbackInterval = null;
    let isDestroyed = false;
    let playerReady = false;

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
            start: start,
            end: end,
            vq: 'tiny'
        }},
        events: {{
            onReady: (event) => {{
                playerReady = true;
                console.log(`Player ready for ${{boxId}}`);
                
                event.target.addEventListener('onStateChange', function(e) {{
                    // Don't do anything if already destroyed
                    if (isDestroyed) return;
                    
                    if(e.data == YT.PlayerState.PLAYING) {{
                        console.log(`${{boxId}} started playing`);
                        
                        // Clear any existing intervals first with safety checks
                        if (qualityInterval) {{
                            clearInterval(qualityInterval);
                            qualityInterval = null;
                        }}
                        if (playbackInterval) {{
                            clearInterval(playbackInterval);
                            playbackInterval = null;
                        }}
                        
                        // Continuously force 144p every second
                        qualityInterval = setInterval(() => {{
                            try {{
                                // Extra safety: check if this specific box still exists and isn't destroyed
                                if (!isDestroyed && !box.classList.contains('destroyed') && 
                                    document.body.contains(box) && event.target && 
                                    typeof event.target.setPlaybackQuality === 'function') {{
                                    event.target.setPlaybackQuality('tiny');
                                }} else {{
                                    // Clean up if box no longer valid
                                    if (qualityInterval) {{
                                        clearInterval(qualityInterval);
                                        qualityInterval = null;
                                    }}
                                }}
                            }} catch(e) {{
                                console.log(`${{boxId}} quality error:`, e);
                            }}
                        }}, 1000);

                        // Track actual playback time - but only for THIS video
                        playbackInterval = setInterval(() => {{
                            try {{
                                // Multiple safety checks
                                if (isDestroyed || !document.body.contains(box) || 
                                    !event.target || typeof event.target.getPlayerState !== 'function') {{
                                    if (playbackInterval) {{
                                        clearInterval(playbackInterval);
                                        playbackInterval = null;
                                    }}
                                    return;
                                }}
                                
                                const state = event.target.getPlayerState();
                                if (state === YT.PlayerState.PLAYING) {{
                                    actualPlayedTime++;
                                    console.log(`${{boxId}} played: ${{actualPlayedTime}}/${{targetDuration}}`);
                                    
                                    // Check if we've actually played for the target duration
                                    if (actualPlayedTime >= targetDuration && !isDestroyed) {{
                                        console.log(`${{boxId}} reached target, destroying`);
                                        destroyVideo();
                                    }}
                                }}
                            }} catch(err) {{
                                console.log(`${{boxId}} tracking error:`, err);
                            }}
                        }}, 1000);
                    }}
                    
                    else if (e.data == YT.PlayerState.ENDED) {{
                        console.log(`${{boxId}} ended naturally`);
                        if (!isDestroyed) {{
                            destroyVideo();
                        }}
                    }}
                    
                    else if (e.data == YT.PlayerState.PAUSED) {{
                        console.log(`${{boxId}} paused - timer stopped`);
                    }}
                    
                    else if (e.data == YT.PlayerState.BUFFERING) {{
                        console.log(`${{boxId}} buffering - timer paused`);
                    }}
                }});
                
                // Helper function to destroy THIS SPECIFIC video only
                function destroyVideo() {{
                    // Mark as destroyed first to prevent any further actions
                    if (isDestroyed) return;
                    isDestroyed = true;
                    box.classList.add('destroyed');
                    
                    console.log(`Destroying ${{boxId}}`);
                    
                    // Clear THIS video's intervals with null checks
                    if (qualityInterval) {{
                        clearInterval(qualityInterval);
                        qualityInterval = null;
                    }}
                    if (playbackInterval) {{
                        clearInterval(playbackInterval);
                        playbackInterval = null;
                    }}
                    
                    // Stop THIS video
                    try {{
                        if (player && typeof player.stopVideo === 'function') {{
                            player.stopVideo();
                        }}
                    }} catch(e) {{
                        console.log(`${{boxId}} stop error:`, e);
                    }}
                    
                    // Destroy the player instance
                    try {{
                        if (player && typeof player.destroy === 'function') {{
                            player.destroy();
                        }}
                    }} catch(e) {{
                        console.log(`${{boxId}} destroy error:`, e);
                    }}
                    
                    // Fade out and remove THIS box only
                    box.style.opacity = 0;
                    setTimeout(() => {{
                        // Extra safety: check if box still exists and hasn't been removed
                        try {{
                            if (box && box.parentNode && document.body.contains(box)) {{
                                box.remove();
                                console.log(`${{boxId}} removed from grid`);
                            }}
                        }} catch(e) {{
                            console.log(`${{boxId}} removal error:`, e);
                        }}
                    }}, 1000);
                }}
            }}
        }}
    }});
}}

document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", () => loadPlayer(box));
}});

document.getElementById("shuffle-load").onclick = () => {{
    let grid = document.getElementById("video-grid");
    let boxes = [...grid.children];

    // Shuffle grid
    for(let i=boxes.length-1; i>0; i--) {{
        const j = Math.floor(Math.random()*(i+1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }}
    boxes.forEach(box => grid.appendChild(box));

    // Sequential loading with 1–5s random delay
    let delay = 0;
    boxes.forEach(box => {{
        let randomDelay = 1000 + Math.random() * 4000; // 1–5s
        setTimeout(() => {{
            loadPlayer(box);
        }}, delay);
        delay += randomDelay;
    }});
}};
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)