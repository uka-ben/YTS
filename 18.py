import streamlit as st

st.set_page_config(layout="wide", page_title="YouTube Player - Smart Buffer Control")

video_id = "LxTZnjraVrM"

html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
<style>
    .video-container {{
        background: #000;
        padding: 20px;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
    }}
    .video-box {{
        cursor: pointer;
        width: 100%;
        max-width: 800px;
        aspect-ratio: 16/9;
        position: relative;
        background: #111;
        border-radius: 8px;
        overflow: hidden;
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
        position: fixed;
        top: 20px;
        left: 20px;
        right: 20px;
        z-index: 100;
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
    <button id="reload-player">🔄 Reload Player</button>
    <span class="loading-status" id="loading-status">📦 Player ready</span>
    <div class="data-warning">⚡ Smart buffering: Only loads up to 50s | 144p | Data saver</div>
</div>

<div class="video-container">
    <div class="video-box" id="video-box" data-video="{video_id}">
    </div>
</div>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
    const VIDEO_ID = "{video_id}";
    let YT_API_ready = false;
    let currentPlayer = null;
    let qualityInterval = null;
    let videoBox = document.getElementById("video-box");
    
    function updateLoadingStatus() {{
        let statusSpan = document.getElementById("loading-status");
        if (currentPlayer && currentPlayer.getPlayerState) {{
            statusSpan.textContent = "📦 Player loaded";
        }} else {{
            statusSpan.textContent = "📦 Player ready";
        }}
    }}
    
    function destroyVideo() {{
        if (qualityInterval) {{
            clearInterval(qualityInterval);
            qualityInterval = null;
        }}
        if (currentPlayer) {{
            try {{
                if (currentPlayer.stopVideo) currentPlayer.stopVideo();
                if (currentPlayer.destroy) currentPlayer.destroy();
            }} catch(e) {{}}
            currentPlayer = null;
        }}
    }}
    
    function getRandomDuration() {{
        return Math.floor(Math.random() * (50 - 36 + 1)) + 36;
    }}
    
    function loadPlayer(autoPlay = false) {{
        if (!YT_API_ready) return;
        
        destroyVideo();
        
        const durationSec = getRandomDuration();
        
        videoBox.innerHTML = '';
        const playerDiv = document.createElement("div");
        playerDiv.style.width = "100%";
        playerDiv.style.height = "100%";
        videoBox.appendChild(playerDiv);
        
        const player = new YT.Player(playerDiv, {{
            height: '100%',
            width: '100%',
            videoId: VIDEO_ID,
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
                    currentPlayer = event.target;
                    updateLoadingStatus();
                    currentPlayer.setVolume(100);
                    
                    qualityInterval = setInterval(() => {{
                        try {{
                            const currentQuality = currentPlayer.getPlaybackQuality();
                            if (currentQuality !== 'tiny' && currentQuality !== 'small') {{
                                currentPlayer.setPlaybackQuality('tiny');
                            }}
                        }} catch(e) {{}}
                    }}, 3000);
                    
                    if (autoPlay) {{
                        setTimeout(() => {{
                            currentPlayer.playVideo();
                        }}, 200);
                    }}
                    
                    currentPlayer.addEventListener('onStateChange', function(stateEvent) {{
                        const state = stateEvent.data;
                        if (state === 0) {{
                            setTimeout(() => {{
                                destroyVideo();
                                videoBox.innerHTML = '';
                                updateLoadingStatus();
                            }}, 1000);
                        }}
                    }});
                }},
                onError: (err) => {{
                    // Silent error handling
                }}
            }}
        }});
    }}
    
    document.getElementById("reload-player").onclick = () => {{
        if (YT_API_ready) {{
            loadPlayer(false);
        }}
    }};
    
    videoBox.addEventListener("click", function(e) {{
        e.stopPropagation();
        if (currentPlayer && currentPlayer.getPlayerState) {{
            const state = currentPlayer.getPlayerState();
            if (state === 1) {{
                currentPlayer.pauseVideo();
            }} else if (state === 2) {{
                currentPlayer.playVideo();
            }} else {{
                if (!YT_API_ready) return;
                loadPlayer(true);
            }}
        }} else {{
            if (!YT_API_ready) return;
            loadPlayer(true);
        }}
    }});
    
    function onYouTubeIframeAPIReady() {{
        YT_API_ready = true;
        updateLoadingStatus();
        // Load player immediately
        loadPlayer(false);
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