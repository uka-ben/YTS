import streamlit as st

st.set_page_config(layout="wide")

video_id = "ZYcZ_nBLG6Y"  # Using your Version 7 video ID
video_ids = [video_id] * 20

html_blocks = []

for vid in video_ids:
    html_blocks.append(f"""
<div class="video-box" data-video="{vid}">
    <img src="https://i.ytimg.com/vi_webp/{vid}/mqdefault.webp"
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
grid-template-columns:repeat(auto-fill,minmax(160px,1fr));
gap:8px;
}}
.video-box {{
cursor:pointer;
aspect-ratio:16/9;
position:relative;
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

<button id="shuffle-load">Shuffle + Load Players</button>

<div id="video-grid">
{''.join(html_blocks)}
</div>

<script>
function loadPlayer(box) {{
    if(box.classList.contains("loaded")) return

    const vid = box.dataset.video
    const boxId = 'box_' + Math.random().toString(36).substr(2, 9) // Unique ID

    /* mixed start strategy */
    let start
    if(Math.random() < 0.7){{
        start = 0
    }}else{{
        start = Math.floor(Math.random()*200)
    }}

    const targetDuration = Math.floor(Math.random()*(46-35+1))+35  // Target play time
    const end = start + targetDuration

    const iframe = document.createElement("iframe")
    iframe.src =
    "https://www.youtube.com/embed/"+vid+
    "?autoplay=0"+
    "&controls=1"+
    "&rel=0"+
    "&modestbranding=1"+
    "&vq=tiny"+
    "&start="+start+
    "&end="+end

    iframe.allow="autoplay"
    iframe.setAttribute('data-box-id', boxId)
    
    box.innerHTML=""
    box.appendChild(iframe)
    box.classList.add("loaded")
    box.setAttribute('data-box-id', boxId)

    let actualPlayedTime = 0
    let playbackInterval = null
    let isDestroyed = false
    let qualityInterval = null

    /* detect play click */
    box.addEventListener("click", () => {{
        if (isDestroyed) return
        
        console.log(`Video ${{boxId}} clicked to play`)
        
        /* Force 144p quality every second */
        qualityInterval = setInterval(() => {{
            try {{
                if (!isDestroyed && iframe && iframe.contentWindow) {{
                    iframe.contentWindow.postMessage(JSON.stringify({{
                        event:'command',
                        func:'setPlaybackQuality',
                        args:['tiny']
                    }}), '*')
                }}
            }} catch(e){{}}
        }}, 1000)

        /* Track actual playback time using YouTube's API via postMessage */
        // We can't directly track playback in iframe, so we'll use a combination approach
        
        // Method 1: Use the end parameter as a safety net (already set in iframe src)
        // Method 2: Track time approximately with an interval that checks if video is still playing
        
        // Since we can't easily get playback state from iframe, we'll use a simplified approach:
        // The iframe will automatically stop at 'end' time, so we just need to detect when it stops
        
        // Listen for when video might have ended (can't directly detect, so we'll poll)
        let checkInterval = setInterval(() => {{
            try {{
                if (isDestroyed || !iframe || !iframe.contentWindow) {{
                    clearInterval(checkInterval)
                    return
                }}
                
                // Request current time from YouTube player
                iframe.contentWindow.postMessage(JSON.stringify({{
                    event:'listening',
                    id: boxId
                }}), '*')
            }} catch(e){{}}
        }}, 1000)
        
        // Listen for messages from YouTube iframe
        window.addEventListener('message', function(event) {{
            try {{
                if (isDestroyed) return
                
                let data = JSON.parse(event.data)
                if (data.id === boxId && data.info && data.info.currentTime) {{
                    actualPlayedTime = Math.floor(data.info.currentTime) - start
                    if (actualPlayedTime < 0) actualPlayedTime = 0
                    
                    console.log(`${{boxId}} played: ${{actualPlayedTime}}/${{targetDuration}}`)
                    
                    // Check if we've reached target duration
                    if (actualPlayedTime >= targetDuration && !isDestroyed) {{
                        destroyVideo()
                    }}
                }}
            }} catch(e){{}}
        }})
        
        /* Simplified approach: Use a timer but check if video is likely still playing */
        // Since we can't perfectly track, we'll use a combination of timer and checking if iframe exists
        let startTime = Date.now()
        let safetyTimer = setInterval(() => {{
            let elapsedSeconds = Math.floor((Date.now() - startTime) / 1000)
            
            // If we've passed the target duration and video hasn't been destroyed yet
            if (elapsedSeconds >= targetDuration && !isDestroyed) {{
                console.log(`${{boxId}} timer-based destroy triggered`)
                destroyVideo()
            }}
        }}, 1000)
        
        /* Main destroy function */
        function destroyVideo() {{
            if (isDestroyed) return
            isDestroyed = true
            
            console.log(`Destroying ${{boxId}}`)
            
            // Clear all intervals
            if (qualityInterval) {{
                clearInterval(qualityInterval)
                qualityInterval = null
            }}
            if (playbackInterval) {{
                clearInterval(playbackInterval)
                playbackInterval = null
            }}
            if (safetyTimer) {{
                clearInterval(safetyTimer)
                safetyTimer = null
            }}
            
            // Clear iframe source (nuclear option)
            if (iframe) {{
                iframe.src = ""
            }}
            
            // Fade out and remove
            box.style.opacity = 0
            setTimeout(() => {{
                if (box && box.parentNode) {{
                    box.remove()
                    console.log(`${{boxId}} removed from grid`)
                }}
            }}, 1000)
        }}
        
        /* Fallback: The end parameter in iframe src will stop video at 'end' time */
        /* So even if our tracking fails, video won't play beyond end */
        
    }}, {{once:true}})
}}

document.querySelectorAll(".video-box").forEach(box=>{{
    box.addEventListener("click",()=>loadPlayer(box))
}})

document.getElementById("shuffle-load").onclick=()=>{{
    let grid=document.getElementById("video-grid")
    let boxes=[...grid.children]

    /* shuffle grid */
    for(let i=boxes.length-1;i>0;i--) {{
        let j=Math.floor(Math.random()*(i+1))
        ;[boxes[i],boxes[j]]=[boxes[j],boxes[i]]
    }}
    boxes.forEach(b=>grid.appendChild(b))

    /* sequential loading with 1–5s random delay */
    let delay=0
    boxes.forEach(box=>{{
        let randomDelay = 1000 + Math.random()*4000  // 1–5 seconds
        setTimeout(()=>{{
            loadPlayer(box)
        }}, delay)
        delay += randomDelay
    }})
}}
</script>
"""

st.components.v1.html(html, height=900, scrolling=True)