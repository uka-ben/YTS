import streamlit as st

st.set_page_config(layout="wide")

# 50 repeated videos
video_id = "JZYnS6ypa2g"
video_ids = [video_id] * 50

# Generate thumbnail HTML blocks
html_blocks = []
for idx, vid in enumerate(video_ids):
    html_blocks.append(f'''
<div class="video-box" data-video="{vid}" data-index="{idx}" style="cursor:pointer;margin:2px;position:relative;transition:opacity 0.5s;">
    <img src="https://i.ytimg.com/vi_webp/{vid}/mqdefault.webp"
         loading="lazy"
         style="width:100%;aspect-ratio:16/9;border-radius:3px;">
</div>
''')

videos_html = "".join(html_blocks)

html = f"""
<div style="margin-bottom:10px;">
    <button id="load-all" style="padding:6px 12px;font-size:12px;cursor:pointer;">
        Shuffle Thumbnails
    </button>
</div>

<div id="video-grid" style="background:#000;padding:10px;
     display:grid;
     grid-template-columns:repeat(auto-fit,minmax(100px,1fr));
     gap:4px;">
{videos_html}
</div>

<script src="https://www.youtube.com/iframe_api"></script>
<script>
let YT_API_ready = false;

// Wait for API ready
function onYouTubeIframeAPIReady() {{
    YT_API_ready = true;
}}

// Replace thumbnail with player on click
function loadVideo(box) {{
    if(box.classList.contains("loaded") || !YT_API_ready) return;

    const vid = box.getAttribute("data-video");
    const maxDuration = Math.floor(Math.random() * (46 - 35 + 1)) + 35;

    // Clear thumbnail
    box.innerHTML = '';
    box.classList.add("loaded");

    const playerDiv = document.createElement("div");
    box.appendChild(playerDiv);

    const player = new YT.Player(playerDiv, {{
        height: '100%',
        width: '100%',
        videoId: vid,
        playerVars: {{
            autoplay: 1,  // start playing after user click
            controls: 1,
            rel: 0,
            modestbranding: 1,
            playsinline: 1,
            vq: 'tiny'
        }},
        events: {{
            onStateChange: function(event) {{
                if(event.data == YT.PlayerState.PLAYING) {{
                    setTimeout(() => {{
                        event.target.stopVideo();
                        box.style.opacity = 0;
                        setTimeout(() => box.remove(), 1000);
                    }}, maxDuration * 1000);
                }}
            }}
        }}
    }});
}}

// Click handler for each thumbnail
document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", () => loadVideo(box));
}});

// "Shuffle Thumbnails" button
document.getElementById("load-all").addEventListener("click", () => {{
    let grid = document.getElementById("video-grid");
    let boxes = Array.from(grid.children);

    // Fisher-Yates shuffle
    for (let i = boxes.length - 1; i > 0; i--) {{
        const j = Math.floor(Math.random() * (i + 1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }}

    // Append back in shuffled order
    boxes.forEach(box => grid.appendChild(box));
}});
</script>
"""

st.components.v1.html(html, height=1000, scrolling=True)