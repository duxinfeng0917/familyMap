#!/usr/bin/env python3
"""
生成家谱网页 - 树形图版本
将 Obsidian 家谱 vault 转换为可在微信群分享的单页 HTML（SVG 树形图，支持拖拽缩放）

用法：
  python3 tools/生成家谱网页.py

输出：
  家谱网页.html（放根目录，可直接发送到微信群）
"""

import re
import json
from pathlib import Path

VAULT  = Path(__file__).parent.parent
PEOPLE = VAULT / "People"
OUTPUT = VAULT / "家谱网页.html"

# ── 配置：填入你的 Formspree endpoint ───────────────────────────────
# 步骤：
#   1. 访问 https://formspree.io 注册（免费）
#   2. 新建 Form，复制 endpoint，格式为 https://formspree.io/f/xxxxxxxx
#   3. 粘贴到下面引号内
# 留空则不显示「申请修改」功能
FORMSPREE_ENDPOINT = "https://formspree.io/f/mzdkklzn"  # 例如 "https://formspree.io/f/abcdefgh"

# 世代排序表
GEN_ORDER = ["一世","二世","三世","四世","五世","六世","七世","八世","九世","十世"]

# 家谱起始世数（一世 = 第15世，辈字：田）
# 完整辈份诗：如峰田绪远，祥开世泽长，继祖承兆庆，勤宗永康昌
# 田=15世（诗中第3字），故一世对应诗索引2
BASE_GEN = 15
_POEM_ALL = list("如峰田绪远祥开世泽长继祖承兆庆勤宗永康昌")
GEN_POEM  = _POEM_ALL[2:]   # 田绪远祥开世泽长继祖承兆庆勤宗永康昌

# 节点尺寸与间距
BOX_W  = 120   # 节点宽度
BOX_H  = 45    # 节点高度
H_GAP  = 32    # 同代节点水平间距
V_STEP = 140   # 世代中心到中心垂直距离
LEFT_PAD = 100 # 左侧世代标签宽度（加宽以容纳双行标签）
TOP_PAD  = 30  # 顶部留白

# 各世代节点颜色 (fill, stroke)
GEN_COLORS = {
    "一世": ("#ffc9c9", "#c92a2a"),
    "二世": ("#a5d8ff", "#1864ab"),
    "三世": ("#b2f2bb", "#2b8a3e"),
    "四世": ("#e9d5ff", "#862e9c"),
    "五世": ("#ffe8cc", "#d4780a"),
    "六世": ("#fff3bf", "#f59f00"),
}

# ── 解析工具 ──────────────────────────────────────────────────────

def strip_link(text):
    return re.sub(r'[\"\'"\u201c\u201d]?\[\[([^\]|]+)(?:\|[^\]]*)?\]\][\"\'"\u201c\u201d]?', r'\1', text or "").strip()

def parse_frontmatter(text):
    m = re.match(r'^---\s*\n(.*?)\n---', text, re.DOTALL)
    if not m:
        return {}
    data = {}
    current_key = None
    current_list = []
    for line in m.group(1).splitlines():
        list_match = re.match(r'^\s+-\s+(.*)', line)
        kv_match   = re.match(r'^(\w+):\s*(.*)', line)
        if list_match:
            if current_key:
                current_list.append(strip_link(list_match.group(1)))
        elif kv_match:
            if current_key and current_list:
                data[current_key + "_list"] = current_list
            current_key  = kv_match.group(1)
            current_list = []
            val = kv_match.group(2).strip().strip('"\'')
            if val and val != "[]":
                data[current_key] = strip_link(val) if "[[" in val else val
            elif val == "[]":
                data[current_key + "_list"] = []
    if current_key and current_list:
        data[current_key + "_list"] = current_list
    return data

def gen_prefix(p):
    return p.get("世代", "").split("（")[0].strip()

def gen_order_index(prefix):
    try:
        return GEN_ORDER.index(prefix)
    except ValueError:
        return 99

# ── 加载人物 ──────────────────────────────────────────────────────

def load_people():
    people = {}
    for f in PEOPLE.glob("*.md"):
        name    = f.stem
        content = f.read_text(encoding="utf-8")
        data    = parse_frontmatter(content)
        data.setdefault("姓名", name)
        data.setdefault("世代", "未知")
        data.setdefault("性别", "")
        data.setdefault("父亲", "")
        data.setdefault("母亲", "")
        data.setdefault("备注", "")
        data.setdefault("子女_list", [])
        data.setdefault("兄弟姐妹_list", [])
        people[name] = data
    return people

# ── 树形布局 ──────────────────────────────────────────────────────

