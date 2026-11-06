"""下载 tools/works-sources.json 里选中的图，做成缩略图放进 img/works/，并生成 works.js。

用法（在项目根目录，先编译 tools/crop.swift 成 tools/crop）:
  python3 tools/fetch_works.py [不要的id...]
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

UA = {"User-Agent": "minghua-map/0.1 (open-source art map)"}
TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
CROP = os.path.join(TOOLS, "crop")


def download(url, path):
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r, open(path, "wb") as f:
                f.write(r.read())
            return
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(int(e.headers.get("Retry-After") or 0) or 5 * (attempt + 1))
        except (urllib.error.URLError, OSError):
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("多次重试仍然失败")


def image_size(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path], capture_output=True, text=True).stdout
    nums = [int(line.split()[-1]) for line in out.splitlines() if "pixel" in line]
    return nums[0], nums[1]


def make_thumb(pick, dest):
    tmp = dest + ".download"
    ratio = (pick.get("width") or 1) / (pick.get("height") or 1)
    if ratio > 3.2:
        # 长卷缩到 960 宽只剩一条细线：取更宽的缩略图，再裁出中间一段。
        # 两端常是引首和题跋，中间才是画心。维基对非标准宽度有时会拒绝，所以依次试几个宽度。
        widths = [min(pick["width"], round(480 * ratio), 8000), 3840, 2560, 1920]
        for wide in widths:
            try:
                download(pick["thumb"].replace("/960px-", f"/{wide}px-"), tmp)
                break
            except urllib.error.HTTPError:
                continue
        else:
            download(pick["thumb"], tmp)
        w, h = image_size(tmp)
        part = min(w, round(h * 2.2))
        subprocess.run([CROP, tmp, dest, str((w - part) // 2), "0", str(part), str(h), "720", "0.8"],
                       check=True, capture_output=True)
    else:
        download(pick["thumb"], tmp)
        # 统一转成 JPEG，最长边 720 像素
        subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "78", "-Z", "720", tmp, "--out", dest],
                       check=True, capture_output=True)
    os.remove(tmp)


def main():
    skip = set(sys.argv[1:])
    with open(os.path.join(TOOLS, "works-sources.json"), encoding="utf-8") as fh:
        found = json.load(fh)
    out_dir = os.path.join(ROOT, "img", "works")
    os.makedirs(out_dir, exist_ok=True)
    meta = {}
    for pid, pick in found.items():
        if not pick or pid in skip:
            continue
        dest = os.path.join(out_dir, f"{pid}.jpg")
        if not os.path.exists(dest):
            make_thumb(pick, dest)
            time.sleep(1)
        meta[pid] = {"src": f"img/works/{pid}.jpg", "title": pick["title"].replace("File:", ""),
                     "page": pick["page"], "license": pick["license"]}
        print(pid, "ok", flush=True)
    with open(os.path.join(ROOT, "works.js"), "w", encoding="utf-8") as fh:
        fh.write("// 每幅画的图像出处，由 tools/fetch_works.py 生成：图都来自维基共享资源，授权见 license\n")
        fh.write("window.WORK_IMAGES = " + json.dumps(meta, ensure_ascii=False, indent=1) + ";\n")


if __name__ == "__main__":
    main()
