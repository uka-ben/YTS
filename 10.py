import streamlit as st

st.set_page_config(layout="wide")

video_id = "ZYcZ_nBLG6Y"
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
}}
</style>

<button id="shuffle-load">Shuffle + Load Players</button>

<div id="video-grid">
{''.join(html_blocks)}
</div>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
let YT_API_ready = false;

function onYouTubeIframeAPIReady() {{
    YT_API_ready = true;
}}

// Different viewer "personalities"
const viewerTypes = [
    {{ type: "binger", pauseChance: 0.1, maxPauses: 1, skipChance: 0.2, volumeRange: [70, 100] }},
    {{ type: "distracted", pauseChance: 0.4, maxPauses: 3, skipChance: 0.6, volumeRange: [30, 70] }},
    {{ type: "skimmer", pauseChance: 0.2, maxPauses: 2, skipChance: 0.8, volumeRange: [50, 85] }}
];

function getRandomStart() {{
    const rand = Math.random();
    
    if (rand < 0.7) {{ return 0; }}
    else if (rand < 0.85) {{ return Math.floor(Math.random() * 20) + 10; }}
    else {{ return Math.floor(Math.random() * 120) + 60; }}
}}

function getRandomDuration() {{
    return Math.floor(Math.random() * 17) + 45;  // 45-61 seconds
}}

function getRandomPause() {{
    return Math.floor(Math.random() * 5) + 2;  // 2-6 seconds
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

document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", () => loadPlayer(box));
}});

document.getElementById("shuffle-load").onclick = () => {{
    let grid = document.getElementById("video-grid");
    let boxes = [...grid.children];

    // Shuffle grid
    for(let i=boxes.length-1; i>0; i--) {{
        const j = Math.floor(Math.random()*(i+1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }}
    boxes.forEach(box => grid.appendChild(box));

    // Sequential loading with irregular spacing (1-8 seconds)
    let delay = 0;
    boxes.forEach(box => {{
        let randomDelay = 1000 + Math.random() * 7000; // 1-8s
        setTimeout(() => {{
            loadPlayer(box);
        }}, delay);
        delay += randomDelay;
    }});
}};
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)