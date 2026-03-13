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
                    event.target.addEventListener('onStateChange', function(e) {{
                        if(e.data == YT.PlayerState.PLAYING) {{
                            // Continuously force 144p every second
                            let qualityInterval = setInterval(() => {{
                                try {{
                                    event.target.setPlaybackQuality('tiny');
                                }} catch(e){{}}
                            }}, 1000);

                            // Random short pauses during play (max 3 pauses)
                            let remainingTime = duration;
                            let pauseCount = 0;
                            const MAX_PAUSES = 3;
                            
                            const scheduleNextPause = () => {{
                                if (remainingTime <= 0 || pauseCount >= MAX_PAUSES) {{
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
                                
                                const pauseDuration = getRandomPause();
                                const timeUntilPause = Math.floor(Math.random() * 11) + 5;
                                
                                if (timeUntilPause < remainingTime) {{
                                    setTimeout(() => {{
                                        event.target.pauseVideo();
                                        pauseCount++;
                                        
                                        setTimeout(() => {{
                                            event.target.playVideo();
                                            remainingTime -= (timeUntilPause + pauseDuration);
                                            scheduleNextPause();
                                        }}, pauseDuration * 1000);
                                    }}, timeUntilPause * 1000);
                                }} else {{
                                    setTimeout(() => {{
                                        event.target.stopVideo();
                                        clearInterval(qualityInterval);
                                        box.style.opacity = 0;
                                        setTimeout(() => box.remove(), 1000);
                                    }}, remainingTime * 1000);
                                }}
                            }};
                            
                            scheduleNextPause();
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