def compute_layout(people):
    """DFS 后序遍历：叶节点顺序分配 x，父节点居中于子节点之上。"""
    # 构建父→子映射：优先使用父亲档案中 子女_list 的顺序（即长幼顺序）
    children = {n: [] for n in people}
    for name, p in people.items():
        ordered = p.get("子女_list", [])
        for child in ordered:
            if child in people and child not in children[name]:
                children[name].append(child)
    # 补充：若某人的父亲字段指向本人，但未出现在父亲的子女列表里，追加到末尾
    for name, p in people.items():
        father = p.get("父亲", "")
        if father and father in people and name not in children[father]:
            children[father].append(name)

    roots = [n for n, p in people.items()
             if not p.get("父亲") or p.get("父亲") not in people]
    roots.sort()

    positions = {}
    x_counter = [0]  # 可变计数器

    def get_y(name):
        prefix = gen_prefix(people[name])
        yi = gen_order_index(prefix)
        return TOP_PAD + yi * V_STEP

    def assign(name):
        kids = children.get(name, [])
        if not kids:
            x = LEFT_PAD + x_counter[0] * (BOX_W + H_GAP)
            positions[name] = (x, get_y(name))
            x_counter[0] += 1
        else:
            for kid in kids:
                assign(kid)
            valid = [positions[k][0] for k in kids if k in positions]
            x = (min(valid) + max(valid)) / 2 if valid else LEFT_PAD + x_counter[0] * (BOX_W + H_GAP)
            positions[name] = (x, get_y(name))

    for root in roots:
        assign(root)

    # 处理孤立节点（无父且不在任何子树中）
    for name in people:
        if name not in positions:
            x = LEFT_PAD + x_counter[0] * (BOX_W + H_GAP)
            positions[name] = (x, get_y(name))
            x_counter[0] += 1

    return positions, children

# ── SVG 渲染 ─────────────────────────────────────────────────────

def render_svg_elements(people, positions, children):
    edges, nodes = [], []

    # 连线（先画，在节点后面）
    for name, kids in children.items():
        if not kids or name not in positions:
            continue
        px, py = positions[name]
        pcx = px + BOX_W / 2
        p_bot = py + BOX_H

        kid_data = [(positions[k][0] + BOX_W / 2, positions[k][1])
                    for k in kids if k in positions]
        if not kid_data:
            continue

        min_cy = min(cy for _, cy in kid_data)
        mid_y  = p_bot + (min_cy - p_bot) * 0.45  # 折点在父子中间偏上

        edges.append(f'<line x1="{pcx:.1f}" y1="{p_bot}" x2="{pcx:.1f}" y2="{mid_y:.1f}"/>')
        if len(kid_data) > 1:
            min_kx = min(cx for cx, _ in kid_data)
            max_kx = max(cx for cx, _ in kid_data)
            edges.append(f'<line x1="{min_kx:.1f}" y1="{mid_y:.1f}" x2="{max_kx:.1f}" y2="{mid_y:.1f}"/>')
        for kcx, kcy in kid_data:
            edges.append(f'<line x1="{kcx:.1f}" y1="{mid_y:.1f}" x2="{kcx:.1f}" y2="{kcy:.1f}"/>')

    # 节点
    for name, (x, y) in positions.items():
        prefix = gen_prefix(people[name])
        fill, stroke = GEN_COLORS.get(prefix, ("#f0f0f0", "#666"))
        cx = x + BOX_W / 2
        cy_text = y + BOX_H / 2 + 6
        safe = name.replace("'", "\\'").replace('"', '&quot;')
        nodes.append(
            f'<g class="node" onclick="showDetail(\'{safe}\')">'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{BOX_W}" height="{BOX_H}" rx="8" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
            f'<text x="{cx:.1f}" y="{cy_text:.1f}" text-anchor="middle" class="node-name">{name}</text>'
            f'</g>'
        )

    # 世代标签（左侧固定列）：辈份诗字 + 绝对世数（两行）
    gen_labels = []
    seen_gens = {}
    for name, p in people.items():
        prefix = gen_prefix(p)
        if prefix in seen_gens or prefix not in GEN_ORDER:
            continue
        seen_gens[prefix] = True
        _, y = positions[name]
        cx = LEFT_PAD // 2
        cy = y + BOX_H / 2
        idx = GEN_ORDER.index(prefix)
        abs_gen = BASE_GEN + idx
        poem_char = GEN_POEM[idx] if idx < len(GEN_POEM) else ""
        gen_labels.append(
            f'<text x="{cx}" y="{cy - 5:.1f}" text-anchor="middle" class="gen-lbl" '
            f'font-size="16px" font-weight="800" fill="#8b4513">{poem_char}</text>'
            f'<text x="{cx}" y="{cy + 13:.1f}" text-anchor="middle" class="gen-lbl" '
            f'font-size="12px" fill="#888">{abs_gen}世</text>'
        )

    # 画布尺寸
    max_x = max(x + BOX_W for x, _ in positions.values()) + 60
    max_y = max(y + BOX_H for _, y in positions.values()) + 60

    return (
        int(max_x), int(max_y),
        "\n  ".join(edges),
        "\n  ".join(nodes),
        "\n  ".join(gen_labels),
    )

# ── 详情 JSON ─────────────────────────────────────────────────────

