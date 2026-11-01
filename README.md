# 名画里的中国

**把历代名画放回它画的地方。**

*An interactive map of China that puts famous paintings back where they were painted — from the Kizil caves in Xinjiang to the murals of Tibet and the tombs of the Northeast. Two masterpieces open as fully zoomable, annotated handscrolls.*

## 能做什么

- **一张地图看两千年**：57 幅名画按描绘的地点落在地图上，从东晋《洛神赋图》到 1960 年代的《万山红遍》，新疆、西藏、东北、云南、台湾都有。
- **按朝代筛选**：魏晋南北朝、隋唐、五代宋辽金、元、明、清、近现代，看每个时代的画家都在画哪里。
- **展开画卷**：
  - 《清明上河图》：38414 像素全卷可无限放大，26 处标注，从卷首的驴队一路看到城门下的骆驼商队。
  - 《富春山居图》：把火烧后分藏两岸的《剩山图》和《无用师卷》按原顺序拼回一卷，14 处标注，包括乾隆认错真假的那段题字。
- **搜索和导览**：在画里搜“骆驼”“纤夫”“乾隆”，或者点“开始导览”从右往左一处处看。

## 本地运行

不需要安装任何依赖：

```bash
python3 -m http.server 8000
```

然后打开 http://localhost:8000 。也可以直接部署到 GitHub Pages。

## 目录

```
index.html          整个应用：地图、名画数据、画卷浏览、标注都在这一个文件里
img/                切好的画卷图片（qm-* 清明上河图，fc-* 富春山居图）
tools/crop.swift    裁图工具：从原图裁出画心、切段、做缩略图（macOS 自带 Swift 即可运行）
```

## 加一幅画

在 `index.html` 的 `PAINTINGS` 数组里加一条：

```js
{ id: "xxx", name: "画名", period: "元", era: "元", artist: "作者", kind: "卷轴",
  place: "描绘的地点", lng: 120.1, lat: 30.2, basis: "一说", keep: "收藏机构",
  note: "一两句话介绍" }
```

`basis` 说明地点是怎么来的：不写表示画中所绘的实景；“一说”表示学界说法不一；“画意”“所在地”用于没有具体实景的作品。

要让一幅画能“展开画卷”，再在 `SCROLLS` 里加一项，配上切好的图片和标注。原图的下载和切图方法：

```bash
# 1. 从维基共享资源下载公有领域的原图，放进 source/（不入库）
# 2. 编译裁图工具
swiftc -O tools/crop.swift -o crop
# 3. 用法：源图 输出 x y 宽 高 [输出宽度] [质量]
./crop source/qingming-full.jpg img/qm-1.jpg 0 0 6400 1800 6400 0.62
```

## 数据来源和授权

| 内容 | 来源 | 授权 |
|---|---|---|
| 《清明上河图》图像 | [维基共享资源](https://commons.wikimedia.org/wiki/File:Alongtheriver_QingMing.jpg)，原作藏北京故宫博物院 | 公有领域 |
| 《富春山居图》图像 | 维基共享资源《[剩山图](https://commons.wikimedia.org/wiki/File:富春山居圖(剩山圖).jpg)》《[无用师卷](https://commons.wikimedia.org/wiki/File:富春山居圖(無用師卷).jpg)》，原作分藏浙江省博物馆、台北故宫博物院 | 公有领域 |
| 中国地图 | [ECharts 4.9.0](https://github.com/apache/echarts) 自带的 china.js | Apache-2.0 |
| 名画介绍、画中标注 | 本项目整理 | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| 代码 | 本项目 | [MIT](LICENSE) |

近现代作品仍在版权保护期内，本项目只收录文字介绍，不收录图像。

## 欢迎纠错

画中标注由 AI 辅助初标、人工核对，名画的地点和收藏信息也可能有疏漏。发现错误，欢迎提 Issue 或 PR，附上出处最好。

## 接下来

- [ ] 更多画卷可以展开：《韩熙载夜宴图》《千里江山图》《姑苏繁华图》
- [ ] 地图上同一地点的不同时代对比，比如长安的《步辇图》和拉萨的布达拉宫壁画讲的是同一段故事
- [ ] 英文版
