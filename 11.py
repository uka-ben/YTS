import streamlit as st

st.set_page_config(layout="wide")

video_id = "JZYnS6ypa2g"
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
}}
#play-all-overlay.active {{
display:block;
}}
.play-all-hint {{
position:fixed;
bottom:20px;
right:20px;
background:rgba(255,255,255,0.9);
padding:10px 20px;
border-radius:30px;
box-shadow:0 2px 10px rgba(0,0,0,0.3);
z-index:10000;
font-weight:bold;
color:#333;
border:2px solid #ff0000;
}}
</style>

<div class="button-container">
    <button id="shuffle-load">Shuffle + Load Players</button>
</div>

<div id="play-all-overlay"></div>
<div class="play-all-hint" id="play-all-hint" style="display:none;">👆 Click anywhere to play all videos naturally</div>

<div id="video-grid">
{''.join(html_blocks)}
</div>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
let YT_API_ready = false;
let loadedPlayers = [];
let playerToBoxMap = new Map();
let overlay = document.getElementById("play-all-overlay");
let hint = document.getElementById("play-all-hint");

function onYouTubeIframeAPIReady() {{
    YT_API_ready = true;
}}

const viewerTypes = [
    {{ type: "binger", pauseChance: 0.1, maxPauses: 1, skipChance: 0.2, volumeRange: [70, 100] }},
    {{ type: "distracted", pauseChance: 0.4, maxPauses: 3, skipChance: 0.6, volumeRange: [30, 70] }},
    {{ type: "skimmer", pauseChance: 0.2, maxPauses: 2, skipChance: 0.8, volumeRange: [50, 85] }}
];

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

function loadPlayer(box) {{
    if(box.classList.contains("loaded") || !YT_API_ready) return;

    const thinkingDelay = Math.floor(Math.random() * 2500) + 500;
    
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
                    loadedPlayers.push(event.target);
                    playerToBoxMap.set(event.target, box);
                    
                    const initialVolume = Math.floor(Math.random() * 
                        (viewerProfile.volumeRange[1] - viewerProfile.volumeRange[0] + 1)) + 
                        viewerProfile.volumeRange[0];
                    event.target.setVolume(initialVolume);
                    
                    simulateVolumeControl(event.target, viewerProfile);
                    
                    event.target.addEventListener('onStateChange', function(e) {{
                        if(e.data == YT.PlayerState.PLAYING) {{
                            let qualityInterval = setInterval(() => {{
                                try {{
                                    event.target.setPlaybackQuality('tiny');
                                }} catch(e){{}}
                            }}, 1000);

                            let remainingTime = duration;
                            let pauseCount = 0;
                            
                            const scheduleNextAction = () => {{
                                if (remainingTime <= 0 || pauseCount >= viewerProfile.maxPauses) {{
                                    if (remainingTime > 0) {{
                                        setTimeout(() => {{
                                            event.target.stopVideo();
                                            clearInterval(qualityInterval);
                                            box.style.opacity = 0;
                                            setTimeout(() => box.remove(), 1000);
                                        }}, remainingTime * 1000);
                                    }}
                                    return;
                                }}
                                
                                if (remainingTime <= 5) {{
                                    setTimeout(() => {{
                                        event.target.stopVideo();
                                        clearInterval(qualityInterval);
                                        box.style.opacity = 0;
                                        setTimeout(() => box.remove(), 1000);
                                    }}, remainingTime * 1000);
                                    return;
                                }}
                                
                                const timeUntilAction = Math.floor(Math.random() * 11) + 5;
                                
                                if (timeUntilAction < remainingTime) {{
                                    setTimeout(() => {{
                                        const action = Math.random() < viewerProfile.pauseChance ? 'pause' : 'skip';
                                        
                                        if (action === 'pause' && pauseCount < viewerProfile.maxPauses) {{
                                            const pauseDuration = getRandomPause();
                                            event.target.pauseVideo();
                                            pauseCount++;
                                            
                                            setTimeout(() => {{
                                                event.target.playVideo();
                                                remainingTime -= (timeUntilAction + pauseDuration);
                                                scheduleNextAction();
                                            }}, pauseDuration * 1000);
                                        }} else {{
                                            event.target.getCurrentTime().then((currentVideoTime) => {{
                                                const newTime = simulateSkip(currentVideoTime, duration, viewerProfile);
                                                event.target.seekTo(newTime, true);
                                                remainingTime -= timeUntilAction;
                                                scheduleNextAction();
                                            }});
                                        }}
                                    }}, timeUntilAction * 1000);
                                }} else {{
                                    setTimeout(() => {{
                                        event.target.stopVideo();
                                        clearInterval(qualityInterval);
                                        box.style.opacity = 0;
                                        setTimeout(() => box.remove(), 1000);
                                    }}, remainingTime * 1000);
                                }}
                            }};
                            
                            scheduleNextAction();
                        }}
                    }});
                }}
            }}
        }});
    }}, thinkingDelay);
}}

function simulateNaturalClicks() {{
    const loadedBoxes = Array.from(document.querySelectorAll(".video-box.loaded"));
    
    if (loadedBoxes.length === 0) {{
        alert("Please click 'Shuffle + Load Players' first to load videos!");
        overlay.classList.remove("active");
        hint.style.display = "none";
        return;
    }}
    
    const shuffledBoxes = [...loadedBoxes];
    for (let i = shuffledBoxes.length - 1; i > 0; i--) {{
        const j = Math.floor(Math.random() * (i + 1));
        [shuffledBoxes[i], shuffledBoxes[j]] = [shuffledBoxes[j], shuffledBoxes[i]];
    }}
    
    overlay.classList.remove("active");
    hint.style.display = "none";
    
    let clickDelay = 0;
    
    shuffledBoxes.forEach((box, index) => {{
        const timeBetweenClicks = 2000 + Math.random() * 5000;
        
        setTimeout(() => {{
            const clickEvent = new MouseEvent('click', {{
                view: window,
                bubbles: true,
                cancelable: true,
                clientX: box.getBoundingClientRect().left + 10,
                clientY: box.getBoundingClientRect().top + 10
            }});
            
            box.dispatchEvent(clickEvent);
            
            box.style.transform = 'scale(0.98)';
            setTimeout(() => {{
                box.style.transform = 'scale(1)';
            }}, 100);
        }}, clickDelay);
        
        clickDelay += timeBetweenClicks;
    }});
    
    setTimeout(() => {{
        if (document.querySelectorAll(".video-box.loaded").length > 0) {{
            overlay.classList.add("active");
            hint.style.display = "block";
        }}
    }}, clickDelay + 5000);
}}

document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", () => {{
        loadPlayer(box);
    }});
}});

overlay.addEventListener("click", () => {{
    simulateNaturalClicks();
}});

document.getElementById("shuffle-load").onclick = () => {{
    let grid = document.getElementById("video-grid");
    let boxes = [...grid.children];

    loadedPlayers = [];
    playerToBoxMap.clear();

    for(let i=boxes.length-1; i>0; i--) {{
        const j = Math.floor(Math.random()*(i+1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }}
    boxes.forEach(box => grid.appendChild(box));

    overlay.classList.add("active");
    hint.style.display = "block";

    let delay = 0;
    boxes.forEach(box => {{
        let randomDelay = 1000 + Math.random() * 7000;
        setTimeout(() => {{
            loadPlayer(box);
        }}, delay);
        delay += randomDelay;
    }});
}};
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)