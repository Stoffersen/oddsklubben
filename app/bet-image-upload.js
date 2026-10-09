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
    help.textContent = "Billedet er ikke sendt til serveren. Automatisk aflæsning og godkendt gemning kræver en sikker backend.";
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
    note.textContent = "Foreløbig manuel registrering: Kontrollér kuponen og udfyld felterne. Ingen automatisk billedaflæsning eller overførsel til klubbens regnskab endnu.";
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