def build_detail_json(people):
    details = {}
    for name, p in people.items():
        father   = p.get("父亲", "")
        siblings = p.get("兄弟姐妹_list", [])
        kids     = p.get("子女_list", [])

        def link(n):
            return f'<a href="javascript:void(0)" onclick="showDetail(\'{n}\')">{n}</a>' \
                   if n in people else n

        details[name] = {
            "name":     name,
            "gen":      p.get("世代", ""),
            "gender":   p.get("性别", ""),
            "father":   link(father) if father else "—",
            "mother":   p.get("母亲", "") or "—",
            "children": "、".join(link(c) for c in kids) if kids else "—",
            "siblings": "、".join(link(s) for s in siblings) if siblings else "—",
            "notes":    p.get("备注", "") or "—",
        }
    return json.dumps(details, ensure_ascii=False)

# ── 生成 HTML ─────────────────────────────────────────────────────

def generate(people):
    positions, children = compute_layout(people)
    canvas_w, canvas_h, edges_svg, nodes_svg, gen_labels_svg = \
        render_svg_elements(people, positions, children)

    details_json = build_detail_json(people)
    count        = len(people)

    if FORMSPREE_ENDPOINT:
        feedback_block = f'''
    <div id="fb-wrap">
      <div class="fb-label">如有信息有误，请提交修改建议：</div>
      <form id="fb-form" onsubmit="submitFb(event)">
        <input type="hidden" id="fb-person" name="人物姓名">
        <textarea name="修改建议" required rows="3"
          placeholder="请描述需要修改的内容（如：出生年、子女信息等）…"></textarea>
        <input type="text" name="你的姓名" placeholder="你的姓名（选填）">
        <button type="submit" class="btn-submit">提交修改建议</button>
        <div id="fb-status"></div>
      </form>
    </div>'''
        feedback_js = f'''
async function submitFb(e) {{
  e.preventDefault();
  const btn = e.target.querySelector('[type=submit]');
  btn.disabled = true; btn.textContent = '提交中…';
  try {{
    const res = await fetch('{FORMSPREE_ENDPOINT}', {{
      method: 'POST', body: new FormData(e.target),
      headers: {{ 'Accept': 'application/json' }}
    }});
    if (res.ok) {{
      document.getElementById('fb-status').textContent = '✓ 已提交，感谢你的建议！';
      e.target.reset();
    }} else {{
      document.getElementById('fb-status').textContent = '提交失败，请稍后重试。';
    }}
  }} catch {{ document.getElementById('fb-status').textContent = '网络错误，请稍后重试。'; }}
  btn.disabled = false; btn.textContent = '提交修改建议';
}}'''
    else:
        feedback_block = ""
        feedback_js    = ""

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>杜氏家谱</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&family=Noto+Serif+SC:wght@400;600;700;900&display=swap');

:root{{
  --red:    #7B1818;
  --red-dk: #4E0F0F;
  --red-md: #9A2424;
  --gold:   #B07800;
  --gold-l: #C9A030;
  --gold-p: #EED890;
  --ink:    #1C0A00;
  --ink-80: #3A1E0A;
  --ink-50: #7A5A3A;
  --ink-30: #B09878;
  --bg:     #FAF6EE;
  --bg-w:   #F2EAE0;
  --paper:  #FFFDF8;
  --bdr:    #CEBB96;
  --bdr-l:  #E5D8BC;
  --sh-xs:  0 1px 3px rgba(80,20,0,.10);
  --sh-sm:  0 2px 8px rgba(80,20,0,.14);
  --sh-md:  0 4px 16px rgba(80,20,0,.18);
  --sh-lg:  0 8px 32px rgba(80,20,0,.22);
  --sh-xl:  0 16px 48px rgba(0,0,0,.28);
  --serif:  "Noto Serif SC","PingFang SC","STSong","SimSun",serif;
  --sans:   "Noto Sans SC","PingFang SC","STHeiti",sans-serif;
  --dur:    200ms;
  --ease:   cubic-bezier(.25,.46,.45,.94);
  --r-s:    8px;
  --r-m:    12px;
  --r-l:    18px;
  --r-xl:   24px;
}}

*{{box-sizing:border-box;margin:0;padding:0}}
body{{
  font-family:var(--serif);
  background:var(--bg);color:var(--ink);
  display:flex;flex-direction:column;height:100vh;overflow:hidden;
}}

/* ── Header ── */
header{{
  background:linear-gradient(160deg,var(--red-dk) 0%,var(--red) 55%,var(--red-md) 100%);
  color:#fff;padding:14px 16px 12px;text-align:center;flex-shrink:0;
  position:relative;box-shadow:0 4px 20px rgba(0,0,0,.38);overflow:hidden;
}}
header::before{{
  content:'';position:absolute;inset:0;
  background-image:
    repeating-linear-gradient(90deg,rgba(255,255,255,.022) 0,rgba(255,255,255,.022) 1px,transparent 1px,transparent 22px),
    repeating-linear-gradient(0deg,rgba(255,255,255,.012) 0,rgba(255,255,255,.012) 1px,transparent 1px,transparent 22px);
  pointer-events:none;
}}
header::after{{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,transparent 0%,var(--gold-l) 30%,var(--gold) 50%,var(--gold-l) 70%,transparent 100%);
}}
.header-body{{position:relative;z-index:1}}
.header-title-row{{
  display:flex;align-items:center;justify-content:center;gap:10px;margin-bottom:5px;
}}
.header-line{{
  flex:1;max-width:72px;height:1px;
  background:linear-gradient(90deg,transparent,rgba(200,160,40,.55));
}}
.header-line:last-child{{
  background:linear-gradient(90deg,rgba(200,160,40,.55),transparent);
}}
.header-diamond{{
  width:5px;height:5px;background:var(--gold-l);
  transform:rotate(45deg);opacity:.85;flex-shrink:0;
}}
header h1{{
  font-size:1.78em;letter-spacing:10px;text-indent:10px;font-weight:900;
  color:#FFF8F0;text-shadow:0 1px 0 rgba(255,255,255,.10),0 2px 12px rgba(0,0,0,.4);
}}
header p{{
  font-family:var(--sans);font-size:.71em;opacity:.68;letter-spacing:2px;
  font-weight:300;color:#F5EEE8;
}}

