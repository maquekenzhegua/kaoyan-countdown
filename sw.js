/* 考研上岸挂历 - Service Worker:缓存优先,后台静默更新 */
var CACHE = "ky28-v2";
var ASSETS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./sw.js",
  "./solarlunar.min.js",
  "./icon-192.png",
  "./icon-512.png",
  "./apple-touch-icon.png",
  "./img/thu.jpg",
  "./img/pku.jpg",
  "./img/fudan.jpg",
  "./img/sjtu.jpg",
  "./img/zju.jpg",
  "./img/nju.jpg",
  "./img/ustc.jpg",
  "./img/hit.jpg",
  "./img/xjtu.jpg"
];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(CACHE).then(function (c) { return c.addAll(ASSETS); }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys()
      .then(function (keys) { return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); })); })
      .then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") return;
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then(function (hit) {
      var fetching = fetch(e.request).then(function (res) {
        if (res && res.ok) {
          try {
            if (new URL(e.request.url).origin === self.location.origin) {
              var copy = res.clone();
              caches.open(CACHE).then(function (c) { c.put(e.request, copy); });
            }
          } catch (err) {}
        }
        return res;
      }).catch(function () { return hit; });
      return hit || fetching;
    })
  );
});
