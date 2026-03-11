import streamlit as st

st.set_page_config(layout="wide")

video_id = "JZYnS6ypa2g"
video_ids = [video_id] * 20  # 20 videos

# Create small thumbnail blocks (~50% smaller)
html_blocks = []
for i, vid in enumerate(video_ids):
    html_blocks.append(f"""
<div class="video-box" data-video="{vid}" data-index="{i}">
    <img src="https://i.ytimg.com/vi_webp/{vid}/mqdefault.webp"
         loading="lazy"
         class="thumb">
</div>
""")

html = """
<style>
#video-grid {
    background:#000;
    padding:10px;
    display:grid;
    grid-template-columns:repeat(auto-fill,minmax(80px,1fr));
    gap:4px;
}
.video-box {
    cursor:pointer;
    aspect-ratio:16/9;
    position:relative;
    transition:opacity 1s;
}
.thumb {
    width:100%;
    height:100%;
    object-fit:cover;
    border-radius:4px;
}
button {
    padding:6px 12px;
    font-size:14px;
    cursor:pointer;
    margin-bottom:10px;
}
iframe {
    width:100%;
    height:100%;
    border:none;
    border-radius:4px;
}
</style>

<button id="shuffle-load">Shuffle + Load Players</button>

<div id="video-grid">
""" + "".join(html_blocks) + """
</div>

<script src="https://www.youtube.com/iframe_api"></script>

<script>
let players = {};
let APIready = false;

function onYouTubeIframeAPIReady() {
    APIready = true;
}

// Watch timer function
function startWatchTimer(player, box) {
    let maxDuration = Math.floor(Math.random()*(46-35+1))+35;
    let watchStart = Date.now();
    let interval = setInterval(()=>{
        if(player.getPlayerState() !== YT.PlayerState.PLAYING) return;
        let watchedSec = (Date.now() - watchStart)/1000;
        if(watchedSec >= maxDuration){
            player.stopVideo();
            box.style.opacity = 0;
            setTimeout(()=>box.remove(),500);
            clearInterval(interval);
        }
    },250);
}

// Load or play player on click
function handleClick(box){
    const vid = box.dataset.video;
    const idx = box.dataset.index;
    if(!APIready) return;

    if(!box.classList.contains("loaded")){
        // Create iframe on user click to satisfy mobile autoplay policies
        box.innerHTML = '<div id="p'+idx+'"></div>';
        box.classList.add("loaded");

        players[idx] = new YT.Player('p'+idx, {
            height:'100%',
            width:'100%',
            videoId: vid,
            playerVars:{
                autoplay:0,  // NO autoplay
                controls:1,
                rel:0,
                modestbranding:1,
                playsinline:1,
                vq:'tiny'
            },
            events:{
                onStateChange:function(e){
                    if(e.data === YT.PlayerState.PLAYING){
                        let player = players[idx];
                        player.setPlaybackQuality('tiny'); // force 144p
                        startWatchTimer(player, box);
                    }
                }
            }
        });
    } else {
        // Already loaded: just play on click
        let player = players[idx];
        if(player && player.playVideo) player.playVideo();
    }
}

// Attach click to all boxes
document.querySelectorAll(".video-box").forEach(box=>{
    box.addEventListener("click", ()=>handleClick(box));
});

// Shuffle + preload lite players visually (no autoplay)
document.getElementById("shuffle-load").onclick = ()=>{
    let grid = document.getElementById("video-grid");
    let boxes = [...grid.children];

    // Shuffle
    for(let i=boxes.length-1; i>0; i--){
        let j = Math.floor(Math.random()*(i+1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }
    boxes.forEach(b => grid.appendChild(b));

    // Sequential visual load with 0-1s random delay (thumbnails only)
    let delay = 0;
    boxes.forEach(box=>{
        let r = Math.random()*1000; // 0-1000ms
        setTimeout(()=>{ 
            // Only prepare boxes visually, DO NOT autoplay on mobile
            // iframe creation will happen on user click
        }, delay);
        delay += r;
    });
};
</script>
"""

st.components.v1.html(html, height=700, scrolling=True)