/* ── 辈份诗横幅 ── */
.poem{{
  background:linear-gradient(90deg,#2A0C00 0%,#521E06 35%,#5A2208 50%,#521E06 65%,#2A0C00 100%);
  color:var(--gold-p);text-align:center;padding:7px 16px;
  font-size:.84em;letter-spacing:5px;text-indent:5px;flex-shrink:0;
  font-weight:600;text-shadow:0 1px 6px rgba(0,0,0,.5);
  border-bottom:1px solid rgba(0,0,0,.2);
}}

/* ── 沿革信息栏 ── */
.info-bar{{
  background:linear-gradient(90deg,var(--bg-w),var(--paper),var(--bg-w));
  border-bottom:1px solid var(--bdr-l);padding:6px 20px;
  font-family:var(--sans);font-size:.73em;color:var(--ink-50);line-height:1.7;
  flex-shrink:0;text-align:center;cursor:pointer;user-select:none;
  transition:background var(--dur) var(--ease);
}}
.info-bar:hover{{background:linear-gradient(90deg,#EDE4D4,#F6F1E9,#EDE4D4)}}
.info-bar .hl{{color:var(--red);font-weight:600}}
.info-bar .arrow{{font-size:.8em;margin-left:4px;transition:transform .25s var(--ease);display:inline-block}}
.info-bar.open .arrow{{transform:rotate(180deg)}}

/* ── 辈份诗对照面板 ── */
.poem-detail{{
  display:none;background:linear-gradient(180deg,var(--paper),var(--bg));
  border-bottom:1px solid var(--bdr-l);padding:14px 20px 16px;flex-shrink:0;
}}
.poem-detail.show{{display:block}}
.poem-origin{{
  font-family:var(--sans);font-size:.71em;color:var(--ink-30);
  text-align:center;margin-bottom:12px;letter-spacing:1px;line-height:1.65;
}}
.poem-grid{{display:flex;flex-wrap:wrap;justify-content:center;gap:6px 8px}}
.poem-cell{{
  display:flex;flex-direction:column;align-items:center;
  background:var(--paper);border:1px solid var(--bdr-l);border-radius:var(--r-m);
  padding:6px 10px;min-width:46px;box-shadow:var(--sh-xs);
  transition:transform var(--dur) var(--ease),box-shadow var(--dur),border-color var(--dur);
}}
.poem-cell:hover{{transform:translateY(-2px);box-shadow:var(--sh-sm);border-color:var(--bdr)}}
.poem-cell .pc{{font-size:1.3em;font-weight:900;color:var(--red);line-height:1.2}}
.poem-cell .pg{{font-family:var(--sans);font-size:.62em;color:var(--ink-30);margin-top:3px}}
.poem-cell.active{{
  background:linear-gradient(145deg,var(--red-dk),var(--red));
  border-color:var(--red);box-shadow:var(--sh-sm),inset 0 1px 0 rgba(255,255,255,.08);
}}
.poem-cell.active .pc{{color:#FFF8F0}}
.poem-cell.active .pg{{color:var(--gold-p);opacity:.88}}

/* ── 视图切换按钮 ── */
.view-btn{{
  position:absolute;top:50%;right:16px;transform:translateY(-50%);z-index:100;
  background:rgba(255,255,255,.13);border:1px solid rgba(255,255,255,.28);
  color:#FFF8F0;border-radius:var(--r-l);
  padding:6px 16px;font-size:.75em;cursor:pointer;
  font-family:var(--sans);letter-spacing:1.5px;font-weight:500;
  backdrop-filter:blur(8px);
  transition:background var(--dur),box-shadow var(--dur),transform .15s;
}}
.view-btn:hover{{background:rgba(255,255,255,.22);box-shadow:0 2px 12px rgba(0,0,0,.28)}}
.view-btn:active{{transform:translateY(calc(-50% + 1px))}}

/* ── 树形画布 ── */
#canvas-wrap{{
  flex:1;overflow:hidden;position:relative;cursor:grab;touch-action:none;
  background:var(--bg);
}}
#canvas-wrap.dragging{{cursor:grabbing}}
svg#tree{{display:block}}
.node{{cursor:pointer}}
.node rect{{transition:filter .15s}}
.node:hover rect{{filter:brightness(.90) drop-shadow(0 2px 6px rgba(0,0,0,.18))}}
.node:active rect{{filter:brightness(.83)}}
.node-name{{
  font-size:14px;font-weight:700;fill:#1A0800;pointer-events:none;
  font-family:"Noto Serif SC","PingFang SC",serif;
}}
.gen-lbl{{font-family:"Noto Serif SC","PingFang SC",serif;font-weight:700}}
svg .edges line{{stroke:#C0A068 !important;stroke-opacity:.65}}
.hint{{
  position:absolute;bottom:16px;right:18px;
  font-family:var(--sans);font-size:.67em;color:var(--ink-30);
  background:rgba(255,252,245,.92);padding:5px 12px;border-radius:var(--r-l);
  pointer-events:none;border:1px solid var(--bdr-l);letter-spacing:.5px;
  backdrop-filter:blur(6px);box-shadow:var(--sh-xs);
}}

/* ── 详情弹窗 ── */
.overlay{{
  display:none;position:fixed;inset:0;
  background:rgba(12,4,0,.62);backdrop-filter:blur(5px);
  z-index:200;align-items:center;justify-content:center;
}}
.overlay.on{{display:flex}}
.modal{{
  background:var(--paper);border-radius:var(--r-xl);
  width:88%;max-width:380px;max-height:88vh;overflow:hidden;
  box-shadow:var(--sh-xl);display:flex;flex-direction:column;
  border:1px solid var(--bdr-l);
}}
.modal-hd{{
  background:linear-gradient(150deg,var(--red-dk) 0%,var(--red) 100%);
  color:#fff;padding:22px 24px 18px;flex-shrink:0;
  position:relative;overflow:hidden;
}}
.modal-hd::before{{
  content:'';position:absolute;inset:0;
  background:repeating-linear-gradient(90deg,rgba(255,255,255,.02) 0,rgba(255,255,255,.02) 1px,transparent 1px,transparent 20px);
  pointer-events:none;
}}
.modal-hd::after{{
  content:'';position:absolute;bottom:0;left:24px;right:24px;height:1px;
  background:linear-gradient(90deg,transparent,rgba(196,160,40,.38),transparent);
}}
.modal-title{{
  font-size:1.6em;font-weight:900;letter-spacing:4px;text-indent:4px;
  text-shadow:0 1px 6px rgba(0,0,0,.3);color:#FFF8F0;position:relative;
}}
.modal-sub{{
  font-family:var(--sans);font-size:.72em;opacity:.68;
  margin-top:5px;letter-spacing:1px;position:relative;color:#F0DDD0;
}}
.modal-body{{padding:20px 24px;overflow-y:auto;flex:1}}
.row{{
  display:flex;align-items:flex-start;
  padding:9px 0;border-bottom:1px solid var(--bdr-l);font-size:.88em;
}}
.row:last-child{{border-bottom:none}}
.lbl{{
  font-family:var(--sans);color:var(--ink-30);width:72px;flex-shrink:0;
  font-size:.83em;padding-top:1px;letter-spacing:.5px;
}}
.val{{color:var(--ink-80);flex:1;line-height:1.75}}
.val a{{
  color:var(--red);text-decoration:none;font-weight:700;
  border-bottom:1px solid rgba(123,24,24,.22);
  transition:border-color var(--dur),color var(--dur);
}}
.val a:hover{{color:var(--red-md);border-bottom-color:var(--red)}}
.modal-ft{{
  padding:16px 24px;
  background:linear-gradient(180deg,var(--bg-w),var(--bg));
  border-top:1px solid var(--bdr-l);flex-shrink:0;
}}
#fb-wrap{{margin-top:16px;border-top:1px solid var(--bdr-l);padding-top:16px}}
#fb-wrap .fb-label{{font-family:var(--sans);font-size:.78em;color:var(--ink-30);margin-bottom:10px}}
#fb-form textarea,#fb-form input[type=text]{{
  width:100%;border:1px solid var(--bdr-l);border-radius:var(--r-s);
  padding:9px 12px;font-size:.84em;font-family:var(--sans);
  color:var(--ink-80);background:var(--paper);
  transition:border-color var(--dur);outline:none;resize:vertical;
}}
#fb-form input[type=text]{{margin-top:8px;resize:none}}
#fb-form textarea:focus,#fb-form input[type=text]:focus{{border-color:var(--red)}}
#fb-form .btn-submit{{
  width:100%;margin-top:10px;padding:11px;
  background:var(--paper);color:var(--red);
  border:1.5px solid var(--red);border-radius:var(--r-s);
  font-family:var(--sans);font-size:.88em;cursor:pointer;
  letter-spacing:1px;font-weight:500;
  transition:background var(--dur),color var(--dur);
}}
#fb-form .btn-submit:hover{{background:var(--red);color:#FFF8F0}}
#fb-status{{font-family:var(--sans);text-align:center;font-size:.78em;margin-top:8px;color:var(--ink-50)}}
.btn-close{{
  width:100%;padding:13px;
  background:linear-gradient(135deg,var(--red),var(--red-md));
  color:#FFF8F0;border:none;border-radius:var(--r-m);
  font-size:.92em;cursor:pointer;font-family:var(--sans);
  letter-spacing:2px;font-weight:500;box-shadow:var(--sh-sm);
  transition:opacity var(--dur),box-shadow var(--dur),transform .15s;
}}
.btn-close:hover{{opacity:.9;box-shadow:var(--sh-md)}}
.btn-close:active{{transform:scale(.99)}}

/* ── 竖列名册 ── */
#list-view{{
  display:none;flex:1;overflow-x:auto;overflow-y:auto;
  background:repeating-linear-gradient(
    0deg,var(--bg-w) 0px,var(--bg-w) 1px,var(--bg) 1px,var(--bg) 32px
  );
  padding:24px 20px;
}}
#list-view.show{{display:flex;align-items:flex-start;gap:0}}
.gen-col{{
  display:flex;flex-direction:column;align-items:center;
  min-width:92px;border-right:1px solid var(--bdr-l);padding:0 10px;
}}
.gen-col:last-child{{border-right:none}}
.gen-col-hd{{
  display:flex;flex-direction:column;align-items:center;
  background:linear-gradient(145deg,var(--red-dk),var(--red));
  color:#FFF8F0;border-radius:var(--r-m);
  padding:10px 14px;margin-bottom:14px;text-align:center;
  box-shadow:var(--sh-md);min-width:68px;
  border:1px solid rgba(255,255,255,.08);
}}
.gen-col-hd .ch{{font-size:1.6em;font-weight:900;line-height:1.1;letter-spacing:1px}}
.gen-col-hd .ws{{font-family:var(--sans);font-size:.62em;opacity:.72;margin-top:4px;letter-spacing:.5px;font-weight:300}}
.name-card{{
  background:rgba(255,253,248,.96);border:1px solid var(--bdr-l);border-radius:var(--r-s);
  padding:8px 12px;margin-bottom:8px;font-size:.88em;font-weight:700;
  color:var(--ink-80);cursor:pointer;text-align:center;width:100%;
  box-shadow:var(--sh-xs);
  transition:background var(--dur),box-shadow var(--dur),transform var(--dur),border-color var(--dur),color var(--dur);
  letter-spacing:.5px;
}}
.name-card:hover{{
  background:#FFF0E5;border-color:var(--red);box-shadow:var(--sh-sm);
  transform:translateY(-1px);color:var(--red);
}}
.name-card:active{{transform:translateY(0)}}
</style>
</head>
<body>

