/* 课件 Bahan ajar HSK 5 untuk Zenta 汉: penampil slide satu pelajaran satu bahan ajar. Gaya: aset/bahan-ajar.css. Dimuat dari index.html (defer).

   Siapa yang bisa membuka
   - Hanya akun pemilik (peran "owner"/"pemilik"). Chip 课件 di pilihan bagian Materi disembunyikan untuk akun lain (atribut hidden).
     Itu hanya kemudahan tampilan: yang menjaga isinya adalah server (lihat bawah), jadi menampilkan chip lewat konsol tidak membuka apa pun.

   Dari mana isinya
   - Isi slide (teks buku dan penjelasan laoshi) TIDAK ada di repo. Diminta ke server: POST hsk-u-isi {secret: token sesi, paket: "bj5"}.
     Workflow n8n hanya melayani paket bj5 kepada pemilik. Jawaban: {ok, paket, v, D: [slide, ...]}. Salinan disimpan di Cache API
     (zenta-isi-v2, kunci /__isi/bj5/<email>), dihapus bersama isi khusus lainnya saat keluar, dan dicek ulang ke server tiap 24 jam.
     Versi isi (VER) ikut disimpan: salinan berversi lama diabaikan, jadi bentuk isi yang berubah tidak tercampur dengan salinan lama.
   - Bentuk satu slide (dicek di slideOk; slide yang bentuknya salah dibuang satu per satu, bukan menggagalkan semuanya):
       {l: nomor pelajaran 1-36, k: jenis, sec: label hanzi, si: label Indonesia, t: judul hanzi (opsional), b: [blok], pg: halaman buku, src: sumber lain,
        sc: nomor adegan, scl: label pendek adegan (pada slide pertama adegan), scn: nama lengkap adegan, ng: 1 = jangan beri ketuk-untuk-arti}
     Jenis k: cv sampul, wu 热身, ks 生词, tx 课文, ct 词语例释, sd 词语搭配, bd 词语辨析, lt latihan, ex 扩展, ap 运用.
     Satu objek khusus {l, k:"gx", gl:{kata:[pinyin, kelas kata, arti]}} adalah kamus pelajaran itu, bukan slide: kata di dalamnya
     otomatis diberi garis titik di blok p, ex, sd dan bisa diketuk untuk melihat artinya.
     Blok b: p kalimat hanzi (+ i terjemahan, g penanda adegan), n catatan, hd subjudul, li daftar, ex contoh kalimat, qa tanya-jawab,
     tb tabel, wb bank kata, kt kartu kosakata (ch rangkaian di teks, u catatan pecahan, k label kata ulang), sd kartu kolokasi, cv sampul,
     pq pertanyaan sebelum membaca, rv kartu ingat-dulu (d: "z" hanzi ke arti, "i" arti ke hanzi). Tanda {{...}} dalam teks = sorotan.
     Blok berjenis lain diabaikan, jadi jenis baru bisa ditambah tanpa merusak versi lama.

   Pemakaian
   - Panah kiri/kanan, PageUp/PageDown, Home/End pindah slide; F layar penuh; P pinyin; T terjemahan; Esc keluar layar penuh. Geser jari di HP.
   - Deretan angka di atas slide = peta adegan; ketuk untuk loncat ke awal adegan itu.
   - Pinyin hanya ada untuk kata yang pinyinnya tercetak di buku atau ditulis tangan di kamus. Kalimat tidak diberi pinyin buatan mesin.
   - Kalimat bisa didengar lewat suara peramban (speechSynthesis), sama seperti tombol suara di bagian lain situs.
   - Posisi slide terakhir tiap pelajaran disimpan di perangkat ini saja (localStorage bj_pos), tidak ikut sinkron. */
