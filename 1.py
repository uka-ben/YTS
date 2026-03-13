# Video repeated 20 times
video_id = "JZYnS6ypa2g"
video_ids = [video_id] * 20

# Generate HTML per video
html_blocks = []

for idx, vid in enumerate(video_ids):
    html_blocks.append(f'''
<div class="video-box" data-video="{vid}" data-index="{idx}" style="cursor:pointer;margin:5px;">
    <img src="https://i.ytimg.com/vi_webp/{vid}/mqdefault.webp"
         loading="lazy"
         style="width:100%;aspect-ratio:16/9;border-radius:6px;">
</div>''')

# Combine HTML with sequential play button
html = f'''
<div style="margin-bottom:10px;">
    <button id="play-all" style="padding:10px 20px;font-size:16px;cursor:pointer;">Play All Sequentially</button>
</div>
<div id="video-grid" style="background:#000;padding:20px;display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;">
    {"".join(html_blocks)}
</div>
<script>
// Load video on click (buffered, 144p)
function loadVideo(box) {{
    if(box.classList.contains("loaded")) return;
    const vid = box.getAttribute("data-video");
    box.innerHTML = `<iframe
        src="https://www.youtube.com/embed/${{vid}}?vq=tiny&playsinline=1&rel=0&modestbranding=1"
        frameborder="0"
        allow="autoplay; fullscreen"
        allowfullscreen
        style="width:100%;aspect-ratio:16/9;border-radius:6px;">
    </iframe>`;
    box.classList.add("loaded");
}}

// Click handler
document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", () => loadVideo(box));
}});

// Sequential play (optional)
document.getElementById("play-all").addEventListener("click", async () => {{
    const boxes = document.querySelectorAll(".video-box");
    for(let i=0;i<boxes.length;i++) {{
        loadVideo(boxes[i]);
        // random delay 2–5s
        await new Promise(r => setTimeout(r, Math.floor(Math.random()*(5000-2000+1))+2000));
    }}
}});
</script>'''

displayHTML(html)