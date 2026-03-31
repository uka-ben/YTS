import streamlit as st

st.set_page_config(layout="wide")

video_id = "hHt84PoKxsQ"
video_ids = [video_id] * 20
import streamlit as st

st.set_page_config(layout="wide")

video_id = "qsnHr1lZ7mA"
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
background:#ff0000;
color:white;
border:none;
border-radius:6px;
}}
button:hover {{
background:#cc0000;
}}
.debug-console {{
position:fixed;
bottom:20px;
right:20px;
background:rgba(0,0,0,0.85);
color:#0f0;
padding:10px;
border-radius:8px;
font-family:monospace;
font-size:11px;
z-index:10001;
max-width:350px;
max-height:250px;
overflow:auto;
}}
.debug-header {{
display:flex;
justify-content:space-between;
margin-bottom:5px;
border-bottom:1px solid #0f0;
}}
.debug-content {{
font-size:10px;
}}
.hidden {{
display:none;
}}
</style>

<button id="shuffle-load">🔀 Shuffle + Load Players</button>

<div id="video-grid">
{''.join(html_blocks)}
</div>

<div class="debug-console" id="debug-console">
    <div class="debug-header">
        <span>📊 Playback Monitor - AGGRESSIVE 144p MODE</span>
        <button id="toggle-debug">Hide</button>
    </div>
    <div class="debug-content" id="debug-content"></div>
</div>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
let YT_API_ready = false;
let activePlayers = new Map();
let qualityIntervals = new Map();
let debugContent = document.getElementById("debug-content");
let toggleDebug = document.getElementById("toggle-debug");
let debugConsole = document.getElementById("debug-console");

function debug(msg) {{
    console.log(msg);
    let timeStr = new Date().toLocaleTimeString();
    let logDiv = document.createElement('div');
    logDiv.textContent = timeStr + ': ' + msg;
    debugContent.appendChild(logDiv);
    debugContent.scrollTop = debugContent.scrollHeight;
    while(debugContent.children.length > 50) {{
        debugContent.removeChild(debugContent.firstChild);
    }}
}}

toggleDebug.addEventListener("click", function() {{
    let content = document.querySelector("#debug-console .debug-content");
    if (content.classList.contains("hidden")) {{
        content.classList.remove("hidden");
        toggleDebug.textContent = "Hide";
    }} else {{
        content.classList.add("hidden");
        toggleDebug.textContent = "Show";
    }}
}});

function onYouTubeIframeAPIReady() {{
    YT_API_ready = true;
    debug("✅ YouTube API ready - AGGRESSIVE 144p FORCING ACTIVE");
}}

function getRandomStart() {{
    const rand = Math.random();
    
    if (rand < 0.7) {{  // 70% start at beginning
        return 0;
    }} else if (rand < 0.85) {{  // 15% start early (10-30s)
        return Math.floor(Math.random() * 20) + 10;  // 10-30 seconds
    }} else {{  // 15% start mid-video (60-180s)
        return Math.floor(Math.random() * 120) + 60;  // 60-180 seconds
    }}
}}

function getRandomDuration() {{
    return Math.floor(Math.random() * 21) + 36;  // 36-56 seconds
}}

function getRandomPause() {{
    return Math.floor(Math.random() * 5) + 1;  // 1-5 seconds
}}

function destroyVideo(box, player) {{
    debug(`🔥 Removing: ${{box.dataset.video}}`);
    
    // Clear quality forcing interval
    if (qualityIntervals.has(box)) {{
        clearInterval(qualityIntervals.get(box));
        qualityIntervals.delete(box);
    }}
    
    try {{
        if (player && player.stopVideo) player.stopVideo();
        if (player && player.destroy) player.destroy();
    }} catch(e) {{}}
    activePlayers.delete(box);
    box.style.transition = 'opacity 1s';
    box.style.opacity = '0';
    setTimeout(() => {{
        if (box.parentNode) {{
            box.remove();
            debug(`✅ Video removed from grid`);
        }}
    }}, 1000);
}}

