import streamlit as st

st.set_page_config(layout="wide")

video_id = "JZYnS6ypa2g"
video_ids = [video_id] * 40   # you can increase to 100+

html_blocks = []

for vid in video_ids:
    html_blocks.append(f"""
<div class="video-box" data-video="{vid}">
    <img
      src="https://i.ytimg.com/vi_webp/{vid}/hqdefault.webp"
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
grid-template-columns:repeat(auto-fill,minmax(140px,1fr));
gap:8px;
}}

.video-box {{
position:relative;
cursor:pointer;
aspect-ratio:16/9;
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

<button id="shuffle">Shuffle Grid</button>

<div id="video-grid">
{''.join(html_blocks)}
</div>

<script>

function createPlayer(box){{

if(box.classList.contains("loaded")) return

const vid = box.dataset.video

const maxDuration = Math.floor(Math.random()*(46-35+1))+35

const iframe = document.createElement("iframe")

iframe.src =
"https://www.youtube.com/embed/"+vid+
"?autoplay=1&mute=0&controls=1&rel=0&modestbranding=1&vq=tiny"

iframe.allow = "autoplay"

box.innerHTML = ""

box.appendChild(iframe)

box.classList.add("loaded")

setTimeout(()=>{{

iframe.src=""

box.style.opacity=0

setTimeout(()=>box.remove(),1000)

}}, maxDuration*1000)

}}

document.querySelectorAll(".video-box").forEach(box=>{{

box.addEventListener("click", ()=>createPlayer(box))

}})

document.getElementById("shuffle").onclick=()=>{{

let grid=document.getElementById("video-grid")

let nodes=[...grid.children]

for(let i=nodes.length-1;i>0;i--){{

let j=Math.floor(Math.random()*(i+1))

;[nodes[i],nodes[j]]=[nodes[j],nodes[i]]

}}

nodes.forEach(n=>grid.appendChild(n))

}}

</script>

"""

st.components.v1.html(html, height=900, scrolling=True)