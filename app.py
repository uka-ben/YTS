import streamlit as st

st.set_page_config(layout="wide")

video_id = "JZYnS6ypa2g"
video_ids = [video_id] * 20

# Smaller thumbnail blocks
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
    grid-template-columns:repeat(auto-fill,minmax(80px,1fr)); /* half size */
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

function loadPlayer(box) {
    if(box.classList.contains("loaded") || !APIready) return;

    const vid = box.dataset.video;
    const idx = box.dataset.index;
    const targetWatch = Math.floor(Math.random()*(46-35+1))+35; // seconds

    box.innerHTML = '<div id="p'+idx+'"></div>';
    box.classList.add("loaded");

    players[idx] = new YT.Player('p'+idx, {
        height:'100%',
        width:'100%',
        videoId:vid,
        playerVars:{
            autoplay:0,
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
                    player.setPlaybackQuality('tiny');

                    // Track real watched time
                    let watchedSec = 0;
                    const tracker = setInterval(()=>{
                        if(player.getPlayerState() === YT.PlayerState.PLAYING){
                            watchedSec += 0.5; // count every 500ms
                        }
                        if(watchedSec >= targetWatch){
                            player.stopVideo();
                            clearInterval(tracker);
                            box.style.opacity = 0;
                            setTimeout(()=>box.remove(),500);
                        }
                    },500);
                }
            }
        }
    });
}

// Click to load a player
document.querySelectorAll(".video-box").forEach(box=>{
    box.addEventListener("click",()=>loadPlayer(box));
});

// Shuffle + sequential load
document.getElementById("shuffle-load").onclick = ()=>{
    let grid = document.getElementById("video-grid");
    let boxes = [...grid.children];

    // Shuffle
    for(let i=boxes.length-1;i>0;i--){
        let j = Math.floor(Math.random()*(i+1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }
    boxes.forEach(b => grid.appendChild(b));

    // Sequential load 0–1s random delay
    let delay = 0;
    boxes.forEach(box=>{
        let r = Math.random()*1000;
        setTimeout(()=>{ loadPlayer(box); }, delay);
        delay += r;
    });
};
</script>
"""

st.components.v1.html(html, height=700, scrolling=True)