function loadPlayer(box) {{
    if(box.classList.contains("loaded") || !YT_API_ready) return;

    // Random thinking delay before clicking play (0.5-3 seconds)
    const thinkingDelay = Math.floor(Math.random() * 2500) + 500;
    
    setTimeout(() => {{
        const vid = box.dataset.video;

        // More natural start distribution
        let start = getRandomStart();

        // Slight variation in watch duration
        const duration = getRandomDuration();
        const end = start + duration;

        box.innerHTML = '';
        box.classList.add("loaded");

        const playerDiv = document.createElement("div");
        box.appendChild(playerDiv);

        debug(`🎬 Loading ${{vid}} | start: ${{start}}s | duration: ${{duration}}s | end: ${{end}}s`);

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
                vq: 'tiny'  // Start with 144p
            }},
            events: {{
                onReady: (event) => {{
                    activePlayers.set(box, event.target);
                    debug(`✅ Player ready: ${{vid}} | will play ${{duration}}s`);
                    event.target.setVolume(100);
                    
                    // AGGRESSIVE QUALITY FORCING - Force 144p every 500ms
                    const qualityInterval = setInterval(() => {{
                        try {{
                            if (event.target && event.target.setPlaybackQuality) {{
                                const currentQuality = event.target.getPlaybackQuality();
                                // Force to 'tiny' (144p) regardless of current quality
                                if (currentQuality !== 'tiny') {{
                                    event.target.setPlaybackQuality('tiny');
                                    debug(`🔒 FORCED 144p for ${{vid}} (was ${{currentQuality}})`);
                                }}
                            }}
                        }} catch(e) {{
                            // Silently fail if quality can't be set
                        }}
                    }}, 500); // Every 500ms for aggressive forcing
                    
                    qualityIntervals.set(box, qualityInterval);
                    
                    event.target.addEventListener('onStateChange', function(e) {{
                        if(e.data == YT.PlayerState.PLAYING) {{
                            debug(`▶️ Playing: ${{vid}} (144p locked, watch time counting)`);
                            
                            // Force 144p immediately when playback starts
                            try {{
                                event.target.setPlaybackQuality('tiny');
                                debug(`🔒 Initial 144p lock for ${{vid}}`);
                            }} catch(e){{}}
                            
                            // Random short pauses during play (max 3 pauses)
                            let remainingTime = duration;
                            let pauseCount = 0;
                            const MAX_PAUSES = 3;
                            
                            const scheduleNextPause = () => {{
                                if (remainingTime <= 0 || pauseCount >= MAX_PAUSES) {{
                                    if (remainingTime > 0) {{
                                        setTimeout(() => {{
                                            debug(`⏹️ Natural end: ${{vid}} after ${{duration}}s`);
                                            event.target.stopVideo();
                                            destroyVideo(box, event.target);
                                        }}, remainingTime * 1000);
                                    }}
                                    return;
                                }}
                                
                                if (remainingTime <= 5) {{
                                    setTimeout(() => {{
                                        debug(`⏹️ End reached: ${{vid}}`);
                                        event.target.stopVideo();
                                        destroyVideo(box, event.target);
                                    }}, remainingTime * 1000);
                                    return;
                                }}
                                
                                const pauseDuration = getRandomPause();
                                const timeUntilPause = Math.floor(Math.random() * 11) + 5;
                                
                                if (timeUntilPause < remainingTime) {{
                                    setTimeout(() => {{
                                        debug(`⏸️ Pausing ${{vid}} for ${{pauseDuration}}s`);
                                        event.target.pauseVideo();
                                        pauseCount++;
                                        
                                        setTimeout(() => {{
                                            debug(`▶️ Resuming ${{vid}}`);
                                            event.target.playVideo();
                                            remainingTime -= (timeUntilPause + pauseDuration);
                                            scheduleNextPause();
                                        }}, pauseDuration * 1000);
                                    }}, timeUntilPause * 1000);
                                }} else {{
                                    setTimeout(() => {{
                                        debug(`⏹️ Ending ${{vid}}`);
                                        event.target.stopVideo();
                                        destroyVideo(box, event.target);
                                    }}, remainingTime * 1000);
                                }}
                            }};
                            
                            scheduleNextPause();
                        }} else if (e.data == YT.PlayerState.BUFFERING) {{
                            debug(`⏳ Buffering ${{vid}} - maintaining 144p`);
                            // Force quality during buffering too
                            try {{
                                event.target.setPlaybackQuality('tiny');
                            }} catch(e){{}}
                        }}
                    }});
                }},
                onError: (err) => {{
                    debug(`❌ Error ${{vid}}: ${{err.data}}`);
                    // Clear interval on error
                    if (qualityIntervals.has(box)) {{
                        clearInterval(qualityIntervals.get(box));
                        qualityIntervals.delete(box);
                    }}
                }}
            }}
        }});
    }}, thinkingDelay);
}}

