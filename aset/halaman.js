/* Skrip bersama halaman Langganan (langganan.html) dan Cara berlangganan (cara-berlangganan.html).
   Dimuat di <head> tanpa defer: bagian awal (bingkai, tema) harus jalan sebelum halaman tampil.
   - Tema: mengikuti pilihan yang disimpan aplikasi (ui_tema), lalu pengaturan perangkat.
   - Akun: hanya MEMBACA sesi yang disimpan halaman depan (acct_auth, acct_last). Tidak pernah menulis atau menghapus apa pun dari sesi.
   - "Sudah bayar": membuka Telegram pengelola dengan pesan terisi (paket dan email akun). Situs tidak memproses pembayaran.
   - Pencatatan funnel: aturan dan kunci sama dengan skrip funnel-ui di index.html (kode acak zenta_did, tanpa email, tanpa IP,
     Do Not Track dan Global Privacy Control dihormati, maksimal 30 peristiwa per perangkat per hari).
   Mengubah paket, harga, atau kontak: konstanta di bawah, teks di langganan.html dan cara-berlangganan.html,
   lalu bagian yang sama di index.html (skrip bayar-ui, <template id="byr-tpl">, kunciHTML). */
(function(){
 /* anti-clickjacking: halaman ini tidak boleh dimuat di dalam bingkai situs lain (GitHub Pages tidak bisa mengirim header X-Frame-Options) */
 try{if(window.top!==window.self){document.documentElement.style.visibility="hidden";window.top.location=window.self.location.href}}catch(e){document.documentElement.style.visibility="hidden"}
 var LS=null;
 try{LS=window.localStorage;LS.getItem("ui_tema")}catch(e){LS=null}
 try{var t=LS&&LS.getItem("ui_tema");if(t==="terang")document.documentElement.setAttribute("data-theme","light");else if(t==="gelap")document.documentElement.setAttribute("data-theme","dark")}catch(e){}

 var TG="axntsu",NAMA="Zenta 汉+",HARGA="Rp 30.000",DUR="1 bulan";
 var RE_EMAIL=/^[^\s@]+@[^\s@]+\.[^\s@]+$/;

 /* sesi dari halaman depan: sah bila token, email, dan masa berlaku masih ada (aturan sama dengan readAuth di index.html) */
 function sesi(){
  try{
   var a=JSON.parse(LS.getItem("acct_auth")||"null");
   if(a&&typeof a.token==="string"&&a.token&&typeof a.email==="string"&&a.email&&typeof a.exp==="number"&&a.exp>Date.now()/1000+60)return a.email.toLowerCase();
  }catch(e){}
  return"";
 }
 function terakhir(){try{var e=String(LS.getItem("acct_last")||"").toLowerCase();return RE_EMAIL.test(e)?e:""}catch(e){return""}}

 /* ---- pencatatan funnel (versi ringkas funnel-ui) ---- */
 var F=(function(){
  var URL="https://n8n.zenta.web.id/webhook/hsk-ev",KD="zenta_did",KS="zenta_f",MAKS=30,N=navigator,D="";
  var nol={ev:function(){}};
  if(!LS||typeof fetch!=="function"||/^(1|yes)$/.test(String(N.doNotTrack||window.doNotTrack||N.msDoNotTrack||""))||N.globalPrivacyControl===true)return nol;
  function hex(){var s="",a,i;try{a=new Uint8Array(8);crypto.getRandomValues(a);for(i=0;i<8;i++)s+=("0"+a[i].toString(16)).slice(-2)}catch(e){s="";for(i=0;i<16;i++)s+=Math.floor(Math.random()*16).toString(16)}return s}
  try{D=LS.getItem(KD)||"";if(!/^[0-9a-f]{16}$/.test(D)){D=hex();LS.setItem(KD,D)}}catch(e){return nol}
  function hari(){var d=new Date();return d.getFullYear()+"-"+("0"+(d.getMonth()+1)).slice(-2)+"-"+("0"+d.getDate()).slice(-2)}
  return{ev:function(nama,info){
   try{
    var ST={};try{ST=JSON.parse(LS.getItem(KS)||"{}")}catch(e){ST={}}
    if(!ST||ST.constructor!==Object)ST={};
    var h=hari(),b=ST.b;
    if(!b||b.h!==h)b=ST.b={h:h,n:0};
    if(b.n>=MAKS)return;
    b.n++;LS.setItem(KS,JSON.stringify(ST));
    fetch(URL,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({did:D,e:[{ev:nama,info:info||""}]}),mode:"cors",credentials:"omit",keepalive:true}).then(null,function(){});
   }catch(x){}
  }};
 })();
 function sekaliSesi(k){try{if(sessionStorage.getItem(k))return false;sessionStorage.setItem(k,"1");return true}catch(e){return false}}

 function pesan(e){return["Halo, saya sudah bayar langganan Zenta 汉.","Paket: "+NAMA+" ("+HARGA+", "+DUR+")","Email akun: "+e,"Bukti bayar saya lampirkan di bawah."].join("\n")}
 function tautan(e){return"https://t.me/"+TG+"?text="+encodeURIComponent(pesan(e))}
 function bukaBaru(u){var a=document.createElement("a");a.href=u;a.target="_blank";a.rel="noopener noreferrer";a.style.display="none";document.body.appendChild(a);a.click();document.body.removeChild(a)}

 document.addEventListener("DOMContentLoaded",function(){
  var aku=sesi(),hal=document.body.getAttribute("data-hal")||"";

  /* kepala: yang sudah masuk melihat "Buka aplikasi" (ke halaman belajar), bukan "Masuk" */
  if(aku){
   var ak=document.querySelectorAll("[data-akun]"),i;
   for(i=0;i<ak.length;i++){ak[i].textContent="Buka aplikasi";ak[i].setAttribute("href","./")}
   var dm=document.querySelectorAll("[data-sudah-masuk]");
   for(i=0;i<dm.length;i++){dm[i].textContent="Kamu sudah masuk sebagai "+aku+".";dm[i].hidden=false}
   var bm=document.querySelectorAll("[data-belum-masuk]");
   for(i=0;i<bm.length;i++)bm[i].hidden=true;
   var bt=document.querySelectorAll("[data-sudah-masuk-tombol]");
   for(i=0;i<bt.length;i++)bt[i].hidden=false;
  }

  /* Tanya soal langganan (Telegram atau kotak pesan di halaman depan): hanya dicatat, tautannya biasa */
  document.addEventListener("click",function(ev){
   var t=ev.target&&ev.target.closest?ev.target.closest("[data-tanya]"):null;
   if(t)F.ev("tanya",hal==="cara"?"cara":"harga");
  });

  /* ---- konfirmasi pembayaran (hanya di cara-berlangganan.html) ---- */
  var root=document.querySelector("[data-byr-root]");if(!root)return;
  if(sekaliSesi("zenta_bl"))F.ev("bayar_lihat","halaman");
  var inp=root.querySelector("#byr-email"),go=root.querySelector("[data-byr-sudah]"),st=root.querySelector("[data-byr-st]"),
      out=root.querySelectorAll("[data-byr-email]"),hint=root.querySelector("#byr-email-hint");
  if(!inp||!go||!st)return;
  if(aku){inp.value=aku;if(hint)hint.textContent="Terisi dari akun yang sedang masuk di perangkat ini."}
  else{var l=terakhir();if(l){inp.value=l;if(hint)hint.textContent="Terisi dari akun terakhir di perangkat ini. Pastikan email ini benar."}}
  function nilai(){return String(inp.value||"").trim().toLowerCase()}
  function segar(){var e=nilai(),j;for(j=0;j<out.length;j++)out[j].textContent=e||"(email akunmu)"}
  function say(teks,err,href){
   st.textContent=teks||"";st.className="st"+(err?" err":"");
   if(href){var a=document.createElement("a");a.href=href;a.target="_blank";a.rel="noopener noreferrer";a.textContent="Buka Telegram @"+TG;st.appendChild(document.createTextNode(" "));st.appendChild(a)}
  }
  inp.addEventListener("input",function(){segar();if(inp.getAttribute("aria-invalid")==="true"&&RE_EMAIL.test(nilai())){inp.removeAttribute("aria-invalid");say("")}});
  segar();
  go.addEventListener("click",function(ev){
   ev.preventDefault();
   var e=nilai();
   if(!RE_EMAIL.test(e)){
    inp.setAttribute("aria-invalid","true");
    say(e?"Alamat email tidak valid. Tulis email yang kamu pakai untuk masuk ke Zenta.":"Tulis dulu email akun Zenta-mu, supaya pengelola tahu akun mana yang diaktifkan.",true);
    inp.focus();return;
   }
   inp.removeAttribute("aria-invalid");
   F.ev("bayar_sudah","halaman");
   var u=tautan(e);bukaBaru(u);
   say("Membuka Telegram. Kirim pesannya, lalu lampirkan bukti bayar. Tidak terbuka?",false,u);
  });
 });
})();
