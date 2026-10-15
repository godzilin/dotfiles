// ==UserScript==
// @name         Apple Music: música local
// @namespace    godzilin
// @version      1.1
// @description  Panel "Local" en music.apple.com que reproduce ~/Music (servido por server.py en 127.0.0.1:47823)
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

  const host = el("div");
  host.id = "local-music";
  const root = host.attachShadow({ mode: "open" });
  root.innerHTML = `<style>
    :host { all: initial; font-family: "IBM Plex Sans", sans-serif; color: #e8dfc8; }
    button { font: inherit; color: inherit; background: none; border: 0; cursor: pointer; }
    .toggle { position: fixed; right: 18px; top: 14px; z-index: 2147483646; padding: 6px 14px;
      border-radius: 6px; background: #24211b; border: 1px solid #3d382d; font-size: 13px; letter-spacing: .08em; }
    .toggle:hover, .toggle.on { border-color: #e9a23b; color: #e9a23b; }
    .panel { position: fixed; inset: 0 0 0 260px; z-index: 2147483645; background: #1a1814;
      display: none; flex-direction: column; border-left: 1px solid #3d382d; }
    .panel.open { display: flex; }
    @media (max-width: 760px) { .panel { left: 0; } }
    header { display: flex; align-items: baseline; gap: 12px; padding: 28px 32px 8px; }
    h1 { margin: 0; font-size: 30px; font-weight: 600; }
    .stripe { height: 4px; width: 120px; margin: 0 32px 16px;
      background: linear-gradient(90deg, #e0c36a 0 25%, #e9a23b 25% 50%, #d9652b 50% 75%, #c8553d 75%); }
    .sub { color: #857c69; font-size: 13px; }
    .list { flex: 1; overflow-y: auto; padding: 0 32px 24px; }
    .album { display: grid; grid-template-columns: 180px 1fr; gap: 24px; margin: 16px 0 32px; }
    @media (max-width: 760px) { .album { grid-template-columns: 1fr; } }
    .cover { width: 180px; aspect-ratio: 1; border-radius: 6px; background: #24211b; object-fit: cover; }
    .album h2 { margin: 0 0 2px; font-size: 20px; }
    .album .sub { margin-bottom: 12px; }
    .track { display: grid; grid-template-columns: 28px 1fr auto; gap: 8px; width: 100%; text-align: left;
      padding: 7px 8px; border-radius: 4px; border-bottom: 1px solid #24211b; font-size: 14px; }
    .track:hover { background: #24211b; }
    .track.now { color: #e9a23b; }
    .track .n, .track .d { color: #857c69; font-variant-numeric: tabular-nums; }
    .bar { display: flex; align-items: center; gap: 14px; padding: 12px 32px; background: #121110;
      border-top: 1px solid #3d382d; font-size: 13px; }
    .bar img { width: 40px; height: 40px; border-radius: 4px; background: #24211b; object-fit: cover; }
    .bar .meta { min-width: 0; width: 220px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .bar .ctl { font-size: 18px; padding: 4px 6px; }
    .bar .ctl:hover { color: #e9a23b; }
    .bar input { flex: 1; accent-color: #e9a23b; }
    .bar .t { color: #857c69; font-variant-numeric: tabular-nums; }
    .err { color: #c8553d; padding: 16px 0; }
  </style>
  <button class="toggle">LOCAL</button>
  <section class="panel">
    <header><h1>Música local</h1><span class="sub"></span></header>
    <div class="stripe"></div>
    <div class="list"></div>
    <div class="bar">
      <img alt="">
      <div class="meta">—</div>
      <button class="ctl prev" title="Anterior">⏮</button>
      <button class="ctl play" title="Play/Pausa">▶</button>
      <button class="ctl next" title="Siguiente">⏭</button>
      <span class="t cur">0:00</span><input type="range" min="0" max="1000" value="0"><span class="t dur">0:00</span>
    </div>
  </section>`;
  const $ = s => root.querySelector(s);

  const audio = new Audio();
  let queue = [], pos = -1, rows = new Map(), covers = new Map();

  const cover = t => {
    if (!t.cover) return Promise.resolve("");
    if (!covers.has(t.album)) covers.set(t.album, blobUrl(`/cover?f=${encodeURIComponent(t.path)}`).catch(() => ""));
    return covers.get(t.album);
  };

  // Que no suenen a la vez Apple Music y la música local
  const musicKit = () => { try { return unsafeWindow.MusicKit.getInstance(); } catch { return null; } };
  const hookMusicKit = () => {
    const mk = musicKit();
    if (!mk || mk.__localHooked) return;
    mk.__localHooked = true;
    mk.addEventListener("playbackStateDidChange", e => { if (e.state === 2) audio.pause(); });
  };

  async function play(i) {
    if (i < 0 || i >= queue.length) return;
    const t = queue[i];
    pos = i;
    try { musicKit()?.pause(); } catch {}
    hookMusicKit();
    rows.forEach((r, p) => r.classList.toggle("now", p === t.path));
    $(".meta").textContent = `${t.title} — ${t.artist}`;
    if (audio.src) URL.revokeObjectURL(audio.src);
    try {
      audio.src = await blobUrl("/" + enc(t.path));
    } catch (e) { $(".meta").textContent = e.message; return; }
    if (pos !== i) return; // se pulsó otra pista mientras cargaba
    audio.play();
    const art = await cover(t);
    $(".bar img").src = art;
    if ("mediaSession" in navigator) {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: t.title, artist: t.artist, album: t.album, artwork: art ? [{ src: art }] : [] });
      navigator.mediaSession.setActionHandler("previoustrack", () => play(pos - 1));
      navigator.mediaSession.setActionHandler("nexttrack", () => play(pos + 1));
    }
  }

  audio.addEventListener("ended", () => play(pos + 1));
  audio.addEventListener("play", () => $(".play").textContent = "⏸");
  audio.addEventListener("pause", () => $(".play").textContent = "▶");
  audio.addEventListener("timeupdate", () => {
    $(".cur").textContent = time(audio.currentTime);
    $(".dur").textContent = time(audio.duration);
    if (audio.duration) $(".bar input").value = audio.currentTime / audio.duration * 1000;
  });
  $(".bar input").addEventListener("input", e => { if (audio.duration) audio.currentTime = e.target.value / 1000 * audio.duration; });
  $(".play").onclick = () => audio.src ? (audio.paused ? audio.play() : audio.pause()) : play(0);
  $(".prev").onclick = () => audio.currentTime > 3 ? (audio.currentTime = 0) : play(pos - 1);
  $(".next").onclick = () => play(pos + 1);

  async function load() {
    const list = $(".list");
    list.textContent = "";
    rows = new Map();
    let tracks;
    try { tracks = await get("/index.json", "json"); }
    catch (e) { list.append(el("div", "err", e.message)); return; }
    const albums = Map.groupBy(tracks, t => `${t.artist}\u0000${t.album}`);
    queue = [...albums.values()].flatMap(a => a.sort((x, y) => x.track - y.track || x.title.localeCompare(y.title)));
    $(".sub").textContent = `${tracks.length} canciones · ${albums.size} álbumes`;
    for (const a of albums.values()) {
      const box = el("div", "album"), img = el("img", "cover"), info = el("div");
      cover(a[0]).then(src => { if (src) img.src = src; });
      info.append(el("h2", "", a[0].album), el("div", "sub", [a[0].artist, a[0].year].filter(Boolean).join(" · ")));
      for (const t of a) {
        const row = el("button", "track");
        row.append(el("span", "n", t.track || ""), el("span", "", t.title), el("span", "d", time(t.duration)));
        row.onclick = () => play(queue.indexOf(t));
        rows.set(t.path, row);
        info.append(row);
      }
      box.append(img, info);
      list.append(box);
    }
  }

  $(".toggle").onclick = () => {
    const open = $(".panel").classList.toggle("open");
    $(".toggle").classList.toggle("on", open);
    if (open) load();
  };

  document.documentElement.append(host);
})();
