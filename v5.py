import streamlit as st

st.set_page_config(layout="wide")

video_id = "LxTZnjraVrM"
video_ids = [video_id] * 50

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
    position:relative;
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
}}
.button-container {{
    display:flex;
    gap:10px;
    margin-bottom:10px;
    align-items:center;
    flex-wrap:wrap;
}}
button {{
    padding:10px 20px;
    font-size:16px;
    cursor:pointer;
}}
.loading-status {{
    margin-left:20px;
    color:#888;
    font-size:14px;
}}
.loading-bar {{
    width:200px;
    height:20px;
    background:#333;
    border-radius:10px;
    overflow:hidden;
    margin-left:10px;
}}
.loading-progress {{
    height:100%;
    background:#ff0000;
    width:0%;
    transition:width 0.3s;
}}
.debug-console {{
    position:fixed;
    bottom:20px;
    left:20px;
    background:rgba(0,0,0,0.8);
    color:#0f0;
    padding:10px;
    border-radius:5px;
    font-family:monospace;
    font-size:12px;
    z-index:10001;
    max-width:400px;
    max-height:300px;
    overflow:auto;
}}
.debug-header {{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:5px;
    padding-bottom:5px;
    border-bottom:1px solid #0f0;
}}
.debug-header button {{
    padding:2px 8px;
    font-size:11px;
    background:#333;
    color:#0f0;
    border:1px solid #0f0;
    border-radius:3px;
    cursor:pointer;
}}
.debug-header button:hover {{
    background:#0f0;
    color:#000;
}}
.debug-content {{
    max-height:250px;
    overflow-y:auto;
}}
.hidden {{
    display:none !important;
}}
.replay-indicator {{
    position: absolute;
    top: 5px;
    right: 5px;
    background: rgba(0,0,0,0.7);
    color: #fff;
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 10px;
    z-index: 10;
    pointer-events: none;
}}
</style>

<div class="button-container">
    <button id="shuffle-load">Shuffle + Load Players</button>
    <span class="loading-status" id="loading-status">0/50 loaded</span>
    <div class="loading-bar">
        <div class="loading-progress" id="loading-progress"></div>
    </div>
</div>

<div class="debug-console" id="debug-console">
    <div class="debug-header">
        <span>🐛 Debug Logs</span>
        <button id="toggle-debug">Hide</button>
    </div>
    <div class="debug-content" id="debug-content"></div>
</div>

<div id="video-grid">
{''.join(html_blocks)}
</div>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
let YT_API_ready = false;
let loadedPlayers = new Map();
let qualityIntervals = new Map();
let debugConsole = document.getElementById("debug-console");
let debugContent = document.getElementById("debug-content");
let toggleDebug = document.getElementById("toggle-debug");
let totalVideos = document.querySelectorAll(".video-box").length;

// Toggle debug logs
toggleDebug.addEventListener("click", function() {{
    if (debugContent.classList.contains("hidden")) {{
        debugContent.classList.remove("hidden");
        toggleDebug.textContent = "Hide";
    }} else {{
        debugContent.classList.add("hidden");
        toggleDebug.textContent = "Show";
    }}
}});

function debug(msg) {{
    console.log(msg);
    let timeStr = new Date().toLocaleTimeString();
    debugContent.innerHTML += '<div>' + timeStr + ': ' + msg + '</div>';
    debugContent.scrollTop = debugContent.scrollHeight;
}}

function onYouTubeIframeAPIReady() {{
    YT_API_ready = true;
    debug("YouTube API ready");
}}

function updateLoadingProgress() {{
    let loadedCount = document.querySelectorAll(".video-box.loaded").length;
    let loadingStatus = document.getElementById("loading-status");
    let loadingProgress = document.getElementById("loading-progress");
    loadingStatus.textContent = `${{loadedCount}}/${{totalVideos}} loaded`;
    let percent = (loadedCount / totalVideos) * 100;
    loadingProgress.style.width = percent + "%";
}}

function pauseAndResetVideo(box, player, vid) {{
    debug("⏸️ Pausing and resetting video: " + vid + " (ready for replay without additional data)");
    
    // Clear quality forcing interval
    if (qualityIntervals.has(box)) {{
        clearInterval(qualityIntervals.get(box));
        qualityIntervals.delete(box);
    }}
    
    try {{
        player.pauseVideo();
        player.seekTo(0);
    }} catch(e) {{}}
    
    // Add replay indicator
    let indicator = box.querySelector('.replay-indicator');
    if (!indicator) {{
        indicator = document.createElement('div');
        indicator.className = 'replay-indicator';
        indicator.textContent = '↻ Ready to replay';
        box.appendChild(indicator);
    }}
    
    // Re-enable click to replay
    box.style.opacity = '1';
}}

