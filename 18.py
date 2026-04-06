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
transition:all 0.2s;
}}
button:hover {{
background:#cc0000;
transform:translateY(-1px);
}}
button:active {{
transform:translateY(1px);
}}
.progress-bar {{
position:absolute;
bottom:0;
left:0;
height:3px;
background:#ff0000;
width:0%;
transition:width 0.3s linear;
z-index:100;
}}
.controls-bar {{
position:fixed;
top:10px;
left:10px;
z-index:10002;
background:rgba(0,0,0,0.8);
padding:10px 15px;
border-radius:8px;
display:flex;
gap:10px;
align-items:center;
font-family:monospace;
font-size:12px;
color:white;
}}
.controls-bar select {{
background:#333;
color:white;
border:1px solid #ff0000;
border-radius:4px;
padding:5px;
cursor:pointer;
}}
.controls-bar label {{
display:flex;
align-items:center;
gap:5px;
}}
</style>

<div class="controls-bar">
    <label>
        ⚡ Quality:
        <select id="quality-select">
            <option value="tiny">144p (Aggressive)</option>
            <option value="small">240p</option>
            <option value="medium">360p</option>
            <option value="large">480p</option>
            <option value="hd720">720p</option>
        </select>
    </label>
    <label>
        🎲 Random pauses:
        <input type="checkbox" id="enable-pauses" checked>
    </label>
    <label>
        📊 Auto-start:
        <input type="checkbox" id="auto-start" checked>
    </label>
</div>

<button id="shuffle-load">🔀 Shuffle + Load Players</button>
<button id="stop-all">⏹️ Stop All Videos</button>

<div id="video-grid">
{''.join(html_blocks)}
</div>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
let YT_API_ready = false;
let activePlayers = new Map();
let qualitySelect = document.getElementById("quality-select");
let enablePauses = document.getElementById("enable-pauses");
let autoStart = document.getElementById("auto-start");
let globalStopRequested = false;

function onYouTubeIframeAPIReady() {{
    YT_API_ready = true;
}}

function getRandomStart() {{
    const rand = Math.random();
    
    if (rand < 0.6) {{
        return 0;
    }} else if (rand < 0.8) {{
        return Math.floor(Math.random() * 30) + 10;
    }} else {{
        return Math.floor(Math.random() * 180) + 60;
    }}
}}

function getRandomDuration() {{
    return Math.floor(Math.random() * 45) + 45;
}}

function getRandomPause() {{
    return Math.floor(Math.random() * 8) + 2;
}}

function updateProgressBar(box, player, duration, startTime) {{
    if (box.progressInterval) {{
        clearInterval(box.progressInterval);
    }}
    
    const interval = setInterval(() => {{
        try {{
            if (!player || !player.getCurrentTime || box.destroyed) {{
                if (box.progressInterval) clearInterval(box.progressInterval);
                return;
            }}
            const currentTime = player.getCurrentTime();
            const elapsed = currentTime - startTime;
            const percent = (elapsed / duration) * 100;
            let progressBar = box.querySelector('.progress-bar');
            if (!progressBar) {{
                progressBar = document.createElement('div');
                progressBar.className = 'progress-bar';
                box.style.position = 'relative';
                box.appendChild(progressBar);
            }}
            progressBar.style.width = `${{Math.min(100, Math.max(0, percent))}}%`;
            
            if (percent >= 100) {{
                clearInterval(box.progressInterval);
                box.progressInterval = null;
            }}
        }} catch(e) {{
            // Silent fail
        }}
    }}, 500);
    
    box.progressInterval = interval;
}}

function getSelectedQuality() {{
    return qualitySelect.value;
}}

function forceQuality(player, box) {{
    if (box.qualityInterval) {{
        clearInterval(box.qualityInterval);
    }}
    
    const interval = setInterval(() => {{
        try {{
            if (player && player.getPlayerState && player.getPlayerState() === 1 && !box.destroyed && !globalStopRequested) {{
                const targetQuality = getSelectedQuality();
                const currentQuality = player.getPlaybackQuality ? player.getPlaybackQuality() : null;
                if (currentQuality !== targetQuality) {{
                    player.setPlaybackQuality(targetQuality);
                }}
            }}
        }} catch(e) {{
            // Silent fail
        }}
    }}, 1500);
    
    box.qualityInterval = interval;
}}

function destroyVideo(box, player, immediate = false) {{
    box.destroyed = true;
    
    if (box.qualityInterval) {{
        clearInterval(box.qualityInterval);
        box.qualityInterval = null;
    }}
    
    if (box.progressInterval) {{
        clearInterval(box.progressInterval);
        box.progressInterval = null;
    }}
    
    if (box.pauseTimeouts) {{
        box.pauseTimeouts.forEach(timeout => clearTimeout(timeout));
        box.pauseTimeouts = [];
    }}
    
    try {{
        if (player && player.stopVideo) player.stopVideo();
        if (player && player.destroy) player.destroy();
    }} catch(e) {{
        // Silent fail
    }}
    
    activePlayers.delete(box);
    
    if (immediate) {{
        box.style.opacity = '0';
        setTimeout(() => {{
            if (box.parentNode && !globalStopRequested) box.remove();
        }}, 500);
    }} else {{
        box.style.transition = 'opacity 1s';
        box.style.opacity = '0';
        setTimeout(() => {{
            if (box.parentNode && !globalStopRequested) box.remove();
        }}, 1000);
    }}
}}