// Click handler - load and play on click
document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", () => {{
        debug(`👆 Clicked: ${{box.dataset.video}}`);
        loadPlayer(box);
    }});
}});

// Shuffle button
document.getElementById("shuffle-load").onclick = () => {{
    debug(`🔄 Shuffling grid...`);
    let grid = document.getElementById("video-grid");
    let boxes = [...grid.children];

    // Destroy all active players first
    for (let [box, player] of activePlayers) {{
        if (qualityIntervals.has(box)) {{
            clearInterval(qualityIntervals.get(box));
            qualityIntervals.delete(box);
        }}
        try {{
            player.destroy();
        }} catch(e) {{}}
        activePlayers.delete(box);
        box.innerHTML = '';
        const thumbImg = document.createElement('img');
        thumbImg.src = `https://i.ytimg.com/vi_webp/${{VIDEO_ID}}/mqdefault.webp`;
        thumbImg.loading = 'lazy';
        thumbImg.className = 'thumb';
        box.appendChild(thumbImg);
        box.classList.remove('loaded');
        box.style.opacity = '1';
    }}

    // Shuffle grid
    for(let i=boxes.length-1; i>0; i--) {{
        const j = Math.floor(Math.random()*(i+1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }}
    grid.innerHTML = '';
    boxes.forEach(box => grid.appendChild(box));

    // Sequential loading with irregular spacing (1-8 seconds)
    let delay = 0;
    boxes.forEach((box, idx) => {{
        let randomDelay = 1000 + Math.random() * 7000; // 1-8s
        setTimeout(() => {{
            debug(`🔄 Loading #${{idx+1}}: ${{box.dataset.video}}`);
            loadPlayer(box);
        }}, delay);
        delay += randomDelay;
    }});
    debug(`✅ Scheduled ${{boxes.length}} videos over ~${{Math.round(delay/1000)}}s with aggressive 144p forcing`);
}};
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)
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
background:#ff0000;
color:white;
border:none;
border-radius:6px;
}}
button:hover {{
background:#cc0000;
}}
.debug-console {{
position:fixed;
bottom:20px;
right:20px;
background:rgba(0,0,0,0.85);
color:#0f0;
padding:10px;
border-radius:8px;
font-family:monospace;
font-size:11px;
z-index:10001;
max-width:350px;
max-height:250px;
overflow:auto;
}}
.debug-header {{
display:flex;
justify-content:space-between;
margin-bottom:5px;
border-bottom:1px solid #0f0;
}}
.debug-content {{
font-size:10px;
}}
.hidden {{
display:none;
}}
</style>

<button id="shuffle-load">🔀 Shuffle + Load Players</button>

<div id="video-grid">
{''.join(html_blocks)}
</div>

<div class="debug-console" id="debug-console">
    <div class="debug-header">
        <span>📊 Playback Monitor - AGGRESSIVE 144p MODE</span>
        <button id="toggle-debug">Hide</button>
    </div>
    <div class="debug-content" id="debug-content"></div>
</div>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
let YT_API_ready = false;
let activePlayers = new Map();
let qualityIntervals = new Map();
let debugContent = document.getElementById("debug-content");
let toggleDebug = document.getElementById("toggle-debug");
let debugConsole = document.getElementById("debug-console");

function debug(msg) {{
    console.log(msg);
    let timeStr = new Date().toLocaleTimeString();
    let logDiv = document.createElement('div');
    logDiv.textContent = timeStr + ': ' + msg;
    debugContent.appendChild(logDiv);
    debugContent.scrollTop = debugContent.scrollHeight;
    while(debugContent.children.length > 50) {{
        debugContent.removeChild(debugContent.firstChild);
    }}
}}

toggleDebug.addEventListener("click", function() {{
    let content = document.querySelector("#debug-console .debug-content");
    if (content.classList.contains("hidden")) {{
        content.classList.remove("hidden");
        toggleDebug.textContent = "Hide";
    }} else {{
        content.classList.add("hidden");
        toggleDebug.textContent = "Show";
    }}
}});

