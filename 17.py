import streamlit as st

st.set_page_config(layout="wide", page_title="YouTube Grid - Zero Excess Buffering")

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
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
<style>
    * {{
        box-sizing: border-box;
    }}
    #video-grid {{
        background: #000;
        padding: 20px;
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 12px;
        position: relative;
    }}
    .video-box {{
        cursor: pointer;
        aspect-ratio: 16/9;
        position: relative;
        background: #111;
        border-radius: 8px;
        overflow: hidden;
    }}
    .thumb {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 8px;
    }}
    iframe {{
        width: 100%;
        height: 100%;
        border: none;
        border-radius: 8px;
    }}
    .button-container {{
        display: flex;
        gap: 16px;
        margin-bottom: 20px;
        align-items: center;
        flex-wrap: wrap;
        background: #0f0f0f;
        padding: 12px 16px;
        border-radius: 40px;
    }}
    button {{
        background: #ff0000;
        border: none;
        color: white;
        padding: 8px 24px;
        font-size: 15px;
        font-weight: 600;
        border-radius: 40px;
        cursor: pointer;
    }}
    button:hover {{
        background: #cc0000;
    }}
    .loading-status {{
        color: #ddd;
        font-size: 14px;
        background: #2a2a2a;
        padding: 6px 14px;
        border-radius: 30px;
        font-family: monospace;
    }}
    .loading-bar {{
        width: 240px;
        height: 8px;
        background: #333;
        border-radius: 10px;
        overflow: hidden;
    }}
    .loading-progress {{
        height: 100%;
        background: #ff0000;
        width: 0%;
        transition: width 0.2s ease;
    }}
    .debug-console {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(0,0,0,0.95);
        color: #0f0;
        padding: 10px;
        border-radius: 12px;
        font-family: monospace;
        font-size: 10px;
        z-index: 10001;
        width: 400px;
        max-height: 300px;
        overflow: auto;
    }}
    .debug-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
        padding-bottom: 4px;
        border-bottom: 1px solid #0f0;
    }}
    .debug-header button {{
        background: #222;
        color: #0f0;
        padding: 2px 10px;
        font-size: 10px;
        border: 1px solid #0f0;
        border-radius: 20px;
    }}
    .debug-content {{
        max-height: 250px;
        overflow-y: auto;
        font-size: 9px;
        line-height: 1.3;
    }}
    .hidden {{
        display: none !important;
    }}
    .data-warning {{
        background: #2a1e1e;
        border-left: 4px solid #ff4444;
        padding: 6px 12px;
        font-size: 12px;
        color: #ff9999;
        border-radius: 20px;
    }}
</style>

<div class="button-container">
    <button id="shuffle-load">🔀 Shuffle + Load (ZERO Buffer)</button>
    <span class="loading-status" id="loading-status">📦 0/50 loaded</span>
    <div class="loading-bar">
        <div class="loading-progress" id="loading-progress"></div>
    </div>
    <div class="data-warning">⚠️ STRICT MODE: Videos DESTROYED at {36-50}s - NO background buffering</div>
</div>

<div id="video-grid">
{''.join(html_blocks)}
</div>

<div class="debug-console" id="debug-console">
    <div class="debug-header">
        <span>🔴 ZERO BUFFER MODE - Active</span>
        <button id="toggle-debug">Hide</button>
    </div>
    <div class="debug-content" id="debug-content"></div>
