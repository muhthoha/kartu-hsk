/* Panduan pengguna baru (tur sorot) untuk Zenta 汉. Gaya: aset/tur.css. Dimuat dari index.html (defer).

   Kapan tampil
   - Otomatis, sekali per akun per perangkat, saat beranda (主页) pertama tampil setelah masuk. Akun baru dan akun lama sama: selama
     belum ada penanda untuk akun itu di perangkat ini, panduan tampil. Penanda: localStorage "zenta_tur_v1_<hash email>" = "1",
     ditulis saat panduan diselesaikan atau dilewati (bukan saat dimulai, jadi yang menutup tab di tengah jalan akan melihatnya lagi).
   - Manual: baris "Panduan penggunaan" di menu akun (#am-list), atau window.hskTur.mulai().
   - Ingin menampilkan ulang ke semua akun (mis. setelah fitur besar bertambah)? Naikkan VER di bawah ("v1" jadi "v2").
   - Kunci zenta_* tidak ikut dibersihkan saat ganti akun, dan tidak ikut sinkron ke server: penanda bersifat per perangkat.

   Cara kerja
   - Langkah menunjuk elemen asli lewat selector. Elemen yang tidak ada atau tidak tampil (mis. panel target harian) dilewati,
     dan nomor langkah dihitung dari yang ada. Letak sorotan dihitung ulang tiap frame bila kotaknya berubah (gulir, ukuran layar, render ulang).
   - Langkah "Menu akun" membuka menu akun sungguhan lalu menutupnya lagi saat pindah langkah.
   - Tidak ada pencatatan, tidak ada permintaan jaringan. Tidak menyentuh data belajar. */