(function(){
 "use strict";
 var ISI="https://n8n.zenta.web.id/webhook/hsk-u-isi",PAKET="bj5",CACHE="zenta-isi-v2",UMUR=864e5,MAXL=36,PERBUKU=18,VER=3;
 var KIND={cv:"课",wu:"金",ks:"木",tx:"土",ct:"水",sd:"水",bd:"水",lt:"火",ex:"金",ap:"火"};
 var st={s:"idle",slides:[],by:{},gl:{},p:null};          /* s: idle | load | ok | net | bukan | sesi */
 var ui={v:"list",buku:1,l:0,i:0,py:true,id:false,full:false};
 var realign=false;
 var el=null,titles=[],listening=false,pres=null,inerted=[],G=null,gcount=0;
 var TTS=typeof speechSynthesis!=="undefined"&&typeof SpeechSynthesisUtterance!=="undefined";
 function $(id){return document.getElementById(id)}
 var e=window.hskEsc||function(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]})};
 function hl(s){return e(s).replace(/\{\{(.+?)\}\}/g,'<mark class="bj-hl">$1</mark>')}
 function plain(s){return String(s==null?"":s).replace(/\{\{|\}\}/g,"")}
 function isStr(x){return typeof x==="string"}
 function isArr(x){return Array.isArray(x)}
 function zh(s){return /[㐀-鿿]/.test(String(s))}
 function lz(s){return zh(s)?' lang="zh"':""}

 /* ---- ikon (keluarga garis yang sama dengan menu situs) ---- */
 var IS='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">';
 var IC={kiri:IS+'<path d="m15 18-6-6 6-6"/></svg>',kanan:IS+'<path d="m9 18 6-6-6-6"/></svg>',
  suara:IS+'<path d="M11 5 6 9H2v6h4l5 4V5z"/><path d="M15.5 8.5a5 5 0 0 1 0 7"/></svg>',
  penuh:IS+'<path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>',
  tutup:IS+'<path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3"/></svg>'};

 /* ---- akun ---- */
 function ownerLS(){try{var a=JSON.parse(localStorage.getItem("acct_auth")||"null");return !!(a&&(a.peran==="owner"||a.peran==="pemilik")&&typeof a.exp==="number"&&a.exp>Date.now()/1000)}catch(x){return false}}
 function owner(){try{var a=window.hskAuth,p=a?String(a.peran()||""):"";if(p==="owner"||p==="pemilik")return true}catch(x){}return ownerLS()}
 function akun(){try{var a=window.hskAuth;return{e:String(a.email()||""),t:String(a.token?a.token()||"":"")}}catch(x){return{e:"",t:""}}}
 function syncChip(){var b=$("n-bj");if(b)b.hidden=!owner()}

 /* ---- pilihan tampilan dan posisi (per perangkat) ---- */
 var pos={last:0,at:{}};
 try{var o=JSON.parse(localStorage.getItem("bj_opt")||"null");if(o&&typeof o==="object"){ui.py=o.py!==0;ui.id=o.id===1}}catch(x){}
 try{var q=JSON.parse(localStorage.getItem("bj_pos")||"null");if(q&&typeof q==="object"){pos.last=+q.last||0;pos.at=q.at&&typeof q.at==="object"?q.at:{}}}catch(x){}
 function saveOpt(){try{localStorage.setItem("bj_opt",JSON.stringify({py:ui.py?1:0,id:ui.id?1:0}))}catch(x){}}
 function savePos(){try{localStorage.setItem("bj_pos",JSON.stringify(pos))}catch(x){}}
 if(pos.last>=1&&pos.last<=MAXL)ui.buku=pos.last>PERBUKU?2:1;

 /* ---- validasi isi dari server ---- */
 function blokOk(b){return !!b&&typeof b==="object"&&isStr(b.t)}
 function slideOk(s){
  if(!s||typeof s!=="object"||isArr(s))return false;
  if(!(s.l>=1&&s.l<=MAXL&&Math.floor(s.l)===s.l))return false;
  if(!isStr(s.k)||!KIND[s.k]||!isStr(s.sec)||!isStr(s.si)||!isArr(s.b))return false;
  if(s.t!==undefined&&!isStr(s.t))return false;
  if(s.sc!==undefined&&!(typeof s.sc==="number"&&s.sc>=0&&s.sc<100&&Math.floor(s.sc)===s.sc))return false;
  if(s.scl!==undefined&&(!isStr(s.scl)||s.scl.length>8))return false;
  if(s.scn!==undefined&&(!isStr(s.scn)||s.scn.length>160))return false;
  for(var i=0;i<s.b.length;i++)if(!blokOk(s.b[i]))return false;
  return true;
 }
 /* kamus pelajaran: {kata: [pinyin, kelas, arti]}; kunci diurut dari yang terpanjang supaya 吵架 menang atas 吵 */
 function glOk(s){
  if(!s||s.k!=="gx"||!(s.l>=1&&s.l<=MAXL&&Math.floor(s.l)===s.l)||!s.gl||typeof s.gl!=="object"||isArr(s.gl))return false;
  var ks=Object.keys(s.gl);if(!ks.length||ks.length>400)return false;
  for(var i=0;i<ks.length;i++){var v=s.gl[ks[i]];if(!isArr(v)||v.length!==3||!isStr(v[0])||!isStr(v[1])||!isStr(v[2])||!ks[i])return false}
  return true;
 }
 function mkGl(o){var k=Object.keys(o);k.sort(function(a,b){return b.length-a.length});return{keys:k,map:o}}
 function apply(D){
  if(!isArr(D))return false;
  var flat=[],ok=[],by={},gl={};
  D.forEach(function(x){if(isArr(x))x.forEach(function(y){flat.push(y)});else flat.push(x)});
  flat.forEach(function(s){
   if(s&&typeof s==="object"&&s.k==="gx"){if(glOk(s))gl[s.l]=mkGl(s.gl);return}
   if(slideOk(s))ok.push(s);
  });
  if(!ok.length)return false;
  ok.forEach(function(s){(by[s.l]=by[s.l]||[]).push(s)});
  st.slides=ok;st.by=by;st.gl=gl;
  if(ui.v==="pres"){if(!by[ui.l])ui.v="list";else if(ui.i>=by[ui.l].length)ui.i=by[ui.l].length-1}
  return true;
 }
 function lepas(){st.slides=[];st.by={};st.gl={}}

 /* ---- Cache API per akun ---- */
 function ckey(m){return "/__isi/"+PAKET+"/"+encodeURIComponent(m)}
 function cache(){try{return typeof caches!=="undefined"&&caches&&caches.open?caches.open(CACHE):Promise.reject(new Error("tanpa cache"))}catch(x){return Promise.reject(x)}}
 function cacheGet(m){return cache().then(function(c){return c.match(ckey(m))}).then(function(r){return r?r.json():null}).catch(function(){return null})}
 function cachePut(m,D){cache().then(function(c){return c.put(ckey(m),new Response(JSON.stringify({t:Date.now(),v:VER,D:D}),{headers:{"Content-Type":"application/json"}}))}).catch(function(){})}
 function cacheDel(m){cache().then(function(c){return c.delete(ckey(m))}).catch(function(){})}

 /* ---- minta isi ke server. Hasil: "ok" | "bukan" (403) | "sesi" (401) | "net" ---- */
 function ambil(a){
  if(!a.t)return Promise.resolve("sesi");
  var ctl=typeof AbortController!=="undefined"?new AbortController():null,to=setTimeout(function(){if(ctl)ctl.abort()},30000);
  return fetch(ISI,{method:"POST",headers:{"Content-Type":"application/json"},mode:"cors",signal:ctl?ctl.signal:undefined,body:JSON.stringify({secret:a.t,paket:PAKET})})
   .then(function(r){
    if(r.status===403)return"bukan";
    if(r.status===401)return"sesi";
    if(!r.ok)return"net";
    return r.json().then(function(j){if(j&&j.ok===true&&j.paket===PAKET&&j.v===VER&&apply(j.D)){cachePut(a.e,flatRaw(j.D));return"ok"}return"net"});
   })
   .catch(function(){return"net"})
   .then(function(x){clearTimeout(to);return x});
 }
 function flatRaw(D){var o=[];D.forEach(function(x){if(isArr(x))x.forEach(function(y){o.push(y)});else o.push(x)});return o}
 function muat(paksa){
  if(st.p)return st.p;
  if(!owner()){st.s="bukan";lepas();return Promise.resolve()}
  var a=akun();st.s="load";
  st.p=(paksa?Promise.resolve(null):cacheGet(a.e)).then(function(c){
   if(c&&c.v===VER&&apply(c.D)){
    st.s="ok";draw();
    if(Date.now()-(+c.t||0)<UMUR)return"ok";
    return ambil(a).then(function(x){return x==="net"?"ok":x});   /* salinan lama tetap dipakai bila server tak terjangkau */
   }
   draw();
   return ambil(a);
  }).then(function(x){
   if(x==="bukan"||x==="sesi"){cacheDel(a.e);lepas()}
   st.s=x;st.p=null;
   if(!(x==="ok"&&ui.v==="pres"&&el&&el.querySelector&&el.querySelector(".bj-pres")))draw();
  },function(){st.s="net";st.p=null;draw()});
  return st.p;
 }

 /* ---- suara ---- */
 function say(t){
  if(!TTS)return;
  try{
   speechSynthesis.cancel();
   var vs=speechSynthesis.getVoices(),v=null,i;
   for(i=0;i<vs.length;i++)if(/^zh/i.test(vs[i].lang)){v=vs[i];break}
   (String(t).match(/[^。！？]+[。！？”"]*/g)||[String(t)]).forEach(function(s){
    var u=new SpeechSynthesisUtterance(s);if(v)u.voice=v;u.lang=v?v.lang:"zh-CN";u.rate=.85;speechSynthesis.speak(u);
   });
  }catch(x){}
 }
 function stopSay(){try{if(TTS)speechSynthesis.cancel()}catch(x){}}
 function sp(t,lab){
  if(!TTS)return"";
  var s=plain(t);
  return '<button type="button" class="bj-sp" data-say="'+e(s)+'" aria-label="'+(lab||"Dengarkan kalimat")+'">'+IC.suara+'</button>';
 }

 /* ---- ketuk-untuk-arti: kata kamus di teks hanzi dibungkus tombol; G = kamus slide yang sedang dirender ---- */
 function glossify(t){
  if(!G||!G.keys.length)return e(t);
  var o="",i=0,n=t.length,k,w,hit;
  while(i<n){
   hit=null;
   for(k=0;k<G.keys.length;k++){w=G.keys[k];if(t.substr(i,w.length)===w){hit=w;break}}
   if(hit){gcount++;o+='<button type="button" class="bj-w" data-w="'+e(hit)+'" aria-pressed="false">'+e(hit)+'</button>';i+=hit.length}
   else{o+=e(t.charAt(i));i++}
  }
  return o;
 }
 /* teks dengan {{sorotan}} dan kata kamus */
 function mark(s){
  s=String(s==null?"":s);
  var out="",re=/\{\{(.+?)\}\}/g,last=0,m;
  while((m=re.exec(s))){out+=glossify(s.slice(last,m.index))+'<mark class="bj-hl">'+glossify(m[1])+'</mark>';last=re.lastIndex}
  return out+glossify(s.slice(last));
 }

 /* ---- blok isi ---- */
 function cell(c,th){
  var x=c,sp=1;
  if(c&&typeof c==="object"){x=c.x;sp=c.sp>1?Math.floor(c.sp):1}
  var t=th?"th":"td",s=(x===""||x==null)?"":hl(x);
  return "<"+t+(sp>1?' colspan="'+sp+'"':"")+(s===""&&!th?' class="e"':"")+(th?' scope="col"':"")+lz(x)+">"+s+"</"+t+">";
 }
 var B={
  p:function(b){
   var g=isStr(b.g)&&b.g?'<span class="bj-g"><span class="bj-vh">Adegan </span>'+e(b.g)+'</span>':"";
   var h='<div class="bj-pb"><p class="bj-p" lang="zh">'+mark(b.x)+sp(b.x)+'</p>'+(isStr(b.i)&&b.i?'<p class="bj-i" data-tr>'+e(b.i)+'</p>':"")+'</div>';
   return g?'<div class="bj-pr">'+g+h+'</div>':h;
  },
  n:function(b){return '<p class="bj-n">'+hl(b.x)+'</p>'},
  hd:function(b){return '<h3 class="bj-h'+(zh(b.x)?'':' id')+'"'+lz(b.x)+'>'+hl(b.x)+'</h3>'},
  li:function(b){return isArr(b.x)?'<ul class="bj-li">'+b.x.map(function(x){return '<li'+lz(x)+'>'+hl(x)+'</li>'}).join("")+'</ul>':""},
  ex:function(b){
   if(!isArr(b.x))return "";
   return '<ol class="bj-ex">'+b.x.map(function(r){return '<li><p class="bj-z" lang="zh">'+mark(r.z)+sp(r.z)+'</p>'+(isStr(r.i)&&r.i?'<p class="bj-i" data-tr>'+e(r.i)+'</p>':"")+'</li>'}).join("")+'</ol>';
  },
  qa:function(b){
   return '<details class="bj-qa"><summary'+lz(b.q)+'>'+hl(b.q)+'</summary><div class="bj-a"><p class="bj-za"'+lz(b.a)+'>'+hl(b.a)+sp(b.a)+'</p>'+(isStr(b.n)&&b.n?'<p class="bj-n">'+e(b.n)+'</p>':"")+'</div></details>';
  },
  tb:function(b){
   if(!isArr(b.r))return "";
   var head=isArr(b.c)&&b.c.some(function(x){return x!==""&&x!=null});
   return '<div class="bj-tbw" role="region" tabindex="0" aria-label="'+e(b.cap||"Tabel")+'"><table>'+(b.cap?'<caption'+lz(b.cap)+'>'+e(b.cap)+'</caption>':"")
    +(head?'<thead><tr>'+b.c.map(function(c){return cell(c,true)}).join("")+'</tr></thead>':"")
    +'<tbody>'+b.r.map(function(r){return '<tr>'+(isArr(r)?r.map(function(c){return cell(c,false)}).join(""):"")+'</tr>'}).join("")+'</tbody></table></div>';
  },
  wb:function(b){return isArr(b.x)?'<ul class="bj-wb" aria-label="Bank kata" lang="zh">'+b.x.map(function(x){return '<li>'+hl(x)+'</li>'}).join("")+'</ul>':""},
  kt:function(b){
   if(!isArr(b.x))return "";
   return '<ul class="bj-kt">'+b.x.map(function(r){
    return '<li'+(r.k?' class="rem"':'')+'><span class="n">'+(r.n?e(r.n):"")+'</span>'
     +'<div class="w"><span class="z"><span lang="zh">'+e(r.z)+'</span>'+(r.s?'<span class="st" aria-label="tanda bintang di buku">*</span>':"")+sp(r.z,"Dengarkan kata")+'</span>'
     +'<span class="p bj-py">'+e(r.p)+(r.c?' <span class="c">'+e(r.c)+'</span>':"")+'</span>'+(r.k?'<span class="tg">'+e(r.k)+'</span>':"")+'</div>'
     +'<span class="m">'+e(r.i)+(r.e?'<small lang="en">'+e(r.e)+'</small>':"")+'</span>'
     +(r.ch?'<span class="ch"><span class="chl">Rangkaian</span><span lang="zh">'+hl(r.ch)+'</span></span>':"")
     +(r.u?'<span class="u">'+e(r.u)+'</span>':"")+'</li>';
   }).join("")+'</ul>';
  },
  sd:function(b){
   return '<article class="bj-sd"><div class="w"><span class="py bj-py">'+e(b.p)+'</span><b class="zz" lang="zh">'+e(b.z)+'</b><span class="en" lang="en">'+e(b.e)+'</span></div>'
    +'<div><p class="f">'+e(b.f)+'</p><p class="cl" lang="zh">'+mark(b.c)+'</p><p class="xx" lang="zh">'+mark(b.x)+sp(b.x)+'</p>'+(isStr(b.i)&&b.i?'<p class="bj-i" data-tr>'+e(b.i)+'</p>':"")+'</div></article>';
  },
  cv:function(b){
   return '<div class="bj-cv"><p class="bj-i no" aria-hidden="true" lang="zh">第 '+e(b.n)+' 课</p><p class="zz" lang="zh">'+e(b.z)+'</p><p class="en">'+e(b.e)+'</p><p class="id">'+e(b.i)+'</p></div>';
  },
  pq:function(b){
   return isArr(b.q)?'<div class="bj-pq"><p class="bj-pql">'+e(b.x)+'</p><ol>'+b.q.map(function(x){return '<li>'+e(x)+'</li>'}).join("")+'</ol></div>':"";
  },
  rv:function(b){
   if(!isArr(b.x))return "";
   var d=b.d==="i"?"i":"z";
   return '<ul class="bj-rv">'+b.x.map(function(r){
    var f=d==="z"?'<span class="f" lang="zh">'+e(r.z)+'</span>':'<span class="f">'+e(r.i)+'</span>';
    var k=d==="z"?'<span class="bj-py">'+e(r.p)+'</span> <span>'+e(r.i)+'</span>':'<b lang="zh">'+e(r.z)+'</b> <span class="bj-py">'+e(r.p)+'</span>';
    return '<li><button type="button" class="bj-rc'+(d==="i"?" i":"")+'" aria-pressed="false">'+f+'<span class="b" hidden>'+k+'</span></button></li>';
   }).join("")+'</ul>';
  }
 };
 function blocks(s){
  return s.b.map(function(b){try{return B[b.t]?B[b.t](b):""}catch(x){return ""}}).join("");
 }
 function hasQa(s){return s.b.some(function(b){return b.t==="qa"||b.t==="rv"})}
 function slideHtml(s,n,tot){
  var foot=s.src?s.src:(s.pg?"Sumber: Buku HSK 标准教程 5 (上), "+s.pg:"");
  G=s.ng?null:(st.gl[s.l]||null);gcount=0;
  var inner=blocks(s);G=null;
  return '<section class="bj-slide k-'+e(s.k)+'" aria-label="Slide '+n+' dari '+tot+'">'
   +'<div class="bj-sh"><span class="bj-cap" aria-hidden="true" lang="zh">'+e(KIND[s.k])+'</span><div><p class="bj-sec" lang="zh">'+e(s.sec)+'</p><p class="bj-si">'+e(s.si)+'</p></div></div>'
   +(s.t&&s.k!=="cv"?'<h2 class="bj-t'+(zh(s.t)?'':' id')+'"'+lz(s.t)+'>'+e(s.t)+'</h2>':"")
   +'<div class="bj-bw"><div class="bj-body" tabindex="0" role="region" aria-label="Isi slide">'+inner+'</div></div>'
   +(gcount?'<div class="bj-gl" id="bj-gl" role="status" aria-live="polite"><span class="h">Ketuk kata bergaris titik untuk artinya.</span></div>':"")
   +(foot?'<p class="bj-sf">'+e(foot)+'</p>':"")+'</section>';
 }
 /* panel arti di bawah isi slide */
 function gloss(w){
  var L=st.by[ui.l],s=L&&L[ui.i],g=s&&st.gl[s.l]&&st.gl[s.l].map[w],p=$("bj-gl");
  if(!g||!p)return;
  p.innerHTML='<b lang="zh">'+e(w)+'</b><span class="py bj-py">'+e(g[0])+'</span>'+(g[1]?'<span class="ps">'+e(g[1])+'</span>':"")+'<span class="mn">'+e(g[2])+'</span>'+sp(w,"Dengarkan kata");
  var cur=null;
  el.querySelectorAll(".bj-w").forEach(function(x){var on=x.getAttribute("data-w")===w;x.classList.toggle("on",on);x.setAttribute("aria-pressed",String(on));if(on&&!cur)cur=x});
  if(cur){var b=el.querySelector(".bj-body");if(b){var r=cur.getBoundingClientRect(),q=b.getBoundingClientRect();if(r.bottom>q.bottom-4)b.scrollTop+=r.bottom-q.bottom+12;else if(r.top<q.top)b.scrollTop-=q.top-r.top+12}cue()}
 }
 /* kartu ingat-dulu */
 function flip(c,v){
  var on=typeof v==="boolean"?v:c.getAttribute("aria-pressed")!=="true",b=c.querySelector(".b");
  c.setAttribute("aria-pressed",String(on));if(b)b.hidden=!on;
 }
 function opens(){return el.querySelectorAll(".bj-qa,.bj-rc")}
 function isOpen(x){return x.classList.contains("bj-rc")?x.getAttribute("aria-pressed")==="true":x.open}
 function setOpen(x,v){if(x.classList.contains("bj-rc"))flip(x,v);else x.open=v}

 /* ---- judul pelajaran dari daftar situs (publik) ---- */
 function judul(l){
  var t=String(titles[l-1]||""),m=/^Pelajaran\s+\d+\s*·\s*(.*)$/.exec(t);
  return m?m[1]:"";
 }
 function bcSet(extra){var b=$("bc");if(b)b.innerHTML='<b lang="zh">课件</b> › HSK 5'+(extra||"")}

 /* ---- tampilan ---- */
 function msg(h){return '<div class="bj"><div class="bj-msg" role="status">'+h+'</div></div>'}
 function draw(){
  if(!el||!el.isConnected)return;
  var host=el.parentNode;
  if(!owner()){bcSet("");swap(host,msg('<p>Bagian 课件 khusus akun pemilik.</p>'));return}
  if(st.s==="sesi"){bcSet("");swap(host,msg('<p>Sesi berakhir. Silakan masuk lagi untuk membuka bahan ajar.</p>'));return}
  if(st.s==="bukan"){bcSet("");swap(host,msg('<p>Akun ini tidak punya akses ke bahan ajar.</p>'));return}
  if((st.s==="load"||st.s==="idle")&&!st.slides.length){bcSet("");swap(host,msg('<p>Memuat bahan ajar…</p>'));return}
  if(st.s==="net"&&!st.slides.length){bcSet("");swap(host,msg('<p>Bahan ajar belum bisa dimuat. Periksa koneksi, lalu coba lagi.</p><p><button type="button" id="bj-ulang">Coba lagi</button></p>'));var u=$("bj-ulang");if(u)u.onclick=function(){muat(true)};return}
  if(ui.v==="pres"&&st.by[ui.l]&&st.by[ui.l].length)drawPres();else{ui.v="list";drawList()}
 }
 function swap(host,html){
  var d=document.createElement("div");d.innerHTML=html;var n=d.firstChild;
  if(el&&el.parentNode===host){host.replaceChild(n,el)}else{host.innerHTML="";host.appendChild(n)}
  el=n;pres=null;
 }
 /* tinggi menu bawah (HP) supaya bilah geser menempel tepat di atasnya; di laptop menu ada di samping, jadi 0 */
 function navH(){
  var n=$("nav");if(!n)return 0;
  var cs=getComputedStyle(n);if(cs.position!=="fixed")return 0;
  var r=n.getBoundingClientRect();return r.width>=innerWidth*.8&&r.height<innerHeight*.5?Math.max(0,Math.round(innerHeight-r.top)):0;
 }
 /* tinggi panggung = sisa layar di bawah judul, supaya slide dan bilah geser terlihat bersama tanpa menggulir halaman */
 function ukur(){
  if(!(el&&el.isConnected))return;
  var nh=navH();el.style.setProperty("--bj-nav",nh+"px");
  var g=$("bj-stage"),bar=el.querySelector(".bj-bar"),tp=el.querySelector(".bj-top");
  if(g&&bar&&tp&&!ui.full){
   /* jarak baris judul ke panggung tidak bergantung pada gulir halaman; pembukaan pelajaran menggulir baris judul ke atas layar (alignTop) */
   var off=g.getBoundingClientRect().top-tp.getBoundingClientRect().top;
   var h=Math.round(innerHeight-off-8-bar.offsetHeight-nh-14);
   el.style.setProperty("--bj-h",Math.max(320,Math.min(720,h))+"px");
  }
  cue();
 }
 /* header situs ada di atas penampil: gulirkan baris judul ke atas layar supaya slide, peta adegan, dan bilah geser terlihat bersama */
 function alignTop(){
  var tp=el&&el.querySelector?el.querySelector(".bj-top"):null;if(!tp||ui.full)return;
  var y=Math.max(0,Math.round(tp.getBoundingClientRect().top+(window.pageYOffset||0)-8));
  if(Math.abs((window.pageYOffset||0)-y)>2)window.scrollTo(0,y);
 }
 /* petunjuk gulir: tampil bila isi slide lebih panjang dari panggung dan belum sampai ujung */
 function cue(){
  var b=el&&el.querySelector?el.querySelector(".bj-body"):null,g=$("bj-stage");
  if(!b||!g)return;
  var more=b.scrollHeight>b.clientHeight+4&&b.scrollTop+b.clientHeight<b.scrollHeight-4;
  if(more)g.setAttribute("data-more","");else g.removeAttribute("data-more");
 }
 function bind(){
  if(!listening){document.addEventListener("keydown",onKey);document.addEventListener("fullscreenchange",onFs);window.addEventListener("resize",ukur);listening=true}
 }
 function cleanup(){
  if(listening){document.removeEventListener("keydown",onKey);document.removeEventListener("fullscreenchange",onFs);window.removeEventListener("resize",ukur);listening=false}
  inertSet(null,false);stopSay();ui.full=false;
 }

 /* daftar pelajaran */
 function drawList(){
  var host=el.parentNode,from=ui.buku===2?PERBUKU+1:1,to=ui.buku===2?MAXL:PERBUKU,h='',l;
  h+='<div class="bj"><div><h2 class="bj-h2"><span lang="zh">课件</span>Bahan ajar HSK 5</h2><p class="bj-lead">Satu pelajaran satu bahan ajar, mengikuti urutan buku HSK 标准教程 5. Khusus akun pemilik.</p></div>';
  h+='<div class="bj-seg" role="group" aria-label="Pilih buku"><button type="button" data-b="1" aria-pressed="'+(ui.buku===1)+'"><b lang="zh">5 上</b>Pelajaran 1 sampai '+PERBUKU+'</button><button type="button" data-b="2" aria-pressed="'+(ui.buku===2)+'"><b lang="zh">5 下</b>Pelajaran '+(PERBUKU+1)+' sampai '+MAXL+'</button></div>';
  h+='<ul class="bj-grid">';
  for(l=from;l<=to;l++){
   var n=(st.by[l]||[]).length,z=judul(l);
   h+='<li><button type="button" class="bj-tile" data-l="'+l+'"'+(n?"":" disabled")+'><span class="n" aria-hidden="true">'+l+'</span><span class="z" lang="zh">'+(z?e(z):"Pelajaran "+l)+'</span><span class="s">'+(n?n+" slide":"Belum ada")+'</span></button></li>';
  }
  h+='</ul></div>';
  swap(host,h);bcSet("");
  el.querySelectorAll(".bj-seg button").forEach(function(b){b.onclick=function(){ui.buku=+b.dataset.b;drawList();var t=el.querySelector('.bj-seg button[aria-pressed="true"]');if(t)t.focus()}});
  el.querySelectorAll(".bj-tile").forEach(function(b){b.onclick=function(){open(+b.dataset.l)}});
 }
 function open(l){
  if(!st.by[l])return;
  ui.l=l;ui.v="pres";
  var i=+pos.at[l]||0;ui.i=i>=0&&i<st.by[l].length?i:0;
  pos.last=l;savePos();realign=true;drawPres();
 }

 /* peta adegan di atas slide: satu tombol per adegan, diambil dari sc/scl/scn pada slide */
 function scenesOf(L){
  var o=[],ix={};
  L.forEach(function(s,i){
   if(typeof s.sc!=="number")return;
   if(ix[s.sc]===undefined){ix[s.sc]=o.length;o.push({sc:s.sc,i:i,l:isStr(s.scl)&&s.scl?s.scl:String(s.sc),n:isStr(s.scn)?s.scn:""})}
   else{var q=o[ix[s.sc]];if(!q.n&&isStr(s.scn))q.n=s.scn}
  });
  return o;
 }
 function railHtml(L){
  var sc=scenesOf(L);if(sc.length<2)return"";
  return '<div class="bj-map"><ol class="bj-rail" id="bj-rail" aria-label="Peta pelajaran">'+sc.map(function(x){
   return '<li><button type="button" class="bj-rl" data-sc="'+x.sc+'" data-i="'+x.i+'" aria-label="'+e(x.n||("Bagian "+x.l))+'">'+e(x.l)+'</button></li>';
  }).join("")+'</ol><p class="bj-rn" id="bj-rn"></p></div>';
 }
 function railSync(L){
  var r=$("bj-rail");if(!r)return;
  var cur=L[ui.i].sc,name="";
  r.querySelectorAll(".bj-rl").forEach(function(b){
   var sc=+b.getAttribute("data-sc"),on=sc===cur;
   if(on){b.setAttribute("aria-current","step");name=b.getAttribute("aria-label")}else b.removeAttribute("aria-current");
   b.classList.toggle("dn",typeof cur==="number"&&sc<cur);
  });
  var n=$("bj-rn");if(n)n.textContent=name;
 }

 /* penampil slide */
 function selOpts(L){
  return L.map(function(s,i){return '<option value="'+i+'"'+(i===ui.i?" selected":"")+'>'+(i+1)+'. '+e(s.sec)+' · '+e(s.t&&s.k!=="cv"?s.t:s.si)+'</option>'}).join("");
 }
 function drawPres(){
  var host=el.parentNode,L=st.by[ui.l],z=judul(ui.l),s=L[ui.i];
  var h='<div class="bj"><div class="bj-top"><button type="button" class="bj-back" id="bj-back" aria-label="Kembali ke daftar pelajaran">'+IC.kiri+'Daftar</button><p class="bj-tt">Pelajaran <b>'+ui.l+'</b> '+(z?'<b lang="zh">'+e(z)+'</b>':"")+'</p></div>'
   +'<div class="bj-pres" id="bj-pres" role="group" aria-roledescription="penampil slide" aria-label="Pelajaran '+ui.l+(z?": "+e(z):"")+'">'
   +railHtml(L)
   +'<div class="bj-stage" id="bj-stage">'+slideHtml(s,ui.i+1,L.length)+'</div>'
   +'<div class="bj-bar"><button type="button" class="bj-nav" id="bj-prev" aria-label="Slide sebelumnya">'+IC.kiri+'</button><div class="bj-prog" aria-hidden="true"><i id="bj-pi"></i></div><span class="bj-cnt" id="bj-cnt"></span><button type="button" class="bj-nav" id="bj-next" aria-label="Slide berikutnya">'+IC.kanan+'</button></div>'
   +'<div class="bj-tools"><select id="bj-sel" aria-label="Loncat ke slide">'+selOpts(L)+'</select>'
   +'<button type="button" id="bj-py" aria-pressed="'+ui.py+'">Pinyin</button><button type="button" id="bj-id" aria-pressed="'+ui.id+'">Terjemahan</button>'
   +'<button type="button" id="bj-qa" hidden>Buka jawaban</button><button type="button" id="bj-fs"></button></div>'
   +'<p class="bj-vh" id="bj-live" role="status" aria-live="polite"></p></div></div>';
  swap(host,h);
  pres=$("bj-pres");
  el.classList.toggle("bj-nopy",!ui.py);el.classList.toggle("bj-id",ui.id);
  $("bj-back").onclick=function(){if(ui.full)setFull(false);stopSay();ui.v="list";ui.buku=ui.l>PERBUKU?2:1;drawList();var t=el.querySelector('.bj-tile[data-l="'+ui.l+'"]');if(t)t.focus()};
  $("bj-prev").onclick=function(){go(-1)};$("bj-next").onclick=function(){go(1)};
  $("bj-sel").onchange=function(ev){ui.i=+ev.target.value;showSlide()};
  $("bj-py").onclick=togglePy;$("bj-id").onclick=toggleId;$("bj-fs").onclick=function(){setFull(!ui.full)};
  $("bj-qa").onclick=function(){var d=opens(),any=false;d.forEach(function(x){if(!isOpen(x))any=true});d.forEach(function(x){setOpen(x,any)});qaLabel()};
  var rl=$("bj-rail");
  if(rl)rl.addEventListener("click",function(ev){var b=ev.target.closest?ev.target.closest(".bj-rl"):null;if(b){ui.i=+b.getAttribute("data-i");showSlide()}});
  var stg=$("bj-stage");
  stg.addEventListener("toggle",function(){qaLabel();cue()},true);
  stg.addEventListener("scroll",cue,true);
  stg.addEventListener("click",function(ev){
   var t=ev.target&&ev.target.closest?ev.target:null;if(!t)return;
   var b=t.closest("[data-say]");if(b){say(b.getAttribute("data-say"));return}
   var w=t.closest(".bj-w");if(w){gloss(w.getAttribute("data-w"));return}
   var c=t.closest(".bj-rc");if(c){flip(c);qaLabel()}
  });
  var x0=null,y0=null;
  stg.addEventListener("touchstart",function(ev){if(ev.touches.length!==1||(ev.target.closest&&ev.target.closest(".bj-tbw"))){x0=null;return}x0=ev.touches[0].clientX;y0=ev.touches[0].clientY},{passive:true});
  stg.addEventListener("touchend",function(ev){if(x0===null)return;var t=ev.changedTouches[0],dx=t.clientX-x0,dy=t.clientY-y0;x0=null;if(Math.abs(dx)>60&&Math.abs(dx)>Math.abs(dy)*1.6)go(dx<0?1:-1)},{passive:true});
  bcSet(' › '+(z?e(z):"Pelajaran "+ui.l));
  bind();meta();ukur();
  if(document.fonts&&document.fonts.ready)document.fonts.ready.then(ukur);
  if(realign){realign=false;alignTop()}
  if(ui.full)setFull(true,true);
  fsLabel();cue();
 }
 function qaLabel(){
  var b=$("bj-qa");if(!b||!el)return;
  var d=opens(),all=d.length>0;d.forEach(function(x){if(!isOpen(x))all=false});
  b.textContent=all?"Tutup jawaban":"Buka jawaban";
 }
 function fsLabel(){var b=$("bj-fs");if(b)b.innerHTML=(ui.full?IC.tutup:IC.penuh)+'<span>'+(ui.full?"Keluar layar penuh":"Layar penuh")+'</span>'}
 function meta(){
  var L=st.by[ui.l],n=L.length;
  $("bj-cnt").textContent=(ui.i+1)+" / "+n;
  $("bj-pi").style.width=Math.round((ui.i+1)/n*100)+"%";
  $("bj-prev").setAttribute("aria-disabled",String(ui.i===0));
  $("bj-next").setAttribute("aria-disabled",String(ui.i===n-1));
  var sel=$("bj-sel");if(sel&&+sel.value!==ui.i)sel.value=String(ui.i);
  var q=$("bj-qa");if(q){q.hidden=!hasQa(L[ui.i]);qaLabel()}
  var lv=$("bj-live");if(lv){var s=L[ui.i];lv.textContent="Slide "+(ui.i+1)+" dari "+n+": "+s.sec+", "+s.si}
  railSync(L);
 }
 function showSlide(){
  var L=st.by[ui.l],stg=$("bj-stage");if(!L||!stg)return;
  stopSay();
  stg.innerHTML=slideHtml(L[ui.i],ui.i+1,L.length);
  meta();cue();
  pos.at[ui.l]=ui.i;savePos();
 }
 function go(d){
  var L=st.by[ui.l];if(!L)return;
  var n=Math.max(0,Math.min(L.length-1,ui.i+d));
  if(n===ui.i)return;
  ui.i=n;showSlide();
 }
 function togglePy(){ui.py=!ui.py;saveOpt();el.classList.toggle("bj-nopy",!ui.py);var b=$("bj-py");if(b)b.setAttribute("aria-pressed",String(ui.py))}
 function toggleId(){ui.id=!ui.id;saveOpt();el.classList.toggle("bj-id",ui.id);var b=$("bj-id");if(b)b.setAttribute("aria-pressed",String(ui.id))}

 /* layar penuh: lapisan sendiri (tanpa Fullscreen API di iPhone); bila API ada, dipakai juga supaya bilah peramban hilang */
 function inertSet(target,on){
  inerted.forEach(function(x){try{x.removeAttribute("inert")}catch(z){}});inerted=[];
  if(!on||!target)return;
  var n=target;
  while(n&&n.parentNode&&n!==document.body){
    Array.prototype.forEach.call(n.parentNode.children,function(c){if(c!==n&&c.tagName!=="SCRIPT"&&c.tagName!=="STYLE"&&!c.hasAttribute("inert")){c.setAttribute("inert","");inerted.push(c)}});
    n=n.parentNode;
  }
 }
 function setFull(on,dariApi){
  ui.full=!!on;
  if(pres){
   pres.classList.toggle("bj-full",ui.full);
   if(ui.full){pres.setAttribute("role","dialog");pres.setAttribute("aria-modal","true")}else{pres.setAttribute("role","group");pres.removeAttribute("aria-modal")}
  }
  inertSet(pres,ui.full);
  if(!dariApi){
   try{
    if(ui.full&&pres&&pres.requestFullscreen){var pr=pres.requestFullscreen();if(pr&&pr.catch)pr.catch(function(){})}
    else if(!ui.full&&document.fullscreenElement&&document.exitFullscreen){var p2=document.exitFullscreen();if(p2&&p2.catch)p2.catch(function(){})}
   }catch(x){}
  }
  fsLabel();
  if(!ui.full)ukur();
 }
 function onFs(){if(ui.full&&!document.fullscreenElement&&fsOn)setFull(false,true);fsOn=!!document.fullscreenElement}
 var fsOn=false;

 function onKey(ev){
  if(!el||!el.isConnected){cleanup();return}
  if(ui.v!=="pres"||ev.ctrlKey||ev.metaKey||ev.altKey)return;
  var t=ev.target,tag=t&&t.tagName;
  if(tag==="INPUT"||tag==="TEXTAREA"||tag==="SELECT"||(t&&t.isContentEditable))return;
  var k=ev.key,tbl=t&&t.classList&&t.classList.contains("bj-tbw");
  if((k==="ArrowRight"||k==="ArrowLeft")&&tbl)return;
  if(k==="ArrowRight"||k==="PageDown"){go(1);ev.preventDefault()}
  else if(k==="ArrowLeft"||k==="PageUp"){go(-1);ev.preventDefault()}
  else if(k==="Home"){ui.i=0;showSlide();ev.preventDefault()}
  else if(k==="End"){ui.i=st.by[ui.l].length-1;showSlide();ev.preventDefault()}
  else if(k==="Escape"&&ui.full){setFull(false)}
  else if(k==="f"||k==="F"){setFull(!ui.full)}
  else if(k==="p"||k==="P"){togglePy()}
  else if(k==="t"||k==="T"){toggleId()}
 }

 /* ---- titik masuk dari index.html ---- */
 function render(view,ctx){
  titles=(ctx&&isArr(ctx.t))?ctx.t:[];
  syncChip();
  var d=document.createElement("div");d.className="bj-slot";view.innerHTML="";view.appendChild(d);
  el=d;pres=null;
  if(!owner()){draw();return}
  if(st.s==="ok"&&st.slides.length){if(ui.v==="pres")realign=true;draw();return}   /* isi sudah ada di memori: cukup tampilkan */
  if(st.s==="bukan"||st.s==="sesi"){draw();return}
  draw();muat();
 }
 window.zBj={render:render,sync:syncChip};
 syncChip();
 try{if(window.hskAuth&&window.hskAuth.onMasa)window.hskAuth.onMasa(syncChip)}catch(x){}
 /* keluar akun / ganti akun di tab lain: isi yang sudah dimuat tidak boleh tertinggal untuk akun berikutnya */
 window.addEventListener("storage",function(ev){if(ev.key==="acct_auth"){syncChip();if(!owner())lepas()}});
})();
