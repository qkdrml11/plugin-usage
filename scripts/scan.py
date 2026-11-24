import json, os, re, sys, time, glob
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 30
home = os.path.expanduser("~")
LOCAL = os.environ.get("LOCALAPPDATA", os.path.join(home, "AppData", "Local"))
cut = time.time() - DAYS * 86400

# 1) installed plugins (desktop app)
plugins = {}
for man in glob.glob(os.path.join(LOCAL, "Claude-Data", "*", "rpm", "*", "*", "manifest.json")):
    base = os.path.dirname(man)
    for p in json.load(open(man, encoding="utf-8")).get("plugins", []):
        d = os.path.join(base, p["id"])
        pj = os.path.join(d, ".claude-plugin", "plugin.json")
        name = json.load(open(pj, encoding="utf-8")).get("name") if os.path.exists(pj) else p["displayName"]
        skills = set()
        for sub in ("skills", "commands", "agents"):
            sd = os.path.join(d, sub)
            if os.path.isdir(sd):
                skills |= {os.path.splitext(x)[0] for x in os.listdir(sd)}
        if os.path.exists(os.path.join(d, "SKILL.md")) or not skills:
            skills.add(name)
        plugins[name] = dict(id=p["id"], display=p["displayName"], skills=skills,
                             hooks=os.path.isdir(os.path.join(d, "hooks")),
                             mcp=os.path.exists(os.path.join(d, ".mcp.json")), uses=0, last=None)

# 2) transcripts from last N days
files = []
for root in [os.path.join(home, ".claude", "projects"), os.path.join(LOCAL, "Claude-Data")]:
    for dp, _, fs in os.walk(root):
        if "rpm" in dp.split(os.sep): continue
        files += [os.path.join(dp, f) for f in fs if f.endswith(".jsonl")]
def _mt(f):
    try: return os.path.getmtime(f)
    except OSError: return 0
files = [f for f in files if _mt(f) >= cut]

def hit(pname, ts):
    p = plugins[pname]; p["uses"] += 1
    if ts and (p["last"] is None or ts > p["last"]): p["last"] = ts

for f in files:
    try: fh = open(f, encoding="utf-8", errors="ignore")
    except OSError: continue
    for line in fh:
        if '"tool_use"' not in line and "command-name" not in line: continue
        try: o = json.loads(line)
        except Exception: continue
        ts = (o.get("timestamp") or "")[:10]
        c = (o.get("message") or {}).get("content")
        names = []
        if isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    n = b.get("name", ""); inp = b.get("input") or {}
                    if n == "Skill": names.append(("skill", str(inp.get("skill", ""))))
                    elif n.startswith("mcp__plugin_"): names.append(("mcp", n.split("__")[1][len("plugin_"):].split("_")[0]))
        elif isinstance(c, str):
            for m in re.findall(r"<command-name>/?([^<]+)</command-name>", c): names.append(("skill", m))
        for kind, v in names:
            for pn, p in plugins.items():
                if kind == "mcp" and v == pn: hit(pn, ts)
                elif kind == "skill":
                    pre, _, s = v.rpartition(":")
                    if (pre == pn and (s in p["skills"] or s == pn)) or (not pre and v in p["skills"]): hit(pn, ts)

rows = sorted(plugins.items(), key=lambda x: -x[1]["uses"])
dates = sorted(time.strftime("%Y-%m-%d", time.localtime(_mt(f))) for f in files)
if "--json" in sys.argv:
    print(json.dumps({"days": DAYS, "transcripts": len(files), "plugins": [dict(name=k, display=v["display"], uses=v["uses"], last=v["last"]) for k, v in rows]}, ensure_ascii=False, indent=1))
    sys.exit()
out = [f"## 플러그인 사용 내역 (최근 {DAYS}일)", "",
       f"대화 기록 {len(files)}개 확인" + (f" · 가장 오래된 기록 {dates[0]}" if dates else ""), "",
       "| 플러그인 | 사용 횟수 | 마지막 사용 | 판단 |", "|---|---|---|---|"]
for k, v in rows:
    tags = [t for t, on in (("훅", v["hooks"]), ("MCP", v["mcp"])) if on]
    name = v["display"] + (f" ({', '.join(tags)})" if tags else "")
    out.append(f"| {name} | {v['uses']} | {v['last'] or '-'} | {'유지' if v['uses'] else '삭제 후보'} |")
unused = [v["display"] for _, v in rows if not v["uses"]]
out += ["", f"**삭제 후보 {len(unused)}개**: " + (", ".join(unused) if unused else "없음"), "",
        "- 이 PC의 Claude Code 기록만 셉니다. claude.ai 웹 채팅·Cowork에서 쓴 건 안 잡혀요.",
        "- 삭제는 Claude 앱의 플러그인 관리 화면에서 직접 해주세요."]
if dates and dates[0] > time.strftime("%Y-%m-%d", time.localtime(cut + 86400)):
    out.append(f"- 기록이 {DAYS}일 치보다 짧아요({dates[0]}부터). 결과를 감안해서 보세요.")
print(chr(10).join(out))
