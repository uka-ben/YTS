import streamlit as st

st.set_page_config(layout="wide")

video_id = "ywivtZhyjx4"
video_ids = [video_id] * 50

html_blocks = []
for idx, vid in enumerate(video_ids):
    html_blocks.append(f'''
<div class="video-box" data-video="{vid}" data-index="{idx}">
    <img src="https://i.ytimg.com/vi_webp/{vid}/mqdefault.webp"
         loading="lazy"
         class="thumb"
         alt="Video {idx + 1}">
</div>''')

html = f'''
<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}
#video-grid {{
    background: #000;
    padding: 0;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 0;
}}
.video-box {{
    aspect-ratio: 16/9;
    position: relative;
    overflow: hidden;
    background: #000;
}}
.thumb {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    cursor: pointer;
}}
iframe {{
    width: 100%;
    height: 100%;
    border: none;
    display: block;
}}
.button-container {{
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
    align-items: center;
    flex-wrap: wrap;
}}
button {{
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
}}
</style>

<div class="button-container">
    <button id="shuffle-btn">Shuffle Grid</button>
    <button id="reset-btn">Reset All</button>
</div>

<div id="video-grid">
    {''.join(html_blocks)}
</div>

<script>
// Clicking the thumbnail loads the YouTube player (paused, no autoplay).
// User must then click YouTube's native red play button to start → view counts.
function loadPlayer(box) {{
    if (box.classList.contains("playing")) return;

    const vid = box.getAttribute("data-video");

    box.innerHTML = `<iframe
        src="https://www.youtube.com/embed/${{vid}}?playsinline=1&rel=0&modestbranding=1"
        frameborder="0"
        allow="autoplay; fullscreen; encrypted-media"
        allowfullscreen>
    </iframe>`;
    box.classList.add("playing");
}}

document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", () => loadPlayer(box));
}});

document.getElementById("shuffle-btn").addEventListener("click", () => {{
    const grid = document.getElementById("video-grid");
    const boxes = [...grid.children];
    for (let i = boxes.length - 1; i > 0; i--) {{
        const j = Math.floor(Math.random() * (i + 1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }}
    boxes.forEach(b => grid.appendChild(b));
}});

document.getElementById("reset-btn").addEventListener("click", () => {{
    location.reload();
}});
</script>
'''

st.components.v1.html(html, height=1000, scrolling=True)