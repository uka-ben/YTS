import streamlit as st

st.set_page_config(layout="wide")

video_id = "JZYnS6ypa2g"
video_ids = [video_id] * 50

# Generate HTML blocks
html_blocks = []
for idx, vid in enumerate(video_ids):
    html_blocks.append(f'''
<div class="video-box" data-video="{vid}" data-index="{idx}" style="cursor:pointer;margin:2px;position:relative;transition:opacity 0.5s;">
    <img src="https://i.ytimg.com/vi_webp/{vid}/mqdefault.webp"
         loading="lazy"
         style="width:100%;aspect-ratio:16/9;border-radius:3px;">
</div>
''')

# Join blocks first
videos_html = "".join(html_blocks)

# Full HTML (no f-string inside JS braces!)
html = """
<div style="margin-bottom:10px;">
    <button id="load-all" style="padding:6px 12px;font-size:12px;cursor:pointer;">
        Load All Videos (Random Order)
    </button>
</div>

<div id="video-grid" style="background:#000;padding:10px;
     display:grid;
     grid-template-columns:repeat(auto-fit,minmax(100px,1fr));
     gap:4px;">
""" + videos_html + """
</div>

<script src="https://www.youtube.com/iframe_api"></script>
<script>
let YT_API_ready = false;

function onYouTubeIframeAPIReady() {{
    YT_API_ready = true;
}}

function loadVideo(box) {{
    if(box.classList.contains("loaded") || !YT_API_ready) return;

    const vid = box.getAttribute("data-video");
    const maxDuration = Math.floor(Math.random() * (46 - 35 + 1)) + 35;

    box.innerHTML = '';
    box.classList.add("loaded");

    const playerDiv = document.createElement("div");
    box.appendChild(playerDiv);

    const player = new YT.Player(playerDiv, {{
        height: '100%',
        width: '100%',
        videoId: vid,
        playerVars: {{
            autoplay:0,
            controls:1,
            rel:0,
            modestbranding:1,
            playsinline:1,
            vq:'tiny'
        }},
        events: {{
            onReady: (event) => {{
                event.target.addEventListener('onStateChange', function(e) {{
                    if(e.data == YT.PlayerState.PLAYING) {{
                        setTimeout(() => {{
                            event.target.stopVideo();
                            box.style.opacity = 0;
                            setTimeout(() => box.remove(), 1000);
                        }}, maxDuration * 1000);
                    }}
                }});
            }}
        }}
    }});
}}

document.querySelectorAll(".video-box").forEach(box => {{
    box.addEventListener("click", () => loadVideo(box));
}});

document.getElementById("load-all").addEventListener("click", async () => {{
    let boxes = Array.from(document.querySelectorAll(".video-box"));
    for (let i = boxes.length - 1; i > 0; i--) {{
        const j = Math.floor(Math.random() * (i + 1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }}
    for(let i=0; i<boxes.length; i++) {{
        loadVideo(boxes[i]);
        await new Promise(r => setTimeout(r, Math.floor(Math.random()*(5000-2000+1))+2000));
    }}
}});
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)