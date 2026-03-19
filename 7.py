import streamlit as st

st.set_page_config(layout="wide")

video_id = "ZYcZ_nBLG6Y"
video_ids = [video_id] * 20

html_blocks = []

for vid in video_ids:
    html_blocks.append(f"""
<div class="video-box" data-video="{vid}" id="box-{vid}-{i}">
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

// Store all active players in a Map for easy reference
const activePlayers = new Map();

function loadPlayer(box) {{
    if(box.classList.contains("loaded") || !YT_API_ready) return;

    const vid = box.dataset.video;

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

    const playerDiv = document.createElement("div");
    playerDiv.style.width = '100%';
    playerDiv.style.height = '100%';
    box.appendChild(playerDiv);

    // Create a unique ID for this player
    const playerId = 'player_' + Math.random().toString(36).substr(2, 9);
    playerDiv.id = playerId;

    // Create completely isolated tracking for THIS video
    let actualPlayedTime = 0;
    let qualityInterval = null;
    let playbackInterval = null;
    let isDestroyed = false;
    
    console.log(`Creating new player for box`);

    const player = new YT.Player(playerId, {{
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
            vq: 'tiny',
            enablejsapi: 1,
            origin: window.location.origin
        }},
        events: {{
            onReady: (event) => {{
                console.log(`Player ready for box`);
                
                // Store in active players map
                activePlayers.set(playerId, {{
                    player: event.target,
                    box: box,
                    targetDuration: targetDuration
                }});
                
                // Add state change listener
                event.target.addEventListener('onStateChange', function(e) {{
                    // Don't do anything if already destroyed
                    if (isDestroyed) return;
                    
                    const state = e.data;
                    
                    if(state == YT.PlayerState.PLAYING) {{
                        console.log(`Video playing`);
                        
                        // Clear any existing intervals first
                        if (qualityInterval) clearInterval(qualityInterval);
                        if (playbackInterval) clearInterval(playbackInterval);
                        
                        // Force 144p every second
                        qualityInterval = setInterval(() => {{
                            try {{
                                if (!isDestroyed && event.target && !isDestroyed) {{
                                    event.target.setPlaybackQuality('tiny');
                                }}
                            }} catch(e){{}}
                        }}, 1000);

                        // Track actual playback time
                        playbackInterval = setInterval(() => {{
                            try {{
                                if (isDestroyed || !event.target || !event.target.getPlayerState) {{
                                    return;
                                }}
                                
                                const currentState = event.target.getPlayerState();
                                if (currentState === YT.PlayerState.PLAYING) {{
                                    actualPlayedTime++;
                                    
                                    // Check if target reached
                                    if (actualPlayedTime >= targetDuration && !isDestroyed) {{
                                        console.log(`Target reached, destroying`);
                                        destroyVideo();
                                    }}
                                }}
                            }} catch(err) {{
                                console.log(`Error tracking:`, err);
                            }}
                        }}, 1000);
                    }}
                    
                    else if (state == YT.PlayerState.ENDED) {{
                        console.log(`Video ended naturally`);
                        if (!isDestroyed) {{
                            destroyVideo();
                        }}
                    }}
                    
                    else if (state == YT.PlayerState.PAUSED) {{
                        console.log(`Video paused - timer stopped`);
                    }}
                    
                    else if (state == YT.PlayerState.BUFFERING) {{
                        console.log(`Video buffering - timer paused`);
                    }}
                }});
                
                // Destroy function - completely isolated to THIS box only
                function destroyVideo() {{
                    console.log(`Destroy function called for box`);
                    
                    // Mark as destroyed immediately to prevent any further actions
                    isDestroyed = true;
                    
                    // Remove from active players map
                    activePlayers.delete(playerId);
                    
                    // Clear intervals
                    if (qualityInterval) {{
                        clearInterval(qualityInterval);
                        qualityInterval = null;
                    }}
                    if (playbackInterval) {{
                        clearInterval(playbackInterval);
                        playbackInterval = null;
                    }}
                    
                    // Stop the video
                    try {{
                        if (event.target && event.target.stopVideo) {{
                            event.target.stopVideo();
                        }}
                    }} catch(e) {{
                        console.log(`Error stopping video:`, e);
                    }}
                    
                    // Destroy the player
                    try {{
                        if (event.target && event.target.destroy) {{
                            event.target.destroy();
                        }}
                    }} catch(e) {{
                        console.log(`Error destroying player:`, e);
                    }}
                    
                    // Fade out and remove THIS box only
                    requestAnimationFrame(() => {{
                        box.style.opacity = 0;
                        box.style.transition = 'opacity 1s';
                        
                        setTimeout(() => {{
                            // Final check - make sure box still exists and we haven't been destroyed twice
                            if (box && box.parentNode && !isDestroyed) {{
                                // This shouldn't happen, but just in case
                                return;
                            }}
                            if (box && box.parentNode) {{
                                box.remove();
                                console.log(`Box removed from grid`);
                            }}
                        }}, 1000);
                    }});
                }}
            }},
            
            onError: (event) => {{
                console.log(`Player error:`, event.data);
                // If there's an error, still destroy after a delay
                setTimeout(() => {{
                    if (!isDestroyed) {{
                        destroyVideo();
                    }}
                }}, 5000);
            }}
        }}
    }});
}}

document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", (e) => {{
        e.stopPropagation(); // Prevent event bubbling
        loadPlayer(box);
    }});
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