function loadPlayer(box, autoPlay = true) {{
    if(box.classList.contains("loaded") || !YT_API_ready || globalStopRequested) return;
    
    box.destroyed = false;
    box.pauseTimeouts = [];

    const thinkingDelay = Math.floor(Math.random() * 2200) + 300;
    
    setTimeout(() => {{
        if(box.classList.contains("loaded") || !YT_API_ready || globalStopRequested || box.destroyed) return;
        
        const vid = box.dataset.video;
        const start = getRandomStart();
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
                autoplay: autoPlay ? 1 : 0,
                controls: 1,
                rel: 0,
                modestbranding: 1,
                playsinline: 1,
                start: start,
                end: end,
                vq: getSelectedQuality()
            }},
            events: {{
                onReady: (event) => {{
                    if (box.destroyed || globalStopRequested) {{
                        try {{ event.target.destroy(); }} catch(e) {{}}
                        return;
                    }}
                    
                    activePlayers.set(box, event.target);
                    event.target.setVolume(100);
                    
                    forceQuality(event.target, box);
                    
                    if (autoPlay) {{
                        setTimeout(() => {{
                            try {{
                                if (!box.destroyed && !globalStopRequested) {{
                                    const startTime = event.target.getCurrentTime();
                                    updateProgressBar(box, event.target, duration, startTime);
                                }}
                            }} catch(e) {{
                                // Silent fail
                            }}
                        }}, 1000);
                    }}
                    
                    event.target.addEventListener('onStateChange', function(e) {{
                        if (box.destroyed || globalStopRequested) return;
                        
                        if(e.data == YT.PlayerState.PLAYING) {{
                            if (!enablePauses.checked) {{
                                const endTimeout = setTimeout(() => {{
                                    if (!box.destroyed && !globalStopRequested) {{
                                        try {{
                                            event.target.stopVideo();
                                            destroyVideo(box, event.target);
                                        }} catch(e) {{
                                            // Silent fail
                                        }}
                                    }}
                                }}, duration * 1000);
                                
                                if (!box.pauseTimeouts) box.pauseTimeouts = [];
                                box.pauseTimeouts.push(endTimeout);
                                return;
                            }}
                            
                            let remainingTime = duration;
                            let pauseCount = 0;
                            const MAX_PAUSES = 4;
                            
                            const scheduleNextPause = () => {{
                                if (box.destroyed || globalStopRequested) return;
                                
                                if (remainingTime <= 0 || pauseCount >= MAX_PAUSES) {{
                                    if (remainingTime > 0 && !box.destroyed && !globalStopRequested) {{
                                        const endTimeout = setTimeout(() => {{
                                            if (!box.destroyed && !globalStopRequested) {{
                                                try {{
                                                    event.target.stopVideo();
                                                    destroyVideo(box, event.target);
                                                }} catch(e) {{
                                                    // Silent fail
                                                }}
                                            }}
                                        }}, remainingTime * 1000);
                                        
                                        if (!box.pauseTimeouts) box.pauseTimeouts = [];
                                        box.pauseTimeouts.push(endTimeout);
                                    }}
                                    return;
                                }}
                                
                                if (remainingTime <= 5) {{
                                    const endTimeout = setTimeout(() => {{
                                        if (!box.destroyed && !globalStopRequested) {{
                                            try {{
                                                event.target.stopVideo();
                                                destroyVideo(box, event.target);
                                            }} catch(e) {{
                                                // Silent fail
                                            }}
                                        }}
                                    }}, remainingTime * 1000);
                                    
                                    if (!box.pauseTimeouts) box.pauseTimeouts = [];
                                    box.pauseTimeouts.push(endTimeout);
                                    return;
                                }}
                                
                                const pauseDuration = getRandomPause();
                                const timeUntilPause = Math.floor(Math.random() * 15) + 8;
                                
                                if (timeUntilPause < remainingTime) {{
                                    const pauseTimeout = setTimeout(() => {{
                                        if (!box.destroyed && !globalStopRequested) {{
                                            try {{
                                                event.target.pauseVideo();
                                                pauseCount++;
                                                
                                                const resumeTimeout = setTimeout(() => {{
                                                    if (!box.destroyed && !globalStopRequested) {{
                                                        try {{
                                                            event.target.playVideo();
                                                            remainingTime -= (timeUntilPause + pauseDuration);
                                                            scheduleNextPause();
                                                        }} catch(e) {{
                                                            // Silent fail
                                                        }}
                                                    }}
                                                }}, pauseDuration * 1000);
                                                
                                                if (!box.pauseTimeouts) box.pauseTimeouts = [];
                                                box.pauseTimeouts.push(resumeTimeout);
                                            }} catch(e) {{
                                                // Silent fail
                                            }}
                                        }}
                                    }}, timeUntilPause * 1000);
                                    
                                    if (!box.pauseTimeouts) box.pauseTimeouts = [];
                                    box.pauseTimeouts.push(pauseTimeout);
                                }} else {{
                                    const endTimeout = setTimeout(() => {{
                                        if (!box.destroyed && !globalStopRequested) {{
                                            try {{
                                                event.target.stopVideo();
                                                destroyVideo(box, event.target);
                                            }} catch(e) {{
                                                // Silent fail
                                            }}
                                        }}
                                    }}, remainingTime * 1000);
                                    
                                    if (!box.pauseTimeouts) box.pauseTimeouts = [];
                                    box.pauseTimeouts.push(endTimeout);
                                }}
                            }};
                            
                            scheduleNextPause();
                        }}
                    }});
                }},
                onError: (err) => {{
                    if (box.qualityInterval) {{
                        clearInterval(box.qualityInterval);
                        box.qualityInterval = null;
                    }}
                    activePlayers.delete(box);
                    box.destroyed = true;
                }}
            }}
        }});
    }}, thinkingDelay);
}}

