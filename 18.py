import streamlit as st

st.set_page_config(layout="wide", page_title="YouTube Grid - Smart Buffer Control")

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
    <button id="shuffle-load">🔀 Shuffle + Load (Smart Buffer)</button>
    <span class="loading-status" id="loading-status">📦 0/50 loaded</span>
    <div class="loading-bar">
        <div class="loading-progress" id="loading-progress"></div>
    </div>
    <div class="data-warning">⚡ Smart buffering: Only loads up to 50s | 144p | Data saver</div>
</div>

<div id="video-grid">
{''.join(html_blocks)}
</div>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
    const TOTAL_VIDEOS = 50;
    const VIDEO_ID = "{video_id}";
    let YT_API_ready = false;
    let loadedPlayers = new Map();
    let playerIntervals = new Map();
    let gridContainer = document.getElementById("video-grid");
    
    function updateLoadingProgress() {{
        let loadedCount = document.querySelectorAll(".video-box.loaded").length;
        let statusSpan = document.getElementById("loading-status");
        let progressFill = document.getElementById("loading-progress");
        statusSpan.textContent = "📦 " + loadedCount + "/" + TOTAL_VIDEOS + " loaded";
        let percent = (loadedCount / TOTAL_VIDEOS) * 100;
        progressFill.style.width = percent + "%";
    }}
    
    function destroyVideo(box, player) {{
        if (playerIntervals.has(box)) {{
            clearInterval(playerIntervals.get(box));
            playerIntervals.delete(box);
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
            }}
        }}, 500);
    }}
    
    function playVideo(box) {{
        const player = loadedPlayers.get(box);
        if (player && typeof player.playVideo === 'function') {{
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
                    event.target.setVolume(100);
                    
                    const qualityInterval = setInterval(() => {{
                        try {{
                            const currentQuality = event.target.getPlaybackQuality();
                            if (currentQuality !== 'tiny' && currentQuality !== 'small') {{
                                event.target.setPlaybackQuality('tiny');
                            }}
                        }} catch(e) {{}}
                    }}, 3000);
                    playerIntervals.set(box, qualityInterval);
                    
                    if (autoPlay) {{
                        setTimeout(() => {{
                            event.target.playVideo();
                        }}, 200);
                    }}
                    
                    event.target.addEventListener('onStateChange', function(stateEvent) {{
                        const state = stateEvent.data;
                        if (state === 0) {{
                            const currentPlayer = loadedPlayers.get(box);
                            if (currentPlayer) {{
                                setTimeout(() => {{
                                    if (box.parentNode) {{
                                        destroyVideo(box, currentPlayer);
                                    }}
                                }}, 1000);
                            }}
                        }}
                    }});
                }},
                onError: (err) => {{
                    // Silent error handling
                }}
            }}
        }});
    }}
    
    function shuffleAndLoad() {{
        for (let [box, player] of loadedPlayers.entries()) {{
            if (playerIntervals.has(box)) {{
                clearInterval(playerIntervals.get(box));
                playerIntervals.delete(box);
            }}
            try {{
                if(player) player.destroy();
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
        
        let boxes = [...gridContainer.children];
        for(let i = boxes.length - 1; i > 0; i--) {{
            const j = Math.floor(Math.random() * (i + 1));
            [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
        }}
        gridContainer.innerHTML = '';
        boxes.forEach(b => gridContainer.appendChild(b));
        updateLoadingProgress();
        
        let currentDelay = 500;
        boxes.forEach((box, idx) => {{
            setTimeout(() => {{
                if (YT_API_ready && !box.classList.contains('loaded')) {{
                    loadPlayer(box, false);
                }}
            }}, currentDelay);
            currentDelay += 800 + Math.random() * 5000;
        }});
    }}
    
    document.querySelectorAll(".video-box").forEach(box => {{
        box.addEventListener("click", function(e) {{
            e.stopPropagation();
            if (this.classList.contains("loaded")) {{
                playVideo(this);
            }} else {{
                if (!YT_API_ready) return;
                loadPlayer(this, true);
            }}
        }});
    }});
    
    document.getElementById("shuffle-load").onclick = () => {{
        if (YT_API_ready) shuffleAndLoad();
    }};
    
    function onYouTubeIframeAPIReady() {{
        YT_API_ready = true;
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