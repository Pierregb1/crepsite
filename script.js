function buildURL(model) {
  const backend = "https://crepsite.onrender.com/run";
  const lat = document.getElementById("lat")?.value;
  const lon = document.getElementById("lon")?.value;
  let url = backend + "?model=" + model;
  if (lat !== undefined) url += "&lat=" + lat;
  if (lon !== undefined) url += "&lon=" + lon;
  if (model === 5) {
    const year = document.getElementById("year").value;
    url += "&year=" + year;
  }
  return url;
}

function fetchGraph(model) {
  const img = document.getElementById("plot");
  img.src = buildURL(model) + "&t=" + Date.now(); // cache-bust
  return false; // prevent form navigation
}