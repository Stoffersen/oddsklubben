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
