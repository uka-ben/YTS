import streamlit as st

st.set_page_config(layout="wide")

video_id = "LxTZnjraVrM"
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
}}
button {{
padding:10px 20px;
font-size:16px;
cursor:pointer;
}}
#play-all-overlay {{
position:fixed;
top:0;
left:0;
width:100%;
height:100%;
background:transparent;
z-index:9999;
cursor:pointer;
display:none;
pointer-events:auto;
}}
#play-all-overlay.active {{
display:block;
}}
#play-all-overlay.playing {{
background:transparent;
}}
.play-all-hint {{
position:fixed;
bottom:20px;
right:20px;
background:rgba(255,255,255,0.95);
padding:15px 25px;
border-radius:30px;
box-shadow:0 4px 20px rgba(0,0,0,0.5);
z-index:10000;
font-weight:bold;
color:#333;
border:3px solid #ff0000;
font-size:16px;
transition:opacity 0.3s;
}}
.play-all-hint.loading {{
opacity:0.7;
border-color:#888;
}}
.play-all-hint.ready {{
opacity:1;
border-color:#ff0000;
animation:pulse 2s infinite;
}}
@keyframes pulse {{
0% {{ transform: scale(1); }}
50% {{ transform: scale(1.05); }}
100% {{ transform: scale(1); }}
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
</style>

<div class="button-container">
    <button id="shuffle-load">Shuffle + Load Players</button>
    <span class="loading-status" id="loading-status">0/20 loaded</span>
    <div class="loading-bar">
        <div class="loading-progress" id="loading-progress"></div>
    </div>
</div>

<div id="play-all-overlay"></div>
<div class="play-all-hint loading" id="play-all-hint" style="display:none;">⏳ Loading videos... please wait</div>

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
let overlay = document.getElementById("play-all-overlay");
let hint = document.getElementById("play-all-hint");
let loadingStatus = document.getElementById("loading-status");
let loadingProgress = document.getElementById("loading-progress");
let debugConsole = document.getElementById("debug-console");
let debugContent = document.getElementById("debug-content");
let toggleDebug = document.getElementById("toggle-debug");
let totalVideos = document.querySelectorAll(".video-box").length;
let isLoadingComplete = false;
let isPlayingActive = false;
let playedBoxes = new Set();

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

const viewerTypes = [
    {{ type: "binger", pauseChance: 0.1, maxPauses: 1, skipChance: 0.2, volumeRange: [70, 100] }},
    {{ type: "distracted", pauseChance: 0.4, maxPauses: 3, skipChance: 0.6, volumeRange: [30, 70] }},
    {{ type: "skimmer", pauseChance: 0.2, maxPauses: 2, skipChance: 0.8, volumeRange: [50, 85] }}
];

function updateLoadingProgress() {{
    let loadedCount = document.querySelectorAll(".video-box.loaded").length;
    loadingStatus.textContent = `${{loadedCount}}/${{totalVideos}} loaded`;
    let percent = (loadedCount / totalVideos) * 100;
    loadingProgress.style.width = percent + "%";
    
    if (loadedCount === totalVideos && !isLoadingComplete) {{
        isLoadingComplete = true;
        debug("All videos loaded - ready to play!");
        hint.innerHTML = "🎬 Click here to start playing (random order)";
        hint.classList.remove("loading");
        hint.classList.add("ready");
        overlay.classList.add("active");
    }}
}}

function getRandomStart() {{
    const rand = Math.random();
    if (rand < 0.7) return 0;
    else if (rand < 0.85) return Math.floor(Math.random() * 20) + 10;
    else return Math.floor(Math.random() * 120) + 60;
}}

function getRandomDuration() {{
    return Math.floor(Math.random() * 17) + 45;
}}

function getRandomPause() {{
    return Math.floor(Math.random() * 5) + 2;
}}

function simulateSkip(currentTime, duration, viewerProfile) {{
    const numSkips = Math.floor(Math.random() * 4);
    let newTime = currentTime;
    
    for (let i = 0; i < numSkips; i++) {{
        if (Math.random() < viewerProfile.skipChance) {{
            const skipDirection = Math.random() < 0.6 ? 10 : -10;
            const skipVariation = Math.floor(Math.random() * 7) - 3;
            const skipAmount = skipDirection + skipVariation;
            newTime += skipAmount;
            newTime = Math.max(0, Math.min(newTime, duration - 5));
        }}
    }}
    return newTime;
}}

function simulateVolumeControl(player, viewerProfile) {{
    const numVolumeChanges = Math.floor(Math.random() * 3) + 1;
    
    for (let i = 0; i < numVolumeChanges; i++) {{
        const delay = Math.floor(Math.random() * 20000) + 5000;
        setTimeout(() => {{
            try {{
                const minVol = viewerProfile.volumeRange[0];
                const maxVol = viewerProfile.volumeRange[1];
                const newVolume = Math.floor(Math.random() * (maxVol - minVol + 1)) + minVol;
                player.setVolume(newVolume);
            }} catch(e) {{}}
        }}, delay);
    }}
}}

function destroyVideo(box, player) {{
    debug("Destroying video: " + box.dataset.video);
    
    // Stop the video if it's playing
    try {{
        player.stopVideo();
    }} catch(e) {{}}
    
    // Remove from map
    loadedPlayers.delete(box);
    
    // Fade out and remove
    box.style.opacity = '0';
    setTimeout(() => {{
        if (box.parentNode) {{
            box.remove();
            updateLoadingProgress();
            debug("Video removed from grid");
        }}
    }}, 1000);
}}

function playVideo(box) {{
    if (!box) return;
    
    const player = loadedPlayers.get(box);
    
    if (player) {{
        debug("Playing video: " + box.dataset.video);
        player.playVideo();
        
        box.style.transform = 'scale(0.95)';
        box.style.transition = 'transform 0.1s';
        setTimeout(() => {{
            box.style.transform = 'scale(1)';
        }}, 100);
        
        return true;
    }}
    return false;
}}

function startRandomPlayback() {{
    if (isPlayingActive || !isLoadingComplete) return;
    
    isPlayingActive = true;
    overlay.classList.remove("active");
    hint.innerHTML = "▶️ Playing in random order...";
    hint.classList.remove("ready");
    debug("Starting RANDOM playback order");
    
    const allBoxes = Array.from(document.querySelectorAll(".video-box.loaded"));
    const shuffledBoxes = [...allBoxes];
    
    for (let i = shuffledBoxes.length - 1; i > 0; i--) {{
        const j = Math.floor(Math.random() * (i + 1));
        [shuffledBoxes[i], shuffledBoxes[j]] = [shuffledBoxes[j], shuffledBoxes[i]];
    }}
    
    debug(`Playing ${{shuffledBoxes.length}} videos in RANDOM order`);
    
    const totalVids = shuffledBoxes.length;
    const earlyCount = Math.floor(totalVids * 0.2);
    const mediumCount = Math.floor(totalVids * 0.3);
    
    debug(`Timing groups: Early: ${{earlyCount}} (0-12s), Medium: ${{mediumCount}} (12-30s), Late: ${{totalVids - earlyCount - mediumCount}} (30-60s)`);
    
    // Track cumulative delay to ensure 2-6 second gaps between starts
    let cumulativeDelay = 0;
    
    shuffledBoxes.forEach((box, index) => {{
        playedBoxes.add(box);
        
        // Base delay from timing group
        let baseDelay;
        if (index < earlyCount) {{
            baseDelay = Math.random() * 12000; // 0-12 seconds
            debug(`Video ${{index+1}} assigned to EARLY group: base delay ${{Math.round(baseDelay/1000)}}s`);
        }} else if (index < earlyCount + mediumCount) {{
            baseDelay = 12000 + Math.random() * 18000; // 12-30 seconds
            debug(`Video ${{index+1}} assigned to MEDIUM group: base delay ${{Math.round(baseDelay/1000)}}s`);
        }} else {{
            baseDelay = 30000 + Math.random() * 30000; // 30-60 seconds
            debug(`Video ${{index+1}} assigned to LATE group: base delay ${{Math.round(baseDelay/1000)}}s`);
        }}
        
        // Add cumulative delay to ensure 2-6 second gaps
        const finalDelay = cumulativeDelay + baseDelay;
        
        // Update cumulative delay with 2-6 second gap for next video
        cumulativeDelay += 2000 + Math.random() * 4000; // 2-6 seconds
        
        setTimeout(() => {{
            playVideo(box);
        }}, finalDelay);
    }});
}}

overlay.addEventListener("click", function(e) {{
    e.stopPropagation();
    debug("Overlay clicked - starting random playback");
    
    if (isLoadingComplete && !isPlayingActive) {{
        startRandomPlayback();
    }}
}});

function loadPlayer(box) {{
    if(box.classList.contains("loaded") || !YT_API_ready) return;

    debug("Loading player for video: " + box.dataset.video);
    
    const thinkingDelay = 1000 + Math.random() * 11000;
    
    setTimeout(() => {{
        const vid = box.dataset.video;
        const viewerProfile = viewerTypes[Math.floor(Math.random() * viewerTypes.length)];
        let start = getRandomStart();
        const duration = getRandomDuration();
        const end = start + duration;

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
                start: start,
                end: end,
                vq: 'tiny'
            }},
            events: {{
                onReady: (event) => {{
                    loadedPlayers.set(box, event.target);
                    updateLoadingProgress();
                    
                    debug("Player ready for video: " + vid + " (duration: " + duration + "s, end: " + end + "s)");
                    
                    const initialVolume = Math.floor(Math.random() * 
                        (viewerProfile.volumeRange[1] - viewerProfile.volumeRange[0] + 1)) + 
                        viewerProfile.volumeRange[0];
                    event.target.setVolume(initialVolume);
                    
                    simulateVolumeControl(event.target, viewerProfile);
                    
                    let qualityInterval = null;
                    let destroyTriggered = false;
                    
                    event.target.addEventListener('onStateChange', function(e) {{
                        if(e.data == YT.PlayerState.PLAYING) {{
                            debug("Video started playing: " + vid);
                            
                            if (qualityInterval) clearInterval(qualityInterval);
                            
                            // Force 144p
                            qualityInterval = setInterval(() => {{
                                try {{
                                    event.target.setPlaybackQuality('tiny');
                                }} catch(e){{}}
                            }}, 1000);
                            
                            let pauseCount = 0;
                            
                            const scheduleNextAction = () => {{
                                // Check if we should continue
                                if (pauseCount >= viewerProfile.maxPauses || destroyTriggered) return;
                                
                                const timeUntilAction = Math.floor(Math.random() * 11) + 5;
                                
                                setTimeout(() => {{
                                    // Before action, check current time against end
                                    event.target.getCurrentTime().then((currentTime) => {{
                                        if (currentTime >= end) {{
                                            debug("Video reached end time naturally: " + vid);
                                            destroyVideo(box, event.target);
                                            if (qualityInterval) clearInterval(qualityInterval);
                                            destroyTriggered = true;
                                            return;
                                        }}
                                        
                                        const action = Math.random() < viewerProfile.pauseChance ? 'pause' : 'skip';
                                        
                                        if (action === 'pause' && pauseCount < viewerProfile.maxPauses) {{
                                            const pauseDuration = getRandomPause();
                                            event.target.pauseVideo();
                                            pauseCount++;
                                            
                                            setTimeout(() => {{
                                                // Check time after pause
                                                event.target.getCurrentTime().then((currentTime) => {{
                                                    if (currentTime >= end) {{
                                                        debug("Video reached end after pause: " + vid);
                                                        destroyVideo(box, event.target);
                                                        if (qualityInterval) clearInterval(qualityInterval);
                                                        destroyTriggered = true;
                                                    }} else {{
                                                        event.target.playVideo();
                                                        scheduleNextAction();
                                                    }}
                                                }});
                                            }}, pauseDuration * 1000);
                                        }} else {{
                                            event.target.getCurrentTime().then((currentVideoTime) => {{
                                                const newTime = simulateSkip(currentVideoTime, duration, viewerProfile);
                                                // Don't skip past end
                                                if (newTime < end) {{
                                                    event.target.seekTo(newTime, true);
                                                    scheduleNextAction();
                                                }} else {{
                                                    debug("Skip would go past end, ending video: " + vid);
                                                    destroyVideo(box, event.target);
                                                    if (qualityInterval) clearInterval(qualityInterval);
                                                    destroyTriggered = true;
                                                }}
                                            }});
                                        }}
                                    }});
                                }}, timeUntilAction * 1000);
                            }};
                            
                            // Start the action scheduling
                            scheduleNextAction();
                            
                            // Also check periodically if we've reached the end
                            const endCheckInterval = setInterval(() => {{
                                if (destroyTriggered) {{
                                    clearInterval(endCheckInterval);
                                    return;
                                }}
                                event.target.getCurrentTime().then((currentTime) => {{
                                    if (currentTime >= end) {{
                                        debug("Video reached end time (periodic check): " + vid);
                                        destroyVideo(box, event.target);
                                        if (qualityInterval) clearInterval(qualityInterval);
                                        clearInterval(endCheckInterval);
                                        destroyTriggered = true;
                                    }}
                                }});
                            }}, 1000);
                            
                        }} else if (e.data == YT.PlayerState.PAUSED) {{
                            debug("Video paused: " + vid);
                        }} else if (e.data == YT.PlayerState.ENDED) {{
                            debug("Video ended naturally: " + vid);
                            destroyVideo(box, event.target);
                            if (qualityInterval) clearInterval(qualityInterval);
                            destroyTriggered = true;
                        }} else if (e.data == YT.PlayerState.UNSTARTED) {{
                            // Check if we're already past end time
                            event.target.getCurrentTime().then((currentTime) => {{
                                if (currentTime >= end) {{
                                    debug("Video past end time on unstarted: " + vid);
                                    destroyVideo(box, event.target);
                                    if (qualityInterval) clearInterval(qualityInterval);
                                    destroyTriggered = true;
                                }}
                            }});
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
        debug("Manual click on video: " + this.dataset.video);
        
        if (this.classList.contains("loaded")) {{
            if (!playedBoxes.has(this)) {{
                playedBoxes.add(this);
                playVideo(this);
            }}
        }} else {{
            loadPlayer(this);
        }}
    }});
}});

document.getElementById("shuffle-load").onclick = function() {{
    debug("Shuffle + Load clicked");
    
    let grid = document.getElementById("video-grid");
    let boxes = [...grid.children];

    // Destroy all existing players first
    for (let [box, player] of loadedPlayers) {{
        try {{
            player.destroy();
        }} catch(e) {{}}
    }}
    
    loadedPlayers.clear();
    playedBoxes.clear();
    isLoadingComplete = false;
    isPlayingActive = false;

    // Shuffle grid
    for(let i=boxes.length-1; i>0; i--) {{
        const j = Math.floor(Math.random()*(i+1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }}
    
    // Clear and rebuild grid
    grid.innerHTML = '';
    boxes.forEach(box => grid.appendChild(box));

    hint.style.display = "block";
    hint.innerHTML = "⏳ Loading videos... please wait";
    hint.classList.add("loading");
    hint.classList.remove("ready");
    overlay.classList.remove("active");

    updateLoadingProgress();

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