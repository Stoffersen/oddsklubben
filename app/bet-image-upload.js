(function () {
  "use strict";
  var input = document.getElementById("betImageInput");
  var preview = document.getElementById("betImagePreview");
  if (!input || !preview) return;
  var objectUrl = null;
  var draftKey = "oddsklubben-local-coupon-drafts-v1";
  var overview = document.createElement("section");
  overview.style.cssText = "margin:16px 0;padding:12px;border:1px solid #d6ddd6;border-radius:12px";
  overview.setAttribute("aria-label", "Gemte bettingkuponer");
  preview.parentNode.appendChild(overview);
  function getDrafts() {
    try {
      var result = JSON.parse(localStorage.getItem(draftKey) || "[]");
      return Array.isArray(result) ? result.filter(function (r) { return r && typeof r === "object"; }) : [];
    } catch (_) { return []; }
  }
  function downloadDrafts(records) {
    var blob = new Blob([JSON.stringify({schema_version:1, exported_at:new Date().toISOString(), coupons:records}, null, 2)], {type:"application/json"});
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = "oddsklubben-kuponkladder-" + new Date().toISOString().slice(0,10) + ".json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1500);
  }
  function renderDrafts() {
    overview.replaceChildren();
    var records = getDrafts();
    var heading = document.createElement("h3");
    heading.textContent = "📋 Gemte kuponkladder (" + records.length + ")";
    overview.appendChild(heading);
    var hint = document.createElement("p");
    hint.className = "foot";
    hint.textContent = "Kun gemt på denne enhed. Ikke synkroniseret med bettingjournalen. Eksportér en sikkerhedskopi, hvis du vil bevare dem.";
    overview.appendChild(hint);
    if (!records.length) return;
    var exportAll = document.createElement("button");
    exportAll.type = "button";
    exportAll.className = "home-secondary";
    exportAll.textContent = "⬇️ Eksportér alle kladder";
    exportAll.addEventListener("click", function () { downloadDrafts(getDrafts()); });
    overview.appendChild(exportAll);
    records.slice().reverse().forEach(function (record) {
      var item = document.createElement("details");
      item.style.cssText = "padding:10px 0;border-bottom:1px solid #ddd";
      var summary = document.createElement("summary");
      summary.textContent = (record.bookmaker || "Ukendt bookmaker") + " · " + (record.selection || "Ukendt kamp").slice(0,55) + " · " + (record.stake_dkk || "?") + " kr";
      item.appendChild(summary);
      var info = document.createElement("p");
      info.style.cssText = "white-space:pre-wrap;overflow-wrap:anywhere";
      info.textContent = "Dato: " + (record.created_at || "ukendt") + "\nSpiltype: " + (record.bet_type || "ukendt") + "\nOdds: " + (record.decimal_odds || "?") + "\nIndsats: " + (record.stake_dkk || "?") + " kr\nUdbetaling: " + (record.payout_dkk == null ? "ukendt" : record.payout_dkk + " kr");
      item.appendChild(info);
      var exportOne = document.createElement("button");
      exportOne.type = "button";
      exportOne.className = "home-secondary";
      exportOne.textContent = "Eksportér denne kladde";
      exportOne.addEventListener("click", function () { downloadDrafts([record]); });
      item.appendChild(exportOne);
      var remove = document.createElement("button");
      remove.type = "button";
      remove.className = "home-secondary";
      remove.textContent = "Slet kladde";
      remove.addEventListener("click", function () {
        if (!window.confirm("Slet denne lokale kuponkladde? Det kan ikke fortrydes.")) return;
        try {
          localStorage.setItem(draftKey, JSON.stringify(getDrafts().filter(function (r) { return r.id !== record.id; })));
          renderDrafts();
        } catch (_) { window.alert("Kunne ikke slette kladden."); }
      });
      item.appendChild(remove);
      overview.appendChild(item);
    });
  }
  renderDrafts();

  input.addEventListener("change", function () {
    if (objectUrl) { URL.revokeObjectURL(objectUrl); objectUrl = null; }
    preview.replaceChildren();
    var file = input.files && input.files[0];
    if (!file) return;
    if (!/^image\/(jpeg|png|webp|heic|heif)$/i.test(file.type) && !/\.(jpe?g|png|webp|heic|heif)$/i.test(file.name)) {
      preview.textContent = "Vælg venligst et billede (JPG, PNG, WEBP eller HEIC).";
      input.value = "";
      return;
    }
    if (file.size > 15 * 1024 * 1024) {
      preview.textContent = "Billedet er for stort. Maksimum er 15 MB.";
      input.value = "";
      return;
    }
    var name = document.createElement("p");
    name.textContent = "Valgt billede: " + file.name;
    preview.appendChild(name);
    objectUrl = URL.createObjectURL(file);
    var img = document.createElement("img");
    img.src = objectUrl;
    img.alt = "Forhåndsvisning af valgt bettingkupon";
    img.style.cssText = "max-width:100%;max-height:420px;object-fit:contain;border-radius:10px";
    preview.appendChild(img);
    var help = document.createElement("p");
    help.className = "foot";
    help.textContent = "Billedet bliver på din enhed. Automatisk tekstaflæsning starter på din enhed, så snart billedet er valgt.";
    preview.appendChild(help);
    var form = document.createElement("form");
    form.style.cssText = "display:grid;gap:9px;margin:12px 0";
    var fields = [
      ["bookmaker", "Bookmaker", "text", ""],
      ["event", "Kamp(e) / spil", "text", ""],
      ["type", "Spiltype (single, double, triple osv.)", "text", ""],
      ["odds", "Samlede odds", "number", "0.01"],
      ["stake", "Indsats i kr.", "number", "0.01"],
      ["payout", "Udbetaling i kr. (valgfri)", "number", "0.01"]
    ];
    fields.forEach(function (spec) {
      var label = document.createElement("label");
      label.textContent = spec[1];
      label.style.cssText = "display:grid;gap:4px;font-size:14px";
      var control = document.createElement("input");
      control.name = spec[0];
      control.type = spec[2];
      if (spec[3]) { control.step = spec[3]; control.min = "0"; }
      control.style.cssText = "box-sizing:border-box;width:100%;padding:10px;border-radius:8px;border:1px solid #aaa;font-size:16px";
      label.appendChild(control);
      form.appendChild(label);
    });
    var note = document.createElement("p");
    note.className = "foot";
    note.textContent = "Billedet aflæses automatisk. Åbn kun felterne, hvis du vil kontrollere eller rette resultatet. Intet overføres til klubbens regnskab.";
    form.appendChild(note);
    var save = document.createElement("button");
    save.type = "submit";
    save.className = "home-secondary";
    save.textContent = "⬇️ Eksportér kupondata til JSON";
    form.appendChild(save);
    var status = document.createElement("p");
    status.setAttribute("role", "status");
    form.appendChild(status);
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var data = Object.fromEntries(new FormData(form).entries());
      if (!data.event.trim() || !(Number(data.odds) > 1) || !(Number(data.stake) > 0)) {
        status.textContent = "Udfyld kamp/spil, odds over 1 og en positiv indsats.";
        return;
      }
      var bet = {
        source: "oddsklubben-manual-image-review",
        created_at: new Date().toISOString(),
        bookmaker: data.bookmaker.trim(),
        selection: data.event.trim(),
        bet_type: data.type.trim(),
        decimal_odds: Number(data.odds),
        stake_dkk: Number(data.stake),
        payout_dkk: data.payout === "" ? null : Number(data.payout)
      };
      // Local duplicate check; this is not a central betting-journal lookup.
      var key = "oddsklubben-exported-coupons-v1";
      var signature = [bet.bookmaker.toLowerCase(), bet.selection.toLowerCase().replace(/\\s+/g, " ").trim(), bet.decimal_odds.toFixed(2), bet.stake_dkk.toFixed(2)].join("|");
      var history = [];
      try { history = JSON.parse(localStorage.getItem(key) || "[]"); if (!Array.isArray(history)) history = []; } catch (_) { history = []; }
      if (history.includes(signature) && !window.confirm("En kupon med samme bookmaker, kampe, odds og indsats er allerede eksporteret på denne enhed. Eksportér alligevel?")) {
        status.textContent = "Eksport annulleret: mulig dublet.";
        return;
      }
      var blob = new Blob([JSON.stringify(bet, null, 2)], {type:"application/json"});
      var url = URL.createObjectURL(blob);
      var link = document.createElement("a");
      link.href = url;
      link.download = "oddsklubben-kupon-" + Date.now() + ".json";
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
      try { localStorage.setItem(key, JSON.stringify([signature].concat(history.filter(function (s) { return s !== signature; })).slice(0, 200))); } catch (_) { /* Private mode or storage disabled. */ }
      status.textContent = "Kupondata eksporteret. Mulige dubletter kontrolleres kun på denne enhed; intet er gemt i klubbens regnskab.";
    });
    var draftButton = document.createElement("button");
    draftButton.type = "button";
    draftButton.className = "home-secondary";
    draftButton.textContent = "✓ Godkend som kladde på denne enhed";
    draftButton.disabled = true;
    form.appendChild(draftButton);
    var draftStatus = document.createElement("p");
    draftStatus.setAttribute("role", "status");
    form.appendChild(draftStatus);
    draftButton.addEventListener("click", function () {
      var data = Object.fromEntries(new FormData(form).entries());
      if (!data.event.trim() || !(Number(data.odds) > 1) || !(Number(data.stake) > 0)) {
        draftStatus.textContent = "Kontrollér kamp, odds og indsats først.";
        return;
      }
      var record = {
        id: "coupon-" + Date.now(),
        created_at: new Date().toISOString(),
        source: "local-ocr-confirmed",
        status: "draft",
        bookmaker: data.bookmaker.trim(),
        selection: data.event.trim(),
        bet_type: data.type.trim(),
        decimal_odds: Number(data.odds),
        stake_dkk: Number(data.stake),
        payout_dkk: data.payout === "" ? null : Number(data.payout)
      };
      var key = "oddsklubben-local-coupon-drafts-v1";
      try {
        var records = JSON.parse(localStorage.getItem(key) || "[]");
        if (!Array.isArray(records)) records = [];
        var signature = [record.bookmaker.toLowerCase(), record.selection.toLowerCase(), record.decimal_odds, record.stake_dkk].join("|");
        var duplicate = records.some(function (item) {
          return [item.bookmaker.toLowerCase(), item.selection.toLowerCase(), item.decimal_odds, item.stake_dkk].join("|") === signature;
        });
        if (duplicate && !window.confirm("Denne kupon ligner en eksisterende kladde. Gem en ny alligevel?")) return;
        records.push(record);
        localStorage.setItem(key, JSON.stringify(records.slice(-200)));
        draftStatus.textContent = "Kladde gemt lokalt på denne enhed. Ikke sendt til bettingjournalen.";
        renderDrafts();
      } catch (error) {
        draftStatus.textContent = "Kunne ikke gemme kladden på denne enhed. Prøv JSON-eksport i stedet.";
      }
    });
    var review = document.createElement("details");
    var reviewTitle = document.createElement("summary");
    reviewTitle.textContent = "Kontrollér eller ret kuponoplysninger";
    review.appendChild(reviewTitle);
    review.appendChild(form);
    preview.appendChild(review);
    // AI endpoint is intentionally opt-in; never place API secrets in this app.
    var aiEndpoint = window.ODDSKLUBBEN_COUPON_AI_ENDPOINT || "";
    if (aiEndpoint) {
      var aiButton = document.createElement("button");
      aiButton.type = "button";
      aiButton.className = "home-secondary";
      aiButton.textContent = "✨ Analysér kupon med AI";
      var aiStatus = document.createElement("p");
      aiStatus.setAttribute("role", "status");
      preview.insertBefore(aiButton, review);
      preview.insertBefore(aiStatus, review);
      aiButton.addEventListener("click", async function () {
        if (!window.confirm("Send dette kuponbillede til den tilknyttede AI-tjeneste til analyse?")) return;
        aiButton.disabled = true;
        aiStatus.textContent = "AI analyserer kuponen …";
        try {
          var payload = new FormData();
          payload.append("image", file, file.name);
          var response = await fetch(aiEndpoint, {method:"POST", body:payload, credentials:"omit"});
          if (!response.ok) throw new Error("AI-tjenesten svarede med fejl " + response.status);
          var parsed = await response.json();
          if (!parsed || !parsed.coupon) throw new Error("Ugyldigt svar fra AI-tjenesten");
          var coupon = parsed.coupon;
          var map = {bookmaker:"bookmaker", selection:"event", bet_type:"type", decimal_odds:"odds", stake_dkk:"stake", payout_dkk:"payout"};
          Object.keys(map).forEach(function (key) {
            if (coupon[key] !== null && coupon[key] !== undefined && coupon[key] !== "") {
              form.elements.namedItem(map[key]).value = coupon[key];
            }
          });
          review.open = true;
          draftButton.disabled = false;
          aiStatus.textContent = "AI-analyse klar. Kontrollér oplysningerne før godkendelse." + (parsed.warnings && parsed.warnings.length ? " Usikkert: " + parsed.warnings.join("; ") : "");
        } catch (error) {
          aiStatus.textContent = "AI-analyse mislykkedes: " + error.message;
        } finally { aiButton.disabled = false; }
      });
    }
    var scan = document.createElement("button");
    scan.type = "button";
    scan.className = "home-secondary";
    scan.textContent = "🔄 Prøv aflæsning igen";
    preview.insertBefore(scan, review);
    var scanStatus = document.createElement("p");
    scanStatus.setAttribute("role", "status");
    preview.insertBefore(scanStatus, review);
    scan.addEventListener("click", async function () {
      scan.disabled = true;
      scanStatus.textContent = "Indlæser billedaflæser og analyserer kuponen …";
      try {
        if (!window.Tesseract) {
          await new Promise(function (resolve, reject) {
            var script = document.createElement("script");
            script.src = "https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/dist/tesseract.min.js";
            script.onload = resolve;
            script.onerror = function () { reject(new Error("Kunne ikke indlæse billedaflæseren. Kontrollér internetforbindelsen.")); };
            document.head.appendChild(script);
          });
        }
        var result = await window.Tesseract.recognize(file, "dan+eng");
        var raw = result.data.text || "";
        if (!raw.trim()) throw new Error("Kunne ikke læse tekst på billedet.");
        var lines = raw.split(/\r?\n/).map(function (x) { return x.trim(); }).filter(Boolean);
        function matchNumber(pattern) {
          var found = raw.match(pattern);
          return found ? found[1].replace(/\s/g, "").replace(",", ".") : "";
        }
        function setField(key, value) {
          if (value) form.elements.namedItem(key).value = value;
        }
        var odds = matchNumber(/(?:samlet\s+odds|total\s+odds|odds\s+i\s+alt|total\s+price|odds)\s*[:=]?\s*(\d{1,4}[,.]\d{1,3})/i);
        var stake = matchNumber(/(?:indsats|stake|beløb|bet\s+amount)\s*[:=]?\s*(\d+[,.]?\d{0,2})/i);
        var payout = matchNumber(/(?:udbetaling|gevinst|return|payout|returns|potential\s+winnings)\s*[:=]?\s*(\d+[,.]?\d{0,2})/i);
        var inferredOdds = false;
        if (!odds && Number(stake) > 0 && Number(payout) > Number(stake)) {
          odds = (Number(payout) / Number(stake)).toFixed(2);
          inferredOdds = true;
        }
        setField("odds", odds);
        setField("stake", stake);
        setField("payout", payout);
        var expected = Number(odds) * Number(stake);
        var amountWarning = Boolean(expected > 0 && Number(payout) > 0 && Math.abs(expected - Number(payout)) > Math.max(2, expected * 0.08));
        var type = raw.match(/\b(single|singler|double|doubler|triple|tripler|akkumulator|kombination|bet\s*builder)\b/i);
        setField("type", type && type[1]);
        var bookmaker = raw.match(/\b(bet365|danske\s+spil|unibet|betfair|betsson|nordicbet|betway|expekt)\b/i);
        setField("bookmaker", bookmaker && bookmaker[1]);
        var events = lines.filter(function (line) {
          if (/fuldtid\s*[-–—]\s*resultat|halvleg\s*[-–—]\s*resultat|full\s*time\s*[-–—]\s*result|kampresultat|double chance|begge hold scorer/i.test(line)) return false;
          if (/odds|indsats|gevinst|udbetaling|samlet|cash\s*out/i.test(line)) return false;
          return /\s(?:-|–|—|vs\.?|v\.)\s/i.test(line) && /[a-zæøå]{2,}/i.test(line);
        }).slice(0, 8);
        setField("event", events.join("; "));
        var details = document.createElement("details");
        var summary = document.createElement("summary");
        summary.textContent = "Se aflæst råtekst";
        var pre = document.createElement("pre");
        pre.textContent = raw;
        pre.style.cssText = "white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px";
        details.setAttribute("data-ocr-raw", "true");
        details.appendChild(summary);
        details.appendChild(pre);
        var prior = preview.querySelector("details[data-ocr-raw]");
        if (prior) prior.remove();
        preview.insertBefore(details, review);
        var missing = ["event", "odds", "stake"].filter(function (key) { return !form.elements.namedItem(key).value; });
        review.open = missing.length > 0 || amountWarning || inferredOdds;
        draftButton.disabled = false;
        scanStatus.textContent = inferredOdds ? "⚠️ Odds er beregnet ud fra indsats og mulig gevinst, ikke aflæst direkte. Kontrollér odds før godkendelse." : amountWarning ? "⚠️ De aflæste beløb stemmer ikke umiddelbart overens. Kontrollér odds, indsats og udbetaling." : missing.length ? "Aflæsningen mangler " + missing.join(", ") + ". Åbn felterne og ret det nødvendige." : "Kuponen er aflæst. Du kan åbne oplysningerne for at kontrollere dem og eksportere, hvis du ønsker det.";
      } catch (error) {
        review.open = true;
        draftButton.disabled = false;
        scanStatus.textContent = "Aflæsning mislykkedes: " + error.message + " Du kan prøve igen eller vælge et tydeligere billede.";
      } finally {
        scan.disabled = false;
      }
    });

    var clear = document.createElement("button");
    clear.type = "button";
    clear.className = "home-secondary";
    clear.textContent = "Fjern billede";
    clear.addEventListener("click", function () {
      input.value = "";
      if (objectUrl) URL.revokeObjectURL(objectUrl);
      objectUrl = null;
      preview.replaceChildren();
    });
    preview.appendChild(clear);
    // Start OCR automatically after image selection; no extra tap required.
    scan.click();
  });
  window.addEventListener("pagehide", function () {
    if (objectUrl) URL.revokeObjectURL(objectUrl);
  });
}());