<header>
  <div class="header-body">
    <div class="header-title-row">
      <div class="header-line"></div>
      <div class="header-diamond"></div>
      <h1>杜氏家谱</h1>
      <div class="header-diamond"></div>
      <div class="header-line"></div>
    </div>
    <p>共 <strong>{count}</strong> 位成员 &nbsp;·&nbsp; 自第15世始记</p>
  </div>
  <button class="view-btn" id="view-btn" onclick="toggleView()">竖列名册</button>
</header>
<div class="poem">如峰田绪远 · 祥开世泽长 · 继祖承兆庆 · 勤宗永康昌</div>
<div class="info-bar" id="info-bar" onclick="togglePoem()">
  <span class="hl">溯源：</span>明洪武元年（约公元1370年）奉诏迁居开封府繁塔侧云寄桥，后逐渐流居于杞县西寨、柿园万寨、祥符仇楼、杜良等地 &nbsp;｜&nbsp;
  <span class="hl">点击查看辈份诗对照 <span class="arrow">▼</span></span>
</div>
<div class="poem-detail" id="poem-detail">
  <div class="poem-origin">自第15世续订辈份（20字）：如峰田绪远，祥开世泽长，继祖承兆庆，勤宗永康昌</div>
  <div class="poem-grid">
    <div class="poem-cell"><span class="pc">如</span><span class="pg">13世</span></div>
    <div class="poem-cell"><span class="pc">峰</span><span class="pg">14世</span></div>
    <div class="poem-cell active"><span class="pc">田</span><span class="pg">15世</span></div>
    <div class="poem-cell active"><span class="pc">绪</span><span class="pg">16世</span></div>
    <div class="poem-cell active"><span class="pc">远</span><span class="pg">17世</span></div>
    <div class="poem-cell active"><span class="pc">祥</span><span class="pg">18世</span></div>
    <div class="poem-cell active"><span class="pc">开</span><span class="pg">19世</span></div>
    <div class="poem-cell active"><span class="pc">世</span><span class="pg">20世</span></div>
    <div class="poem-cell"><span class="pc">泽</span><span class="pg">21世</span></div>
    <div class="poem-cell"><span class="pc">长</span><span class="pg">22世</span></div>
    <div class="poem-cell"><span class="pc">继</span><span class="pg">23世</span></div>
    <div class="poem-cell"><span class="pc">祖</span><span class="pg">24世</span></div>
    <div class="poem-cell"><span class="pc">承</span><span class="pg">25世</span></div>
    <div class="poem-cell"><span class="pc">兆</span><span class="pg">26世</span></div>
    <div class="poem-cell"><span class="pc">庆</span><span class="pg">27世</span></div>
    <div class="poem-cell"><span class="pc">勤</span><span class="pg">28世</span></div>
    <div class="poem-cell"><span class="pc">宗</span><span class="pg">29世</span></div>
    <div class="poem-cell"><span class="pc">永</span><span class="pg">30世</span></div>
    <div class="poem-cell"><span class="pc">康</span><span class="pg">31世</span></div>
    <div class="poem-cell"><span class="pc">昌</span><span class="pg">32世</span></div>
  </div>
