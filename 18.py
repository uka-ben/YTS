import streamlit as st

st.set_page_config(layout="wide", page_title="YouTube Player")

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
    body {{
        margin: 0;
        padding: 0;
        background: #000;
    }}
    .video-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        background: #000;
    }}
    .video-box {{
        cursor: pointer;
        width: 100%;
        max-width: 1200px;
        aspect-ratio: 16/9;
        position: relative;
        background: #000;
    }}
    iframe {{
        width: 100%;
        height: 100%;
        border: none;
    }}
</style>

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