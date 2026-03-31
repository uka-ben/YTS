import streamlit as st

st.set_page_config(layout="wide", page_title="YouTube Grid - Data Saver Mode")

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
        transition: opacity 0.3s ease, transform 0.1s;
        background: #111;
        border-radius: 8px;
        overflow: hidden;
    }}
    .video-box:hover {{
        transform: scale(1.02);
    }}
    .thumb {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 8px;
    }}
    iframe, .yt-player {{
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
        transform: scale(0.98);
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
        background: rgba(0,0,0,0.9);
        color: #0f0;
        padding: 10px;
        border-radius: 12px;
        font-family: monospace;
        font-size: 11px;
        z-index: 10001;
        width: 360px;
        border-left: 3px solid #ff0000;
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
        max-height: 200px;
        overflow-y: auto;
        line-height: 1.4;
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
    @media (max-width: 600px) {{
        .debug-console {{ width: 260px; font-size: 9px; }}
        button {{ padding: 6px 16px; font-size: 13px; }}
    }}
</style>

<div class="button-container">
    <button id="shuffle-load">🔀 Shuffle + Load Players (Data Saver)</button>
    <span class="loading-status" id="loading-status">📦 0/50 loaded</span>
    <div class="loading-bar">
        <div class="loading-progress" id="loading-progress"></div>
    </div>
    <div class="data-warning">⚠️ Buffering capped at 36-50s | 144p quality | Data saver ON</div>
</div>

<div id="video-grid">
{''.join(html_blocks)}
</div>

<div class="debug-console" id="debug-console">
    <div class="debug-header">
        <span>📡 STRICT BUFFER MODE | Watch time counts</span>
        <button id="toggle-debug">Hide</button>
    </div>
    <div class="debug-content" id="debug-content"></div>
</div>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
    const TOTAL_VIDEOS = 50;
    let YT_API_ready = false;
    let loadedPlayers = new Map();
    let playerIntervals = new Map();
    let debugConsole = document.getElementById("debug-console");
    let debugContent = document.getElementById("debug-content");
    let toggleDebug = document.getElementById("toggle-debug");
    let gridContainer = document.getElementById("video-grid");
    
    function debug(msg) {{
        console.log(msg);
        let timeStr = new Date().toLocaleTimeString();
        let logDiv = document.createElement('div');
        logDiv.textContent = timeStr + ': ' + msg;
        debugContent.appendChild(logDiv);
        debugContent.scrollTop = debugContent.scrollHeight;
        while(debugContent.children.length > 100) {{
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
        try {{
            if (player.stopVideo) player.stopVideo();
            if (player.destroy) player.destroy();
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
            debug(`▶️ PLAYING video: ${{box.dataset.video}} (watch time will count)`);
            player.setVolume(100);
            player.playVideo();
            box.style.transform = 'scale(0.97)';
            setTimeout(() => {{ if(box) box.style.transform = 'scale(1)'; }}, 120);
        }} else {{
            debug(`⚠️ Cannot play: player not ready`);
        }}
    }}
    
    function getRandomDuration() {{
        return Math.floor(Math.random() * (50 - 36 + 1)) + 36;
    }}
    
    function loadPlayer(box, autoPlay = false) {{
        if (box.classList.contains("loaded") || !YT_API_ready) return;
        
        const vid = box.dataset.video;
        const durationSec = getRandomDuration();
        const endSec = durationSec;
        
        debug(`⏳ Loading player for ${{vid}} | duration cap: ${{durationSec}}s (NO extra buffering)`);
        
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
                end: endSec,
                vq: 'tiny',
                iv_load_policy: 3
            }},
            events: {{
                onReady: (event) => {{
                    loadedPlayers.set(box, event.target);
                    updateLoadingProgress();
                    debug(`✅ Player READY: ${{vid}} | duration limit = ${{durationSec}}s | quality 144p`);
                    event.target.setVolume(100);
                    
                    const qualityInterval = setInterval(() => {{
                        try {{
                            if (event.target && event.target.setPlaybackQuality) {{
                                event.target.setPlaybackQuality('tiny');
                            }}
                        }} catch(e) {{}}
                    }}, 2000);
                    playerIntervals.set(box, qualityInterval);
                    
                    if (autoPlay) {{
                        debug(`▶️ AUTO-PLAY after click for ${{vid}}`);
                        event.target.playVideo();
                    }}
                    
                    event.target.addEventListener('onStateChange', function(stateEvent) {{
                        const state = stateEvent.data;
                        if (state === YT.PlayerState.ENDED) {{
                            debug(`⏹️ VIDEO ENDED (duration reached: ${{durationSec}}s) -> destroying player: ${{vid}}`);
                            const currentPlayer = loadedPlayers.get(box);
                            if (currentPlayer) destroyVideo(box, currentPlayer);
                        }} else if (state === YT.PlayerState.PLAYING) {{
                            debug(`▶️ PLAYBACK STARTED: ${{vid}} | watch minutes counting`);
                            try {{
                                event.target.setPlaybackQuality('tiny');
                            }} catch(e) {{}}
                        }}
                    }});
                }},
                onError: (err) => {{
                    debug(`❌ Player error for ${{vid}}: ${{err.data}}`);
                }}
            }}
        }});
    }}
    
    function shuffleAndLoad() {{
        debug(`🔄 SHUFFLE + LOAD (data-saver mode) - destroying all current players`);
        
        for (let [box, player] of loadedPlayers.entries()) {{
            if (playerIntervals.has(box)) {{
                clearInterval(playerIntervals.get(box));
                playerIntervals.delete(box);
            }}
            try {{
                if(player.stopVideo) player.stopVideo();
                if(player.destroy) player.destroy();
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
            const staggerInterval = 1000 + Math.random() * 11000;
            setTimeout(() => {{
                if (YT_API_ready && !box.classList.contains('loaded')) {{
                    loadPlayer(box, false);
                    debug(`🔄 Staggered load #${{idx+1}}: ${{box.dataset.video}}`);
                }}
            }}, currentDelay);
            currentDelay += staggerInterval;
        }});
        debug(`✅ Shuffle complete: ${{boxes.length}} videos loading with ${{Math.round(currentDelay/1000)}}s staggered delay`);
    }}
    
    document.querySelectorAll(".video-box").forEach(box => {{
        box.addEventListener("click", function(e) {{
            e.stopPropagation();
            debug(`👆 Click on video: ${{this.dataset.video}}`);
            if (this.classList.contains("loaded")) {{
                playVideo(this);
            }} else {{
                if (!YT_API_ready) {{
                    debug(`API not ready yet`);
                    return;
                }}
                loadPlayer(this, true);
            }}
        }});
    }});
    
    document.getElementById("shuffle-load").onclick = function() {{
        if (YT_API_ready) {{
            shuffleAndLoad();
        }} else {{
            debug("API not ready, please wait...");
        }}
    }};
    
    function onYouTubeIframeAPIReady() {{
        YT_API_ready = true;
        debug("🎬 YouTube API ready — STRICT DATA SAVER MODE ACTIVE");
        debug("💡 Each video capped at 36-50 seconds | 144p quality | No extra buffering");
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