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

    // Mixed start strategy
    let start;
    if(Math.random() < 0.7){{
        start = 0;
    }} else {{
        start = Math.floor(Math.random() * 200);
    }}

    const targetDuration = Math.floor(Math.random()*(46-35+1)) + 35; // Renamed for clarity
    const end = start + targetDuration;

    box.innerHTML = '';
    box.classList.add("loaded");

    const playerDiv = document.createElement("div");
    box.appendChild(playerDiv);

    let actualPlayedTime = 0; // Track actual seconds played
    let qualityInterval;
    let playbackInterval;

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
                event.target.addEventListener('onStateChange', function(e) {{
                    if(e.data == YT.PlayerState.PLAYING) {{
                        // Continuously force 144p every second
                        qualityInterval = setInterval(() => {{
                            try {{
                                event.target.setPlaybackQuality('tiny');
                            }} catch(e){{}}
                        }}, 1000);

                        // Track actual playback time
                        playbackInterval = setInterval(() => {{
                            try {{
                                // Only increment if actually playing
                                if (event.target && event.target.getPlayerState) {{
                                    const state = event.target.getPlayerState();
                                    if (state === YT.PlayerState.PLAYING) {{
                                        actualPlayedTime++;
                                        console.log(`Actual played: ${{actualPlayedTime}}/${{targetDuration}}`);
                                        
                                        // Check if we've actually played for the target duration
                                        if (actualPlayedTime >= targetDuration) {{
                                            console.log("Target duration reached, destroying video");
                                            destroyVideo();
                                        }}
                                    }}
                                }}
                            }} catch(err) {{
                                console.log("Error tracking playback:", err);
                            }}
                        }}, 1000);
                    }}
                    
                    else if (e.data == YT.PlayerState.ENDED) {{
                        // Video naturally ended - check if we reached target
                        if (actualPlayedTime >= targetDuration) {{
                            destroyVideo();
                        }}
                    }}
                }});
                
                // Helper function to destroy video
                function destroyVideo() {{
                    // Clear all intervals
                    if (qualityInterval) clearInterval(qualityInterval);
                    if (playbackInterval) clearInterval(playbackInterval);
                    
                    try {{
                        if (player && player.stopVideo) {{
                            player.stopVideo();
                        }}
                    }} catch(e) {{}}
                    
                    // Fade out and remove
                    box.style.opacity = 0;
                    setTimeout(() => {{
                        if (box.parentNode) {{
                            box.remove();
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