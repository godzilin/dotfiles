// ==UserScript==
// @name         Apple Music: música local
// @namespace    godzilin
// @version      2.3
// @description  "Música local" en la barra lateral de music.apple.com: reproduce ~/Music (servido por server.py en 127.0.0.1:47823)
// @match        https://music.apple.com/*
// @grant        GM_xmlhttpRequest
// @grant        unsafeWindow
// @connect      127.0.0.1
// @updateURL    http://127.0.0.1:47823/local-music.user.js
// @downloadURL  http://127.0.0.1:47823/local-music.user.js
// @run-at       document-idle
// @noframes
// ==/UserScript==

(() => {
  const API = "http://127.0.0.1:47823";

  // La CSP de Apple bloquea fetch a localhost; GM_xmlhttpRequest la salta y blob: sí está permitido
  const get = (path, type) => new Promise((ok, fail) => GM_xmlhttpRequest({
    url: API + path, responseType: type,
    onload: r => r.status === 200 ? ok(r.response) : fail(new Error(`${path}: HTTP ${r.status}`)),
    onerror: () => fail(new Error("server.py no responde (systemctl --user status local-music)")),
  }));
  const blobUrl = async path => URL.createObjectURL(await get(path, "blob"));
  const enc = p => p.split("/").map(encodeURIComponent).join("/");
  const time = s => isFinite(s) ? `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}` : "0:00";
  const el = (tag, cls, text) => Object.assign(document.createElement(tag), cls ? { className: cls } : {}, text != null ? { textContent: text } : {});
  const NOTE = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path transform="translate(3.6 3.6) scale(.7)" d="M9 18.5a3 3 0 1 1-1.5-2.6V5.6c0-.5.3-.9.8-1l10-2.4c.6-.1 1.2.3 1.2 1v12.3a3 3 0 1 1-1.5-2.6V7.3L9 9.4z"/></svg>`;

  // Lo de Apple se oculta (no se borra) mientras se ve/suena lo local, para que Svelte no se rompa
  document.head.append(Object.assign(document.createElement("style"), { textContent: `
    #scrollable-page.lm-open > :not(#lm-page) { display: none !important; }
    .player-bar.lm-playing > :not(#lm-bar) { display: none !important; }
  ` }));

  // ---------- página "Música local", dentro del área de contenido de Apple ----------
  const page = el("div");
  page.id = "lm-page";
  const pr = page.attachShadow({ mode: "open" });
  pr.innerHTML = `<style>
    :host { display: block; font-family: "IBM Plex Sans", sans-serif; color: #e8dfc8; }
    button { font: inherit; color: inherit; background: none; border: 0; cursor: pointer; }
    .wrap { padding: 32px 40px 140px; }
    header { display: flex; align-items: baseline; gap: 12px; }
    h1 { margin: 0; font-size: 30px; font-weight: 700; }
    .stripe { height: 4px; width: 120px; margin: 10px 0 24px;
      background: linear-gradient(90deg, #e0c36a 0 25%, #e9a23b 25% 50%, #d9652b 50% 75%, #c8553d 75%); }
    .sub { color: #857c69; font-size: 13px; }
    .album { display: grid; grid-template-columns: 200px 1fr; gap: 28px; margin: 0 0 40px; }
    @media (max-width: 700px) { .album { grid-template-columns: 1fr; } }
    .cover { width: 200px; aspect-ratio: 1; border-radius: 8px; background: #24211b; object-fit: cover; }
    .album h2 { margin: 0 0 2px; font-size: 22px; }
    .album .sub { margin-bottom: 14px; }
    .playall { margin-bottom: 12px; padding: 6px 18px; border-radius: 6px; background: #e9a23b; color: #121110; font-weight: 600; }
    .track { display: grid; grid-template-columns: 28px 1fr auto; gap: 8px; width: 100%; text-align: left;
      padding: 8px; border-radius: 4px; border-bottom: 1px solid #24211b; font-size: 14px; }
    .track:hover { background: #24211b; }
    .track.now { color: #e9a23b; }
    .track .n, .track .d { color: #857c69; font-variant-numeric: tabular-nums; }
    .err { color: #c8553d; }
  </style>
  <div class="wrap">
    <header><h1>Música local</h1><span class="sub count"></span></header>
    <div class="stripe"></div>
    <div class="list"></div>
  </div>`;

  // ---------- controles locales, dentro de la barra de reproducción de Apple ----------
  const bar = el("div");
  bar.id = "lm-bar";
  const br = bar.attachShadow({ mode: "open" });
  br.innerHTML = `<style>
    :host { display: flex; width: 100%; height: 100%; font-family: "IBM Plex Sans", sans-serif; color: #e8dfc8;
      background: #1a1814e6; backdrop-filter: blur(20px) saturate(140%); border: 1px solid #3d382d; border-radius: 18px; box-sizing: border-box; }
    button { font: inherit; color: inherit; background: none; border: 0; cursor: pointer; }
    .row { flex: 1; display: flex; align-items: center; gap: 16px; padding: 0 18px; min-width: 0; }
    .ctl { font-size: 17px; padding: 4px; opacity: .9; } .ctl:hover { color: #e9a23b; }
    .lcd { flex: 1; display: flex; align-items: center; gap: 10px; min-width: 0; height: 44px;
      background: #121110cc; border: 1px solid #3d382d; border-radius: 6px; padding: 0 10px 0 0; overflow: hidden; }
    .lcd img { width: 44px; height: 44px; object-fit: cover; background: #24211b; }
    .txt { flex: 1; min-width: 0; font-size: 12px; line-height: 1.3; }
    .txt div { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .txt .a { color: #b3a891; }
    .seek { width: 100%; height: 3px; margin-top: 3px; background: #3d382d; border-radius: 2px; cursor: pointer; position: relative; }
    .seek i { position: absolute; inset: 0 auto 0 0; background: #e9a23b; border-radius: 2px; }
    .t { font-size: 11px; color: #857c69; font-variant-numeric: tabular-nums; }
    .tag { font-size: 10px; letter-spacing: .12em; color: #e9a23b; }
  </style>
  <div class="row">
    <button class="ctl prev" title="Anterior">⏮</button>
    <button class="ctl play" title="Play/Pausa">⏸</button>
    <button class="ctl next" title="Siguiente">⏭</button>
    <div class="lcd">
      <img alt="">
      <div class="txt"><div class="ti">—</div><div class="a"></div><div class="seek"><i></i></div></div>
      <span class="t">0:00</span>
    </div>
    <span class="tag">LOCAL</span>
    <button class="ctl stop" title="Parar música local">✕</button>
  </div>`;
  const $p = s => pr.querySelector(s), $b = s => br.querySelector(s);

  const audio = new Audio();
  let queue = [], pos = -1, rows = new Map(), covers = new Map(), loaded = false;
  let open = false, playing = false, lastUrl = location.href, navItem = null, prevSelected = null;

  const cover = t => {
    if (!t.cover) return Promise.resolve("");
    if (!covers.has(t.album)) covers.set(t.album, blobUrl(`/cover?f=${encodeURIComponent(t.path)}`).catch(() => ""));
    return covers.get(t.album);
  };

  // Que no suenen a la vez Apple Music y la música local
  const musicKit = () => { try { return unsafeWindow.MusicKit.getInstance(); } catch { return null; } };
  const hookMusicKit = () => {
    const mk = musicKit();
    if (!mk || mk.__lmHooked) return;
    mk.__lmHooked = true;
    mk.addEventListener("playbackStateDidChange", e => { if (e.state === 2) stop(); });
  };

  function stop() {
    audio.pause();
    playing = false;
    document.querySelector(".player-bar")?.classList.remove("lm-playing");
    bar.remove();
  }

  async function play(i) {
    if (i < 0 || i >= queue.length) return;
    const t = queue[i];
    pos = i;
    try { musicKit()?.pause(); } catch {}
    hookMusicKit();
    playing = true;
    ensure();
    rows.forEach((r, p) => r.classList.toggle("now", p === t.path));
    $b(".ti").textContent = t.title;
    $b(".a").textContent = `${t.artist} — ${t.album}`;
    if (audio.src) URL.revokeObjectURL(audio.src);
    try {
      audio.src = await blobUrl("/" + enc(t.path));
    } catch (e) { $b(".ti").textContent = e.message; return; }
    if (pos !== i) return; // se pulsó otra pista mientras cargaba
    audio.play();
    const art = await cover(t);
    $b("img").src = art;
    if ("mediaSession" in navigator) {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: t.title, artist: t.artist, album: t.album, artwork: art ? [{ src: art }] : [] });
      navigator.mediaSession.setActionHandler("previoustrack", () => play(pos - 1));
      navigator.mediaSession.setActionHandler("nexttrack", () => play(pos + 1));
    }
  }

  audio.addEventListener("ended", () => pos + 1 < queue.length ? play(pos + 1) : stop());
  audio.addEventListener("play", () => $b(".play").textContent = "⏸");
  audio.addEventListener("pause", () => $b(".play").textContent = "▶");
  audio.addEventListener("timeupdate", () => {
    $b(".t").textContent = `${time(audio.currentTime)} / ${time(audio.duration)}`;
    $b(".seek i").style.width = audio.duration ? `${audio.currentTime / audio.duration * 100}%` : "0";
  });
  $b(".seek").addEventListener("click", e => {
    const r = e.currentTarget.getBoundingClientRect();
    if (audio.duration) audio.currentTime = (e.clientX - r.left) / r.width * audio.duration;
  });
  $b(".play").onclick = () => audio.paused ? audio.play() : audio.pause();
  $b(".prev").onclick = () => audio.currentTime > 3 ? (audio.currentTime = 0) : play(pos - 1);
  $b(".next").onclick = () => play(pos + 1);
  $b(".stop").onclick = stop;

  async function load() {
    const list = $p(".list");
    list.textContent = "";
    rows = new Map();
    let tracks;
    try { tracks = await get("/index.json", "json"); }
    catch (e) { list.append(el("div", "err", e.message)); return; }
    const albums = Map.groupBy(tracks, t => `${t.artist}\u0000${t.album}`);
    const current = queue[pos]?.path;
    queue = [...albums.values()].flatMap(a => a.sort((x, y) => x.track - y.track || x.title.localeCompare(y.title)));
    pos = queue.findIndex(t => t.path === current);
    $p(".count").textContent = `${tracks.length} canciones · ${albums.size} álbumes`;
    for (const a of albums.values()) {
      const box = el("div", "album"), img = el("img", "cover"), info = el("div"), all = el("button", "playall", "▶ Reproducir");
      cover(a[0]).then(src => { if (src) img.src = src; });
      all.onclick = () => play(queue.indexOf(a[0]));
      info.append(el("h2", "", a[0].album), el("div", "sub", [a[0].artist, a[0].year].filter(Boolean).join(" · ")), all);
      for (const t of a) {
        const row = el("button", "track" + (t.path === current ? " now" : ""));
        row.append(el("span", "n", t.track || ""), el("span", "", t.title), el("span", "d", time(t.duration)));
        row.onclick = () => play(queue.indexOf(t));
        rows.set(t.path, row);
        info.append(row);
      }
      box.append(img, info);
      list.append(box);
    }
    loaded = true;
  }

  // ---------- entrada en la barra lateral ----------
  // Apple marca la entrada activa con aria-selected y la clase navigation-item--selected
  const select = (li, v) => { li?.setAttribute("aria-selected", String(v)); li?.classList.toggle("navigation-item--selected", v); };

  function setOpen(v) {
    if (open === v) return;
    open = v;
    const items = [...document.querySelectorAll("li.navigation-item")];
    if (v) {
      prevSelected = items.find(li => li !== navItem && li.classList.contains("navigation-item--selected"));
      select(prevSelected, false);
      if (!loaded) load();
      document.querySelector("#scrollable-page")?.scrollTo(0, 0);
    } else if (prevSelected && location.href === lastUrl) {
      select(prevSelected, true);
    }
    select(navItem, v);
    if (!v) { page.remove(); document.querySelector("#scrollable-page")?.classList.remove("lm-open"); }
    ensure();
  }

  // Bajo "Canciones" de Biblioteca; si aún no ha cargado, tras "Radio"
  const navAnchor = () => document.querySelector('li.navigation-item a[href*="/library/songs"]')?.closest("li")
    || document.querySelector("li.navigation-item__radio");

  function makeNavItem() {
    // Se clona una entrada de Apple para heredar su aspecto exacto; los clones no llevan sus eventos
    const anchor = navAnchor();
    if (!anchor) return null;
    const li = anchor.cloneNode(true);
    li.classList.add("lm-nav");
    select(li, false);
    const a = li.querySelector("a");
    a.removeAttribute("href");
    a.removeAttribute("data-testid");
    a.setAttribute("aria-pressed", "false");
    a.style.cursor = "pointer";
    li.querySelector(".navigation-item__icon").innerHTML = NOTE;
    li.querySelector(".navigation-item__label").textContent = "Música local";
    a.addEventListener("click", e => { e.preventDefault(); e.stopPropagation(); setOpen(true); });
    anchor.after(li);
    return li;
  }

  // Svelte re-renderiza a menudo: se vuelve a colocar todo lo nuestro si desaparece
  function ensure() {
    if (location.href !== lastUrl) { lastUrl = location.href; setOpen(false); }
    if (!navItem?.isConnected) {
      document.querySelectorAll("li.lm-nav").forEach(n => n.remove());
      navItem = makeNavItem();
      select(navItem, open);
    }
    const anchor = navAnchor();
    if (navItem && anchor && navItem.previousElementSibling !== anchor) anchor.after(navItem);
    const sp = document.querySelector("#scrollable-page");
    if (open && sp) {
      sp.classList.add("lm-open");
      if (page.parentNode !== sp) sp.prepend(page);
    }
    const pb = document.querySelector(".player-bar");
    if (playing && pb) {
      pb.classList.add("lm-playing");
      if (bar.parentNode !== pb) pb.append(bar);
    }
  }

  // Cualquier otro clic en la barra lateral (aunque no cambie la URL) cierra la página local
  document.addEventListener("click", e => {
    if (open && e.target.closest?.("li.navigation-item") && !e.target.closest("li.lm-nav")) setOpen(false);
  }, true);

  let scheduled = false;
  new MutationObserver(() => {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => { scheduled = false; ensure(); });
  }).observe(document.body, { childList: true, subtree: true });
  ensure();
})();
