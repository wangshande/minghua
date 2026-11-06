"""给每幅画在维基共享资源上找一张授权可用的图，结果写进 tools/works-sources.json。

用法（在项目根目录）:
  python3 tools/find_works.py            # 查所有还没查过的
  python3 tools/find_works.py id1 id2    # 重查指定的几幅

找到的只是候选，下载后要人工逐张核对是不是对应的画。
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = {"User-Agent": "minghua-map/0.1 (open-source art map)"}
OK_LICENSE = re.compile(r"public domain|^pd|cc0|cc by(-sa)? ?\d", re.I)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "works-sources.json")

# 查询词按顺序试，以 File: 开头的表示直接指定文件
QUERIES = {
    "luoshen": ["Nymph of the Luo River Gu Kaizhi", "洛神賦圖"],
    "kizil": ["Kizil Caves painting", "Kizil cave mural"],
    "jian": ["Goguryeo tomb mural Ji'an", "Tomb of the Dancers Goguryeo"],
    "bunian": ["Emperor Taizong Receiving the Tibetan Envoy", "步輦圖"],
    "guoguo": ["Lady Guoguo's Spring Outing", "虢國夫人遊春圖"],
    "xingshu": ["Emperor Minghuang's Journey to Shu", "明皇幸蜀圖"],
    "wangchuan": ["Wangchuan Villa Wang Wei", "輞川圖"],
    "dunhuang": ["Zhang Yichao Mogao Cave 156", "張議潮統軍出行圖"],
    "astana": ["Fuxi Nüwa Astana", "Fuxi and Nüwa painting Turfan"],
    "yeyan": ["Night Revels of Han Xizai", "韓熙載夜宴圖"],
    "xiaoxiang": ["Dong Yuan Xiao and Xiang Rivers", "瀟湘圖 董源"],
    "kuanglu": ["Mount Kuanglu Jing Hao", "匡廬圖"],
    "ruihe": ["Auspicious Cranes Huizong", "瑞鶴圖"],
    "xiyuan": ["Elegant Gathering in the Western Garden", "西園雅集圖"],
    "xishan": ["File:Fan Kuan - Travelers Among Mountains and Streams - Google Art Project.jpg"],
    "qianli": ["A Panorama of Rivers and Mountains Wang Ximeng", "千里江山圖"],
    "xihu": ["Li Song West Lake", "西湖圖 李嵩"],
    "siji": ["Liu Songnian Landscapes of the Four Seasons", "四景山水圖"],
    "bezeklik": ["Bezeklik mural", "Bezeklik Thousand Buddha Caves painting"],
    "fanxiang": ["Zhang Shengwen Buddhist Images", "梵像卷"],
    "wenji": ["Wenji Returns to Han Zhang Yu", "文姬歸漢圖 張瑀"],
    "quehua": ["File:Autumn Colors on the Qiao and Hua Mountains (cropped).jpg"],
    "shuicun": ["Water Village Zhao Mengfu", "水村圖"],
    "qingbian": ["Wang Meng Qingbian", "青卞隱居圖 王蒙"],
    "tengwang": ["Xia Yong Teng", "滕王閣 夏永"],
    "shalu": ["Shalu Monastery mural", "Shalu monastery painting"],
    "lushan": ["Lofty Mount Lu Shen Zhou", "廬山高圖"],
    "huishan": ["Wen Zhengming Tea Gathering Mount Hui", "惠山茶會圖"],
    "zhuozheng": ["File:Garden of the Inept Administrator - leaf a.jpg"],
    "nandu": ["南都繁會圖", "Prosperous Nanjing Ming painting"],
    "qixia": ["Zhang Hong Qixia", "棲霞山圖 張宏"],
    "guge": ["Tsaparang mural", "Guge kingdom mural"],
    "gusu": ["Prosperous Suzhou Xu Yang", "姑蘇繁華圖"],
    "huangshan": ["Shitao Huangshan", "石濤 黃山"],
    "yuanming": ["Forty Scenes of the Yuanming Yuan", "圓明園四十景圖"],
    "wanshuyuan": ["Banquet in the Garden of Ten Thousand Trees", "萬樹園賜宴圖"],
    "pingding": ["Conquests of the Emperor Qianlong engraving", "平定西域戰圖"],
    "fanshe": ["番社采風", "Taiwan aborigines Qing dynasty painting"],
}


def api(params):
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(dict(params, format="json"))
    for attempt in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            # 被限流就按服务器给的时间退避再试
            time.sleep(int(e.headers.get("Retry-After") or 0) or 5 * (attempt + 1))
        except (urllib.error.URLError, OSError):
            # 网络偶尔断开（比如 SSL 握手失败），稍等再试
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("多次重试仍然失败")


def strip_html(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def candidates(query):
    common = {"prop": "imageinfo", "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 960}
    if query.startswith("File:"):
        r = api(dict(common, action="query", titles=query))
    else:
        r = api(dict(common, action="query", generator="search", gsrnamespace=6, gsrlimit=8, gsrsearch=query))
    pages = sorted((r.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata") or {}
        yield {
            "title": p["title"],
            "mime": ii.get("mime"),
            "width": ii.get("width"), "height": ii.get("height"),
            "license": strip_html((em.get("LicenseShortName") or {}).get("value")),
            "artist": strip_html((em.get("Artist") or {}).get("value"))[:80],
            "page": ii.get("descriptionurl"),
            "thumb": ii.get("thumburl"),
        }


def main():
    only = set(sys.argv[1:])
    try:
        with open(OUT, encoding="utf-8") as fh:
            found = json.load(fh)   # 接着上次的结果继续
    except (OSError, ValueError):
        found = {}
    for pid, queries in QUERIES.items():
        if (only and pid not in only) or (not only and pid in found):
            continue
        pick = None
        for q in queries:
            for c in candidates(q):
                if c["mime"] in ("image/jpeg", "image/png", "image/tiff") and OK_LICENSE.search(c["license"] or ""):
                    pick = c
                    break
            if pick:
                break
            time.sleep(1.5)
        found[pid] = pick
        print(f"{pid:11} {(pick or {}).get('license', '—'):16} {(pick or {}).get('title', '没找到')[:90]}", flush=True)
        with open(OUT, "w", encoding="utf-8") as fh:
            json.dump(found, fh, ensure_ascii=False, indent=1)
        time.sleep(1.5)


if __name__ == "__main__":
    main()