(function(){
 "use strict";
 var VER="v1",KEY="zenta_tur_"+VER+"_";
 var root=document.documentElement,LS=null,on=false,cur=0,raf=0,lastKey="",lastView="",fixN=0,prevFocus=null,toastT=0,E=null;
 try{LS=window.localStorage;LS.getItem("acct_auth")}catch(e){LS=null}

 function $(id){return document.getElementById(id)}
 function email(){try{return window.hskAuth&&window.hskAuth.email?String(window.hskAuth.email()||""):""}catch(e){return""}}
 function kunci(){var e=email(),h=0,i;for(i=0;i<e.length;i++)h=(h*31+e.charCodeAt(i))>>>0;return KEY+h.toString(36)}
 function sudah(){try{return LS.getItem(kunci())==="1"}catch(e){return true}}   /* penyimpanan rusak: anggap sudah, supaya tidak berulang tiap muat */
 function tandai(){try{LS.setItem(kunci(),"1")}catch(e){}}

 /* Langkah. t: selector elemen yang disorot (beberapa selector = satu kotak yang mencakup semuanya).
    z: huruf di cap kepala kartu; e: unsur warna (1 木, 2 水, 3 土, 4 火, 5 金; 0 netral).
    jz + jt: judul berbahasa Mandarin + Indonesia (seperti judul kartu materi di beranda); jt saja untuk judul biasa.
    opsi: "pusat" = bila elemennya tidak ada, tampil di tengah layar (bukan dilewati). pusat: true = selalu di tengah. */
 var ST=[
  {id:"mulai",pusat:true,z:"",e:"0",jt:"Panduan singkat Zenta 汉",
   teks:"Panduan ini menunjukkan fungsi tiap bagian, satu per satu. Kamu bisa melewatinya sekarang dan membukanya lagi kapan saja dari menu akun."},
  {id:"cari",t:["#hs"],z:"搜",e:"0",jt:"Cari",
   teks:"Ketik hanzi, pinyin, atau arti dalam bahasa Indonesia. Kosakata, tata bahasa, dan cerita yang cocok akan muncul."},
  {id:"hari",t:["#view .daily-panel"],z:"今",e:"0",jt:"Target harian",
   teks:"Atur berapa kartu yang ingin kamu pelajari tiap hari, lalu lihat runtun belajarmu. Kartu yang jadwalnya jatuh tempo muncul di Pengulangan kosakata, tepat di bawahnya. Ulangi dulu sebelum menambah kartu baru."},
  {id:"kosakata",t:["#view .hb-voc"],z:"木",e:"1",jz:"词汇",jt:"Kosakata",
   teks:"Tiga daftar kata: HSK 2.0, HSK 3.0, dan Teknis. Ketuk kartu untuk melihat pinyin dan arti, lalu pilih Masih belajar atau Sudah tahu. Tab Tulis melatih menulis hanzi, tab Ringkasan memuat seluruh daftar beserta statusnya."},
  {id:"gr",t:["#view .tl[data-m=\"gr\"]"],z:"水",e:"2",jz:"语法",jt:"Tata bahasa",
   teks:"Pelajaran tata bahasa dengan contoh kalimat. Tandai poin yang sudah kamu pahami, atau beri bookmark supaya mudah dibuka lagi dari tab 进度 Progres."},
  {id:"rd",t:["#view .tl[data-m=\"rd\"]"],z:"土",e:"3",jz:"阅读",jt:"Membaca",
   teks:"Cerita pendek per level. Tandai Sudah dibaca setelah selesai, dan jumlahnya tampil di kartu ini."},
  {id:"lt",t:["#view .tl[data-m=\"lt\"]"],z:"火",e:"4",jz:"练习",jt:"Latihan",
   teks:"Latihan soal dalam beberapa jenis, termasuk soal HSK 5 dan HSKK. Pilih jenisnya setelah membuka bagian ini."},
  {id:"hz",t:["#view .tl[data-m=\"hz\"]"],z:"金",e:"5",jz:"汉字",jt:"Aksara",
   teks:"Radikal, jenis goresan, dan aturan urutan goresan. Bagian ini terbuka untuk semua akun."},
  {id:"gembok",t:["#view .aksesinfo"],opsi:"pusat",z:"锁",e:"0",jt:"Gembok dan cuplikan",
   teks:"Di akun gratis, sebagian materi berupa cuplikan dan ditandai gembok. Isi lengkapnya khusus Zenta 汉+. Seluruh kosakata HSK 2.0 dan bagian 汉字 tetap terbuka."},
  {id:"uji",t:["#view #hb-uji"],z:"考",e:"0",jt:"Simulasi ujian",
   teks:"Simulasi ujian berisi lembar jawaban untuk kertas HSK asli, HSK 1 sampai 5. Kosakata yang salah atau belum dijawab disimpan di Bank Kesalahan supaya bisa diulang."},
  {id:"akun",t:["#acct","#acct-menu"],z:"我",e:"0",jt:"Menu akun",
   teks:"Tombol berhuruf di bagian atas membuka menu akun: progres & cadangan, persiapan ujian dengan hitung mundur (opsional), warna nada pinyin, dan pilihan tampilan terang atau gelap. Panduan ini bisa dibuka lagi dari menu yang sama.",
   pra:function(){var m=$("acct-menu"),b=$("acct");if(b&&m&&m.hidden)b.click()},
   pasca:function(){try{if(window.hskMenu)window.hskMenu.close()}catch(e){}}}
 ];

 /* ---------- elemen sasaran ---------- */
 function tampak(el){return !!(el&&el.isConnected&&(el.offsetWidth||el.offsetHeight||el.getClientRects().length))}
 function sasaran(s){
  if(s.pusat)return null;
  var out=[],i,x;
  for(i=0;i<s.t.length;i++){x=document.querySelector(s.t[i]);if(tampak(x))out.push(x)}
  return out.length?out:null;
 }
 function ada(i){var s=ST[i];return !!(s.pusat||s.opsi==="pusat"||sasaran(s))}
 function kotak(a){
  var l=1e9,t=1e9,r=-1e9,b=-1e9,i,x;
  for(i=0;i<a.length;i++){x=a[i].getBoundingClientRect();l=Math.min(l,x.left);t=Math.min(t,x.top);r=Math.max(r,x.right);b=Math.max(b,x.bottom)}
  return{l:l,t:t,w:r-l,h:b-t};
 }
 /* nomor langkah dihitung dari langkah isi yang ada sekarang (sambutan tidak dihitung) */
 function nomor(){
  var n=0,t=0,i;
  for(i=1;i<ST.length;i++){if(ada(i)){t++;if(i<=cur)n++}}
  return{n:n,t:t};
 }
 function terakhir(){var i;for(i=cur+1;i<ST.length;i++)if(ada(i))return false;return true}

 /* ---------- bangun elemen ---------- */
 function el(tag,cls,txt){var e=document.createElement(tag);if(cls)e.className=cls;if(txt!=null)e.textContent=txt;return e}
 function btn(cls,txt){var b=el("button","tur-"+cls,txt);b.type="button";return b}
 function buat(){
  if(E)return;
  var r=el("div","tur");r.id="tur";r.hidden=true;r.setAttribute("data-e","0");
  var back=el("div","tur-back"),spot=el("div","tur-spot");
  var pop=el("div","tur-pop");pop.setAttribute("role","dialog");pop.setAttribute("aria-modal","true");pop.setAttribute("aria-label","Panduan penggunaan Zenta 汉");pop.tabIndex=-1;
  var bar=el("div","tur-bar"),fill=document.createElement("i");bar.appendChild(fill);
  var hd=el("div","tur-hd"),seal=el("span","tur-seal");seal.setAttribute("lang","zh");seal.setAttribute("aria-hidden","true");
  var box=document.createElement("div"),num=el("small","tur-n"),h=document.createElement("h2"),p=document.createElement("p");
  box.appendChild(num);box.appendChild(h);hd.appendChild(seal);hd.appendChild(box);
  var ft=el("div","tur-ft"),skip=btn("skip","Lewati"),nav=el("div","tur-nav"),prev=btn("prev","Kembali"),next=btn("next tur-pri","Berikutnya");
  nav.appendChild(prev);nav.appendChild(next);ft.appendChild(skip);ft.appendChild(nav);
  pop.appendChild(bar);pop.appendChild(hd);pop.appendChild(p);pop.appendChild(ft);
  var live=el("div","tur-live");live.setAttribute("role","status");
  r.appendChild(back);r.appendChild(spot);r.appendChild(pop);r.appendChild(live);
  var toast=el("div","tur-toast");toast.setAttribute("role","status");
  document.body.appendChild(r);document.body.appendChild(toast);
  /* klik di dalam panduan tidak boleh sampai ke dokumen: menu akun yang sedang dibuka menutup diri bila ada klik di luarnya */
  r.addEventListener("click",function(e){e.stopPropagation()});
  /* gulir halaman dikunci selama panduan berjalan; kartu sendiri boleh digulir bila isinya lebih tinggi dari layar */
  function kunciGulir(e){var p=E&&E.pop;if(p&&p.contains(e.target)&&p.scrollHeight>p.clientHeight)return;e.preventDefault()}
  r.addEventListener("wheel",kunciGulir,{passive:false});r.addEventListener("touchmove",kunciGulir,{passive:false});
  skip.addEventListener("click",lewati);prev.addEventListener("click",mundur);next.addEventListener("click",maju);
  E={r:r,spot:spot,pop:pop,fill:fill,seal:seal,num:num,h:h,p:p,skip:skip,prev:prev,next:next,live:live,toast:toast};
 }

 /* ---------- tata letak ---------- */
 function geser(a){   /* gulirkan halaman supaya sasaran dan kartu sama-sama muat */
  var b=kotak(a),vh=window.innerHeight,avail=vh-E.pop.offsetHeight-32,want=b.h<=avail?Math.max(16,(avail-b.h)/2+8):16,dy=b.t-want;
  if(Math.abs(dy)>1)window.scrollBy(0,dy);
 }
 function tata(a){
  var vw=window.innerWidth,vh=window.innerHeight,M=12,pw=Math.min(360,vw-2*M),pop=E.pop,x,y,b,P=6,sh,sw,sl,st,below,above;
  pop.style.width=pw+"px";
  var ph=pop.offsetHeight;
  if(!a){
   E.r.classList.add("tur-c");
   x=(vw-pw)/2;y=Math.max(M,(vh-ph)/2);
  }else{
   E.r.classList.remove("tur-c");
   b=kotak(a);sl=b.l-P;st=b.t-P;sw=b.w+2*P;sh=b.h+2*P;
   E.spot.style.left=sl+"px";E.spot.style.top=st+"px";E.spot.style.width=sw+"px";E.spot.style.height=sh+"px";
   try{var rd=parseFloat(window.getComputedStyle(a[0]).borderRadius)||0;E.spot.style.borderRadius=(a.length>1?20:Math.min(rd+P,40))+"px"}catch(e){}
   x=Math.max(M,Math.min(b.l+b.w/2-pw/2,vw-pw-M));
   below=vh-(st+sh)-M;above=st-M;
   if(below>=ph+8)y=st+sh+8;            /* di bawah sasaran */
   else if(above>=ph+8)y=st-ph-8;       /* di atas sasaran */
   else if(vw-(sl+sw)-M>=pw+8){x=sl+sw+8;y=Math.max(M,Math.min(st,vh-ph-M))}   /* lanskap: di kanan sasaran */
   else if(sl-M>=pw+8){x=sl-pw-8;y=Math.max(M,Math.min(st,vh-ph-M))}          /* di kiri sasaran */
   else y=Math.max(M,vh-ph-M);          /* sasaran terlalu tinggi dan tak ada ruang di samping: kartu menempel di dasar layar */
  }
  pop.style.left=x+"px";pop.style.top=y+"px";
 }
 function tick(){
  if(!on)return;
  var s=ST[cur],a=sasaran(s),b=a?kotak(a):null,vk=window.innerWidth+"x"+window.innerHeight;
  /* ukuran layar berubah (diputar), atau sasaran terlempar keluar layar (render ulang, tata letak bergeser): gulirkan lagi supaya sasaran terlihat */
  if(a&&(vk!==lastView||(fixN<3&&(b.t+b.h<0||b.t>window.innerHeight)))){
   if(vk===lastView)fixN++;
   geser(a);b=kotak(a);
  }
  lastView=vk;
  var k=(b?[b.l,b.t,b.w,b.h].map(Math.round).join(","):"c")+"|"+window.innerWidth+"x"+window.innerHeight+"|"+E.pop.offsetHeight;
  if(k!==lastKey){lastKey=k;tata(a)}
 }
 function loop(){if(!on)return;tick();raf=window.requestAnimationFrame(loop)}

 /* ---------- isi kartu ---------- */
 function isi(s){
  var no=nomor(),akhir=terakhir();
  E.r.setAttribute("data-e",s.e||"0");
  E.seal.hidden=!s.z;E.seal.textContent=s.z||"";
  E.num.textContent=s.id==="mulai"?"":no.n+" dari "+no.t;
  E.fill.style.width=(s.id==="mulai"?0:Math.round(no.n/no.t*100))+"%";
  E.h.textContent="";
  if(s.jz){var b=document.createElement("b");b.setAttribute("lang","zh");b.textContent=s.jz;E.h.appendChild(b);E.h.appendChild(document.createTextNode(" "+s.jt))}
  else E.h.textContent=s.jt;
  E.p.textContent=s.teks;
  E.prev.hidden=cur===0;
  E.skip.hidden=akhir;
  E.next.textContent=s.id==="mulai"?"Mulai panduan":akhir?"Selesai":"Berikutnya";
  E.live.textContent=(s.id==="mulai"?"":"Langkah "+no.n+" dari "+no.t+". ")+(s.jz?s.jz+" ":"")+s.jt+". "+s.teks;
 }

 /* ---------- alur ---------- */
 function tampil(i,arah){
  while(i>=0&&i<ST.length&&!ada(i))i+=arah;
  if(i>=ST.length){selesai();return}
  if(i<0)i=0;
  if(cur!==i&&on&&ST[cur].pasca){try{ST[cur].pasca()}catch(e){}}
  cur=i;
  var s=ST[i];
  if(s.pra){try{s.pra()}catch(e){}}
  isi(s);
  var a=sasaran(s);
  lastKey="";fixN=0;lastView=window.innerWidth+"x"+window.innerHeight;
  E.pop.style.width=Math.min(360,window.innerWidth-24)+"px";
  if(a)geser(a);
  tick();
  var f=E.next;
  if(document.activeElement&&E.pop.contains(document.activeElement)&&!document.activeElement.hidden)f=document.activeElement;
  try{f.focus({preventScroll:true})}catch(e){}
 }
 function maju(){if(on)tampil(cur+1,1)}
 function mundur(){if(on&&cur>0)tampil(cur-1,-1)}
 function selesai(){tutup(true,false)}
 function lewati(){tutup(true,true)}
 function tutup(simpan,catat){
  if(!on)return;
  on=false;window.cancelAnimationFrame(raf);
  try{if(ST[cur]&&ST[cur].pasca)ST[cur].pasca()}catch(e){}
  E.r.hidden=true;
  document.removeEventListener("keydown",tombolKeyboard,true);
  if(simpan)tandai();
  var f=prevFocus;prevFocus=null;
  try{
   /* fokus kembali ke elemen yang memicu panduan; bila itu baris menu yang kini tertutup, ke tombol akun.
      Mulai otomatis tidak punya pemicu (fokus ada di body), jadi fokus dibiarkan di awal halaman. */
   if(f&&f!==document.body&&f!==document.documentElement){
    if(!tampak(f))f=$("acct")||$("hs");
    if(f&&f.focus)f.focus({preventScroll:true});
   }
  }catch(e){}
  if(catat)beri("Panduan bisa dibuka lagi dari menu akun, di baris Panduan penggunaan.");
 }
 function beri(t){
  if(!E)return;
  E.toast.textContent=t;E.toast.classList.add("on");
  window.clearTimeout(toastT);toastT=window.setTimeout(function(){E.toast.classList.remove("on")},7000);
 }
 function tombolKeyboard(e){
  if(!on)return;
  var k=e.key,b,i;
  if(k==="Escape"){e.preventDefault();e.stopPropagation();lewati();return}
  if(k==="ArrowRight"){e.preventDefault();e.stopPropagation();maju();return}
  if(k==="ArrowLeft"){e.preventDefault();e.stopPropagation();mundur();return}
  if(k==="Tab"){
   b=[E.skip,E.prev,E.next].filter(function(x){return !x.hidden});
   i=b.indexOf(document.activeElement);
   if(i<0){e.preventDefault();b[b.length-1].focus()}
   else if(e.shiftKey&&i===0){e.preventDefault();b[b.length-1].focus()}
   else if(!e.shiftKey&&i===b.length-1){e.preventDefault();b[0].focus()}
  }
 }
 function mulai(){
  if(on||!email())return;
  buat();
  if(E.toast.classList.contains("on"))E.toast.classList.remove("on");
  try{if(window.hskMenu)window.hskMenu.close()}catch(e){}
  on=true;cur=0;prevFocus=document.activeElement;
  E.r.hidden=false;
  document.addEventListener("keydown",tombolKeyboard,true);
  window.scrollTo(0,0);
  tampil(0,1);
  loop();
 }

 /* ---------- kapan mulai ---------- */
 function beranda(){return !!document.querySelector("#view .hb")}
 function tunggu(fn,maks){
  var n=0;
  (function cek(){
   if(!root.classList.contains("booting")&&!root.classList.contains("gated")&&beranda()){fn();return}
   if(++n<maks)window.setTimeout(cek,250);
  })();
 }
 function otomatis(){
  if(!LS||!email()||sudah())return;
  tunggu(function(){
   window.setTimeout(function(){   /* beri waktu panel beranda yang menyusul (gembok, akses terbatas) */
    var m=$("acct-menu");
    if(on||sudah()||!beranda()||(m&&!m.hidden))return;
    mulai();
   },700);
  },80);
 }
 function manual(){
  if(on)return;
  if(!beranda()){var n=$("n-hm");if(n)n.click()}
  tunggu(mulai,40);
 }

 /* baris "Panduan penggunaan" di menu akun (dibuat skrip auth-gate; skrip lain boleh menambah baris) */
 function barisMenu(){
  var list=$("am-list");
  if(!list||$("acct-panduan"))return;
  var b=document.createElement("button");b.type="button";b.id="acct-panduan";b.className="am-row";
  b.innerHTML='<span class="am-ic"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M9.6 9.4a2.5 2.5 0 0 1 4.8.9c0 1.6-2.4 2-2.4 3.5"/><path d="M12 17h.01"/></svg></span><span class="am-tx">Panduan penggunaan<small>Lihat lagi fungsi tiap bagian</small></span>';
  b.addEventListener("click",function(){try{if(window.hskMenu)window.hskMenu.close()}catch(e){}manual()});
  list.appendChild(b);
 }

 window.hskTur={mulai:manual,tutup:function(){tutup(false,false)},sudah:sudah};
 /* Skrip defer jalan sebelum DOMContentLoaded; menu akun dibangun di pendengar DOMContentLoaded milik skrip lain yang lebih dulu terdaftar,
    jadi baris menu baru bisa ditambahkan di pendengar milik sini (berjalan setelahnya). "load" jadi cadangan. */
 function init(){barisMenu();otomatis()}
 document.addEventListener("DOMContentLoaded",init);
 window.addEventListener("load",barisMenu);
 if(document.readyState==="complete")init();
})();
