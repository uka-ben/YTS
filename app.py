# Video repeated 50 times
video_id = "JZYnS6ypa2g"
video_ids = [video_id] * 50

# Generate HTML per video
html_blocks = []
for idx, vid in enumerate(video_ids):
    html_blocks.append(f'''
<div class="video-box" data-video="{vid}" data-index="{idx}" style="cursor:pointer;margin:2px;position:relative;transition:opacity 0.5s;">
    <img src="https://i.ytimg.com/vi_webp/{vid}/mqdefault.webp"
         loading="lazy"
         style="width:100%;aspect-ratio:16/9;border-radius:3px;">
</div>
''')

# Combine HTML with shuffle button and very small grid
html = f'''
<div style="margin-bottom:10px;">
    <button id="load-all" style="padding:6px 12px;font-size:12px;cursor:pointer;">
        Load All Videos (Random Order)
    </button>
</div>

<div id="video-grid" style="background:#000;padding:10px;
     display:grid;
     grid-template-columns:repeat(auto-fit,minmax(100px,1fr));
     gap:4px;">
    {"".join(html_blocks)}
</div>

<!-- Load YouTube IFrame API -->
<script src="https://www.youtube.com/iframe_api"></script>
<script>
let YT_API_ready = false;

// Wait for API ready
function onYouTubeIframeAPIReady() {
    YT_API_ready = true;
}

// Load video on click, with max duration and fade-out
function loadVideo(box) {
    if(box.classList.contains("loaded") || !YT_API_ready) return;

    const vid = box.getAttribute("data-video");
    const maxDuration = Math.floor(Math.random() * (46 - 35 + 1)) + 35; // 35-46 sec

    box.innerHTML = '';
    box.classList.add("loaded");

    const playerDiv = document.createElement("div");
    box.appendChild(playerDiv);

    const player = new YT.Player(playerDiv, {
        height: '100%',
        width: '100%',
        videoId: vid,
        playerVars: {
            autoplay: 0,   // manual play only
            controls: 1,
            rel: 0,
            modestbranding: 1,
            playsinline: 1,
            vq: 'tiny'
        },
        events: {
            onReady: (event) => {
                event.target.addEventListener('onStateChange', function(e) {
                    if(e.data == YT.PlayerState.PLAYING) {
                        setTimeout(() => {
                            event.target.stopVideo();
                            box.style.opacity = 0;
                            setTimeout(() => box.remove(), 1000);
                        }, maxDuration * 1000);
                    }
                });
            }
        }
    });
}

// Click handler for each video
document.querySelectorAll(".video-box").forEach(box => {
    box.addEventListener("click", () => loadVideo(box));
});

// "Load All" button: only shuffles boxes
document.getElementById("load-all").addEventListener("click", async () => {
    let boxes = Array.from(document.querySelectorAll(".video-box"));

    // Shuffle array (Fisher-Yates)
    for (let i = boxes.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [boxes[i], boxes[j]] = [boxes[j], boxes[i]];
    }

    // Load each video box in shuffled order, no autoplay
    for(let i=0; i<boxes.length; i++) {
        loadVideo(boxes[i]);
        await new Promise(r => setTimeout(r, Math.floor(Math.random()*(5000-2000+1))+2000));
    }
});
</script>
'''

displayHTML(html)