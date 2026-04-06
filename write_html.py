html = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>杜氏家谱</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;
      background:#f5f0e8;color:#333;display:flex;flex-direction:column;height:100vh;overflow:hidden}
header{background:linear-gradient(135deg,#8b4513,#c0722a);color:#fff;
        padding:14px 16px;text-align:center;flex-shrink:0}
header h1{font-size:1.6em;letter-spacing:4px;text-shadow:0 1px 4px rgba(0,0,0,.3)}
header p{font-size:.75em;margin-top:4px;opacity:.85}
.poem{background:#6b2e08;color:#ffd700;text-align:center;padding:7px;
       font-size:.82em;letter-spacing:2px;flex-shrink:0}
#canvas-wrap{flex:1;overflow:hidden;position:relative;cursor:grab;touch-action:none}
#canvas-wrap.dragging{cursor:grabbing}
svg#tree{display:block}
.node{cursor:pointer}
.node rect{transition:filter .15s}
.node:hover rect{filter:brightness(.9)}
.node-name{font-size:15px;font-weight:700;fill:#333;pointer-events:none;
            font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}
.gen-lbl{font-size:13px;fill:#888;font-weight:600;
          font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}
.hint{position:absolute;bottom:12px;right:16px;font-size:.72em;color:#bbb;
       background:rgba(255,255,255,.8);padding:3px 8px;border-radius:6px;pointer-events:none}
.overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);
          z-index:200;align-items:center;justify-content:center}
.overlay.on{display:flex}
.modal{background:#fff;border-radius:18px;padding:24px;width:88%;
        max-width:380px;max-height:82vh;overflow-y:auto;box-shadow:0 8px 32px rgba(0,0,0,.2)}
