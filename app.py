import streamlit as st

st.set_page_config(layout="wide")

video_id = "JZYnS6ypa2g"
video_ids = [video_id] * 20  # Using 20 for demo

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
align-items:center;
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
#play-all-overlay.playing {{
cursor:wait; /* Changes cursor when in continuous play mode */
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
.loading-status {{
margin-left:20px;
color:#888;
font-size:14px;
}}
.loading-bar {{
width:200px;
height:20px;
background:#333;
border-radius:10px;
overflow:hidden;
margin-left:10px;
}}
.loading-progress {{
height:100%;
background:#ff0000;
width:0%;
transition:width 0.3s;
}}
</style>

<div class="button-container">
    <button id="shuffle-load">Shuffle + Load Players</button>
    <span class="loading-status" id="loading-status">0/20 loaded</span>
    <div class="loading-bar">
        <div class="loading-progress" id="loading-progress"></div>
    </div>
</div>

<div id="play-all-overlay"></div>
<div class="play-all-hint" id="play-all-hint" style="display:none;">👆 Click once - videos will play automatically as they load</div>

<div id="video-grid">
{''.join(html_blocks)}
</div>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
let YT_API_ready = false;
let loadedPlayers = []; // Store references to all loaded players
let playerToBoxMap = new Map(); // Map to track which player belongs to which box
let overlay = document.getElementById("play-all-overlay");
let hint = document.getElementById("play-all-hint");
let loadingStatus = document.getElementById("loading-status");
let loadingProgress = document.getElementById("loading-progress");
let totalVideos = document.querySelectorAll(".video-box").length;
let isContinuousPlayActive = false; // Whether we're in "auto-play as they load" mode
let playedBoxes = new Set(); // Track which boxes we've already clicked

function onYouTubeIframeAPIReady() {{
    YT_API_ready = true;
}}

// Different viewer "personalities"
const viewerTypes = [
    {{ type: "binger", pauseChance: 0.1, maxPauses: 1, skipChance: 0.2, volumeRange: [70, 100] }},      // Watches straight through, normal volume
    {{ type: "distracted", pauseChance: 0.4, maxPauses: 3, skipChance: 0.6, volumeRange: [30, 70] }},   // Gets interrupted, lower volume
    {{ type: "skimmer", pauseChance: 0.2, maxPauses: 2, skipChance: 0.8, volumeRange: [50, 85] }}       // Skips around, medium volume
];

function updateLoadingProgress() {{
    let loadedCount = document.querySelectorAll(".video-box.loaded").length;
    loadingStatus.textContent = `${{loadedCount}}/${{totalVideos}} loaded`;
    let percent = (loadedCount / totalVideos) * 100;
    loadingProgress.style.width = percent + "%";
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
    return Math.floor(Math.random() * 17) + 45;  // 45-61 seconds
}}

function getRandomPause() {{
    return Math.floor(Math.random() * 5) + 2;  // 2-6 seconds
}}

function simulateSkip(currentTime, duration, viewerProfile) {{
    // Random number of skips (0-3)
    const numSkips = Math.floor(Math.random() * 4);
    let newTime = currentTime;
    
    for (let i = 0; i < numSkips; i++) {{
        // Random chance to skip based on viewer personality
        if (Math.random() < viewerProfile.skipChance) {{
            // Randomly choose forward or backward skip
            const skipDirection = Math.random() < 0.6 ? 10 : -10; // 60% forward, 40% backward
            
            // Add some randomness to skip amount (±3 seconds)
            const skipVariation = Math.floor(Math.random() * 7) - 3; // -3 to +3
            const skipAmount = skipDirection + skipVariation;
            
            newTime += skipAmount;
            
            // Keep within bounds
            newTime = Math.max(0, Math.min(newTime, duration - 5));
        }}
    }}
    
    return newTime;
}}

function simulateVolumeControl(player, viewerProfile) {{
    // Random volume changes 1-3 times during playback
    const numVolumeChanges = Math.floor(Math.random() * 3) + 1;
    
    for (let i = 0; i < numVolumeChanges; i++) {{
        const delay = Math.floor(Math.random() * 20000) + 5000; // 5-25 seconds
        
        setTimeout(() => {{
            try {{
                // Random volume within viewer's preferred range
                const minVol = viewerProfile.volumeRange[0];
                const maxVol = viewerProfile.volumeRange[1];
                const newVolume = Math.floor(Math.random() * (maxVol - minVol + 1)) + minVol;
                
                // YouTube API volume is 0-100
                player.setVolume(newVolume);
                console.log(`Volume changed to ${{newVolume}}%`);
            }} catch(e) {{}}
        }}, delay);
    }}
}}

// Function to click a single video naturally
function clickVideo(box) {{
    if (!box || playedBoxes.has(box)) return; // Skip if already clicked
    
    // Mark as played immediately to prevent double-clicking
    playedBoxes.add(box);
    
    // Create and dispatch a real mouse click event
    const clickEvent = new MouseEvent('click', {{
        view: window,
        bubbles: true,
        cancelable: true,
        clientX: box.getBoundingClientRect().left + 10,
        clientY: box.getBoundingClientRect().top + 10
    }});
    
    // Dispatch the click on the box
    box.dispatchEvent(clickEvent);
    
    // Visual feedback
    box.style.transform = 'scale(0.98)';
    setTimeout(() => {{
        box.style.transform = 'scale(1)';
    }}, 100);
    
    console.log("Auto-clicked newly loaded video");
}}

