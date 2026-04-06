#!/usr/bin/env python3
"""
根据 JSON 家族数据重建 People/*.md 文件
"""
import json
from pathlib import Path
from collections import defaultdict

PEOPLE_DIR = Path(__file__).parent.parent / "People"

FAMILY_JSON = r"""
{
  "name": "杜如松",
  "generation": "田",
  "children": [
    {
      "name": "杜好仁",
      "generation": "绪",
      "children": [
        {
          "name": "杜诗凡",
          "generation": "远",
          "children": [
            {
              "name": "杜继武",
              "generation": "祥",
              "children": [
                { "name": "杜文杰", "generation": "开" },
                {
                  "name": "杜文峰",
                  "generation": "开",
                  "children": [{ "name": "杜奥翔", "generation": "世" }]
                },
                {
                  "name": "杜文彬",
                  "generation": "开",
                  "children": [
                    { "name": "杜秋润", "generation": "世" },
                    { "name": "杜雨润", "generation": "世" }
                  ]
                }
              ]
            },
            {
              "name": "杜继文",
              "generation": "祥",
              "children": [
                {
                  "name": "杜文坡",
                  "generation": "开",
                  "children": [{ "name": "杜雨辰", "generation": "世" }]
                }
              ]
            },
            {
              "name": "杜继双",
              "generation": "祥",
              "children": [
                {
                  "name": "杜文涛",
                  "generation": "开",
                  "children": [{ "name": "杜尚哲", "generation": "世" }]
                },
                {
                  "name": "杜文辉",
                  "generation": "开",
                  "children": [
                    { "name": "杜大多", "generation": "世" },
                    { "name": "杜二多", "generation": "世" }
                  ]
                }
              ]
            },
            {
              "name": "杜继全",
              "generation": "祥",
              "children": [
                {
                  "name": "杜文凯",
                  "generation": "开",
                  "children": [{ "name": "杜科举", "generation": "世" }]
                },
                { "name": "杜文明", "generation": "开" }
              ]
            }
          ]
        }
      ]
    },
    {
      "name": "杜好贤",
      "generation": "绪",
      "children": [
        {
          "name": "杜诗豪",
          "generation": "远",
          "children": [
            {
              "name": "杜继民",
              "generation": "祥",
              "children": [
                {
                  "name": "杜文鹏",
                  "generation": "开",
                  "children": [{ "name": "杜龙翔", "generation": "世" }]
                }
              ]
            },
            {
              "name": "杜继田",
              "generation": "祥",
              "children": [
                {
                  "name": "杜康宁",
                  "generation": "开",
                  "children": [{ "name": "杜俊熙", "generation": "世" }]
                },
                {
                  "name": "杜永海",
                  "generation": "开",
                  "children": [{ "name": "杜思麟", "generation": "世" }]
                }
              ]
            },
            {
              "name": "杜继合",
              "generation": "祥",
              "children": [
                {
                  "name": "杜华威",
                  "generation": "开",
                  "children": [{ "name": "杜浩宇", "generation": "世" }]
                },
                {
                  "name": "杜搏威",
                  "generation": "开",
                  "children": [{ "name": "杜浩然", "generation": "世" }]
                }
              ]
            }
          ]
        },
        {
          "name": "杜诗义",
          "generation": "远",
          "children": [
            {
              "name": "杜继俊",
              "generation": "祥",
              "children": [
                { "name": "杜洋", "generation": "开" }
              ]
            }
          ]
        }
      ]
    },
    {
      "name": "杜好林",
      "generation": "绪",
      "children": [
        {
          "name": "杜诗信",
          "generation": "远",
          "children": [
            {
              "name": "杜继安",
              "generation": "祥",
              "children": [
                {
                  "name": "杜新威",
                  "generation": "开",
                  "children": [{ "name": "杜俊宇", "generation": "世" }]
                },
                {
                  "name": "杜新鹏",
                  "generation": "开",
                  "children": [{ "name": "杜宇晗", "generation": "世" }]
                },
                {
                  "name": "杜新辉",
                  "generation": "开",
                  "children": [{ "name": "杜宇恒", "generation": "世" }]
                }
              ]
            },
            {
              "name": "杜继恩",
              "generation": "祥",
              "children": [
                {
                  "name": "杜志伟",
                  "generation": "开",
                  "children": [{ "name": "杜奕辰", "generation": "世" }]
                }
              ]
            },
            {
              "name": "杜继平",
              "generation": "祥",
              "children": [
                { "name": "杜新峰", "generation": "开" }
              ]
            }
          ]
        },
        {
          "name": "杜诗中",
          "generation": "远",
          "children": [
            {
              "name": "杜继军",
              "generation": "祥",
              "children": [
                { "name": "杜晨龙", "generation": "开" }
              ]
            }
          ]
        },
        {
          "name": "杜诗太",
          "generation": "远",
          "children": [
            {
              "name": "杜继亮",
              "generation": "祥",
              "children": [
                { "name": "杜刘威", "generation": "开" },
                { "name": "杜刘阳", "generation": "开" }
              ]
            },
            {
              "name": "杜继明",
              "generation": "祥"
            },
            {
              "name": "杜顺科",
              "generation": "祥",
              "children": [
                { "name": "杜鸣一", "generation": "开" }
              ]
            }
          ]
        }
      ]
    }
  ]
}
"""