.modal-title{font-size:1.4em;font-weight:700;color:#8b4513;
              border-bottom:2px solid #f0dcc8;padding-bottom:10px;margin-bottom:14px}
.row{display:flex;margin-bottom:10px;font-size:.88em}
.lbl{color:#aaa;width:72px;flex-shrink:0;padding-top:1px}
.val{color:#333;flex:1;line-height:1.6}
.val a{color:#8b4513;text-decoration:none;font-weight:600}
.btn-close{width:100%;margin-top:18px;padding:11px;background:#8b4513;
            color:#fff;border:none;border-radius:10px;font-size:1em;cursor:pointer}
</style>
</head>
<body>
<header>
  <h1>杜氏家谱</h1>
  <p>明洪武元年（约1370年）奉诏迁居开封府繁塔侧云寄桥 &nbsp;·&nbsp; 共 65 位成员</p>
</header>
<div class="poem">如峰田绪远 · 祥开世泽长 · 继祖承兆庆 · 勤宗永康昌</div>
<div id="canvas-wrap">
  <svg id="tree" width="2960" height="600" xmlns="http://www.w3.org/2000/svg">
    <g id="root-g">
      <g class="edges" stroke="#aaa" stroke-width="1.5" fill="none">
  <!-- 一世→二世 -->
  <line x1="1369" y1="75" x2="1369" y2="105"/>
  <line x1="430" y1="105" x2="2397" y2="105"/>
  <line x1="430" y1="105" x2="430" y2="135"/>
  <line x1="1280" y1="105" x2="1280" y2="135"/>
  <line x1="2397" y1="105" x2="2397" y2="135"/>
  <!-- 二世→三世 -->
  <line x1="430" y1="175" x2="430" y2="235"/>
  <line x1="1280" y1="175" x2="1280" y2="205"/>
  <line x1="1080" y1="205" x2="1480" y2="205"/>
  <line x1="1080" y1="205" x2="1080" y2="235"/>
  <line x1="1480" y1="205" x2="1480" y2="235"/>
  <line x1="2397" y1="175" x2="2397" y2="205"/>
  <line x1="2047" y1="205" x2="2763" y2="205"/>
  <line x1="2047" y1="205" x2="2047" y2="235"/>
  <line x1="2380" y1="205" x2="2380" y2="235"/>
  <line x1="2763" y1="205" x2="2763" y2="235"/>
  <!-- 三世→四世 -->
  <line x1="430" y1="275" x2="430" y2="305"/>
  <line x1="130" y1="305" x2="730" y2="305"/>
  <line x1="130" y1="305" x2="130" y2="335"/>
  <line x1="330" y1="305" x2="330" y2="335"/>
  <line x1="530" y1="305" x2="530" y2="335"/>
  <line x1="730" y1="305" x2="730" y2="335"/>
  <line x1="1080" y1="275" x2="1080" y2="305"/>
  <line x1="980" y1="305" x2="1180" y2="305"/>
  <line x1="980" y1="305" x2="980" y2="335"/>
  <line x1="1080" y1="305" x2="1080" y2="335"/>
  <line x1="1180" y1="305" x2="1180" y2="335"/>
  <line x1="1480" y1="275" x2="1480" y2="335"/>
  <line x1="2047" y1="275" x2="2047" y2="305"/>
  <line x1="1880" y1="305" x2="2180" y2="305"/>
  <line x1="1880" y1="305" x2="1880" y2="335"/>
  <line x1="2080" y1="305" x2="2080" y2="335"/>
  <line x1="2180" y1="305" x2="2180" y2="335"/>
  <line x1="2380" y1="275" x2="2380" y2="335"/>
  <line x1="2763" y1="275" x2="2763" y2="305"/>
  <line x1="2630" y1="305" x2="2880" y2="305"/>
  <line x1="2630" y1="305" x2="2630" y2="335"/>
  <line x1="2780" y1="305" x2="2780" y2="335"/>
  <line x1="2880" y1="305" x2="2880" y2="335"/>
  <!-- 四世→五世 -->
  <line x1="130" y1="375" x2="130" y2="405"/>
  <line x1="80" y1="405" x2="180" y2="405"/>
  <line x1="80" y1="405" x2="80" y2="435"/>
  <line x1="180" y1="405" x2="180" y2="435"/>
  <line x1="330" y1="375" x2="330" y2="405"/>
  <line x1="280" y1="405" x2="380" y2="405"/>
  <line x1="280" y1="405" x2="280" y2="435"/>
  <line x1="380" y1="405" x2="380" y2="435"/>
  <line x1="530" y1="375" x2="530" y2="405"/>
  <line x1="480" y1="405" x2="580" y2="405"/>
  <line x1="480" y1="405" x2="480" y2="435"/>
  <line x1="580" y1="405" x2="580" y2="435"/>
  <line x1="730" y1="375" x2="730" y2="405"/>
  <line x1="680" y1="405" x2="780" y2="405"/>
  <line x1="680" y1="405" x2="680" y2="435"/>
  <line x1="780" y1="405" x2="780" y2="435"/>
  <line x1="980" y1="375" x2="980" y2="435"/>
  <line x1="1080" y1="375" x2="1080" y2="435"/>
  <line x1="1180" y1="375" x2="1180" y2="435"/>
  <line x1="1480" y1="375" x2="1480" y2="405"/>
  <line x1="1380" y1="405" x2="1580" y2="405"/>
  <line x1="1380" y1="405" x2="1380" y2="435"/>
  <line x1="1480" y1="405" x2="1480" y2="435"/>
  <line x1="1580" y1="405" x2="1580" y2="435"/>
  <line x1="1880" y1="375" x2="1880" y2="405"/>
  <line x1="1780" y1="405" x2="1980" y2="405"/>
  <line x1="1780" y1="405" x2="1780" y2="435"/>
  <line x1="1880" y1="405" x2="1880" y2="435"/>
  <line x1="1980" y1="405" x2="1980" y2="435"/>
  <line x1="2080" y1="375" x2="2080" y2="435"/>
  <line x1="2180" y1="375" x2="2180" y2="435"/>
  <line x1="2380" y1="375" x2="2380" y2="435"/>
  <line x1="2630" y1="375" x2="2630" y2="405"/>
  <line x1="2580" y1="405" x2="2680" y2="405"/>
  <line x1="2580" y1="405" x2="2580" y2="435"/>
  <line x1="2680" y1="405" x2="2680" y2="435"/>
  <line x1="2880" y1="375" x2="2880" y2="435"/>
  <!-- 五世→六世 -->
  <line x1="80" y1="475" x2="80" y2="535"/>
  <line x1="180" y1="475" x2="180" y2="535"/>
  <line x1="280" y1="475" x2="280" y2="535"/>
  <line x1="380" y1="475" x2="380" y2="535"/>
  <line x1="480" y1="475" x2="480" y2="535"/>
  <line x1="580" y1="475" x2="580" y2="535"/>
  <line x1="680" y1="475" x2="680" y2="535"/>
  <line x1="780" y1="475" x2="780" y2="535"/>
  <line x1="980" y1="475" x2="980" y2="535"/>
  <line x1="1080" y1="475" x2="1080" y2="535"/>
  <line x1="1180" y1="475" x2="1180" y2="535"/>
  <line x1="1380" y1="475" x2="1380" y2="535"/>
  <line x1="1480" y1="475" x2="1480" y2="535"/>
  <line x1="1780" y1="475" x2="1780" y2="535"/>
  <line x1="1880" y1="475" x2="1880" y2="535"/>
  <line x1="1980" y1="475" x2="1980" y2="535"/>
  <line x1="2080" y1="475" x2="2080" y2="535"/>
      </g>
      <g class="gen-labels">
  <text x="20" y="61" text-anchor="middle" class="gen-lbl">（田）</text>
  <text x="20" y="161" text-anchor="middle" class="gen-lbl">（绪）</text>
  <text x="20" y="261" text-anchor="middle" class="gen-lbl">（远）</text>
  <text x="20" y="361" text-anchor="middle" class="gen-lbl">（祥）</text>
  <text x="20" y="461" text-anchor="middle" class="gen-lbl">（开）</text>
  <text x="20" y="561" text-anchor="middle" class="gen-lbl">（世）</text>
      </g>
      <g class="nodes">
  <!-- 田世 -->
  <g class="node" onclick="showDetail('杜如松')"><rect x="1329" y="35" width="80" height="40" rx="8" fill="#ffc9c9" stroke="#c92a2a" stroke-width="2"/><text x="1369" y="61" text-anchor="middle" class="node-name">杜如松</text></g>
  <!-- 绪世 -->
  <g class="node" onclick="showDetail('杜好仁')"><rect x="390" y="135" width="80" height="40" rx="8" fill="#a5d8ff" stroke="#1864ab" stroke-width="2"/><text x="430" y="161" text-anchor="middle" class="node-name">杜好仁</text></g>
  <g class="node" onclick="showDetail('杜好贤')"><rect x="1240" y="135" width="80" height="40" rx="8" fill="#a5d8ff" stroke="#1864ab" stroke-width="2"/><text x="1280" y="161" text-anchor="middle" class="node-name">杜好贤</text></g>
  <g class="node" onclick="showDetail('杜好林')"><rect x="2357" y="135" width="80" height="40" rx="8" fill="#a5d8ff" stroke="#1864ab" stroke-width="2"/><text x="2397" y="161" text-anchor="middle" class="node-name">杜好林</text></g>
  <!-- 远世 -->
  <g class="node" onclick="showDetail('杜诗凡')"><rect x="390" y="235" width="80" height="40" rx="8" fill="#b2f2bb" stroke="#2b8a3e" stroke-width="2"/><text x="430" y="261" text-anchor="middle" class="node-name">杜诗凡</text></g>
  <g class="node" onclick="showDetail('杜诗豪')"><rect x="1040" y="235" width="80" height="40" rx="8" fill="#b2f2bb" stroke="#2b8a3e" stroke-width="2"/><text x="1080" y="261" text-anchor="middle" class="node-name">杜诗豪</text></g>
  <g class="node" onclick="showDetail('杜诗义')"><rect x="1440" y="235" width="80" height="40" rx="8" fill="#b2f2bb" stroke="#2b8a3e" stroke-width="2"/><text x="1480" y="261" text-anchor="middle" class="node-name">杜诗义</text></g>
  <g class="node" onclick="showDetail('杜诗信')"><rect x="2007" y="235" width="80" height="40" rx="8" fill="#b2f2bb" stroke="#2b8a3e" stroke-width="2"/><text x="2047" y="261" text-anchor="middle" class="node-name">杜诗信</text></g>
  <g class="node" onclick="showDetail('杜诗中')"><rect x="2340" y="235" width="80" height="40" rx="8" fill="#b2f2bb" stroke="#2b8a3e" stroke-width="2"/><text x="2380" y="261" text-anchor="middle" class="node-name">杜诗中</text></g>
  <g class="node" onclick="showDetail('杜诗太')"><rect x="2723" y="235" width="80" height="40" rx="8" fill="#b2f2bb" stroke="#2b8a3e" stroke-width="2"/><text x="2763" y="261" text-anchor="middle" class="node-name">杜诗太</text></g>
  <!-- 祥世 -->
  <g class="node" onclick="showDetail('杜继武')"><rect x="90" y="335" width="80" height="40" rx="8" fill="#e9d5ff" stroke="#862e9c" stroke-width="2"/><text x="130" y="361" text-anchor="middle" class="node-name">杜继武</text></g>
  <g class="node" onclick="showDetail('杜继文')"><rect x="290" y="335" width="80" height="40" rx="8" fill="#e9d5ff" stroke="#862e9c" stroke-width="2"/><text x="330" y="361" text-anchor="middle" class="node-name">杜继文</text></g>
  <g class="node" onclick="showDetail('杜继双')"><rect x="490" y="335" width="80" height="40" rx="8" fill="#e9d5ff" stroke="#862e9c" stroke-width="2"/><text x="530" y="361" text-anchor="middle" class="node-name">杜继双</text></g>
  <g class="node" onclick="showDetail('杜继全')"><rect x="690" y="335" width="80" height="40" rx="8" fill="#e9d5ff" stroke="#862e9c" stroke-width="2"/><text x="730" y="361" text-anchor="middle" class="node-name">杜继全</text></g>
  <g class="node" onclick="showDetail('杜继民')"><rect x="940" y="335" width="80" height="40" rx="8" fill="#e9d5ff" stroke="#862e9c" stroke-width="2"/><text x="980" y="361" text-anchor="middle" class="node-name">杜继民</text></g>
  <g class="node" onclick="showDetail('杜继田')"><rect x="1040" y="335" width="80" height="40" rx="8" fill="#e9d5ff" stroke="#862e9c" stroke-width="2"/><text x="1080" y="361" text-anchor="middle" class="node-name">杜继田</text></g>
  <g class="node" onclick="showDetail('杜继合')"><rect x="1140" y="335" width="80" height="40" rx="8" fill="#e9d5ff" stroke="#862e9c" stroke-width="2"/><text x="1180" y="361" text-anchor="middle" class="node-name">杜继合</text></g>
  <g class="node" onclick="showDetail('杜继俊')"><rect x="1440" y="335" width="80" height="40" rx="8" fill="#e9d5ff" stroke="#862e9c" stroke-width="2"/><text x="1480" y="361" text-anchor="middle" class="node-name">杜继俊</text></g>
  <g class="node" onclick="showDetail('杜继安')"><rect x="1840" y="335" width="80" height="40" rx="8" fill="#e9d5ff" stroke="#862e9c" stroke-width="2"/><text x="1880" y="361" text-anchor="middle" class="node-name">杜继安</text></g>
  <g class="node" onclick="showDetail('杜继恩')"><rect x="2040" y="335" width="80" height="40" rx="8" fill="#e9d5ff" stroke="#862e9c" stroke-width="2"/><text x="2080" y="361" text-anchor="middle" class="node-name">杜继恩</text></g>
  <g class="node" onclick="showDetail('杜继平')"><rect x="2140" y="335" width="80" height="40" rx="8" fill="#e9d5ff" stroke="#862e9c" stroke-width="2"/><text x="2180" y="361" text-anchor="middle" class="node-name">杜继平</text></g>
  <g class="node" onclick="showDetail('杜继军')"><rect x="2340" y="335" width="80" height="40" rx="8" fill="#e9d5ff" stroke="#862e9c" stroke-width="2"/><text x="2380" y="361" text-anchor="middle" class="node-name">杜继军</text></g>
  <g class="node" onclick="showDetail('杜继亮')"><rect x="2590" y="335" width="80" height="40" rx="8" fill="#e9d5ff" stroke="#862e9c" stroke-width="2"/><text x="2630" y="361" text-anchor="middle" class="node-name">杜继亮</text></g>
  <g class="node" onclick="showDetail('杜继明')"><rect x="2740" y="335" width="80" height="40" rx="8" fill="#e9d5ff" stroke="#862e9c" stroke-width="2"/><text x="2780" y="361" text-anchor="middle" class="node-name">杜继明</text></g>
  <g class="node" onclick="showDetail('杜顺科')"><rect x="2840" y="335" width="80" height="40" rx="8" fill="#e9d5ff" stroke="#862e9c" stroke-width="2"/><text x="2880" y="361" text-anchor="middle" class="node-name">杜顺科</text></g>
  <!-- 开世 -->
  <g class="node" onclick="showDetail('杜文杰')"><rect x="40" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="80" y="461" text-anchor="middle" class="node-name">杜文杰</text></g>
  <g class="node" onclick="showDetail('杜文锋')"><rect x="140" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="180" y="461" text-anchor="middle" class="node-name">杜文锋</text></g>
  <g class="node" onclick="showDetail('杜文彬')"><rect x="240" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="280" y="461" text-anchor="middle" class="node-name">杜文彬</text></g>
  <g class="node" onclick="showDetail('杜文坡')"><rect x="340" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="380" y="461" text-anchor="middle" class="node-name">杜文坡</text></g>
  <g class="node" onclick="showDetail('杜文涛')"><rect x="440" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="480" y="461" text-anchor="middle" class="node-name">杜文涛</text></g>
  <g class="node" onclick="showDetail('杜文辉')"><rect x="540" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="580" y="461" text-anchor="middle" class="node-name">杜文辉</text></g>
  <g class="node" onclick="showDetail('杜文凯')"><rect x="640" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="680" y="461" text-anchor="middle" class="node-name">杜文凯</text></g>
  <g class="node" onclick="showDetail('杜文明')"><rect x="740" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="780" y="461" text-anchor="middle" class="node-name">杜文明</text></g>
  <g class="node" onclick="showDetail('杜文鹏')"><rect x="940" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="980" y="461" text-anchor="middle" class="node-name">杜文鹏</text></g>
  <g class="node" onclick="showDetail('杜康宁')"><rect x="1040" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="1080" y="461" text-anchor="middle" class="node-name">杜康宁</text></g>
  <g class="node" onclick="showDetail('杜永海')"><rect x="1140" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="1180" y="461" text-anchor="middle" class="node-name">杜永海</text></g>
  <g class="node" onclick="showDetail('杜华威')"><rect x="1340" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="1380" y="461" text-anchor="middle" class="node-name">杜华威</text></g>
  <g class="node" onclick="showDetail('杜搏威')"><rect x="1440" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="1480" y="461" text-anchor="middle" class="node-name">杜搏威</text></g>
  <g class="node" onclick="showDetail('杜洋')"><rect x="1540" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="1580" y="461" text-anchor="middle" class="node-name">杜洋</text></g>
  <g class="node" onclick="showDetail('杜新威')"><rect x="1740" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="1780" y="461" text-anchor="middle" class="node-name">杜新威</text></g>
  <g class="node" onclick="showDetail('杜新鹏')"><rect x="1840" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="1880" y="461" text-anchor="middle" class="node-name">杜新鹏</text></g>
  <g class="node" onclick="showDetail('杜新辉')"><rect x="1940" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="1980" y="461" text-anchor="middle" class="node-name">杜新辉</text></g>
  <g class="node" onclick="showDetail('杜志伟')"><rect x="2040" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="2080" y="461" text-anchor="middle" class="node-name">杜志伟</text></g>
  <g class="node" onclick="showDetail('杜新峰')"><rect x="2140" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="2180" y="461" text-anchor="middle" class="node-name">杜新峰</text></g>
  <g class="node" onclick="showDetail('杜晨龙')"><rect x="2340" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="2380" y="461" text-anchor="middle" class="node-name">杜晨龙</text></g>
  <g class="node" onclick="showDetail('杜刘威')"><rect x="2540" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="2580" y="461" text-anchor="middle" class="node-name">杜刘威</text></g>
  <g class="node" onclick="showDetail('杜刘阳')"><rect x="2640" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="2680" y="461" text-anchor="middle" class="node-name">杜刘阳</text></g>
  <g class="node" onclick="showDetail('杜鸣一')"><rect x="2840" y="435" width="80" height="40" rx="8" fill="#ffe8cc" stroke="#d4780a" stroke-width="2"/><text x="2880" y="461" text-anchor="middle" class="node-name">杜鸣一</text></g>
  <!-- 世世 -->
  <g class="node" onclick="showDetail('杜奥翔')"><rect x="40" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="80" y="561" text-anchor="middle" class="node-name">杜奥翔</text></g>
  <g class="node" onclick="showDetail('杜秋润')"><rect x="140" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="180" y="561" text-anchor="middle" class="node-name">杜秋润</text></g>
  <g class="node" onclick="showDetail('杜雨润')"><rect x="240" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="280" y="561" text-anchor="middle" class="node-name">杜雨润</text></g>
  <g class="node" onclick="showDetail('杜雨辰')"><rect x="340" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="380" y="561" text-anchor="middle" class="node-name">杜雨辰</text></g>
  <g class="node" onclick="showDetail('杜尚哲')"><rect x="440" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="480" y="561" text-anchor="middle" class="node-name">杜尚哲</text></g>
  <g class="node" onclick="showDetail('杜大多')"><rect x="540" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="580" y="561" text-anchor="middle" class="node-name">杜大多</text></g>
  <g class="node" onclick="showDetail('杜二多')"><rect x="640" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="680" y="561" text-anchor="middle" class="node-name">杜二多</text></g>
  <g class="node" onclick="showDetail('杜科举')"><rect x="740" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="780" y="561" text-anchor="middle" class="node-name">杜科举</text></g>
  <g class="node" onclick="showDetail('杜龙翔')"><rect x="940" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="980" y="561" text-anchor="middle" class="node-name">杜龙翔</text></g>
  <g class="node" onclick="showDetail('杜俊熙')"><rect x="1040" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="1080" y="561" text-anchor="middle" class="node-name">杜俊熙</text></g>
  <g class="node" onclick="showDetail('杜思麒')"><rect x="1140" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="1180" y="561" text-anchor="middle" class="node-name">杜思麒</text></g>
  <g class="node" onclick="showDetail('杜浩宇')"><rect x="1340" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="1380" y="561" text-anchor="middle" class="node-name">杜浩宇</text></g>
  <g class="node" onclick="showDetail('杜浩然')"><rect x="1440" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="1480" y="561" text-anchor="middle" class="node-name">杜浩然</text></g>
  <g class="node" onclick="showDetail('杜俊宇')"><rect x="1740" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="1780" y="561" text-anchor="middle" class="node-name">杜俊宇</text></g>
  <g class="node" onclick="showDetail('杜宇晗')"><rect x="1840" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="1880" y="561" text-anchor="middle" class="node-name">杜宇晗</text></g>
  <g class="node" onclick="showDetail('杜宇恒')"><rect x="1940" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="1980" y="561" text-anchor="middle" class="node-name">杜宇恒</text></g>
  <g class="node" onclick="showDetail('杜奕辰')"><rect x="2040" y="535" width="80" height="40" rx="8" fill="#fff3bf" stroke="#f59f00" stroke-width="2"/><text x="2080" y="561" text-anchor="middle" class="node-name">杜奕辰</text></g>
      </g>
    </g>
  </svg>
  <div class="hint">拖拽移动 · 双指/滚轮缩放</div>
</div>
"""

with open('/Users/duxinfeng/data_sata/workspace/MyProjects/familyMap/家谱网页.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Written part1: {len(html)} bytes")
