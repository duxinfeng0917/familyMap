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
FORMSPREE_ENDPOINT = ""  # 例如 "https://formspree.io/f/abcdefgh"

# 世代排序表
GEN_ORDER = ["一世","二世","三世","四世","五世","六世","七世","八世","九世","十世"]

# 节点尺寸与间距
BOX_W  = 120   # 节点宽度
BOX_H  = 45    # 节点高度
H_GAP  = 32    # 同代节点水平间距
V_STEP = 140   # 世代中心到中心垂直距离
LEFT_PAD = 80  # 左侧世代标签宽度
TOP_PAD  = 30  # 顶部留白

# 各世代节点颜色 (fill, stroke)
GEN_COLORS = {
    "一世": ("#ffc9c9", "#c92a2a"),
    "二世": ("#a5d8ff", "#1864ab"),
    "三世": ("#b2f2bb", "#2b8a3e"),
    "四世": ("#e9d5ff", "#862e9c"),
    "五世": ("#ffe8cc", "#d4780a"),
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

    # 世代标签（左侧固定列）
    gen_labels = []
    seen_gens = {}
    for name, p in people.items():
        prefix = gen_prefix(p)
        if prefix in seen_gens or prefix not in GEN_ORDER:
            continue
        seen_gens[prefix] = True
        _, y = positions[name]
        label_y = y + BOX_H / 2 + 6
        gen_labels.append(
            f'<text x="{LEFT_PAD // 2}" y="{label_y:.1f}" '
            f'text-anchor="middle" class="gen-lbl">{prefix}</text>'
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
    <div id="fb-wrap" style="margin-top:14px;border-top:1px solid #f0dcc8;padding-top:14px">
      <div style="font-size:.8em;color:#aaa;margin-bottom:8px">如有信息有误，请提交修改建议：</div>
      <form id="fb-form" onsubmit="submitFb(event)">
        <input type="hidden" id="fb-person" name="人物姓名">
        <textarea name="修改建议" required rows="3"
          style="width:100%;border:1px solid #ddd;border-radius:8px;padding:8px;
                 font-size:.85em;resize:vertical;font-family:inherit"
          placeholder="请描述需要修改的内容（如：出生年、子女信息等）…"></textarea>
        <input type="text" name="你的姓名" placeholder="你的姓名（选填）"
          style="width:100%;margin-top:6px;border:1px solid #ddd;border-radius:8px;
                 padding:8px;font-size:.85em;font-family:inherit">
        <button type="submit"
          style="width:100%;margin-top:8px;padding:10px;background:#fff;color:#8b4513;
                 border:1.5px solid #8b4513;border-radius:10px;font-size:.9em;cursor:pointer">
          提交修改建议
        </button>
        <div id="fb-status" style="text-align:center;font-size:.8em;margin-top:6px;color:#666"></div>
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
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;
      background:#f5f0e8;color:#333;display:flex;flex-direction:column;height:100vh;overflow:hidden}}
header{{background:linear-gradient(135deg,#8b4513,#c0722a);color:#fff;
        padding:14px 16px;text-align:center;flex-shrink:0}}
header h1{{font-size:1.6em;letter-spacing:4px;text-shadow:0 1px 4px rgba(0,0,0,.3)}}
header p{{font-size:.75em;margin-top:4px;opacity:.85}}
.poem{{background:#6b2e08;color:#ffd700;text-align:center;padding:7px;
       font-size:.82em;letter-spacing:2px;flex-shrink:0}}
#canvas-wrap{{flex:1;overflow:hidden;position:relative;cursor:grab;touch-action:none}}
#canvas-wrap.dragging{{cursor:grabbing}}
svg#tree{{display:block}}
.edge{{stroke:#aaa;stroke-width:1.5;fill:none}}
.node{{cursor:pointer}}
.node rect{{transition:filter .15s}}
.node:hover rect{{filter:brightness(.9)}}
.node-name{{font-size:15px;font-weight:700;fill:#333;pointer-events:none;
            font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}}
.gen-lbl{{font-size:13px;fill:#888;font-weight:600;
          font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}}
/* 缩放提示 */
.hint{{position:absolute;bottom:12px;right:16px;font-size:.72em;color:#bbb;
       background:rgba(255,255,255,.8);padding:3px 8px;border-radius:6px;pointer-events:none}}
/* Modal */
.overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);
          z-index:200;align-items:center;justify-content:center}}
.overlay.on{{display:flex}}
.modal{{background:#fff;border-radius:18px;padding:24px;width:88%;
        max-width:380px;max-height:82vh;overflow-y:auto;box-shadow:0 8px 32px rgba(0,0,0,.2)}}
.modal-title{{font-size:1.4em;font-weight:700;color:#8b4513;
              border-bottom:2px solid #f0dcc8;padding-bottom:10px;margin-bottom:14px}}
.row{{display:flex;margin-bottom:10px;font-size:.88em}}
.lbl{{color:#aaa;width:72px;flex-shrink:0;padding-top:1px}}
.val{{color:#333;flex:1;line-height:1.6}}
.val a{{color:#8b4513;text-decoration:none;font-weight:600}}
.btn-close{{width:100%;margin-top:18px;padding:11px;background:#8b4513;
            color:#fff;border:none;border-radius:10px;font-size:1em;cursor:pointer}}
.btn-edit{{width:100%;margin-top:10px;padding:11px;background:#fff;color:#8b4513;
           border:1.5px solid #8b4513;border-radius:10px;font-size:1em;cursor:pointer}}
</style>
</head>
<body>

<header>
  <h1>杜氏家谱</h1>
  <p>明洪武元年（约1370年）奉诏迁居开封府繁塔侧云寄桥 &nbsp;·&nbsp; 共 {count} 位成员</p>
</header>
<div class="poem">如峰田绪远 · 祥开世泽长 · 继祖承兆庆 · 勤宗永康昌</div>

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

<div class="overlay" id="overlay" onclick="bgClose(event)">
  <div class="modal">
    <div class="modal-title" id="m-name"></div>
    <div id="m-body"></div>
    {feedback_block}
    <button class="btn-close" onclick="closeModal()">关闭</button>
  </div>
</div>

<script>
const D = {details_json};
{feedback_js}

// ── 详情弹窗 ──
function showDetail(n) {{
  const d = D[n]; if (!d) return;
  document.getElementById('m-name').textContent = d.name;
  document.getElementById('m-body').innerHTML = `
    <div class="row"><span class="lbl">世代</span><span class="val">${{d.gen}}</span></div>
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
{feedback_js}
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
  if (e.touches.length === 0) dragging = false;
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