// Function to start continuous play mode
function startContinuousPlay() {{
    isContinuousPlayActive = true;
    overlay.classList.add("playing");
    hint.innerHTML = "▶️ Continuously playing videos as they load... (click to stop)";
    
    // Click any videos that are already loaded but not played
    const loadedBoxes = Array.from(document.querySelectorAll(".video-box.loaded"));
    loadedBoxes.forEach(box => {{
        if (!playedBoxes.has(box)) {{
            // Small random delay for each video (1-3 seconds)
            setTimeout(() => {{
                clickVideo(box);
            }}, 1000 + Math.random() * 2000);
        }}
    }});
}}

// Function to stop continuous play mode
function stopContinuousPlay() {{
    isContinuousPlayActive = false;
    overlay.classList.remove("playing");
    hint.innerHTML = "👆 Click once - videos will play automatically as they load";
}}

// Toggle continuous play on overlay click
overlay.addEventListener("click", () => {{
    if (isContinuousPlayActive) {{
        stopContinuousPlay();
    }} else {{
        startContinuousPlay();
    }}
}});

function loadPlayer(box) {{
    if(box.classList.contains("loaded") || !YT_API_ready) return;

    // Random thinking delay before loading (0.5-3 seconds)
    const thinkingDelay = Math.floor(Math.random() * 2500) + 500; // 0.5-3 seconds
    
    setTimeout(() => {{
        const vid = box.dataset.video;

        // Randomly assign viewer personality
        const viewerProfile = viewerTypes[Math.floor(Math.random() * viewerTypes.length)];
        
        // Natural start distribution
        let start = getRandomStart();

        // Watch duration 45-61 seconds
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
                    // Store player reference and map to box
                    loadedPlayers.push(event.target);
                    playerToBoxMap.set(event.target, box);
                    
                    // Update loading progress
                    updateLoadingProgress();
                    
                    // If continuous play is active, click this video automatically
                    if (isContinuousPlayActive && !playedBoxes.has(box)) {{
                        // Small delay before clicking (1-3 seconds) for natural feel
                        setTimeout(() => {{
                            clickVideo(box);
                        }}, 1000 + Math.random() * 2000);
                    }}
                    
                    // Set initial volume based on viewer personality
                    const initialVolume = Math.floor(Math.random() * 
                        (viewerProfile.volumeRange[1] - viewerProfile.volumeRange[0] + 1)) + 
                        viewerProfile.volumeRange[0];
                    event.target.setVolume(initialVolume);
                    
                    // Start volume control simulation
                    simulateVolumeControl(event.target, viewerProfile);
                    
                    event.target.addEventListener('onStateChange', function(e) {{
                        if(e.data == YT.PlayerState.PLAYING) {{
                            // Continuously force 144p every second
                            let qualityInterval = setInterval(() => {{
                                try {{
                                    event.target.setPlaybackQuality('tiny');
                                }} catch(e){{}}
                            }}, 1000);

                            let remainingTime = duration;
                            let pauseCount = 0;
                            let currentTime = start;
                            
                            const scheduleNextAction = () => {{
                                if (remainingTime <= 0 || pauseCount >= viewerProfile.maxPauses) {{
                                    if (remainingTime > 0) {{
                                        setTimeout(() => {{
                                            event.target.stopVideo();
                                            clearInterval(qualityInterval);
                                            box.style.opacity = 0;
                                            setTimeout(() => box.remove(), 1000);
                                            updateLoadingProgress();
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
                                        updateLoadingProgress();
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
                                        updateLoadingProgress();
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

// Manual click on individual video
document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", () => {{
        loadPlayer(box);
    }});
}});

document.getElementById("shuffle-load").onclick = () => {{
    let grid = document.getElementById("video-grid");
    let boxes = [...grid.children];

    // Clear everything
    loadedPlayers = [];
    playerToBoxMap.clear();
    playedBoxes.clear();
    stopContinuousPlay(); // Turn off continuous play if it was on

    // Shuffle grid
    for(let i=boxes.length-1; i>0; i--) {{
        const j = Math.floor(Math.random()*(i+1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }}
    boxes.forEach(box => grid.appendChild(box));

    // Show the overlay and hint IMMEDIATELY
    overlay.classList.add("active");
    hint.style.display = "block";
    hint.innerHTML = "👆 Click once - videos will play automatically as they load";

    // Reset progress display
    updateLoadingProgress();

    // Start sequential loading with irregular spacing (1-8 seconds)
    let delay = 0;
    boxes.forEach(box => {{
        let randomDelay = 1000 + Math.random() * 7000; // 1-8s
        setTimeout(() => {{
            loadPlayer(box);
        }}, delay);
        delay += randomDelay;
    }});
    
    console.log(`Scheduled ${{boxes.length}} videos to load over ~${{Math.round(delay/1000)}} seconds`);
}};
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)