document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", () => {{
        if (!globalStopRequested) {{
            loadPlayer(box, autoStart.checked);
        }}
    }});
}});

document.getElementById("stop-all").onclick = () => {{
    globalStopRequested = true;
    
    for (let [box, player] of activePlayers) {{
        if (box.qualityInterval) {{
            clearInterval(box.qualityInterval);
            box.qualityInterval = null;
        }}
        
        if (box.progressInterval) {{
            clearInterval(box.progressInterval);
            box.progressInterval = null;
        }}
        
        if (box.pauseTimeouts) {{
            box.pauseTimeouts.forEach(timeout => clearTimeout(timeout));
            box.pauseTimeouts = [];
        }}
        
        box.destroyed = true;
        
        try {{
            player.stopVideo();
            player.destroy();
        }} catch(e) {{
            // Silent fail
        }}
        
        box.innerHTML = '';
        const thumbImg = document.createElement('img');
        thumbImg.src = `https://i.ytimg.com/vi_webp/${{box.dataset.video}}/mqdefault.webp`;
        thumbImg.loading = 'lazy';
        thumbImg.className = 'thumb';
        box.appendChild(thumbImg);
        box.classList.remove('loaded');
        box.style.opacity = '1';
    }}
    activePlayers.clear();
    setTimeout(() => {{ globalStopRequested = false; }}, 1000);
}};

document.getElementById("shuffle-load").onclick = () => {{
    globalStopRequested = true;
    
    let grid = document.getElementById("video-grid");
    let boxes = [...grid.children];

    for (let [box, player] of activePlayers) {{
        if (box.qualityInterval) {{
            clearInterval(box.qualityInterval);
            box.qualityInterval = null;
        }}
        
        if (box.progressInterval) {{
            clearInterval(box.progressInterval);
            box.progressInterval = null;
        }}
        
        if (box.pauseTimeouts) {{
            box.pauseTimeouts.forEach(timeout => clearTimeout(timeout));
            box.pauseTimeouts = [];
        }}
        
        box.destroyed = true;
        
        try {{
            player.destroy();
        }} catch(e) {{
            // Silent fail
        }}
        activePlayers.delete(box);
    }}

    boxes.forEach(box => {{
        box.innerHTML = '';
        const thumbImg = document.createElement('img');
        thumbImg.src = `https://i.ytimg.com/vi_webp/${{box.dataset.video}}/mqdefault.webp`;
        thumbImg.loading = 'lazy';
        thumbImg.className = 'thumb';
        box.appendChild(thumbImg);
        box.classList.remove('loaded');
        box.style.opacity = '1';
        box.destroyed = false;
    }});

    for(let i=boxes.length-1; i>0; i--) {{
        const j = Math.floor(Math.random()*(i+1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }}
    grid.innerHTML = '';
    boxes.forEach(box => grid.appendChild(box));

    setTimeout(() => {{ globalStopRequested = false; }}, 500);

    let delay = 0;
    boxes.forEach((box, idx) => {{
        let randomDelay = 2000 + Math.random() * 8000;
        setTimeout(() => {{
            if (!globalStopRequested && !box.destroyed) {{
                loadPlayer(box, autoStart.checked);
            }}
        }}, delay);
        delay += randomDelay;
    }});
}};

qualitySelect.addEventListener("change", () => {{
    for (let [box, player] of activePlayers) {{
        try {{
            if (!box.destroyed && player.getPlayerState() === 1) {{
                player.setPlaybackQuality(qualitySelect.value);
            }}
        }} catch(e) {{
            // Silent fail
        }}
    }}
}});
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)