#!/bin/zsh
# Produce web-sized derivatives of every archived image referenced by projects/posts.
cd /Users/mikebundy/www/stevetalkowski
python3 - <<'PY' > /tmp/imglist.txt
import json
p=json.load(open('archive/projects.json')); s=set()
for v in p.values():
    for i in v['items']:
        if i.get('file'): s.add(i['file'])
for post in json.load(open('archive/posts.json')):
    if post.get('image'): s.add(post['image'])
for v in json.load(open('archive/images/manifest.json')).values():
    if v.get('file') and 'blog' in str(v.get('page','')): s.add(v['file'])
print("\n".join(sorted(s)))
PY
n=0
while read f; do
  [ -f "archive/$f" ] || continue
  b=$(basename "$f"); ext="${b##*.}"; base="${b%.*}"
  lower=$(echo "$ext" | tr 'A-Z' 'a-z')
  if [ "$lower" = "png" ]; then fmt=png; out="$base.png"; else fmt=jpeg; out="$base.jpg"; fi
  [ -f "site/assets/img/full/$out" ] || sips -Z 1800 -s format $fmt -s formatOptions 82 "archive/$f" --out "site/assets/img/full/$out" >/dev/null 2>&1
  [ -f "site/assets/img/thumb/$out" ] || sips -Z 720 -s format $fmt -s formatOptions 78 "archive/$f" --out "site/assets/img/thumb/$out" >/dev/null 2>&1
  n=$((n+1))
done < /tmp/imglist.txt
echo "optimized $n images"; du -sh site/assets/img/full site/assets/img/thumb
