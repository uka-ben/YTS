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

// Store all active players in a Map for safety
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
    box.appendChild(playerDiv);

    // Create unique tracking variables for THIS video only
    let actualPlayedTime = 0;
    let qualityInterval = null;
    let playbackInterval = null;
    let isDestroyed = false;
    
    // Generate a unique ID for this player
    const playerId = 'player_' + Math.random().toString(36).substr(2, 9);

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
                // Store in active players map
                activePlayers.set(playerId, {{
                    player: event.target,
                    box: box,
                    isDestroyed: false
                }});
                
                event.target.addEventListener('onStateChange', function(e) {{
                    // Don't do anything if already destroyed
                    if (isDestroyed) return;
                    
                    if(e.data == YT.PlayerState.PLAYING) {{
                        console.log(`Video ${playerId} started playing`);
                        
                        // Clear any existing intervals first
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
                                // Check if this specific player still exists and isn't destroyed
                                const playerData = activePlayers.get(playerId);
                                if (!isDestroyed && playerData && !playerData.isDestroyed && event.target && event.target.setPlaybackQuality) {{
                                    event.target.setPlaybackQuality('tiny');
                                }} else {{
                                    // If player no longer valid, clear this interval
                                    if (qualityInterval) {{
                                        clearInterval(qualityInterval);
                                        qualityInterval = null;
                                    }}
                                }}
                            }} catch(e) {{
                                console.log(`Error setting quality for ${playerId}:`, e);
                            }}
                        }}, 1000);

                        // Track actual playback time
                        playbackInterval = setInterval(() => {{
                            try {{
                                // Check if this specific player still exists
                                const playerData = activePlayers.get(playerId);
                                if (isDestroyed || !playerData || playerData.isDestroyed || !event.target || !event.target.getPlayerState) {{
                                    if (playbackInterval) {{
                                        clearInterval(playbackInterval);
                                        playbackInterval = null;
                                    }}
                                    return;
                                }}
                                
                                const state = event.target.getPlayerState();
                                if (state === YT.PlayerState.PLAYING) {{
                                    actualPlayedTime++;
                                    console.log(`Video ${playerId} played: ${{actualPlayedTime}}/${{targetDuration}}`);
                                    
                                    // Check if we've actually played for the target duration
                                    if (actualPlayedTime >= targetDuration && !isDestroyed) {{
                                        console.log(`Video ${playerId} reached target`);
                                        destroyVideo();
                                    }}
                                }}
                            }} catch(err) {{
                                console.log(`Error tracking video ${playerId}:`, err);
                            }}
                        }}, 1000);
                    }}
                    
                    else if (e.data == YT.PlayerState.ENDED) {{
                        // Video naturally ended - destroy if not already
                        if (!isDestroyed) {{
                            destroyVideo();
                        }}
                    }}
                }});
                
                // Helper function to destroy THIS SPECIFIC video only
                function destroyVideo() {{
                    // Mark as destroyed first
                    isDestroyed = true;
                    
                    // Update map
                    const playerData = activePlayers.get(playerId);
                    if (playerData) {{
                        playerData.isDestroyed = true;
                    }}
                    
                    console.log(`Destroying video ${playerId}`);
                    
                    // Clear THIS video's intervals
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
                        if (player && player.stopVideo) {{
                            player.stopVideo();
                        }}
                    }} catch(e) {{
                        console.log(`Error stopping video ${playerId}:`, e);
                    }}
                    
                    // Remove from active players map after a delay
                    setTimeout(() => {{
                        activePlayers.delete(playerId);
                    }}, 1000);
                    
                    // Fade out and remove THIS box only
                    box.style.opacity = 0;
                    setTimeout(() => {{
                        // Check if box still exists and hasn't been removed already
                        if (box && box.parentNode) {{
                            box.remove();
                            console.log(`Video ${playerId} removed from grid`);
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

// Optional: Add a health check to clean up any stuck intervals
setInterval(() => {{
    // This runs independently and doesn't interfere with videos
    console.log(`Active players: ${activePlayers.size}`);
}}, 30000);
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)