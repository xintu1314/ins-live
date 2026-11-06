const sharp=require('sharp'),fs=require('fs'),path=require('path');
const ROOT=process.env.INS_EXAMPLE_ROOT||path.resolve(__dirname,'..'),W=720,H=960,FPS=20,DURATION=6;
const clamp=x=>Math.max(0,Math.min(1,x)),smooth=x=>{x=clamp(x);return x*x*(3-2*x)},data=b=>'data:image/png;base64,'+b.toString('base64');
const svg=s=>Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}">${s}</svg>`);
const person=`M339 384 C318 382 299 400 293 420 C289 435 285 456 286 474 C283 488 289 499 301 505 L409 513 C405 499 400 493 396 485 C402 481 414 475 412 462 C414 451 406 442 405 433 C402 410 386 390 365 386Z`;
async function prepare(id){const dir=path.join(ROOT,id);fs.mkdirSync(path.join(dir,'frames'),{recursive:true});await sharp(path.join(dir,'source.png')).resize(W,H).png().toFile(path.join(dir,'base.png'));return fs.readFileSync(path.join(dir,'base.png'));}
function player(t,blur,cover){
 const x=52,y=272,w=616,h=221,p=.19+.57*smooth((t-.55)/4.8),a=Math.min(smooth(t/.45),1-smooth((t-5.55)/.45));
 const bars=Array.from({length:5},(_,i)=>{let v=8+15*(.5+.5*Math.sin(t*7+i*1.3));return `<rect x="${615+i*4}" y="${316-v/2}" width="2.4" height="${v}" rx="1.2" fill="#65666a"/>`}).join('');
 return svg(`<defs><clipPath id="card"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="30"/></clipPath><clipPath id="album"><rect x="76" y="295" width="80" height="80" rx="12"/></clipPath><mask id="front"><rect width="720" height="960" fill="white"/><path d="${person}" fill="black"/></mask><linearGradient id="glass" x2="0.7" y2="1"><stop stop-color="#f0f0f2" stop-opacity=".88"/><stop offset="1" stop-color="#c8c9ce" stop-opacity=".83"/></linearGradient></defs><g opacity="${a}" mask="url(#front)"><rect x="54" y="277" width="616" height="221" rx="30" fill="#15171c" opacity=".11"/><g clip-path="url(#card)"><image x="52" y="272" width="616" height="221" href="${blur}"/><rect x="52" y="272" width="616" height="221" fill="url(#glass)"/></g><rect x="52.6" y="272.6" width="614.8" height="219.8" rx="29.4" fill="none" stroke="white" stroke-opacity=".5"/><image x="76" y="295" width="80" height="80" href="${cover}" clip-path="url(#album)"/><g font-family="Helvetica Neue,Helvetica,Arial,sans-serif" fill="#343539"><text x="174" y="320" font-size="23" font-weight="600">A quieter kind of day</text><text x="174" y="347" font-size="19" fill="#74757a">Courtyard sessions</text><text x="76" y="413" font-size="12" fill="#77787d">0:${String(42+Math.floor(t)).padStart(2,'0')}</text><text x="643" y="413" font-size="12" fill="#77787d" text-anchor="end">−3:18</text></g>${bars}<path d="M120 407 H596" stroke="#97989d" stroke-opacity=".47" stroke-width="5" stroke-linecap="round"/><path d="M120 407 H${120+p*476}" stroke="#66676c" stroke-width="5" stroke-linecap="round"/><circle cx="${120+p*476}" cy="407" r="4.4" fill="#57585d"/><g fill="#44454a"><path d="M230 439 L212 452 L230 465Z M213 439 L195 452 L213 465Z"/><rect x="350" y="438" width="7" height="28" rx="1.3"/><rect x="364" y="438" width="7" height="28" rx="1.3"/><path d="M492 439 L510 452 L492 465Z M509 439 L527 452 L509 465Z"/></g><g transform="translate(618 450)" fill="none" stroke="#5b5c61" stroke-width="1.8"><path d="M-12 1 A12 12 0 1 1 12 1 M-8 0 A8 8 0 1 1 8 0 M-4 -1 A4 4 0 1 1 4 -1"/><path d="M-6 10 L0 2 L6 10Z" fill="#5b5c61" stroke="none"/></g></g>`);
}
const words=['Listen','to','the','ocean’s','whisper'];
const widths={'Listen':166,'to':52,'the':82,'ocean’s':217,'whisper':214};
function letters(t){let content='';const release=smooth((t-4.35)/1.5),entrance=smooth(t/.4);let k=0;
 for(let row=0;row<words.length;row++){
 const word=words[row],w=widths[word],step=w/word.length;
 for(let j=0;j<word.length;j++,k++){
  const u=smooth((t-.08*k)/1.05),flight=1-u,side=(k%2?1:-1),dx=side*(95*flight+100*release),dy=(row%2?1:-1)*35*flight-55*release+release*18*Math.sin(j*.7+t*4),rot=side*(14*flight+18*release),alpha=entrance*(1-release)*(.35+.65*u);
  const xx=360-w/2+(j+.5)*step+dx,yy=256+row*99+dy;
  content+=`<text x="${xx}" y="${yy}" text-anchor="middle" transform="rotate(${rot} ${xx} ${yy})" opacity="${alpha}" font-family="Helvetica Neue,Helvetica,Arial,sans-serif" font-size="55" font-weight="750" fill="#f7f6e9">${word[j]==='’'?'&#8217;':word[j]}</text>`;
 }
 }
 // Transparent glass attenuates rear letters, retaining legibility rather than using an opaque rectangular mask.
 const backWeight=.25+.75*smooth((t-1.8)/1.2);
 return svg(`<defs><mask id="glassDepth"><rect width="720" height="960" fill="white"/><path d="M271 373 C274 338 444 336 447 374 L416 633 Q364 658 300 631Z" fill="rgb(${Math.round(255*backWeight)},${Math.round(255*backWeight)},${Math.round(255*backWeight)})"/></mask></defs><g mask="url(#glassDepth)">${content}</g>`);
}
async function main(){
 const mode=process.argv[2]||'keyframes',id=process.argv[3];
 for(const name of id?[id]:['portrait-player','vertical-letters']){
 const dir=path.join(ROOT,name),bg=await prepare(name);let blur,cover;
 if(name==='portrait-player'){
 blur=data(await sharp(bg).extract({left:52,top:272,width:616,height:221}).blur(22).png().toBuffer());
 cover=data(await sharp(svg(`<rect width="720" height="960" fill="#849197"/><path d="M0 580 L720 270 V960 H0Z" fill="#d7d4cb"/><circle cx="480" cy="280" r="150" fill="#c1ccd0"/><path d="M60 800 L600 410" stroke="#515f65" stroke-width="35"/>`)).resize(80,80).png().toBuffer());
 }
 const frame=async(t,out)=>sharp(bg).composite([{input:name==='portrait-player'?player(t,blur,cover):letters(t)}]).png().toFile(out);
 if(mode==='full'){for(let f=0;f<FPS*DURATION;f++)await frame(f/FPS,path.join(dir,'frames',String(f).padStart(3,'0')+'.png'));}
 else{await frame(3.2,path.join(dir,'keyframe.png'));await sharp(path.join(dir,'keyframe.png')).resize({width:390}).toFile(path.join(dir,'phone.png'));for(const [n,t]of [['start',0],['enter',1.0],['hold',3.2],['exit',5.3]])await frame(t,path.join(dir,n+'.png'));}
 console.log(name+' '+mode+' complete');
 }
}
main().catch(e=>{console.error(e);process.exit(1)});