function onYouTubeIframeAPIReady() {{
    YT_API_ready = true;
    debug("✅ YouTube API ready - AGGRESSIVE 144p FORCING ACTIVE");
}}

function getRandomStart() {{
    const rand = Math.random();
    
    if (rand < 0.7) {{  // 70% start at beginning
        return 0;
    }} else if (rand < 0.85) {{  // 15% start early (10-30s)
        return Math.floor(Math.random() * 20) + 10;  // 10-30 seconds
    }} else {{  // 15% start mid-video (60-180s)
        return Math.floor(Math.random() * 120) + 60;  // 60-180 seconds
    }}
}}

function getRandomDuration() {{
    return Math.floor(Math.random() * 21) + 36;  // 36-56 seconds
}}

function getRandomPause() {{
    return Math.floor(Math.random() * 5) + 1;  // 1-5 seconds
}}

function destroyVideo(box, player) {{
    debug(`🔥 Removing: ${{box.dataset.video}}`);
    
    // Clear quality forcing interval
    if (qualityIntervals.has(box)) {{
        clearInterval(qualityIntervals.get(box));
        qualityIntervals.delete(box);
    }}
    
    try {{
        if (player && player.stopVideo) player.stopVideo();
        if (player && player.destroy) player.destroy();
    }} catch(e) {{}}
    activePlayers.delete(box);
    box.style.transition = 'opacity 1s';
    box.style.opacity = '0';
    setTimeout(() => {{
        if (box.parentNode) {{
            box.remove();
            debug(`✅ Video removed from grid`);
        }}
    }}, 1000);
}}

function loadPlayer(box) {{
    if(box.classList.contains("loaded") || !YT_API_ready) return;

    // Random thinking delay before clicking play (0.5-3 seconds)
    const thinkingDelay = Math.floor(Math.random() * 2500) + 500;
    
    setTimeout(() => {{
        const vid = box.dataset.video;

        // More natural start distribution
        let start = getRandomStart();

        // Slight variation in watch duration
        const duration = getRandomDuration();
        const end = start + duration;

        box.innerHTML = '';
        box.classList.add("loaded");

        const playerDiv = document.createElement("div");
        box.appendChild(playerDiv);

        debug(`🎬 Loading ${{vid}} | start: ${{start}}s | duration: ${{duration}}s | end: ${{end}}s`);

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
                vq: 'tiny'  // Start with 144p
            }},
            events: {{
                onReady: (event) => {{
                    activePlayers.set(box, event.target);
                    debug(`✅ Player ready: ${{vid}} | will play ${{duration}}s`);
                    event.target.setVolume(100);
                    
                    // AGGRESSIVE QUALITY FORCING - Force 144p every 500ms
                    const qualityInterval = setInterval(() => {{
                        try {{
                            if (event.target && event.target.setPlaybackQuality) {{
                                const currentQuality = event.target.getPlaybackQuality();
                                // Force to 'tiny' (144p) regardless of current quality
                                if (currentQuality !== 'tiny') {{
                                    event.target.setPlaybackQuality('tiny');
                                    debug(`🔒 FORCED 144p for ${{vid}} (was ${{currentQuality}})`);
                                }}
                            }}
                        }} catch(e) {{
                            // Silently fail if quality can't be set
                        }}
                    }}, 500); // Every 500ms for aggressive forcing
                    
                    qualityIntervals.set(box, qualityInterval);
                    
                    event.target.addEventListener('onStateChange', function(e) {{
                        if(e.data == YT.PlayerState.PLAYING) {{
                            debug(`▶️ Playing: ${{vid}} (144p locked, watch time counting)`);
                            
                            // Force 144p immediately when playback starts
                            try {{
                                event.target.setPlaybackQuality('tiny');
                                debug(`🔒 Initial 144p lock for ${{vid}}`);
                            }} catch(e){{}}
                            
                            // Random short pauses during play (max 3 pauses)
                            let remainingTime = duration;
                            let pauseCount = 0;
                            const MAX_PAUSES = 3;
                            
                            const scheduleNextPause = () => {{
                                if (remainingTime <= 0 || pauseCount >= MAX_PAUSES) {{
                                    if (remainingTime > 0) {{
                                        setTimeout(() => {{
                                            debug(`⏹️ Natural end: ${{vid}} after ${{duration}}s`);
                                            event.target.stopVideo();
                                            destroyVideo(box, event.target);
                                        }}, remainingTime * 1000);
                                    }}
                                    return;
                                }}
                                
                                if (remainingTime <= 5) {{
                                    setTimeout(() => {{
                                        debug(`⏹️ End reached: ${{vid}}`);
                                        event.target.stopVideo();
                                        destroyVideo(box, event.target);
                                    }}, remainingTime * 1000);
                                    return;
                                }}
                                
                                const pauseDuration = getRandomPause();
                                const timeUntilPause = Math.floor(Math.random() * 11) + 5;
                                
                                if (timeUntilPause < remainingTime) {{
                                    setTimeout(() => {{
                                        debug(`⏸️ Pausing ${{vid}} for ${{pauseDuration}}s`);
                                        event.target.pauseVideo();
                                        pauseCount++;
                                        
                                        setTimeout(() => {{
                                            debug(`▶️ Resuming ${{vid}}`);
                                            event.target.playVideo();
                                            remainingTime -= (timeUntilPause + pauseDuration);
                                            scheduleNextPause();
                                        }}, pauseDuration * 1000);
                                    }}, timeUntilPause * 1000);
                                }} else {{
                                    setTimeout(() => {{
                                        debug(`⏹️ Ending ${{vid}}`);
                                        event.target.stopVideo();
                                        destroyVideo(box, event.target);
                                    }}, remainingTime * 1000);
                                }}
                            }};
                            
                            scheduleNextPause();
                        }} else if (e.data == YT.PlayerState.BUFFERING) {{
                            debug(`⏳ Buffering ${{vid}} - maintaining 144p`);
                            // Force quality during buffering too
                            try {{
                                event.target.setPlaybackQuality('tiny');
                            }} catch(e){{}}
                        }}
                    }});
                }},
                onError: (err) => {{
                    debug(`❌ Error ${{vid}}: ${{err.data}}`);
                    // Clear interval on error
                    if (qualityIntervals.has(box)) {{
                        clearInterval(qualityIntervals.get(box));
                        qualityIntervals.delete(box);
                    }}
                }}
            }}
        }});
    }}, thinkingDelay);
}}

