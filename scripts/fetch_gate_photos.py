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
    # (id, 查询词, 排除的文件名关键词, 标题必须包含的关键词)
    ("thu", ["清华大学主楼", "清华学堂", "清华大学西门", "Tsinghua University main building"], ["二校門", "二校门", "bus", "Bus"], ["清华", "Tsinghua"]),
    ("pku", ["北京大学西门", "北京大学图书馆", "北京大学百周年纪念讲堂", "Peking University library"], ["Boya", "Weiming", "bus", "Bus"], ["北京大", "Peking"]),
    ("fudan", ["复旦大学校门", "复旦大学正门", "Fudan University gate", "Fudan University campus", "Fudan University"], ["Guanghua", "bus"], ["复旦", "Fudan"]),
    ("sjtu", [], [], []),  # 已有图书馆照片,跳过
    ("zju", ["浙江大学校门", "浙江大学求是大讲堂", "Zhejiang University gate", "Zhejiang University Yuquan"], ["Third Teaching", "20231123", "bus"], ["浙江大", "Zhejiang"]),
    ("nju", ["南京大学校门", "南京大学鼓楼校区", "Nanjing University campus", "Nanjing University gate", "Nanjing University"], ["Nanjing University 3", "北大楼", "Yingtian", "bus"], ["南京大", "Nanjing"]),
    ("ustc", ["中国科学技术大学校门", "中国科学技术大学东门", "University of Science and Technology of China gate", "USTC"], ["H2O", "水上报告厅", "canteen", "eating", "Students eating"], ["科学技术大", "USTC", "University of Science and Technology of China"]),
    ("hit", ["哈尔滨工业大学主楼", "哈尔滨工业大学校门", "Harbin Institute of Technology", "HIT main building"], ["201907 Harbin", "bus"], ["哈尔滨工业", "Harbin"]),
    ("xjtu", ["西安交通大学校门", "西安交通大学主楼", "Xi'an Jiaotong University gate", "Xi'an Jiaotong University", "Xian Jiaotong University campus"], ["PengKang", "Xi'an Jiaotong University 4", "bus"], ["西安交通", "Xi'an Jiaotong", "Xian Jiaotong"]),
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


def pick(pages, exclude, must):
    cands = []
    for p in (pages or {}).values():
        title = p.get("title", "")
        if any(x in title for x in exclude):
            continue
        if must and not any(m in title for m in must):
            continue
        infos = p.get("imageinfo") or []
        if not infos:
            continue
        ii = infos[0]
        if ii.get("mime") != "image/jpeg":
            continue
        w, h = ii.get("width", 0), ii.get("height", 0)
        if w < 800 or h < 520:
            continue
        ratio = w / h
        if ratio < 0.9 or ratio > 3.0:
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
    for sid, queries, exclude, must in PLAN:
        dest = os.path.join(OUT_DIR, f"{sid}-2.jpg")
        if os.path.exists(dest):
            print(f"skip {sid} (exists)")
            continue
        if not queries:
            continue
        got = None
        for q in queries:
            try:
                data = api_search(q)
                c = pick(data.get("query", {}).get("pages"), exclude, must)
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
