      // ---- keyframe tracks: state is a pure function of time
      const EZ = {};
      const ez = (n) => EZ[n] || (EZ[n] = gsap.parseEase(n));
      function T(v0) { return { v0, segs: [] }; }
      function tw(tr, t, d, v, e) { tr.segs.push({ t, d: Math.max(d, 1e-4), v, e: ez(e || "power2.inOut") }); tr.segs.sort((a, b) => a.t - b.t); return tr; }
      function val(tr, time, n) {
        n = n === undefined ? tr.segs.length : n;
        let v = tr.v0;
        for (let i = 0; i < n; i++) {
          const s = tr.segs[i];
          if (time < s.t) break;
          const from = i === 0 ? tr.v0 : val(tr, s.t, i);
          const p = Math.min(1, (time - s.t) / s.d);
          v = from + (s.v - from) * s.e(p);
        }
        return v;
      }
      const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
      const back = ez("back.out(2.4)");

      // ---- camera
      const camX = T(DATA.cam0[0]), camY = T(DATA.cam0[1]), camL = T(Math.log(DATA.cam0[2])), camT = T(DATA.cam0[3]);
      DATA.cam.forEach(([t, d, x, y, s, tilt, e]) => { tw(camX, t, d, x, e); tw(camY, t, d, y, e); tw(camL, t, d, Math.log(s), e); tw(camT, t, d, tilt, e); });
      function shake(time) {
        let x = 0;
        [[14.6, 0.3, 18], [71.45, 0.34, 22]].forEach(([t, d, a]) => {
          if (time >= t && time < t + d) x += a * Math.sin((time - t) * 80) * (1 - (time - t) / d);
        });
        return x;
      }

      // ---- element tracks
      const nsFill = T(0); tw(nsFill, 6.6, 0.5, 0.42, "power2.out"); tw(nsFill, 11.0, 0.25, 0.55); tw(nsFill, 11.25, 0.25, 0.42); tw(nsFill, 19.2, 0.5, 0);
      tw(nsFill, 50.9, 0.6, 0.3); tw(nsFill, 54.0, 1.6, 0.48, "power1.inOut"); tw(nsFill, 58.5, 1.6, 0.32); tw(nsFill, 67.4, 0.6, 0.45); tw(nsFill, 71.6, 0.6, 0);
      const coastA = T(0); tw(coastA, 6.6, 0.6, 1); tw(coastA, 11.9, 0.4, 0); tw(coastA, 71.6, 0.8, 0.9);
      const nsDraw = T(0); tw(nsDraw, 3.25, 0.9, 1);
      const nsLineA = T(1); tw(nsLineA, 19.2, 0.4, 0);
      function pulse(time, t0, half, n, amp) {
        if (time < t0 || time > t0 + half * 2 * n) return 0;
        const ph = ((time - t0) / half) % 2;
        return amp * (ph < 1 ? ph : 2 - ph);
      }
      const order = ["GBR", "NOR", "DNK", "DEU", "NLD", "BEL", "FRA"];
      const cA = {}, flA = {}, flS = {};
      order.forEach((c, i) => {
        const t = 12.45 + i * 0.2;
        cA[c] = tw(tw(T(0), t, 0.25, 0.3), 14.55, 0.3, 0);
        flA[c] = tw(tw(T(0), t + 0.05, 0.2, 1), 14.5 + i * 0.03, 0.25, 0);
        flS[c] = tw(tw(T(0.2), t + 0.05, 0.35, 1, "back.out(2.4)"), 14.5 + i * 0.03, 0.25, 0.6);
      });
      tw(tw(cA.FRA, 35.3, 0.3, 0.35), 39.6, 0.4, 0);
      tw(tw(cA.GBR, 36.0, 0.3, 0.35), 39.6, 0.4, 0);

      const d1Draw = T(0); tw(d1Draw, 4.2, 0.55, 1, "power3.out"); tw(d1Draw, 32.9, 0, 0); tw(d1Draw, 37.2, 1.3, 1);
      const d1A = T(1); tw(d1A, 19.2, 0.3, 0); tw(d1A, 32.9, 0, 1); tw(d1A, 71.6, 0.5, 0);
      const d1Tick = T(0); tw(d1Tick, 5.0, 0.3, 0.8); tw(d1Tick, 32.9, 0, 0); tw(d1Tick, 38.4, 0.3, 0.8);
      const d2Draw = T(0); tw(d2Draw, 4.4, 0.75, 1, "power3.out"); tw(d2Draw, 39.7, 0, 0); tw(d2Draw, 42.4, 2.5, 1, "power1.inOut");
      const d2A = T(1); tw(d2A, 19.2, 0.3, 0); tw(d2A, 39.7, 0, 1); tw(d2A, 71.6, 0.5, 0);
      const d2Tick = T(0); tw(d2Tick, 5.0, 0.3, 0.8); tw(d2Tick, 39.7, 0, 0); tw(d2Tick, 44.8, 0.3, 0.8);

      const floodA = T(0); tw(floodA, 20.1, 1.4, 0.45, "power1.inOut"); tw(floodA, 24.5, 1.0, 0.95, "power2.out"); tw(floodA, 26.0, 0.6, 0);

      const rivers = [["Rhein", 52.2], ["Elbe", 52.75], ["Thames", 53.4]];
      const rDraw = {}, rA = T(1); tw(rA, 60.0, 0.4, 0);
      rivers.forEach(([r, t]) => { rDraw[r] = tw(T(0), t, 0.75, 1, "power2.out"); });
      const flowA = T(0); tw(flowA, 54.0, 0.4, 0.95); tw(flowA, 59.6, 0.4, 0);
      const outA = [0, 1, 2].map((i) => tw(tw(T(0), 58.5 + i * 0.1, 0.3, 1), 60.2, 0.3, 0));
      const pumpS = [0, 1, 2].map((i) => tw(T(0), 56.25 + i * 0.12, 0.35, 1, "back.out(2.6)"));
      const pumpA = T(1); tw(pumpA, 60.0, 0.3, 0);

      const markers = [["kiel", 28.45, 32.9, 1.0], ["mk1", 33.4, 37.1, 0.9], ["mk2", 40.3, 42.3, 0.9]];
      const R = 18;

      // labels: typewriter (chars), alpha, counters
      const L = DATA.labels;
      const lab = {};
      function typeL(k, t, per, tOut) {
        const n = L[k].t.length;
        lab[k] = { t0: t, per, a: tw(T(1), tOut, 0.2, 0), n };
      }
      typeL("nordsee", 3.35, 0.06, 6.5); typeL("see", 6.75, 0.035, 9.2);
      typeL("fr", 35.3, 0.03, 39.6); typeL("en", 36.0, 0.03, 39.6);
      typeL("sco", 41.5, 0.03, 47.5); typeL("shet", 42.6, 0.04, 47.5); typeL("nor", 43.9, 0.04, 47.5);
      typeL("kiel", 29.2, 0.06, 32.9);
      typeL("rhein", 52.25, 0.04, 60.0); typeL("elbe", 52.8, 0.04, 60.0); typeL("themse", 53.45, 0.04, 60.0);
      typeL("atl", 58.5, 0.04, 60.2);
      const ctr = {
        area: { show: 9.5, hide: 11.9, t: 9.6, d: 1.4, to: 500000, f: (v) => Math.round(v).toLocaleString("de-DE") + "+ KM²" },
        l161: { show: 37.3, hide: 39.6, t: 37.3, d: 1.2, to: 161, f: (v) => Math.round(v) + " KM" },
        l476: { show: 45.35, hide: 47.5, t: 45.35, d: 1.3, to: 476, f: (v) => Math.round(v) + " KM" },
      };
      const p2o = ez("power2.out");

      // ---- resources
      const cv = document.getElementById("map-cv");
      const ctx = cv.getContext("2d");
      const tw_ = document.getElementById("map-tw");
      const imW = document.getElementById("map-wide"), imD = document.getElementById("map-detail"), imF = document.getElementById("map-flood");
      const PA = {};
      Object.keys(DATA.paths).forEach((k) => { PA[k] = new Path2D(DATA.paths[k]); });
      const FX = 1000, FY = 2000;

      function flagCanvas(code) {
        const c = document.createElement("canvas"); c.width = 240; c.height = 160;
        const g = c.getContext("2d"); g.scale(4, 4);
        const rect = (x, y, w, h, col) => { g.fillStyle = col; g.fillRect(x, y, w, h); };
        if (code === "DEU") { rect(0, 0, 60, 13.4, "#000"); rect(0, 13.3, 60, 13.4, "#DD0000"); rect(0, 26.6, 60, 13.4, "#FFCE00"); }
        if (code === "NLD") { rect(0, 0, 60, 13.4, "#AE1C28"); rect(0, 13.3, 60, 13.4, "#fff"); rect(0, 26.6, 60, 13.4, "#21468B"); }
        if (code === "BEL") { rect(0, 0, 20.1, 40, "#000"); rect(20, 0, 20.1, 40, "#FDDA24"); rect(40, 0, 20, 40, "#EF3340"); }
        if (code === "FRA") { rect(0, 0, 20.1, 40, "#0055A4"); rect(20, 0, 20.1, 40, "#fff"); rect(40, 0, 20, 40, "#EF4135"); }
        if (code === "DNK") { rect(0, 0, 60, 40, "#C8102E"); rect(18, 0, 7, 40, "#fff"); rect(0, 16.5, 60, 7, "#fff"); }
        if (code === "NOR") { rect(0, 0, 60, 40, "#BA0C2F"); rect(16, 0, 10, 40, "#fff"); rect(0, 15, 60, 10, "#fff"); rect(18.5, 0, 5, 40, "#00205B"); rect(0, 17.5, 60, 5, "#00205B"); }
        if (code === "GBR") {
          rect(0, 0, 60, 40, "#012169");
          const ln = (w, col, d) => { g.strokeStyle = col; g.lineWidth = w; g.beginPath(); d(); g.stroke(); };
          ln(8, "#fff", () => { g.moveTo(0, 0); g.lineTo(60, 40); g.moveTo(60, 0); g.lineTo(0, 40); });
          ln(3, "#C8102E", () => { g.moveTo(0, 0); g.lineTo(60, 40); g.moveTo(60, 0); g.lineTo(0, 40); });
          ln(12, "#fff", () => { g.moveTo(30, 0); g.lineTo(30, 40); g.moveTo(0, 20); g.lineTo(60, 20); });
          ln(7, "#C8102E", () => { g.moveTo(30, 0); g.lineTo(30, 40); g.moveTo(0, 20); g.lineTo(60, 20); });
        }
        return c;
      }
      const FL = {};
      order.forEach((c) => { FL[c] = flagCanvas(c); });

      // ---- drawing helpers
      let S = 1;
      function strokeP(k, col, sw, a, prog, extra) {
        if (a <= 0.001) return;
        ctx.save();
        ctx.globalAlpha = a;
        ctx.strokeStyle = col;
        ctx.lineWidth = sw / S;
        ctx.lineCap = (extra && extra.cap) || "round";
        ctx.lineJoin = "round";
        if (extra && extra.off) ctx.translate(extra.off[0] / S, extra.off[1] / S);
        if (prog !== undefined && prog < 1) {
          const len = DATA.lens[k];
          if (prog <= 0.0005) { ctx.restore(); return; }
          ctx.setLineDash([len * prog, len * 2]);
        } else if (extra && extra.dash) {
          ctx.setLineDash(extra.dash.map((v) => v / S));
          ctx.lineDashOffset = extra.dashOff || 0;
        }
        ctx.stroke(PA[k]);
        ctx.restore();
      }
      function fillP(k, col, a) {
        if (a <= 0.001) return;
        ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = col; ctx.fill(PA[k], "evenodd"); ctx.restore();
      }
      function text(l, str, a, sc) {
        if (a <= 0.001 || !str) return;
        ctx.save();
        ctx.globalAlpha = a;
        ctx.translate(l.x, l.y);
        ctx.rotate((l.r * Math.PI) / 180);
        if (sc && sc !== 1) ctx.scale(sc, sc);
        ctx.font = "700 " + l.fs + "px Oswald";
        ctx.letterSpacing = (l.fs * l.sp).toFixed(1) + "px";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.lineJoin = "round";
        ctx.strokeStyle = "rgba(6,21,42,.85)";
        ctx.lineWidth = l.fs * 0.2;
        ctx.strokeText(str, 0, 0);
        ctx.fillStyle = l.c;
        ctx.fillText(str, 0, 0);
        ctx.restore();
      }
      function ring(x, y, r, col, w, a) {
        if (a <= 0.001) return;
        ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = col; ctx.lineWidth = w; ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.stroke(); ctx.restore();
      }
      function dot(x, y, r, col, a) {
        if (a <= 0.001) return;
        ctx.save(); ctx.globalAlpha = a; ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill(); ctx.restore();
      }

      function renderAt(time) {
        const s = Math.exp(val(camL, time)); S = s;
        const cx = val(camX, time), cy = val(camY, time), tilt = val(camT, time);
        tw_.style.transform = "perspective(1500px) rotateX(" + tilt.toFixed(3) + "deg)";
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.fillStyle = "#06152A";
        ctx.fillRect(0, 0, cv.width, cv.height);
        ctx.setTransform(s, 0, 0, s, FX - cx * s + shake(time), FY - cy * s);
        ctx.imageSmoothingQuality = "high";
        if (imW.complete) ctx.drawImage(imW, 0, 0, DATA.world[0], DATA.world[1]);
        const [dx, dy, dw, dh] = DATA.det;
        if (imD.complete) ctx.drawImage(imD, dx, dy, dw, dh);
        const fa = val(floodA, time);
        if (fa > 0.001 && imF.complete) { ctx.globalAlpha = fa; ctx.drawImage(imF, dx, dy, dw, dh); ctx.globalAlpha = 1; }

        // countries
        order.forEach((c) => {
          const a = val(cA[c], time);
          if (a > 0.001) { fillP("c" + c, "#FF7A1A", a); strokeP("c" + c, "#FFE2CC", 1.6, Math.min(1, a * 3)); }
        });
        // north sea
        const nf = val(nsFill, time);
        fillP("ns", "#4DF0C8", nf);
        const fl = pulse(time, 6.7, 0.18, 1, 0.35) + pulse(time, 54.2, 0.3, 2, 0.28);
        fillP("ns", "#9FFFE6", fl);
        const ca = val(coastA, time);
        if (ca > 0.001) { strokeP("coast", "#fff", 5, 0.18 * ca); strokeP("coast", "#fff", 1.4, 0.85 * ca); }
        const nd = val(nsDraw, time), na = val(nsLineA, time);
        strokeP("ns", "#4DF0C8", 9, 0.35 * na, nd);
        strokeP("ns", "#EFFFFA", 2.6, na, nd);
        // rivers
        const ra = val(rA, time);
        rivers.forEach(([r]) => {
          const p = val(rDraw[r], time);
          if (p <= 0) return;
          strokeP("r" + r, "#4DF0C8", 11, 0.4 * ra, p);
          strokeP("r" + r, "#E9FFF8", 3.4, ra, p);
          const fa2 = val(flowA, time) * ra;
          if (fa2 > 0.001) strokeP("r" + r, "#ffffff", 3.8, fa2, undefined, { dash: [4, 12], dashOff: -(time - 54) * 60 / S });
        });
        // dams
        [["dam1", d1Draw, d1A, d1Tick], ["dam2", d2Draw, d2A, d2Tick]].forEach(([k, dr, al, tk]) => {
          const p = val(dr, time), a = val(al, time);
          if (p <= 0 || a <= 0) return;
          strokeP(k, "#000", 15, 0.45 * a, p, { off: [2, 4] });
          strokeP(k, "#DCE4EC", 11, a, p);
          strokeP(k, "#8FA0B2", 11, val(tk, time) * a, undefined, { dash: [1.5, 6], cap: "butt" });
          strokeP(k, "#FF7A1A", 4, a, p, { off: [0, -3] });
        });
        // outflow arrows
        [0, 1, 2].forEach((i) => {
          const a = val(outA[i], time);
          if (a <= 0.001) return;
          strokeP("out" + i, "#FF7A1A", 10, 0.35 * a);
          strokeP("out" + i, "#FFE7D2", 3.4, a, undefined, { dash: [8, 9], dashOff: -(time - 58.5) * 90 / S });
        });
        // markers
        markers.forEach(([k, t0, t1, per]) => {
          if (time < t0 || time > t1 + 0.3) return;
          const a = time > t1 ? 1 - (time - t1) / 0.3 : clamp((time - t0) / 0.2, 0, 1);
          const [x, y] = DATA.pts[k];
          const r = R / S;
          const ph = ((time - t0) % per) / per;
          ring(x, y, r * 2.4 * (0.4 + 0.9 * ph), "#FF7A1A", r * 0.18, a * (1 - ph));
          ring(x, y, r * 1.15, "#fff", r * 0.22, a);
          dot(x, y, r * 0.55, "#FF7A1A", a);
        });
        // pumps
        const pa = val(pumpA, time);
        [0, 1, 2].forEach((i) => {
          const sc = val(pumpS[i], time) * 1;
          if (sc <= 0.001 || pa <= 0.001) return;
          const [x, y] = DATA.pts["pump" + i];
          const r = (26 / S) * sc;
          ctx.save();
          ctx.globalAlpha = pa * clamp(sc * 2, 0, 1);
          ctx.translate(x, y);
          ctx.fillStyle = "#06152A"; ctx.strokeStyle = "#FF7A1A"; ctx.lineWidth = r * 0.16;
          ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
          ctx.rotate(Math.max(0, time - 56.3) * 8);
          ctx.fillStyle = "#fff";
          for (let b = 0; b < 3; b++) {
            ctx.rotate((Math.PI * 2) / 3);
            ctx.beginPath(); ctx.moveTo(0, 0); ctx.quadraticCurveTo(r * 0.55, -r * 0.25, r * 0.62, -r * 0.62); ctx.quadraticCurveTo(r * 0.15, -r * 0.5, 0, 0); ctx.fill();
          }
          ctx.fillStyle = "#FF7A1A"; ctx.beginPath(); ctx.arc(0, 0, r * 0.14, 0, Math.PI * 2); ctx.fill();
          ctx.restore();
        });
        // flags
        order.forEach((c) => {
          const a = val(flA[c], time);
          if (a <= 0.001) return;
          const sc = val(flS[c], time);
          const [x, y] = DATA.flags[c];
          const w = DATA.flagW * sc, h = (w * 2) / 3, b = w * 0.05;
          ctx.save();
          ctx.globalAlpha = a;
          ctx.fillStyle = "rgba(0,0,0,.3)"; ctx.fillRect(x - w / 2 + b, y - h / 2 + b * 2, w, h);
          ctx.fillStyle = "#fff"; ctx.fillRect(x - w / 2 - b, y - h / 2 - b, w + 2 * b, h + 2 * b);
          ctx.drawImage(FL[c], x - w / 2, y - h / 2, w, h);
          ctx.restore();
        });
        // labels
        Object.keys(lab).forEach((k) => {
          const o = lab[k];
          if (time < o.t0) return;
          const n = Math.min(o.n, Math.floor((time - o.t0) / o.per) + 1);
          text(L[k], L[k].t.slice(0, n), val(o.a, time));
        });
        Object.keys(ctr).forEach((k) => {
          const o = ctr[k];
          if (time < o.show || time > o.hide + 0.25) return;
          const a = time > o.hide ? 1 - (time - o.hide) / 0.25 : clamp((time - o.show) / 0.2, 0, 1);
          const sc = time < o.show + 0.3 ? 0.5 + 0.5 * back(clamp((time - o.show) / 0.3, 0, 1)) : 1;
          const v = o.to * p2o(clamp((time - o.t) / o.d, 0, 1));
          text(L[k], o.f(v), a, sc);
        });
      }

      const ready = Promise.all([imW, imD, imF].map((im) => (im.complete ? Promise.resolve() : im.decode().catch(() => {})))
        .concat([document.fonts.load("700 40px Oswald")]));
      let isReady = false;
      ready.then(() => { isReady = true; });
      window.addEventListener("hf-seek", (e) => {
        if (!isReady) e.detail.waitUntil(ready.then(() => renderAt(e.detail.time)));
        renderAt(e.detail.time);
      });
      renderAt(0);
      ready.then(() => renderAt(0));

      const tl = gsap.timeline({ paused: true });
      tl.to({}, { duration: DUR }, 0);
      window.__timelines["map"] = tl;
