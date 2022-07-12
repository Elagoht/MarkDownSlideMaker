// slide control
let slides=[...document.getElementsByClassName("slide")]
const navnum=document.getElementById("slide-number")
const header=document.getElementById("slide_info")
const controlbar=document.getElementById("controls")
const slidecount=document.getElementById("slide-count")
const transcon=document.getElementById("transition-con")
slidecount.innerText=" / "+slides.length
navnum.max=slides.length
setTimeout(()=>{
  transcon.style.display="none"
},1000)
let cur=1
let controllable=false
slides[0].style.display="flex"
const hide_all=()=>{
  slides.forEach(sld=>{
    sld.style.display="none"
  })
}
const go_to=nth=>{
  if (controllable) {
    if (nth>slides.length) {nth=slides.length}
    else if (nth<1) {nth=1}
    else {
      transcon.innerHTML="        <div id=\"transition\"></div>\n"
      transcon.style.display="flex"
    }
    setTimeout(()=>{
      hide_all()
      cur=nth
      slides[cur-1].style.display="flex"
      navnum.value=cur
    },500)
    setTimeout(()=>{
      transcon.style.display="none"
    },1000)
    show_hud(false,1000)
  }
}
const slide_first=()=>{go_to(1)}
const slide_last=()=>{go_to(slides.length)}
const slide_next=()=>{go_to(cur+1)}
const slide_prev=()=>{go_to(cur-1)}
hide_all()
slides[0].style.display="flex"
// mouse move and show gui
const hide_hud=()=>{
  header.style.opacity=0
  controlbar.style.opacity=0
}
let hudcd=setTimeout(hide_hud,2000)
const show_hud=(title=true,time=2000)=>{
  if (title) {header.style.opacity=1}
  controlbar.style.opacity=1
  clearTimeout(hudcd)
  hudcd=setTimeout(hide_hud,time)}
document.onmousemove=()=>{show_hud()}
document.onclick=()=>{show_hud()}
// control shortcuts
window.onkeydown=(key)=>{
  if ([37,65,72,33].includes(key.keyCode)) {slide_prev()}
  if ([39,32,68,76,34].includes(key.keyCode)) {slide_next()}
  if (key.keyCode===36) {slide_first()}
  if (key.keyCode===35) {slide_last()}
  if (key.keyCode===13) {go_to(parseInt(navnum.value))}
  if (document.getElementById("never-warn")) {
    const neverwarn=document.getElementById("never-warn")
    if (key.keyCode===87) {neverwarn.checked=!neverwarn.checked}
    if ([122,13,85].includes(key.keyCode)) {controllable=true;localStorage["dontwarn"]=neverwarn.checked;document.getElementById('warn-con').remove();}
  }
}
// don't show warning option
if (localStorage["dontwarn"]==="true") {
  console.log("tamam bak uyarmıyorum")
  controllable=true
} else {
  if ((/Mobi|Android/i.test(navigator.userAgent)) || (window.innerWidth==screen.width && window.innerHeight==screen.height)) {controllable=true}
  else {
    document.getElementsByTagName("body")[0].insertAdjacentHTML('afterend',`<div id="warn-con">
    <div id="warn">
        <div id="warn-text">For best experience go fullscreen by pressing F11.</div>
        <div id="not-warn">
            <label><input id="never-warn" type="checkbox">Don't <ins>w</ins>arn me again.</label>
            <div class="warn-button" onclick="controllable=true;localStorage['dontwarn']=document.getElementById('never-warn').checked;document.getElementById('warn-con').remove();">I <ins>U</ins>nderstand</div>
        </div>
    </div>
</div>
`)
  }
}