</div>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
    const TOTAL_VIDEOS = 50;
    const VIDEO_ID = "{video_id}";
    let YT_API_ready = false;
    let loadedPlayers = new Map();
    let debugContent = document.getElementById("debug-content");
    let toggleDebug = document.getElementById("toggle-debug");
    let gridContainer = document.getElementById("video-grid");
    let activePlayTimers = new Map();
    
    function debug(msg) {{
        console.log(msg);
        let timeStr = new Date().toLocaleTimeString();
        let logDiv = document.createElement('div');
        logDiv.style.color = '#88ff88';
        logDiv.textContent = timeStr + ': ' + msg;
        debugContent.appendChild(logDiv);
        debugContent.scrollTop = debugContent.scrollHeight;
        while(debugContent.children.length > 80) {{
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
    
    function updateLoadingProgress() {{
        let loadedCount = document.querySelectorAll(".video-box.loaded").length;
        let statusSpan = document.getElementById("loading-status");
        let progressFill = document.getElementById("loading-progress");
        statusSpan.textContent = "📦 " + loadedCount + "/" + TOTAL_VIDEOS + " loaded";
        let percent = (loadedCount / TOTAL_VIDEOS) * 100;
        progressFill.style.width = percent + "%";
    }}
    
    // FORCE STOP - completely destroys player to stop all buffering
    function forceStopAndDestroy(box, player, reason) {{
        debug("💀 FORCE STOP: " + box.dataset.video + " | Reason: " + reason);
        
        if (activePlayTimers.has(box)) {{
            clearTimeout(activePlayTimers.get(box));
            activePlayTimers.delete(box);
        }}
        
        try {{
            if (player && player.stopVideo) player.stopVideo();
            if (player && player.destroy) player.destroy();
        }} catch(e) {{}}
        
        loadedPlayers.delete(box);
        
        // Restore thumbnail
        box.innerHTML = '';
        const thumbImg = document.createElement('img');
        thumbImg.src = "https://i.ytimg.com/vi_webp/" + VIDEO_ID + "/mqdefault.webp";
        thumbImg.loading = 'lazy';
        thumbImg.className = 'thumb';
        box.appendChild(thumbImg);
        box.classList.remove('loaded');
        box.style.opacity = '1';
        updateLoadingProgress();
        
        debug("✅ Video destroyed - no more buffering possible");
    }}
    
    function getRandomDuration() {{
        return Math.floor(Math.random() * (50 - 36 + 1)) + 36;
    }}
    
    function playWithTimeout(box, player, durationSeconds) {{
        debug("▶️ Playing: " + box.dataset.video + " for " + durationSeconds + " seconds");
        player.setVolume(100);
        player.playVideo();
        
        // CRITICAL: Set a timer to destroy the video EXACTLY at duration
        const timer = setTimeout(() => {{
            debug("⏰ TIME'S UP! Destroying video after " + durationSeconds + "s: " + box.dataset.video);
            if (loadedPlayers.get(box) === player) {{
                forceStopAndDestroy(box, player, "duration reached");
            }}
        }}, durationSeconds * 1000);
        
        activePlayTimers.set(box, timer);
        
        // Also monitor state changes to catch ENDED event early
        const stateHandler = function(stateEvent) {{
            if (stateEvent.data === 0) {{ // ENDED
                debug("⏹️ Video ended naturally: " + box.dataset.video);
                if (activePlayTimers.has(box)) {{
                    clearTimeout(activePlayTimers.get(box));
                    activePlayTimers.delete(box);
                }}
                forceStopAndDestroy(box, player, "video ended");
                player.removeEventListener('onStateChange', stateHandler);
            }}
        }};
        player.addEventListener('onStateChange', stateHandler);
    }}
    
    function loadPlayer(box, autoPlay = false) {{
        if (box.classList.contains("loaded") || !YT_API_ready) return;
        
        const vid = box.dataset.video;
        const durationSec = getRandomDuration();
        
        debug("⏳ Loading player for: " + vid + " (will play max " + durationSec + "s)");
        
        box.innerHTML = '';
        const playerDiv = document.createElement("div");
        playerDiv.style.width = "100%";
        playerDiv.style.height = "100%";
        box.appendChild(playerDiv);
        box.classList.add("loaded");
        
        // Use minimal buffer by setting low quality and no extra features
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
                iv_load_policy: 3,
                enablejsapi: 1
            }},
            events: {{
                onReady: (event) => {{
                    loadedPlayers.set(box, event.target);
                    updateLoadingProgress();
                    debug("✅ Player ready: " + vid + " | 144p quality");
                    event.target.setVolume(100);
                    
                    // Force lowest quality immediately
                    try {{
                        event.target.setPlaybackQuality('tiny');
                    }} catch(e) {{}}
                    
                    if (autoPlay) {{
                        playWithTimeout(box, event.target, durationSec);
                    }}
                }},
                onError: (err) => {{
                    debug("❌ Error: " + vid + " - " + err.data);
                    box.classList.remove('loaded');
                    updateLoadingProgress();
                }}
            }}
        }});
    }}
    
    function shuffleAndLoad() {{
        debug("🔄 SHUFFLE MODE - Destroying ALL active players to stop buffering");
        
        // Kill all active videos immediately
        for (let [box, player] of loadedPlayers.entries()) {{
            if (activePlayTimers.has(box)) {{
                clearTimeout(activePlayTimers.get(box));
                activePlayTimers.delete(box);
            }}
            try {{
                if(player) {{
                    player.stopVideo();
                    player.destroy();
                }}
            }} catch(e) {{}}
            loadedPlayers.delete(box);
            box.innerHTML = '';
            const thumbImg = document.createElement('img');
            thumbImg.src = "https://i.ytimg.com/vi_webp/" + VIDEO_ID + "/mqdefault.webp";
            thumbImg.loading = 'lazy';
            thumbImg.className = 'thumb';
            box.appendChild(thumbImg);
            box.classList.remove('loaded');
            box.style.opacity = '1';
        }}
        
        // Shuffle grid
        let boxes = [...gridContainer.children];
        for(let i = boxes.length - 1; i > 0; i--) {{
            const j = Math.floor(Math.random() * (i + 1));
            [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
        }}
        gridContainer.innerHTML = '';
        boxes.forEach(b => gridContainer.appendChild(b));
        updateLoadingProgress();
        
        debug("✅ Grid shuffled. Click any video to play (will stop after 36-50s)");
    }}
    
    // Click handler - load and play with hard timeout
    document.querySelectorAll(".video-box").forEach(box => {{
        box.addEventListener("click", function(e) {{
            e.stopPropagation();
            debug("👆 CLICK: " + this.dataset.video);
            
            // If already loaded and playing, don't do anything
            if (this.classList.contains("loaded") && loadedPlayers.has(this)) {{
                const player = loadedPlayers.get(this);
                if (player && player.getPlayerState && player.getPlayerState() === 1) {{
                    debug("Video already playing: " + this.dataset.video);
                    return;
                }}
            }}
            
            if (!YT_API_ready) {{
                debug("⏳ YouTube API not ready");
                return;
            }}
            
            // Load and auto-play
            loadPlayer(this, true);
        }});
    }});
    
    document.getElementById("shuffle-load").onclick = () => {{
        if (YT_API_ready) shuffleAndLoad();
        else debug("Waiting for YouTube API...");
    }};
    
    function onYouTubeIframeAPIReady() {{
        YT_API_ready = true;
        debug("🎬 YouTube API READY - ZERO BUFFER MODE ACTIVE");
        debug("⚡ CRITICAL: Videos will be DESTROYED after 36-50 seconds");
        debug("⚡ NO background buffering - each video stops exactly at limit");
        debug("💡 Click any video to play - it will self-destruct after duration");
        updateLoadingProgress();
    }}
    
    window.onYouTubeIframeAPIReady = onYouTubeIframeAPIReady;
    
    if (typeof YT !== 'undefined' && YT.loaded) {{
        onYouTubeIframeAPIReady();
    }}
</script>
</body>
</html>
"""

st.components.v1.html(html, height=900, scrolling=True)