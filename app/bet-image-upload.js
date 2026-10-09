(function () {
  "use strict";
  var input = document.getElementById("betImageInput");
  var preview = document.getElementById("betImagePreview");
  if (!input || !preview) return;
  var objectUrl = null;
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
    help.textContent = "Billedet bliver på din enhed. Automatisk tekstaflæsning sker lokalt i browseren, når du trykker Aflæs.";
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
    note.textContent = "Tryk på Aflæs billedet automatisk. Kontrollér de aflæste oplysninger før eksport. Intet overføres til klubbens regnskab.";
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
      var blob = new Blob([JSON.stringify(bet, null, 2)], {type:"application/json"});
      var url = URL.createObjectURL(blob);
      var link = document.createElement("a");
      link.href = url;
      link.download = "oddsklubben-kupon-" + Date.now() + ".json";
      document.body.appendChild(link);
      link.click();
      link.remove();
      setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
      status.textContent = "Kupondata eksporteret. Intet er gemt i klubbens regnskab.";
    });
    preview.appendChild(form);
    var scan = document.createElement("button");
    scan.type = "button";
    scan.className = "home-secondary";
    scan.textContent = "✨ Aflæs billedet automatisk";
    preview.insertBefore(scan, form);
    var scanStatus = document.createElement("p");
    scanStatus.setAttribute("role", "status");
    preview.insertBefore(scanStatus, form);
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
        setField("odds", odds);
        setField("stake", stake);
        setField("payout", payout);
        var type = raw.match(/\b(single|singler|double|doubler|triple|tripler|akkumulator|kombination|bet\s*builder)\b/i);
        setField("type", type && type[1]);
        var bookmaker = raw.match(/\b(bet365|danske\s+spil|unibet|betfair|betsson|nordicbet|betway|expekt)\b/i);
        setField("bookmaker", bookmaker && bookmaker[1]);
        var events = lines.filter(function (line) {
          return /\s(?:-|–|—|vs\.?|v\.)\s/i.test(line) && !/odds|indsats|gevinst|udbetaling/i.test(line);
        }).slice(0, 8);
        setField("event", events.join("; "));
        var details = document.createElement("details");
        var summary = document.createElement("summary");
        summary.textContent = "Se aflæst råtekst";
        var pre = document.createElement("pre");
        pre.textContent = raw;
        pre.style.cssText = "white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px";
        details.appendChild(summary);
        details.appendChild(pre);
        var prior = preview.querySelector("details");
        if (prior) prior.remove();
        preview.insertBefore(details, form);
        scanStatus.textContent = "Aflæsning færdig. Kontrollér felterne før eksport – utydelige eller ukendte værdier efterlades tomme.";
      } catch (error) {
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
  });
  window.addEventListener("pagehide", function () {
    if (objectUrl) URL.revokeObjectURL(objectUrl);
  });
}());
