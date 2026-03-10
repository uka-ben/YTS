import streamlit as st

st.set_page_config(page_title="Compact YouTube Grid", layout="wide")

video_id = "JZYnS6ypa2g"
video_ids = [video_id]*100

blocks = []

for i, vid in enumerate(video_ids):
    blocks.append("""
    <div class="video-box" id="player{0}" data-video="{1}" data-index="{0}">
        <img src="https://i.ytimg.com/vi_webp/{1}/mqdefault.webp" loading="lazy">
    </div>
    """.format(i, vid))

html = """
<div style="margin-bottom:6px;">
<button id="load-all">Load All Videos (Random Countdown Enabled)</button>
</div>

<div id="video-grid">
{blocks}
</div>

<style>

#video-grid {{
background:#000;
padding:6px;
display:grid;
grid-template-columns:repeat(auto-fit,minmax(60px,1fr));
gap:4px;
max-height:90vh;
overflow-y:auto;
}}

.video-box {{
width:100%;
aspect-ratio:16/9;
cursor:pointer;
}}

.video-box img {{
width:100%;
height:100%;
object-fit:cover;
border-radius:2px;
}}

.video-box iframe {{
width:100% !important;
height:100% !important;
border:0;
}}

.fade-out {{
opacity:0;
transition:opacity 0.5s;
}}

</style>

<script src="https://www.youtube.com/iframe_api"></script>

<script>

let players = {{}};
let timers = {{}};

// Generate random stop time for each video
function randomStopTime(){{
    return Math.floor(Math.random()*(45-35+1))+35;
}}

// Load players on click of each box
function onYouTubeIframeAPIReady(){{
    document.querySelectorAll(".video-box").forEach(box=>{{
        let vid = box.dataset.video;
        let idx = box.dataset.index;

        box.addEventListener("click", ()=>loadVideo(idx, vid));
    }});
}}

// Load video iframe but do NOT play
function loadVideo(index, video){{

    if(players[index]) {{
        // already loaded, do nothing
        return;
    }}

    players[index] = new YT.Player("player"+index,{{
        width:"100%",
        height:"100%",
        videoId:video,
        playerVars:{{
            autoplay:0,
            playsinline:1,
            rel:0,
            vq:"tiny",
            controls:1
        }},
        events:{{
            'onStateChange': function(e){{
                if(e.data === YT.PlayerState.PLAYING){{
                    // Start random stop timer only AFTER user manually plays
                    clearTimeout(timers[index]);
                    let stop = randomStopTime();
                    timers[index] = setTimeout(()=>{{
                        players[index].stopVideo();
                        players[index].destroy();
                        delete players[index];

                        let box = document.getElementById("player"+index);
                        box.classList.add("fade-out");
                        setTimeout(()=>{{box.remove()}},500);

                    }}, stop*1000);
                }}
            }}
        }}
    }});
}}

// "Load All" button — only loads players, does NOT autoplay
document.getElementById("load-all").addEventListener("click", ()=>{{
    const boxes = document.querySelectorAll(".video-box");
    for(let i=0;i<boxes.length;i++) {{
        let vid = boxes[i].dataset.video;
        loadVideo(i, vid);
    }}
}});

</script>
""".format(blocks="".join(blocks))

st.components.v1.html(html, height=900, scrolling=True)