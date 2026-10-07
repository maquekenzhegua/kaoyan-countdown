/* 考研上岸挂历 - Service Worker:缓存优先,后台静默更新 */
var CACHE = "ky28-v6";
var ASSETS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./sw.js",
  "./solarlunar.min.js",
  "./icon-192.png",
  "./icon-512.png",
  "./apple-touch-icon.png",
  "./img/thu-1.jpg",
  "./img/pku-1.jpg",
  "./img/fudan-1.jpg",
  "./img/sjtu-1.jpg",
  "./img/zju-1.jpg",
  "./img/nju-1.jpg",
  "./img/ustc-1.jpg",
  "./img/hit-1.jpg",
  "./img/xjtu-1.jpg"
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
