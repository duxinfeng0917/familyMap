#!/bin/bash
# 一键发布家谱更新到网站
# 用法：bash tools/发布更新.sh "更新了谁的什么信息"

cd "$(dirname "$0")/.."

MSG="${1:-更新家谱信息}"

git add People/ tools/生成家谱网页.py
git commit -m "$MSG" 2>/dev/null || { echo "没有检测到修改，无需发布。"; exit 0; }
git push

echo ""
echo "✅ 已推送，GitHub 正在自动重新生成网页（约1分钟后生效）"
echo "   网页地址：https://duxinfeng0917.github.io/familyMap/"
