// ==UserScript==
// @name         Apple Music: música local
// @namespace    godzilin
// @version      3.2
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
    .player-bar.lm-playing .chrome-player__lcd > :not(#lm-lcd) { display: none !important; }
    #lm-lcd .lm-progress { cursor: pointer; padding-block: 4px; }
    #lm-lcd .lm-progress::before { content: ""; display: block; height: 2px; border-radius: 2px; background: var(--systemQuaternary-onDark, #ffffff4d); }
    #lm-lcd .lm-progress i { position: absolute; left: 0; bottom: 4px; height: 2px; border-radius: 2px; background: var(--systemSecondary-onDark, #ffffffb3); }
    #lm-lcd .lm-progress { position: relative; }
    #lm-lcd .player-lcd__artwork { width: 34px; height: 34px; overflow: hidden; }
    #lm-lcd .player-lcd__artwork img { width: 100%; height: 100%; object-fit: cover; }
    #lm-lcd .lm-progress:hover::before, #lm-lcd .lm-progress:hover i { height: 4px; }
  ` }));

  // ---------- página "Música local", dentro del área de contenido de Apple ----------
  const page = el("div");
  page.id = "lm-page";
  const pr = page.attachShadow({ mode: "open" });
  pr.innerHTML = `<style>
    :host { display: block; color: var(--systemPrimary-onDark); }  /* colours and font come from the theme's userContent.css */
    button { font: inherit; color: inherit; background: none; border: 0; cursor: pointer; }
    .wrap { padding: 32px 40px 140px; }
    header { display: flex; align-items: baseline; gap: 12px; }
    h1 { margin: 0; font-size: 30px; font-weight: 700; }
    .stripe { height: 4px; width: 120px; margin: 10px 0 24px;
      background: linear-gradient(90deg, var(--lm-stripe-1) 0 25%, var(--lm-stripe-2) 25% 50%, var(--lm-stripe-3) 50% 75%, var(--lm-stripe-4) 75%); }
    .sub { color: var(--systemTertiary-onDark); font-size: 13px; }
    .album { display: grid; grid-template-columns: 200px 1fr; gap: 28px; margin: 0 0 40px; }
    @media (max-width: 700px) { .album { grid-template-columns: 1fr; } }
    .cover { width: 200px; aspect-ratio: 1; border-radius: 8px; background: var(--playerBackground); object-fit: cover; }
    .album h2 { margin: 0 0 2px; font-size: 22px; }
    .album .sub { margin-bottom: 14px; }
    .playall { margin-bottom: 12px; padding: 6px 18px; border-radius: 6px; background: var(--keyColor); color: var(--navSidebarBG); font-weight: 600; }
    .track { display: grid; grid-template-columns: 28px 1fr auto; gap: 8px; width: 100%; text-align: left;
      padding: 8px; border-radius: 4px; border-bottom: 1px solid var(--playerBackground); font-size: 14px; }
    .track:hover { background: var(--playerBackground); }
    .track.now { color: var(--keyColor); }
    .track .n, .track .d { color: var(--systemTertiary-onDark); font-variant-numeric: tabular-nums; }
    .err { color: var(--lm-error); }
  </style>
  <div class="wrap">
    <header><h1>Música local</h1><span class="sub count"></span></header>
    <div class="stripe"></div>
    <div class="list"></div>
  </div>`;

  // ---------- barra de reproducción: la de Apple, con su LCD rellenado con lo local ----------
  // Los hashes svelte-xxxx cambian en cada despliegue de Apple: se leen de sus hojas de estilo
  let selectors = "";
  const hash = cls => {
    const re = new RegExp(`\\.${cls}\\.(svelte-[a-z0-9]+)`);
    if (!re.test(selectors)) {
      const walk = rules => [...rules].flatMap(r => [r.selectorText || "", ...(r.cssRules ? walk(r.cssRules) : [])]);
      selectors = [...document.styleSheets].flatMap(s => { try { return walk(s.cssRules); } catch { return []; } }).join("\n");
    }
    return selectors.match(re)?.[1] || "";
  };

  function buildLcd() {
    const [L, A, Q, M, F, P] = ["player-lcd", "artwork-component", "lcd-meta", "marquee--primary", "marquee-line__fragment", "player-lcd__progress"].map(hash);
    const line = (kind, inner) => `<div class="marquee marquee--${kind} ${M}"><div class="marquee-line-container ${M}"><div class="marquee-line ${M} inactive"><div class="marquee-line__string-container ${M}"><div class="marquee-line__mask ${M}" dir="auto"><div class="marquee-line__scroller ${M}"><div class="marquee-line__scrolling-text-chunk ${M}"><span class="marquee-line__text-content ${M}">${inner}</span></div></div></div></div></div></div></div>`;
    const lcd = el("div");
    lcd.id = "lm-lcd";
    lcd.innerHTML = `<div class="player-lcd ${L}">
      <div class="player-lcd__artwork ${L}"><div class="artwork-component artwork-component--aspect-ratio artwork-component--orientation-square ${A} artwork-component--fullwidth artwork-component--has-borders artwork-component--downloaded" style="--aspect-ratio: 1; --placeholder-bg-color: transparent;"><picture class="${A}"><img alt="" class="artwork-component__contents artwork-component__image ${A}" width="40" height="40" style="opacity: 1;"></picture></div></div>
      <div class="player-lcd__metadata ${L}"><div class="metadata"><div class="lcd-meta ${Q}" aria-live="assertive"><div class="lcd-meta__primary-container ${Q}">${line("primary", `<span class="marquee-line__fragment ${F} lm-title"></span>`)}</div>${line("secondary",
        `<span class="marquee-line__fragment ${F}"><button class="lcd-meta-line__fragment ${F} lm-artist"></button></span><span class="marquee-line__fragment ${F}">—</span><span class="marquee-line__fragment ${F}"><button class="lcd-meta-line__fragment ${F} lm-album"></button></span>`)}</div></div></div>
      <div class="player-lcd__after-metadata ${L}"></div>
      <div class="player-lcd__progress ${P || L} lm-progress"><i></i></div>
    </div>`;
    lcd.querySelector(".lm-artist").onclick = lcd.querySelector(".lm-album").onclick = () => setOpen(true);
    lcd.querySelector(".lm-progress").addEventListener("click", e => {
      const r = e.currentTarget.getBoundingClientRect();
      if (audio.duration) audio.currentTime = (e.clientX - r.left) / r.width * audio.duration;
    });
    return lcd;
  }
  let lcd = null;
  const $l = s => (lcd ||= buildLcd()).querySelector(s);
  const $p = s => pr.querySelector(s);

  const audio = new Audio();
  let queue = [], pos = -1, rows = new Map(), covers = new Map(), loaded = false;
  let open = false, playing = false, lastUrl = location.href, navItem = null, prevSelected = null;

  const cover = t => {
    if (!t.cover) return Promise.resolve("");
    if (!covers.has(t.album)) covers.set(t.album, blobUrl(`/cover?f=${encodeURIComponent(t.path)}`).catch(() => ""));
    return covers.get(t.album);
  };

  // Que no suenen a la vez Apple Music y la música local; el volumen es el de la barra de Apple
  const musicKit = () => { try { return unsafeWindow.MusicKit.getInstance(); } catch { return null; } };
  const hookMusicKit = () => {
    const mk = musicKit();
    if (!mk) return;
    audio.volume = mk.volume ?? 1;
    if (mk.__lmHooked) return;
    mk.__lmHooked = true;
    mk.addEventListener("playbackStateDidChange", e => { if (e.state === 2) stop(); });
    mk.addEventListener("playbackVolumeDidChange", () => { audio.volume = mk.volume; });
  };

  // Botones de Apple: se fuerza el icono play/pausa y se habilitan aunque Apple no tenga cola
  function syncControls() {
    const pb = document.querySelector(".player-bar");
    if (!playing || !pb) return;
    const on = !audio.paused;
    const [p, z] = [".playback-play__play", ".playback-play__pause"].map(s => pb.querySelector(s));
    p?.toggleAttribute("aria-hidden", on); z?.toggleAttribute("aria-hidden", !on);
    if (p?.getAttribute("aria-hidden") === "") p.setAttribute("aria-hidden", "true");
    if (z?.getAttribute("aria-hidden") === "") z.setAttribute("aria-hidden", "true");
    pb.querySelectorAll(".playback-play__play[disabled], .playback-play__pause[disabled]").forEach(b => b.disabled = false);
    pb.querySelectorAll("amp-playback-controls-item-skip").forEach(s => s.shadowRoot?.querySelectorAll("button[disabled]").forEach(b => b.disabled = false));
  }

  document.addEventListener("click", e => {
    if (!playing || !e.target.closest?.(".player-bar")) return;
    const ctl = e.target.closest("amp-playback-controls-play, amp-playback-controls-item-skip");
    if (!ctl) return;
    e.preventDefault(); e.stopImmediatePropagation();
    if (ctl.matches("amp-playback-controls-play")) audio.paused ? audio.play() : audio.pause();
    else if (ctl.getAttribute("direction") === "next") play(pos + 1);
    else audio.currentTime > 3 ? (audio.currentTime = 0) : play(pos - 1);
  }, true);

  function stop() {
    audio.pause();
    playing = false;
    lcd?.remove();
    const pb = document.querySelector(".player-bar");
    pb?.classList.remove("lm-playing");
    pb?.querySelector(".playback-play__play")?.removeAttribute("aria-hidden");
    pb?.querySelector(".playback-play__pause")?.setAttribute("aria-hidden", "true");
    rows.forEach(r => r.classList.remove("now"));
    if ("mediaSession" in navigator) for (const a of ["play", "pause", "previoustrack", "nexttrack"]) navigator.mediaSession.setActionHandler(a, null);
  }

  async function play(i) {
    if (i < 0 || i >= queue.length) return;
    const t = queue[i];
    pos = i;
    try { musicKit()?.pause(); } catch {}
    hookMusicKit();
    playing = true;
    rows.forEach((r, p) => r.classList.toggle("now", p === t.path));
    $l(".lm-title").textContent = t.title;
    $l(".lm-artist").textContent = t.artist;
    $l(".lm-album").textContent = t.album;
    ensure();
    if (audio.src) URL.revokeObjectURL(audio.src);
    try {
      audio.src = await blobUrl("/" + enc(t.path));
    } catch (e) { $l(".lm-title").textContent = e.message; return; }
    if (pos !== i) return; // se pulsó otra pista mientras cargaba
    audio.play();
    const art = await cover(t);
    $l("img").src = art || "/assets/artwork/1x1.gif";
    if ("mediaSession" in navigator) {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: t.title, artist: t.artist, album: t.album, artwork: art ? [{ src: art }] : [] });
      // Si no, las teclas multimedia irían a MusicKit y cortarían lo local
      navigator.mediaSession.setActionHandler("play", () => audio.play());
      navigator.mediaSession.setActionHandler("pause", () => audio.pause());
      navigator.mediaSession.setActionHandler("previoustrack", () => play(pos - 1));
      navigator.mediaSession.setActionHandler("nexttrack", () => play(pos + 1));
    }
  }

  audio.addEventListener("ended", () => pos + 1 < queue.length ? play(pos + 1) : stop());
  audio.addEventListener("play", syncControls);
  audio.addEventListener("pause", syncControls);
  audio.addEventListener("timeupdate", () => {
    $l(".lm-progress i").style.width = audio.duration ? `${audio.currentTime / audio.duration * 100}%` : "0";
  });

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
    const slot = document.querySelector(".player-bar .chrome-player__lcd");
    if (playing && slot) {
      slot.closest(".player-bar").classList.add("lm-playing");
      if (lcd && lcd.parentNode !== slot) slot.append(lcd);
      syncControls();
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
