#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CI 图片下载:从 Wikimedia Commons 抓取各高校第二张照片(优先校门),存为 img/{id}-2.jpg。
只下载缺失的文件;输出 img/credits-gates.json 供署名更新。"""
import json
import os
import sys
import urllib.parse
import urllib.request

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "img")
UA = {"User-Agent": "KaoyanShanganApp/1.0 (personal countdown app; contact via github)"}

PLAN = [
    ("thu", ["Tsinghua University west gate", "Tsinghua University gate", "Tsinghua University main building"], ["二校門", "2019年二校门"]),
    ("pku", ["Peking University west gate", "Peking University gate", "Peking University library"], ["Boya Pagoda", "Weiming Lake"]),
    ("fudan", ["Fudan University gate", "Fudan University school gate", "Fudan University Handan"], ["GuanghuaTower"]),
    ("sjtu", ["Shanghai Jiao Tong University library", "Shanghai Jiao Tong University Xuhui gate", "Shanghai Jiao Tong University historical"], ["Sjtu east gate"]),
    ("zju", ["Zhejiang University gate", "Zhejiang University Qiushi", "Zhejiang University campu gate"], ["Third Teaching Building"]),
    ("nju", ["Nanjing University gate", "Nanjing University Gulou campus", "Nanjing Universitybuilding"], ["Nanjing University 3"]),
    ("ustc", ["Gate of University of Science and Technology of China", "USTC gate Hefei", "University of Science and Technology of China campus Hefei"], ["H2O", "水上报告厅"]),
    ("hit", ["Harbin Institute of Technology main building", "Harbin Institute of Technology gate", "Harbin Institute of Technology museum"], ["201907 Harbin"]),
    ("xjtu", ["Xi'an Jiaotong University gate", "Xi'an Jiaotong University north gate", "Xi'an Jiaotong University buildings"], ["PengKang", "Xi'an Jiaotong University 4"]),
]


def api_search(query):
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": query + " filetype:bitmap", "gsrnamespace": "6", "gsrlimit": "20",
        "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": "1280",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def pick(pages, exclude):
    cands = []
    for p in (pages or {}).values():
        title = p.get("title", "")
        if any(x in title for x in exclude):
            continue
        infos = p.get("imageinfo") or []
        if not infos:
            continue
        ii = infos[0]
        if ii.get("mime") != "image/jpeg":
            continue
        w, h = ii.get("width", 0), ii.get("height", 0)
        if w < 900 or h < 560:
            continue
        ratio = w / h
        if ratio < 0.95 or ratio > 2.7:
            continue
        meta = ii.get("extmetadata") or {}
        artist = meta.get("Artist", {}).get("value", "")
        artist = artist.replace("<", " ").replace(">", " ").strip()
        cands.append({
            "title": title,
            "url": ii.get("thumburl", "").replace("thumb.wikimedia.org", "upload.wikimedia.org").split("?")[0],
            "ratio": ratio,
            "artist": artist[:80],
            "license": meta.get("LicenseShortName", {}).get("value", ""),
        })
    cands.sort(key=lambda c: abs(c["ratio"] - 1.5))
    return cands[0] if cands else None


def download(url, dest):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        f.write(r.read())


def compress(path):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    if im.width > 1280:
        im = im.resize((1280, int(im.height * 1280 / im.width)), Image.LANCZOS)
    im.save(path, quality=72, optimize=True, progressive=True)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    credits = {}
    failed = []
    for sid, queries, exclude in PLAN:
        dest = os.path.join(OUT_DIR, f"{sid}-2.jpg")
        if os.path.exists(dest):
            print(f"skip {sid} (exists)")
            continue
        got = None
        for q in queries:
            try:
                data = api_search(q)
                c = pick(data.get("query", {}).get("pages"), exclude)
                if not c:
                    continue
                download(c["url"], dest)
                compress(dest)
                got = c
                break
            except Exception as e:
                print(f"{sid} query '{q}' failed: {e}", file=sys.stderr)
        if got:
            credits[sid] = {"title": got["title"], "artist": got["artist"], "license": got["license"]}
            print(f"OK {sid}: {got['title']} ({got['license']})")
        else:
            failed.append(sid)
            if os.path.exists(dest):
                os.remove(dest)
            print(f"FAILED {sid}")
    with open(os.path.join(OUT_DIR, "credits-gates.json"), "w", encoding="utf-8") as f:
        json.dump(credits, f, ensure_ascii=False, indent=2)
    print(f"done. downloaded={len(credits)} failed={failed}")
    # 有失败时以非零退出,便于日志观察,但不阻塞提交(提交步骤单独判断文件是否存在)


if __name__ == "__main__":
    main()
