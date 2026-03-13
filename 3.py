import streamlit as st

st.set_page_config(layout="wide")

# 20 videos (same video repeated for demo)
video_id = "vKqRZXGBdxo"
video_ids = [video_id] * 20

# Create thumbnail blocks
html_blocks = []
for i, vid in enumerate(video_ids):
    html_blocks.append(f"""
<div class="video-box" data-video="{vid}" data-index="{i}">
    <img src="https://i.ytimg.com/vi_webp/{vid}/mqdefault.webp"
         loading="lazy"
         class="thumb">
</div>
""")

# Full HTML + JS (triple quotes, no f-string)
html = """
<style>
#video-grid {
    background:#000;
    padding:20px;
    display:grid;
    grid-template-columns:repeat(auto-fill,minmax(160px,1fr));
    gap:8px;
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
    border-radius:6px;
}
button {
    padding:10px 20px;
    font-size:16px;
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
    const maxDuration = Math.floor(Math.random()*(46-35+1))+35;

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
                    // Force 144p again
                    player.setPlaybackQuality('tiny');

                    // Reduce DASH buffer to save data
                    setTimeout(()=>{
                        try {
                            let t = player.getCurrentTime();
                            player.seekTo(t + 0.05, true);
                        } catch(e){}
                    },1500);

                    // Stop video after random 35-46 sec
                    setTimeout(()=>{
                        player.stopVideo();
                        box.style.opacity = 0;
                        setTimeout(()=>box.remove(),1000);
                    }, maxDuration * 1000);
                }
            }
        }
    });
}

// Click to load a player
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

    // Sequential load with random 0-1s delay
    let delay = 0;
    boxes.forEach(box=>{
        let r = Math.random()*1000; // 0-1000ms
        setTimeout(()=>{ loadPlayer(box); }, delay);
        delay += r;
    });
};
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)