# 辈份诗对照：辈字 → (相对世, 绝对世)
GEN_MAP = {
    "田": ("一世", 15),
    "绪": ("二世", 16),
    "远": ("三世", 17),
    "祥": ("四世", 18),
    "开": ("五世", 19),
    "世": ("六世", 20),
}

def traverse(node, parent=None, result=None, siblings_map=None):
    if result is None:
        result = {}
    if siblings_map is None:
        siblings_map = defaultdict(list)

    name = node["name"]
    gen_char = node["generation"]
    rel, abs_gen = GEN_MAP[gen_char]

    children = [c["name"] for c in node.get("children", [])]

    result[name] = {
        "姓名": name,
        "世代": f"{rel}（{abs_gen}世，辈字：{gen_char}）",
        "父亲": parent or "",
        "子女": children,
    }

    if parent:
        siblings_map[parent].append(name)

    for child in node.get("children", []):
        traverse(child, parent=name, result=result, siblings_map=siblings_map)

    return result, siblings_map

def write_md(name, info, siblings):
    father = info["父亲"]
    children = info["子女"]

    def yaml_list(items):
        if not items:
            return "  []"
        return "\n".join(f'  - "[[{i}]]"' for i in items)

    father_yaml = f'"[[{father}]]"' if father else ""
    content = f"""---
姓名: {name}
性别: 男
出生年:
卒年:
世代: {info['世代']}
籍贯:
父亲: {father_yaml}
母亲:
配偶: []
子女:
{yaml_list(children)}
兄弟姐妹:
{yaml_list(siblings)}
备注:
---

# {name}

## 基本信息

| 项目 | 内容 |
|------|------|
| 姓名 | {name} |
| 世代 | {info['世代']} |

## 家庭关系

### 父母
{"- 父：[[" + father + "]]" if father else "（无记录）"}

### 子女
{"（无）" if not children else chr(10).join("- [[" + c + "]]" for c in children)}

### 兄弟姐妹
{"（无）" if not siblings else chr(10).join("- [[" + s + "]]" for s in siblings)}
"""
    (PEOPLE_DIR / f"{name}.md").write_text(content, encoding="utf-8")
    print(f"  ✓ {name}  {info['世代']}")

def main():
    data = json.loads(FAMILY_JSON)
    people, siblings_map = traverse(data)

    # 删除旧文件（处理改名：如 杜文锋→杜文峰）
    new_names = set(people.keys())
    for old_file in PEOPLE_DIR.glob("*.md"):
        if old_file.stem not in new_names:
            print(f"  🗑  删除旧文件：{old_file.name}")
            old_file.unlink()

    print(f"共 {len(people)} 位成员，开始写入 People/\n")
    for name, info in people.items():
        father = info["父亲"]
        sibs = [s for s in siblings_map.get(father, []) if s != name] if father else []
        write_md(name, info, sibs)

    print(f"\n✅ 完成！共写入 {len(people)} 个文件")

if __name__ == "__main__":
    main()