</div>

<div id="canvas-wrap">
  <svg id="tree" width="{canvas_w}" height="{canvas_h}" xmlns="http://www.w3.org/2000/svg">
    <g id="root-g">
      <g class="edges" stroke="#aaa" stroke-width="1.5" fill="none">
  {edges_svg}
      </g>
      <g class="gen-labels">
  {gen_labels_svg}
      </g>
      <g class="nodes">
  {nodes_svg}
      </g>
    </g>
  </svg>
  <div class="hint">拖拽移动 · 双指/滚轮缩放</div>
</div>

<div id="list-view"></div>

<div class="overlay" id="overlay" onclick="bgClose(event)">
  <div class="modal">
    <div class="modal-hd">
      <div class="modal-title" id="m-name"></div>
      <div class="modal-sub" id="m-gen"></div>
    </div>
    <div class="modal-body" id="m-body"></div>
    <div class="modal-ft">
      {feedback_block}
      <button class="btn-close" onclick="closeModal()">关 闭</button>
    </div>
  </div>
</div>

<script>
const D = {details_json};
{feedback_js}

// ── 竖列名册视图 ──
const GEN_POEM_MAP = {{"田":"15世","绪":"16世","远":"17世","祥":"18世","开":"19世","世":"20世"}};
const GEN_CHAR_ORDER = ["田","绪","远","祥","开","世"];

