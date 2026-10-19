/* Local-only 3D perspective renderer. No external assets, network calls or user data. */
(() => {
  'use strict';
  const w = window, d = document;
  if (w.__araPremiumGlobe159999) { w.__araPremiumGlobe159999.refresh(); return; }
  const reduced = w.matchMedia('(prefers-reduced-motion: reduce)');
  let canvas = null, ctx = null, raf = 0, last = 0, rotation = 0, observer = null;
  let visible = true;
  const THREE_D = Math.PI * 2;
  function linePoint(lat, lon) {
    return [Math.cos(lat)*Math.cos(lon), Math.sin(lat), Math.cos(lat)*Math.sin(lon)];
  }
  function transform(p, t) {
    const cy = Math.cos(t), sy = Math.sin(t), cx = Math.cos(-.22), sx = Math.sin(-.22);
    const x = p[0]*cy + p[2]*sy, z = -p[0]*sy + p[2]*cy;
    return [x, p[1]*cx-z*sx, p[1]*sx+z*cx];
  }
  function project(p, mid, radius) {
    const perspective = 3.35 / (3.35 - p[2]*.42);
    return [mid+p[0]*radius*perspective, mid-p[1]*radius*perspective];
  }
  function draw() {
    if (!canvas || !canvas.isConnected || !ctx) return;
    const side = canvas.clientWidth || 440;
    if (side < 8) return;
    const ratio = Math.min(w.devicePixelRatio || 1, 2);
    const pixels = Math.round(side*ratio);
    if (canvas.width !== pixels || canvas.height !== pixels) {
      canvas.width = pixels; canvas.height = pixels;
    }
    const c = ctx;
    c.setTransform(ratio,0,0,ratio,0,0);
    c.clearRect(0,0,side,side);
    const mid = side/2, radius = side*.315;
    const glow = c.createRadialGradient(mid,mid,side*.04,mid,mid,side*.45);
    glow.addColorStop(0,'rgba(91,113,207,.22)');
    glow.addColorStop(.5,'rgba(69,76,152,.15)');
    glow.addColorStop(1,'rgba(40,44,99,0)');
    c.fillStyle=glow;c.beginPath();c.arc(mid,mid,side*.45,0,THREE_D);c.fill();
    const sphere=c.createRadialGradient(mid-radius*.25,mid-radius*.38,radius*.03,mid,mid,radius*1.13);
    sphere.addColorStop(0,'rgba(139,171,255,.26)');sphere.addColorStop(.55,'rgba(54,84,167,.16)');sphere.addColorStop(1,'rgba(8,15,47,.07)');
    c.beginPath();c.arc(mid,mid,radius,0,THREE_D);c.fillStyle=sphere;c.fill();
    // Sort near-side and far-side mesh separately: rear meridians remain visible, but muted.
    const segments = [];
    function pathSegment(a,b){
      const pa=transform(a,rotation), pb=transform(b,rotation);
      segments.push({a:project(pa,mid,radius),b:project(pb,mid,radius),depth:(pa[2]+pb[2])/2});
    }
    for(let i=-5;i<=5;i++) {
      const lat=i*Math.PI/12;
      for(let j=0;j<72;j++) pathSegment(linePoint(lat,j*THREE_D/72),linePoint(lat,(j+1)*THREE_D/72));
    }
    for(let i=0;i<20;i++) {
      const lon=i*THREE_D/20;
      for(let j=-22;j<22;j++) pathSegment(linePoint(j*Math.PI/46,lon),linePoint((j+1)*Math.PI/46,lon));
    }
    for(const isFront of [false,true]) {
      c.beginPath();
      for(const s of segments) if((s.depth>=0)===isFront){c.moveTo(...s.a);c.lineTo(...s.b);}
      c.lineWidth=isFront?1.05:.55;
      c.strokeStyle=isFront?'rgba(127,189,255,.68)':'rgba(101,116,201,.18)';
      c.stroke();
    }
    // Moving nodes: highlights are brighter on the near hemisphere.
    for(let i=0;i<156;i++) {
      const lat=Math.asin(-1+2*((i*.61803398875)%1));
      const lon=i*2.399963229728653;
      const p=transform(linePoint(lat,lon),rotation);
      const xy=project(p,mid,radius);
      const strength=p[2]>0?.6+.4*p[2]:.14;
      const size=p[2]>0?1.2+1.05*p[2]:.65;
      c.beginPath();c.arc(xy[0],xy[1],size,0,THREE_D);
      c.fillStyle=i%8===0?`rgba(236,200,148,${strength})`:`rgba(166,185,255,${strength})`;c.fill();
    }
    function orbital(tilt, rx, ry, color, phase) {
      // Orbital plane with perspective depth; draw the rear arc before the front.
      for(const front of [false,true]) {
        c.beginPath(); let pen=false;
        for(let i=0;i<=240;i++) {
          const a=i*THREE_D/240+phase, x=rx*Math.cos(a),y=ry*Math.sin(a);
          const yy=y*Math.cos(tilt)-x*Math.sin(tilt);
          const zz=y*Math.sin(tilt)+x*Math.cos(tilt);
          if((zz>=0)!==front){pen=false;continue;}
          const perspective=1+.08*zz;
          const px=mid+(x*Math.cos(tilt)+y*Math.sin(tilt))*perspective;
          const py=mid-yy*perspective;
          if(!pen)c.moveTo(px,py);else c.lineTo(px,py);
          pen=true;
        }
        c.lineWidth=front?2.1:1.05;
        c.strokeStyle=front?color:'rgba(134,129,199,.20)';
        c.shadowColor=front?color:'transparent';c.shadowBlur=front?8:0;c.stroke();c.shadowBlur=0;
      }
    }
    orbital(-.26,radius*1.37,radius*.39,'rgba(224,195,139,.85)',rotation*.14);
    orbital(1.08,radius*1.20,radius*.52,'rgba(162,140,244,.80)',rotation*.11);
    c.beginPath();c.arc(mid,mid,radius,0,THREE_D);
    c.strokeStyle='rgba(173,201,255,.35)';c.lineWidth=1.5;c.stroke();
    // Switch to Canvas only when its first frame has actually rendered.
    if (canvas.parentElement) canvas.parentElement.classList.add('ara-canvas-ready');
  }
  function frame(time) {
    raf=0;
    if (!canvas || !canvas.isConnected || d.hidden || !visible) return;
    if(!reduced.matches) rotation += Math.min((time-(last||time))/1000,.05)*.20;
    last=time;
    draw();
    if (!reduced.matches) raf=w.requestAnimationFrame(frame);
  }
  function schedule(){if(!raf && canvas)raf=w.requestAnimationFrame(frame);}
  function refresh() {
    const next=d.getElementById('ara-premium-globe');
    if(next!==canvas) {
      if(observer)observer.disconnect();
      canvas=next;
      if (next && next.parentElement) next.parentElement.classList.remove('ara-canvas-ready');
      ctx=next?next.getContext('2d',{alpha:true}):null;
      if(canvas && w.IntersectionObserver) {
        observer=new IntersectionObserver(entries => {visible=entries.some(e=>e.isIntersecting);if(visible){last=0;schedule();}}, {rootMargin:'60px'});
        observer.observe(canvas);
      } else visible=true;
    }
    schedule();
  }
  const mutations=new MutationObserver(() => {
    if (d.getElementById('ara-premium-globe')!==canvas) refresh();
  });
  mutations.observe(d.body,{childList:true,subtree:true});
  d.addEventListener('visibilitychange',()=>{last=0;schedule()});
  w.addEventListener('resize',schedule,{passive:true});
  if (reduced.addEventListener) reduced.addEventListener('change',()=>{last=0;schedule()});
  w.__araPremiumGlobe159999={refresh,version:'1.5.9.9.9'};
  refresh();
})();