function playVideo(box) {{
    if (!box) return;
    const player = loadedPlayers.get(box);
    if (player) {{
        const vid = box.dataset.video;
        debug("▶️ Playing video: " + vid);
        
        // Remove replay indicator when playing
        let indicator = box.querySelector('.replay-indicator');
        if (indicator) indicator.remove();
        
        player.playVideo();
        
        // Restart quality forcing
        if (qualityIntervals.has(box)) {{
            clearInterval(qualityIntervals.get(box));
        }}
        const qualityInterval = setInterval(() => {{
            try {{
                player.setPlaybackQuality('tiny');
            }} catch(e){{}}
        }}, 1000);
        qualityIntervals.set(box, qualityInterval);
        
        // Schedule pause and reset after duration (1h33s - 2h18s)
        const duration = Math.floor(Math.random() * (7218 - 3633 + 1)) + 3633;
        setTimeout(() => {{
            pauseAndResetVideo(box, player, vid);
        }}, duration * 1000);
        
        box.style.transform = 'scale(0.95)';
        box.style.transition = 'transform 0.1s';
        setTimeout(() => {{
            box.style.transform = 'scale(1)';
        }}, 100);
    }}
}}

function loadPlayer(box) {{
    if(box.classList.contains("loaded") || !YT_API_ready) return;

    debug("Loading player for video: " + box.dataset.video);
    const thinkingDelay = 1000 + Math.random() * 11000; // staggered loading

    setTimeout(() => {{
        const vid = box.dataset.video;
        
        box.innerHTML = '';
        box.classList.add("loaded");

        const playerDiv = document.createElement("div");
        box.appendChild(playerDiv);

        debug(`Creating player for: ${{vid}}`);

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
                    loadedPlayers.set(box, event.target);
                    updateLoadingProgress();
                    debug("Player ready for video: " + vid);
                    event.target.setVolume(100);

                    event.target.addEventListener('onStateChange', function(e) {{
                        if(e.data == YT.PlayerState.PLAYING) {{
                            debug("▶️ Video started playing: " + vid);
                            
                            // Force 144p using V15's aggressive method
                            if (qualityIntervals.has(box)) {{
                                clearInterval(qualityIntervals.get(box));
                            }}
                            const qualityInterval = setInterval(() => {{
                                try {{
                                    event.target.setPlaybackQuality('tiny');
                                }} catch(e){{}}
                            }}, 1000);
                            qualityIntervals.set(box, qualityInterval);
                        }}
                    }});
                }}
            }}
        }});
    }}, thinkingDelay);
}}

document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", function(e) {{
        e.stopPropagation();
        debug("👆 Manual click on video: " + this.dataset.video);
        if (this.classList.contains("loaded")) {{
            playVideo(this);
        }} else {{
            loadPlayer(this);
        }}
    }});
}});

document.getElementById("shuffle-load").onclick = function() {{
    debug("🔄 Shuffle + Load clicked");
    let grid = document.getElementById("video-grid");
    let boxes = [...grid.children];

    // Clear all quality intervals
    for (let [box, interval] of qualityIntervals) {{
        clearInterval(interval);
    }}
    qualityIntervals.clear();

    // Destroy all existing players
    for (let [box, player] of loadedPlayers) {{
        try {{
            player.destroy();
        }} catch(e) {{}}
    }}
    loadedPlayers.clear();

    // Shuffle grid
    for(let i=boxes.length-1; i>0; i--) {{
        const j = Math.floor(Math.random()*(i+1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }}
    grid.innerHTML = '';
    boxes.forEach(box => {{
        // Reset box
        box.innerHTML = `<img src="https://i.ytimg.com/vi_webp/${{box.dataset.video}}/mqdefault.webp" loading="lazy" class="thumb">`;
        box.classList.remove('loaded');
        box.style.opacity = '1';
        grid.appendChild(box);
    }});

    updateLoadingProgress();

    // Load videos with 1-12s delays
    let delay = 0;
    boxes.forEach(box => {{
        let randomDelay = 1000 + Math.random() * 11000;
        setTimeout(() => {{
            loadPlayer(box);
        }}, delay);
        delay += randomDelay;
    }});
    debug(`Scheduled ${{boxes.length}} videos to load over ~${{Math.round(delay/1000)}} seconds (1-12s between loads)`);
}};
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)