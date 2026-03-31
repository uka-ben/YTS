import streamlit as st

st.set_page_config(layout="wide")

# Configuration
VIDEO_ID = "LxTZnjraVrM"  # Your video ID
VIDEO_COUNT = 50
MIN_DURATION = 36  # seconds
MAX_DURATION = 50  # seconds

video_ids = [VIDEO_ID] * VIDEO_COUNT

html_blocks = []
for vid in video_ids:
    html_blocks.append(f"""
<div class="video-box" data-video="{vid}">
    <img src="https://i.ytimg.com/vi_webp/{vid}/mqdefault.webp"
         loading="lazy"
         class="thumb">
    <div class="play-overlay">▶</div>
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
    transition:opacity 1s, transform 0.2s;
}}
.video-box:hover {{
    transform:scale(1.02);
}}
.thumb {{
    width:100%;
    height:100%;
    object-fit:cover;
    border-radius:6px;
}}
.play-overlay {{
    position:absolute;
    top:50%;
    left:50%;
    transform:translate(-50%, -50%);
    background:rgba(0,0,0,0.75);
    color:white;
    font-size:48px;
    width:70px;
    height:70px;
    border-radius:50%;
    display:flex;
    align-items:center;
    justify-content:center;
    pointer-events:none;
    z-index:10;
    transition:all 0.2s;
    backdrop-filter:blur(4px);
}}
.video-box:hover .play-overlay {{
    background:rgba(255,0,0,0.8);
    transform:translate(-50%, -50%) scale(1.1);
}}
iframe {{
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
    padding:10px;
    background:#111;
    border-radius:8px;
}}
button {{
    padding:10px 20px;
    font-size:16px;
    cursor:pointer;
    background:#ff0000;
    color:white;
    border:none;
    border-radius:6px;
    font-weight:bold;
    transition:all 0.2s;
}}
button:hover {{
    background:#cc0000;
    transform:scale(1.02);
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
    right:20px;
    background:rgba(0,0,0,0.9);
    color:#0f0;
    padding:10px;
    border-radius:5px;
    font-family:monospace;
    font-size:11px;
    z-index:10001;
    width:350px;
    max-height:300px;
    display:flex;
    flex-direction:column;
    border:1px solid #0f0;
}}
.debug-header {{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:8px;
    padding-bottom:5px;
    border-bottom:1px solid #0f0;
}}
.debug-header button {{
    padding:2px 8px;
    font-size:10px;
    background:#333;
    color:#0f0;
    border:1px solid #0f0;
    border-radius:3px;
    cursor:pointer;
    margin-left:5px;
}}
.debug-header button:hover {{
    background:#0f0;
    color:#000;
    transform:none;
}}
.debug-content {{
    max-height:250px;
    overflow-y:auto;
    font-size:10px;
}}
.debug-content div {{
    margin-bottom:3px;
    word-break:break-word;
}}
.hidden {{
    display:none !important;
}}
.stats {{
    margin-left:auto;
    color:#0f0;
    font-size:12px;
}}
</style>

<div class="button-container">
    <button id="shuffle-load">🎲 Shuffle & Load Videos</button>
    <span class="loading-status" id="loading-status">0/{VIDEO_COUNT} loaded</span>
    <div class="loading-bar">
        <div class="loading-progress" id="loading-progress"></div>
    </div>
    <div class="stats" id="stats">📊 Views: 0 | 💾 Data: 0 MB</div>
</div>

<div class="debug-console" id="debug-console">
    <div class="debug-header">
        <span>🐛 Debug Logs</span>
        <div>
            <button id="clear-debug">Clear</button>
            <button id="toggle-debug">Hide</button>
        </div>
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
let debugConsole = document.getElementById("debug-console");
let debugContent = document.getElementById("debug-content");
let clearDebug = document.getElementById("clear-debug");
let toggleDebug = document.getElementById("toggle-debug");
let totalVideos = document.querySelectorAll(".video-box").length;
let totalViews = 0;
let totalDataMB = 0;

// Stats tracking
function updateStats() {{
    document.getElementById("stats").innerHTML = `📊 Views: ${{totalViews}} | 💾 Data: ${{totalDataMB.toFixed(1)}} MB`;
}}

function debug(msg, type="info") {{
    let timeStr = new Date().toLocaleTimeString();
    let icon = type === "view" ? "👁️" : type === "data" ? "💾" : "🔧";
    debugContent.innerHTML += `<div>${{timeStr}} ${{icon}} ${{msg}}</div>`;
    debugContent.scrollTop = debugContent.scrollHeight;
    console.log(msg);
}}

clearDebug.addEventListener("click", () => {{
    debugContent.innerHTML = "";
}});

toggleDebug.addEventListener("click", function() {{
    if (debugContent.classList.contains("hidden")) {{
        debugContent.classList.remove("hidden");
        toggleDebug.textContent = "Hide";
    }} else {{
        debugContent.classList.add("hidden");
        toggleDebug.textContent = "Show";
    }}
}});

function onYouTubeIframeAPIReady() {{
    YT_API_ready = true;
    debug("YouTube API ready - waiting for user clicks");
}}

function updateLoadingProgress() {{
    let loadedCount = document.querySelectorAll(".video-box.loaded").length;
    let loadingStatus = document.getElementById("loading-status");
    let loadingProgress = document.getElementById("loading-progress");
    loadingStatus.textContent = `${{loadedCount}}/${{totalVideos}} loaded`;
    let percent = (loadedCount / totalVideos) * 100;
    loadingProgress.style.width = percent + "%";
}}

function destroyVideo(box, player, viewCounted=false) {{
    if(viewCounted) {{
        totalViews++;
        debug(`✅ VIEW COUNTED! Total views: ${{totalViews}}`, "view");
        updateStats();
    }}
    
    debug(`🗑️ Destroying video: ${{box.dataset.video}}`);
    try {{
        if(player && player.stopVideo) player.stopVideo();
        if(player && player.destroy) player.destroy();
    }} catch(e) {{}}
    
    loadedPlayers.delete(box);
    box.style.opacity = '0';
    box.style.transition = 'opacity 1s';
    
    setTimeout(() => {{
        if (box.parentNode) {{
            box.remove();
            updateLoadingProgress();
            debug(`✅ Video removed from grid`);
        }}
    }}, 1000);
}}

function getRandomDuration() {{
    return Math.floor(Math.random() * (MAX_DURATION - MIN_DURATION + 1)) + MIN_DURATION;
}}

function getRandomClickDelay() {{
    // Natural human-like delay: 2-15 seconds
    return Math.random() * 13000 + 2000;
}}

function loadPlayer(box) {{
    if(box.classList.contains("loaded") || !YT_API_ready) return;
    
    const exactDuration = getRandomDuration();
    const vid = box.dataset.video;
    
    debug(`📦 Loading player: ${{vid}} (duration: ${{exactDuration}}s)`);
    
    // Calculate potential data usage at 144p (~0.1 MB per second)
    const estimatedDataMB = (exactDuration * 0.1);
    totalDataMB += estimatedDataMB;
    debug(`💾 Estimated data: ${{estimatedDataMB.toFixed(2)}} MB (total: ${{totalDataMB.toFixed(1)}} MB)`, "data");
    updateStats();
    
    box.innerHTML = '';
    box.classList.add("loaded");
    
    const playerDiv = document.createElement("div");
    box.appendChild(playerDiv);
    
    let viewCounted = false;
    let watchStartTime = 0;
    let watchInterval = null;
    
    const player = new YT.Player(playerDiv, {{
        height: '100%',
        width: '100%',
        videoId: vid,
        playerVars: {{
            start: 0,
            end: exactDuration,
            autoplay: 0,              // NO AUTOPLAY - views require user interaction
            controls: 1,
            rel: 0,
            modestbranding: 1,
            playsinline: 1,
            vq: 'tiny',               // 144p - minimal data
            iv_load_policy: 3,        // No annotations
            fs: 0
        }},
        events: {{
            onReady: (event) => {{
                loadedPlayers.set(box, event.target);
                updateLoadingProgress();
                
                // User must click to play (ensures view counts)
                let userInteracted = false;
                
                const startPlayback = () => {{
                    if (!userInteracted) {{
                        userInteracted = true;
                        debug(`👆 USER CLICK - Starting playback for view counting`, "view");
                        event.target.playVideo();
                        box.removeEventListener('click', startPlayback);
                    }}
                }};
                
                box.addEventListener('click', startPlayback);
                
                // Optional: Auto-click with natural delay (for automated testing)
                // Comment out if you want strictly manual clicks
                const naturalDelay = getRandomClickDelay();
                setTimeout(() => {{
                    if (!userInteracted && box.parentNode) {{
                        debug(`🤖 Simulated natural click after ${{(naturalDelay/1000).toFixed(1)}}s`);
                        startPlayback();
                    }}
                }}, naturalDelay);
            }},
            
            onStateChange: (e) => {{
                if (e.data === YT.PlayerState.PLAYING) {{
                    debug(`▶️ Video playing - view will count after 30+ seconds`);
                    
                    // Force 144p once at start
                    try {{
                        e.target.setPlaybackQuality('tiny');
                    }} catch(err) {{}}
                    
                    // Track watch time for view confirmation
                    watchStartTime = Date.now();
                    watchInterval = setInterval(() => {{
                        const watchDuration = (Date.now() - watchStartTime) / 1000;
                        
                        if (watchDuration >= 30 && !viewCounted) {{
                            viewCounted = true;
                            debug(`🎉 VIEW COUNTED! User watched ${{watchDuration.toFixed(1)}} seconds`, "view");
                            totalViews++;
                            updateStats();
                        }}
                        
                        if (e.target.getPlayerState() !== YT.PlayerState.PLAYING) {{
                            clearInterval(watchInterval);
                        }}
                    }}, 1000);
                }}
                
                if (e.data === YT.PlayerState.ENDED) {{
                    debug(`🏁 Video ended - total watch time: ${{(Date.now() - watchStartTime)/1000}}s`);
                    if (watchInterval) clearInterval(watchInterval);
                    destroyVideo(box, e.target, viewCounted);
                }}
                
                if (e.data === YT.PlayerState.PAUSED) {{
                    debug(`⏸️ Video paused - watch tracking continues on resume`);
                }}
            }},
            
            onError: (error) => {{
                debug(`❌ Player error: ${{error.data}}`);
            }}
        }}
    }});
}}

// Manual click on video box (if not loaded yet)
document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", function(e) {{
        e.stopPropagation();
        debug(`🖱️ Manual click on video: ${{this.dataset.video}}`);
        if (!this.classList.contains("loaded")) {{
            loadPlayer(this);
        }}
    }});
}});

// Shuffle and load
document.getElementById("shuffle-load").onclick = function() {{
    debug(`🔄 SHUFFLE + LOAD triggered`);
    let grid = document.getElementById("video-grid");
    let boxes = [...grid.children];
    
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
    boxes.forEach(box => grid.appendChild(box));
    
    updateLoadingProgress();
    
    // Load videos with staggered delays (2-15 seconds between loads)
    let delay = 0;
    boxes.forEach(box => {{
        let randomDelay = 2000 + Math.random() * 13000;
        setTimeout(() => {{
            if (box.parentNode) {{
                loadPlayer(box);
            }}
        }}, delay);
        delay += randomDelay;
    }});
    debug(`📋 Scheduled ${{boxes.length}} videos over ~${{Math.round(delay/1000)}} seconds`);
}};

debug(`✅ App ready - ${totalVideos} videos loaded`);
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)