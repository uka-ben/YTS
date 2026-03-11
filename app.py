import streamlit as st

st.set_page_config(layout="wide")

# Video list (demo: same video repeated 20x)
video_id = "JZYnS6ypa2g"
video_ids = [video_id] * 20

# Create small thumbnail blocks
html_blocks = []
for i, vid in enumerate(video_ids):
    html_blocks.append(f"""
<div class="video-box" data-video="{vid}" data-index="{i}">
    <img src="https://i.ytimg.com/vi_webp/{vid}/mqdefault.webp"
         loading="lazy"
         class="thumb">
</div>
""")

# Full HTML + JS (triple quotes to avoid f-string issues)
html = """
<style>
#video-grid {
    background:#000;
    padding:10px;
    display:grid;
    grid-template-columns:repeat(auto-fill,minmax(48px,1fr)); /* very small 70% smaller */
    gap:4px;
}
.video-box {
    cursor:pointer;
    aspect-ratio:16/9;
    position:relative;
    transition:opacity 1s;
    width:100%;
}
.thumb {
    width:100%;
    height:100%;
    object-fit:cover;
    border-radius:4px;
}
button {
    padding:8px 16px;
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
let watchedTimes = {};
let APIready = false;

function onYouTubeIframeAPIReady() {
    APIready = true;
}

function loadPlayer(box) {
    if(box.classList.contains("loaded") || !APIready) return;

    const vid = box.dataset.video;
    const idx = box.dataset.index;
    const targetWatch = Math.floor(Math.random()*(46-35+1))+35;

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
                const player = players[idx];

                if(e.data === YT.PlayerState.PLAYING){
                    if(!watchedTimes[idx]) watchedTimes[idx] = 0;

                    // Force 144p
                    player.setPlaybackQuality('tiny');

                    // Reduce DASH pre-buffer
                    setTimeout(()=>{
                        try {
                            let t = player.getCurrentTime();
                            player.seekTo(t + 0.05, true);
                        } catch(e){}
                    },1500);

                    // Track actual watched seconds
                    const intervalId = setInterval(()=>{
                        if(player.getPlayerState() === YT.PlayerState.PLAYING){
                            watchedTimes[idx] += 1;
                        }

                        if(watchedTimes[idx] >= targetWatch){
                            player.stopVideo();
                            clearInterval(intervalId);
                            box.style.opacity = 0;
                            setTimeout(()=>box.remove(),1000);
                        }
                    },1000);
                }
            }
        }
    });
}

// Click to load individual player
document.querySelectorAll(".video-box").forEach(box=>{
    box.addEventListener("click",()=>loadPlayer(box));
});

// Shuffle + sequential load with 0-1s random delay
document.getElementById("shuffle-load").onclick = ()=>{
    let grid = document.getElementById("video-grid");
    let boxes = [...grid.children];

    // Shuffle
    for(let i=boxes.length-1; i>0; i--){
        let j = Math.floor(Math.random()*(i+1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }
    boxes.forEach(b => grid.appendChild(b));

    // Sequential load with random 0–1s delay
    let delay = 0;
    boxes.forEach(box=>{
        let r = Math.random()*1000;
        setTimeout(()=>{ loadPlayer(box); }, delay);
        delay += r;
    });
};
</script>
"""

st.components.v1.html(html, height=600, scrolling=True)