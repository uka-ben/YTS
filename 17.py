import streamlit as st

st.set_page_config(layout="wide", page_title="YouTube Grid - No Buffer Mode")

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
        transition: opacity 0.3s ease;
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
        transition: 0.2s;
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
        width: 380px;
        border-left: 3px solid #ff0000;
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
        background: #1e2a1e;
        border-left: 4px solid #ffaa00;
        padding: 6px 12px;
        font-size: 12px;
        color: #ffdd99;
        border-radius: 20px;
    }}
</style>

<div class="button-container">
    <button id="shuffle-load">🔀 Shuffle + Load (NO Buffer Mode)</button>
    <span class="loading-status" id="loading-status">📦 0/50 loaded</span>
    <div class="loading-bar">
        <div class="loading-progress" id="loading-progress"></div>
    </div>
    <div class="data-warning">⚡ NO BUFFERING: Videos stop after 36-50s | 144p | Data saver</div>
</div>

<div id="video-grid">
{''.join(html_blocks)}
</div>

<div class="debug-console" id="debug-console">
    <div class="debug-header">
        <span>🔴 AGGRESSIVE BUFFER CONTROL ACTIVE</span>
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
    let playerIntervals = new Map();
    let bufferMonitors = new Map();
    let debugContent = document.getElementById("debug-content");
    let toggleDebug = document.getElementById("toggle-debug");
    let gridContainer = document.getElementById("video-grid");
    
    function debug(msg, isError = false) {{
        console.log(msg);
        let timeStr = new Date().toLocaleTimeString();
        let logDiv = document.createElement('div');
        logDiv.style.color = isError ? '#ff8888' : '#88ff88';
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
        statusSpan.textContent = `📦 ${{loadedCount}}/${{TOTAL_VIDEOS}} loaded`;
        let percent = (loadedCount / TOTAL_VIDEOS) * 100;
        progressFill.style.width = percent + "%";
    }}
    
    function destroyVideo(box, player) {{
        debug(`🔥 DESTROYING video: ${{box.dataset.video}}`);
        if (playerIntervals.has(box)) {{
            clearInterval(playerIntervals.get(box));
            playerIntervals.delete(box);
        }}
        if (bufferMonitors.has(box)) {{
            clearInterval(bufferMonitors.get(box));
            bufferMonitors.delete(box);
        }}
        try {{
            if (player && player.stopVideo) player.stopVideo();
            if (player && player.destroy) player.destroy();
        }} catch(e) {{}}
        loadedPlayers.delete(box);
        box.style.transition = 'opacity 0.5s ease';
        box.style.opacity = '0';
        setTimeout(() => {{
            if (box.parentNode) {{
                box.remove();
                updateLoadingProgress();
                debug(`✅ Video removed from grid`);
            }}
        }}, 500);
    }}
    
    function playVideo(box) {{
        const player = loadedPlayers.get(box);
        if (player && typeof player.playVideo === 'function') {{
            debug(`▶️ PLAYING: ${{box.dataset.video}} (watch time counts)`);
            player.setVolume(100);
            player.playVideo();
        }}
    }}
    
    function getRandomDuration() {{
        return Math.floor(Math.random() * (50 - 36 + 1)) + 36;
    }}
    
    function loadPlayer(box, autoPlay = false) {{
        if (box.classList.contains("loaded") || !YT_API_ready) return;
        
        const vid = box.dataset.video;
        const durationSec = getRandomDuration();
        
        debug(`⏳ Loading ${{vid}} | duration: ${{durationSec}}s | NO PRE-BUFFER`);
        
        box.innerHTML = '';
        const playerDiv = document.createElement("div");
        playerDiv.style.width = "100%";
        playerDiv.style.height = "100%";
        box.appendChild(playerDiv);
        box.classList.add("loaded");
        
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
                start: 0,
                end: durationSec,
                vq: 'tiny',
                iv_load_policy: 3,
                enablejsapi: 1
            }},
            events: {{
                onReady: (event) => {{
                    loadedPlayers.set(box, event.target);
                    updateLoadingProgress();
                    debug(`✅ READY: ${{vid}} | ${{durationSec}}s limit | 144p quality`);
                    event.target.setVolume(100);
                    
                    const qualityInterval = setInterval(() => {{
                        try {{
                            if (event.target && event.target.setPlaybackQuality) {{
                                event.target.setPlaybackQuality('tiny');
                            }}
                        }} catch(e) {{}}
                    }}, 1000);
                    playerIntervals.set(box, qualityInterval);
                    
                    const bufferMonitor = setInterval(() => {{
                        try {{
                            let state = event.target.getPlayerState();
                            if (state === 3) {{
                                debug(`🔴 BUFFER DETECTED on ${{vid}} - KILLING IT`);
                                event.target.pauseVideo();
                                setTimeout(() => {{
                                    if (event.target && event.target.getPlayerState() === 3) {{
                                        event.target.stopVideo();
                                        debug(`💀 Force stopped buffering on ${{vid}}`);
                                    }}
                                }}, 100);
                            }}
                        }} catch(e) {{}}
                    }}, 500);
                    bufferMonitors.set(box, bufferMonitor);
                    
                    if (autoPlay) {{
                        setTimeout(() => {{
                            debug(`🎬 AUTO-PLAY: ${{vid}}`);
                            event.target.playVideo();
                        }}, 100);
                    }}
                    
                    event.target.addEventListener('onStateChange', function(stateEvent) {{
                        const state = stateEvent.data;
                        if (state === 0) {{
                            debug(`⏹️ ENDED (${{durationSec}}s reached): ${{vid}} -> destroying`);
                            const currentPlayer = loadedPlayers.get(box);
                            if (currentPlayer) destroyVideo(box, currentPlayer);
                        }} else if (state === 1) {{
                            debug(`🎥 PLAYING: ${{vid}} | Watch time counting`);
                            try {{
                                event.target.setPlaybackQuality('tiny');
                            }} catch(e) {{}}
                        }}
                    }});
                }},
                onError: (err) => {{
                    debug(`❌ ERROR ${{vid}}: ${{err.data}}`, true);
                }}
            }}
        }});
    }}
    
    function shuffleAndLoad() {{
        debug(`🔄 SHUFFLE MODE - Destroying all players to stop buffering`);
        
        for (let [box, player] of loadedPlayers.entries()) {{
            if (playerIntervals.has(box)) {{
                clearInterval(playerIntervals.get(box));
                playerIntervals.delete(box);
            }}
            if (bufferMonitors.has(box)) {{
                clearInterval(bufferMonitors.get(box));
                bufferMonitors.delete(box);
            }}
            try {{
                if(player) player.destroy();
            }} catch(e) {{}}
            loadedPlayers.delete(box);
            box.innerHTML = '';
            const thumbImg = document.createElement('img');
            thumbImg.src = `https://i.ytimg.com/vi_webp/${{VIDEO_ID}}/mqdefault.webp`;
            thumbImg.loading = 'lazy';
            thumbImg.className = 'thumb';
            box.appendChild(thumbImg);
            box.classList.remove('loaded');
            box.style.opacity = '1';
        }}
        
        let boxes = [...gridContainer.children];
        for(let i = boxes.length - 1; i > 0; i--) {{
            const j = Math.floor(Math.random() * (i + 1));
            [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
        }}
        gridContainer.innerHTML = '';
        boxes.forEach(b => gridContainer.appendChild(b));
        updateLoadingProgress();
        
        let currentDelay = 0;
        boxes.forEach((box, idx) => {{
            const staggerDelay = 800 + Math.random() * 8000;
            setTimeout(() => {{
                if (YT_API_ready && !box.classList.contains('loaded')) {{
                    loadPlayer(box, false);
                    debug(`🔄 Loaded #${{idx+1}}: ${{box.dataset.video}}`);
                }}
            }}, currentDelay);
            currentDelay += staggerDelay;
        }});
        debug(`✅ Shuffled ${{boxes.length}} videos | No pre-buffering | Click to play`);
    }}
    
    document.querySelectorAll(".video-box").forEach(box => {{
        box.addEventListener("click", function(e) {{
            e.stopPropagation();
            debug(`👆 CLICK: ${{this.dataset.video}}`);
            if (this.classList.contains("loaded")) {{
                playVideo(this);
            }} else {{
                if (!YT_API_ready) {{
                    debug(`API not ready`);
                    return;
                }}
                loadPlayer(this, true);
            }}
        }});
    }});
    
    document.getElementById("shuffle-load").onclick = () => {{
        if (YT_API_ready) shuffleAndLoad();
        else debug("Waiting for YouTube API...");
    }};
    
    function onYouTubeIframeAPIReady() {{
        YT_API_ready = true;
        debug("🎬 YouTube API READY | AGGRESSIVE BUFFER CONTROL ENABLED");
        debug("⚡ Videos capped at 36-50s | 144p | Buffer killing active");
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