function toggleView() {{
  const wrap = document.getElementById('canvas-wrap');
  const list = document.getElementById('list-view');
  const btn  = document.getElementById('view-btn');
  const isTree = list.style.display !== 'flex' && !list.classList.contains('show');
  if (isTree) {{
    wrap.style.display = 'none';
    list.classList.add('show');
    btn.textContent = '树形图';
    buildListView();
  }} else {{
    wrap.style.display = '';
    list.classList.remove('show');
    btn.textContent = '竖列名册';
  }}
}}

function buildListView() {{
  const list = document.getElementById('list-view');
  if (list.dataset.built) return;
  list.dataset.built = '1';

  // 按辈字分组
  const groups = {{}};
  GEN_CHAR_ORDER.forEach(ch => groups[ch] = []);
  for (const [name, d] of Object.entries(D)) {{
    // 从世代字段提取辈字，格式：XX世（N世，辈字：X）
    const m = d.gen.match(/辈字：(.)/);
    if (m && groups[m[1]] !== undefined) groups[m[1]].push(name);
  }}

  let html = '';
  GEN_CHAR_ORDER.forEach(ch => {{
    const ws = GEN_POEM_MAP[ch];
    const names = groups[ch];
    if (!names.length) return;
    html += `<div class="gen-col">
      <div class="gen-col-hd"><span class="ch">${{ch}}</span><span class="ws">${{ws}}</span></div>`;
    names.forEach(n => {{
      html += `<div class="name-card" onclick="showDetail('${{n}}')">${{n}}</div>`;
    }});
    html += '</div>';
  }});
  list.innerHTML = html;
}}

// ── 辈份诗对照展开 ──
function togglePoem() {{
  const bar    = document.getElementById('info-bar');
  const detail = document.getElementById('poem-detail');
  bar.classList.toggle('open');
  detail.classList.toggle('show');
}}

// ── 详情弹窗 ──
function showDetail(n) {{
  const d = D[n]; if (!d) return;
  document.getElementById('m-name').textContent = d.name;
  document.getElementById('m-gen').textContent  = d.gen;
  document.getElementById('m-body').innerHTML = `
    <div class="row"><span class="lbl">性别</span><span class="val">${{d.gender||'—'}}</span></div>
    <div class="row"><span class="lbl">父亲</span><span class="val">${{d.father}}</span></div>
    <div class="row"><span class="lbl">母亲</span><span class="val">${{d.mother}}</span></div>
    <div class="row"><span class="lbl">子女</span><span class="val">${{d.children}}</span></div>
    <div class="row"><span class="lbl">兄弟姐妹</span><span class="val">${{d.siblings}}</span></div>
    <div class="row"><span class="lbl">备注</span><span class="val">${{d.notes}}</span></div>`;
  document.getElementById('fb-person') && (document.getElementById('fb-person').value = n);
  document.getElementById('fb-status') && (document.getElementById('fb-status').textContent = '');
  document.getElementById('overlay').classList.add('on');
}}
function closeModal() {{ document.getElementById('overlay').classList.remove('on'); }}
function bgClose(e) {{ if (e.target.id === 'overlay') closeModal(); }}
// ── 拖拽 & 缩放 ──
const wrap = document.getElementById('canvas-wrap');
const g    = document.getElementById('root-g');
const SVG_W = {canvas_w}, SVG_H = {canvas_h};