// Click handler - load and play on click
document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", () => {{
        debug(`👆 Clicked: ${{box.dataset.video}}`);
        loadPlayer(box);
    }});
}});

// Shuffle button
document.getElementById("shuffle-load").onclick = () => {{
    debug(`🔄 Shuffling grid...`);
    let grid = document.getElementById("video-grid");
    let boxes = [...grid.children];

    // Destroy all active players first
    for (let [box, player] of activePlayers) {{
        if (qualityIntervals.has(box)) {{
            clearInterval(qualityIntervals.get(box));
            qualityIntervals.delete(box);
        }}
        try {{
            player.destroy();
        }} catch(e) {{}}
        activePlayers.delete(box);
        box.innerHTML = '';
        const thumbImg = document.createElement('img');
        thumbImg.src = `https://i.ytimg.com/vi_webp/${{VIDEO_ID}}/mqdefault.webp`;
        thumbImg.loading = 'lazy';
        thumbImg.className = 'thumb';
        box.appendChild(thumbImg);
        box.classList.remove('loaded');
        box.style.opacity = '1';
    }}

    // Shuffle grid
    for(let i=boxes.length-1; i>0; i--) {{
        const j = Math.floor(Math.random()*(i+1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }}
    grid.innerHTML = '';
    boxes.forEach(box => grid.appendChild(box));

    // Sequential loading with irregular spacing (1-8 seconds)
    let delay = 0;
    boxes.forEach((box, idx) => {{
        let randomDelay = 1000 + Math.random() * 7000; // 1-8s
        setTimeout(() => {{
            debug(`🔄 Loading #${{idx+1}}: ${{box.dataset.video}}`);
            loadPlayer(box);
        }}, delay);
        delay += randomDelay;
    }});
    debug(`✅ Scheduled ${{boxes.length}} videos over ~${{Math.round(delay/1000)}}s with aggressive 144p forcing`);
}};
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)