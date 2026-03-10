import streamlit as st

st.set_page_config(layout="wide")

video_id = "JZYnS6ypa2g"
video_ids = [video_id] * 20

html_blocks = []

for idx, vid in enumerate(video_ids):
    html_blocks.append(f"""
<div class="video-box" data-video="{vid}" data-index="{idx}"
style="cursor:pointer;margin:5px;position:relative;transition:opacity 1s;">

<img src="https://i.ytimg.com/vi_webp/{vid}/mqdefault.webp"
loading="lazy"
style="width:100%;aspect-ratio:16/9;border-radius:6px;">

</div>
""")

html = f"""

<div style="margin-bottom:10px;">
<button id="shuffle-load"
style="padding:10px 20px;font-size:16px;cursor:pointer;">
Shuffle + Load All Players
</button>
</div>

<div id="video-grid"
style="background:#000;padding:20px;
display:grid;
grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
gap:10px;">

{''.join(html_blocks)}

</div>

<script src="https://www.youtube.com/iframe_api"></script>

<script>

let YT_API_ready=false

function onYouTubeIframeAPIReady(){{
    YT_API_ready=true
}}

function loadVideo(box){{

if(box.classList.contains("loaded") || !YT_API_ready) return

const vid=box.getAttribute("data-video")

const maxDuration=Math.floor(Math.random()*(46-35+1))+35

box.innerHTML=''
box.classList.add("loaded")

const playerDiv=document.createElement("div")

box.appendChild(playerDiv)

const player=new YT.Player(playerDiv,{{
height:'100%',
width:'100%',
videoId:vid,

playerVars:{{
autoplay:0,
controls:1,
rel:0,
modestbranding:1,
playsinline:1,
vq:'tiny'
}},

events:{{

onReady:(event)=>{{

event.target.addEventListener('onStateChange',function(e){{

if(e.data==YT.PlayerState.PLAYING){{

setTimeout(()=>{{

event.target.stopVideo()

box.style.opacity=0

setTimeout(()=>box.remove(),1000)

}},maxDuration*1000)

}}

}})

}}

}}

}})

}}

document.querySelectorAll(".video-box").forEach(box=>{{

box.addEventListener("click",()=>loadVideo(box))

}})

document.getElementById("shuffle-load").addEventListener("click",()=>{{

let grid=document.getElementById("video-grid")

let boxes=Array.from(grid.children)

for(let i=boxes.length-1;i>0;i--){{
const j=Math.floor(Math.random()*(i+1))
;[boxes[i],boxes[j]]=[boxes[j],boxes[i]]
}}

boxes.forEach(box=>grid.appendChild(box))

let delay=0

boxes.forEach(box=>{{

setTimeout(()=>{{
loadVideo(box)
}},delay)

delay+=400

}})

}})

</script>

"""

st.components.v1.html(html, height=900, scrolling=True)