let tx = 0, ty = 0, scale = 1;
let dragging = false, startX = 0, startY = 0, startTx = 0, startTy = 0;
let pinchDist = 0, pinchScale = 1, pinchTx = 0, pinchTy = 0;

function applyTransform() {{
  g.setAttribute('transform', `translate(${{tx}},${{ty}}) scale(${{scale}})`);
}}

// 初始居中
function initView() {{
  const cw = wrap.clientWidth, ch = wrap.clientHeight;
  scale = Math.min(cw / SVG_W, ch / SVG_H, 1) * 0.95;
  tx = (cw - SVG_W * scale) / 2;
  ty = (ch - SVG_H * scale) / 2;
  applyTransform();
}}
initView();
window.addEventListener('resize', initView);

// 鼠标拖拽
wrap.addEventListener('mousedown', e => {{
  if (e.button !== 0) return;
  dragging = true; startX = e.clientX; startY = e.clientY;
  startTx = tx; startTy = ty;
  wrap.classList.add('dragging');
}});
window.addEventListener('mousemove', e => {{
  if (!dragging) return;
  tx = startTx + e.clientX - startX;
  ty = startTy + e.clientY - startY;
  applyTransform();
}});
window.addEventListener('mouseup', () => {{ dragging = false; wrap.classList.remove('dragging'); }});

// 滚轮缩放
wrap.addEventListener('wheel', e => {{
  e.preventDefault();
  const rect = wrap.getBoundingClientRect();
  const mx = e.clientX - rect.left, my = e.clientY - rect.top;
  const delta = e.deltaY < 0 ? 1.12 : 0.89;
  const ns = Math.max(0.2, Math.min(4, scale * delta));
  tx = mx - (mx - tx) * ns / scale;
  ty = my - (my - ty) * ns / scale;
  scale = ns;
  applyTransform();
}}, {{ passive: false }});

// 触摸拖拽 & 双指缩放
function touchDist(t) {{
  const dx = t[0].clientX - t[1].clientX, dy = t[0].clientY - t[1].clientY;
  return Math.sqrt(dx*dx + dy*dy);
}}
function touchMid(t, rect) {{
  return [(t[0].clientX + t[1].clientX)/2 - rect.left,
          (t[0].clientY + t[1].clientY)/2 - rect.top];
}}

wrap.addEventListener('touchstart', e => {{
  e.preventDefault();
  const ts = e.touches;
  if (ts.length === 1) {{
    dragging = true; startX = ts[0].clientX; startY = ts[0].clientY;
    startTx = tx; startTy = ty;
  }} else if (ts.length === 2) {{
    dragging = false;
    pinchDist = touchDist(ts); pinchScale = scale; pinchTx = tx; pinchTy = ty;
  }}
}}, {{ passive: false }});

wrap.addEventListener('touchmove', e => {{
  e.preventDefault();
  const ts = e.touches;
  if (ts.length === 1 && dragging) {{
    tx = startTx + ts[0].clientX - startX;
    ty = startTy + ts[0].clientY - startY;
  }} else if (ts.length === 2) {{
    const rect = wrap.getBoundingClientRect();
    const d = touchDist(ts);
    const ratio = d / pinchDist;
    const ns = Math.max(0.2, Math.min(4, pinchScale * ratio));
    const [mx, my] = touchMid(ts, rect);
    tx = mx - (mx - pinchTx) * ns / pinchScale;
    ty = my - (my - pinchTy) * ns / pinchScale;
    scale = ns;
  }}
  applyTransform();
}}, {{ passive: false }});

wrap.addEventListener('touchend', e => {{
  if (e.touches.length === 0) {{
    const touch = e.changedTouches[0];
    const dx = touch.clientX - startX;
    const dy = touch.clientY - startY;
    // 移动小于 10px 视为点击，手动触发 showDetail
    if (dragging && Math.abs(dx) < 10 && Math.abs(dy) < 10) {{
      const el = document.elementFromPoint(touch.clientX, touch.clientY);
      const node = el && el.closest('.node');
      if (node) {{
        const m = (node.getAttribute('onclick') || '').match(/showDetail[(]'(.+?)'[)]/);
        if (m) showDetail(m[1]);
      }}
    }}
    dragging = false;
  }}
}});
</script>
</body>
</html>'''

# ── 入口 ──────────────────────────────────────────────────────────

def main():
    print("📖 正在读取人物档案...")
    people = load_people()
    print(f"   已加载 {len(people)} 位家族成员")

    print("🔨 正在生成树形图网页...")
    html = generate(people)
    OUTPUT.write_text(html, encoding="utf-8")

    print(f"""
✅ 生成完成！

   文件路径：{OUTPUT}

📱 微信群分享方式：
   ① 将「家谱网页.html」发送到微信群
   ② 群成员点击文件 → 选择「用浏览器打开」
   ③ 拖拽移动、双指缩放查看，点击节点查看详情

🔗 也可上传到网盘后分享链接（无需安装任何软件）
""")

if __name__ == "__main__":
    main()
