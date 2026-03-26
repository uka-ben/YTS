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
/* Style for completed videos - hidden but still taking up space */
.video-box.completed {{
opacity:0;
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

function onYouTubeIframeAPIReady() {{
    YT_API_ready = true;
}}

function loadPlayer(box) {{
    if(box.classList.contains("loaded") || !YT_API_ready) return;

    const vid = box.dataset.video;

    // Random duration 35-46 seconds
    const targetDuration = Math.floor(Math.random()*(46-35+1)) + 35;
    // NO start parameter - video plays naturally from beginning
    // NO end parameter - we'll track duration ourselves

    box.innerHTML = '';
    box.classList.add("loaded");

    const playerDiv = document.createElement("div");
    box.appendChild(playerDiv);

    // Create unique tracking variables for THIS video only
    let actualPlayedTime = 0;
    let qualityInterval = null;
    let playbackInterval = null;
    let isDestroyed = false;

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
            // REMOVED: start parameter completely
            // REMOVED: end parameter completely
        }},
        events: {{
            onReady: (event) => {{
                event.target.addEventListener('onStateChange', function(e) {{
                    // Don't do anything if already destroyed
                    if (isDestroyed) return;
                    
                    if(e.data == YT.PlayerState.PLAYING) {{
                        // Clear any existing intervals first (safety)
                        if (qualityInterval) clearInterval(qualityInterval);
                        if (playbackInterval) clearInterval(playbackInterval);
                        
                        // Continuously force 144p every second
                        qualityInterval = setInterval(() => {{
                            try {{
                                if (!isDestroyed && event.target && event.target.setPlaybackQuality) {{
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
                                
                                const state = event.target.getPlayerState();
                                if (state === YT.PlayerState.PLAYING) {{
                                    actualPlayedTime++;
                                    
                                    // Check if we've actually played for the target duration
                                    if (actualPlayedTime >= targetDuration && !isDestroyed) {{
                                        destroyVideo();
                                    }}
                                }}
                            }} catch(err) {{
                                console.log(`Error tracking video:`, err);
                            }}
                        }}, 1000);
                    }}
                    
                    else if (e.data == YT.PlayerState.ENDED) {{
                        if (!isDestroyed) {{
                            destroyVideo();
                        }}
                    }}
                }});
                
                function destroyVideo() {{
                    // Mark as destroyed first
                    isDestroyed = true;
                    
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
                        if (player && player.stopVideo) {{
                            player.stopVideo();
                        }}
                    }} catch(e) {{}}
                    
                    // Hide but keep in DOM to prevent grid reflow
                    box.style.opacity = 0;
                    box.classList.add("completed");
                    box.style.pointerEvents = 'none';
                    
                    // Clear the iframe content to free memory
                    try {{
                        box.innerHTML = '';
                        // Add back a placeholder to maintain size
                        box.style.backgroundColor = '#000';
                    }} catch(e) {{}}
                    
                    console.log("Video completed after ${actualPlayedTime} seconds and hidden");
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

    // Reset all boxes
    boxes.forEach(box => {{
        box.classList.remove("completed", "loaded");
        box.style.opacity = 1;
        box.style.pointerEvents = 'auto';
        box.style.backgroundColor = '';
        // Restore thumbnail
        const vid = box.dataset.video;
        box.innerHTML = `<img src="https://i.ytimg.com/vi_webp/${vid}/mqdefault.webp" loading="lazy" class="thumb">`;
    }});

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