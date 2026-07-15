#!/usr/bin/env python3
# Build the Coolizi backlink task board (team posts these manually). Reads bl_<geo>.json (18 articles),
# emits a self-contained dark dashboard-style page with copy buttons + posted-status tracking.
import os, json, html as _html, re

SRC = "/tmp/claude-0/-root-workspace/527f57eb-a5e9-46ec-8dda-978b695d9d0f/scratchpad"
OUT = os.path.dirname(os.path.abspath(__file__))
GEOS = [("en","🇬🇧","UK · Ireland","https://trycoolizi.com/en/"),
        ("de","🇩🇪","DE · AT · CH","https://trycoolizi.com/de/"),
        ("fr","🇫🇷","France · BE","https://trycoolizi.com/fr/"),
        ("it","🇮🇹","Italy","https://trycoolizi.com/it/"),
        ("es","🇪🇸","Spain","https://trycoolizi.com/es/"),
        ("nl","🇳🇱","Netherlands","https://trycoolizi.com/nl/")]

def load(geo):
    with open(os.path.join(SRC, f"bl_{geo}.json"), encoding="utf-8") as f:
        arr = json.load(f)
    for a in arr:  # unescape any HTML entities that survived transport
        a["title"]=_html.unescape(a["title"]); a["author"]=_html.unescape(a["author"])
        a["body"]=_html.unescape(a["body"])
        for l in a["links"]:
            l["anchor"]=_html.unescape(l["anchor"])
    return arr

def plain(bodyhtml):  # article body -> clean plain text (paragraphs kept, tags stripped) for pasting
    t=re.sub(r"</p\s*>","\n\n",bodyhtml,flags=re.I)
    t=re.sub(r"<[^>]+>","",t)
    return _html.unescape(t).strip()

def jesc(s): return json.dumps(s)  # safe JS string literal

CARDS=[]; NAV=[]; SUMMARY={"Google Sites":[True,0],"Medium":[False,0],"Tumblr":[False,0]}
for geo,flag,name,target in GEOS:
    arr=load(geo); NAV.append(f'<a href="#{geo}">{flag} {name.split(" ")[0]}</a>')
    cards=""
    for i,a in enumerate(arr):
        plat=a["platform"]; SUMMARY.setdefault(plat,[a["dofollow"],0]); SUMMARY[plat][1]+=1
        df='<span class="tag df">dofollow</span>' if a["dofollow"] else '<span class="tag nf">nofollow</span>'
        body_words=len(plain(a["body"]).split())
        _pd=plain(a["body"]).replace("\n"," ")
        desc=(_pd[:150].rsplit(" ",1)[0]+"…") if len(_pd)>150 else _pd
        imgfile=["coolizi-hero.webp","hot-summer.webp","cool-bedroom.webp"][i%3]
        imgurl="https://melvingoodman7507.github.io/coolizi-backlinks/img/"+imgfile
        links="".join(
            f'<tr><td class="anc">{_html.escape(l["anchor"])}<button class="mini" data-copy={jesc(l["anchor"])}>copy phrase</button></td>'
            f'<td class="url"><code>{_html.escape(l["target"])}</code><button class="mini" data-copy={jesc(l["target"])}>copy URL</button></td></tr>'
            for l in a["links"])
        cid=f"{geo}-{i}"
        cards+=f'''
        <div class="art" id="art-{cid}">
          <div class="ahead">
            <div class="pmeta"><span class="plat">{_html.escape(plat)}</span>{df}<span class="wc">~{body_words} words</span></div>
            <label class="done"><input type="checkbox" data-status="{cid}"> Posted</label>
          </div>
          <div class="trow"><div class="ttl">{_html.escape(a["title"])}</div><button class="mini" data-copy={jesc(a["title"])}>copy title</button></div>
          <div class="byl">by <b>{_html.escape(a["author"])}</b> <span class="hint">(pen name — use a fresh geo-matched account, don't reuse across platforms)</span></div>
          <div class="mdesc"><b>Meta description / excerpt:</b> {_html.escape(desc)} <button class="mini" data-copy={jesc(desc)}>copy</button></div>
          <div class="imgblock"><img src="{imgurl}" alt="" loading="lazy"><div class="imgc"><div class="il">Suggested image</div><a class="mini" href="{imgurl}" download>⬇ download</a><button class="mini" data-copy={jesc(imgurl)}>copy image URL</button></div></div>
          <div class="body">{a["body"]}</div>
          <div class="actions"><button class="cbtn" data-copy={jesc(plain(a["body"]))}>📋 Copy article text</button></div>
          <table class="links"><thead><tr><th>Link this phrase…</th><th>…to this URL</th></tr></thead><tbody>{links}</tbody></table>
        </div>'''
    CARDS.append(f'<section class="geo" id="{geo}"><h2>{flag} {name} <span class="gt">→ {target}</span></h2>{cards}</section>')

sumrows="".join(f'<tr><td>{p}</td><td>{"✓ dofollow" if v[0] else "nofollow"}</td><td>{v[1]}</td><td>1 per geo × 6</td></tr>' for p,v in SUMMARY.items())

HTML=f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>Coolizi · Backlink Task Board</title>
<style>
:root{{--bg:#080b12;--card:#121927;--card2:#0e1522;--line:#243046;--txt:#e6ecf6;--mut:#8595ad;--acc:#22d3a8;--acc2:#3b9dff;--good:#34d399;--warn:#ffb020;--red:#ff6b57}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(1000px 480px at 84% -8%,rgba(34,211,168,.10),transparent),var(--bg);color:var(--txt);font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}}
.wrap{{max-width:900px;margin:0 auto;padding:24px 18px 80px}}
a{{color:var(--acc2);text-decoration:none}}
h1{{font-size:25px;margin:2px 0 2px;letter-spacing:-.02em}}
.sub{{color:var(--mut);font-size:13.5px;margin:2px 0 18px}}
.nav{{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;gap:7px;padding:10px 0;background:linear-gradient(var(--bg),rgba(8,11,18,.85));backdrop-filter:blur(6px);margin-bottom:8px}}
.nav a{{font-size:13px;font-weight:600;color:var(--mut);padding:6px 12px;border-radius:9px;border:1px solid var(--line);background:var(--card)}}
.nav a:hover{{color:var(--txt);border-color:var(--acc)}}
.panel{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:14px 0}}
.panel h3{{margin:0 0 10px;font-size:15px;color:var(--acc)}}
.goal{{border-left:3px solid var(--acc)}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}
th,td{{text-align:left;padding:8px 8px;border-bottom:1px solid var(--line)}}
th{{color:var(--mut);font-size:11px;text-transform:uppercase;letter-spacing:.5px}}
tr:last-child td{{border-bottom:0}}
ul{{margin:6px 0;padding-left:20px}}li{{margin:4px 0}}
.rules li b{{color:var(--txt)}}
.how{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}}@media(max-width:720px){{.how{{grid-template-columns:1fr}}}}
.how .h{{background:var(--card2);border:1px solid var(--line);border-radius:12px;padding:12px 14px}}
.how .h b{{color:var(--acc2)}} .how .h ol{{margin:8px 0 0;padding-left:18px;font-size:13px;color:var(--mut)}}
.geo{{margin-top:26px}}
.geo>h2{{font-size:19px;border-bottom:1px solid var(--line);padding-bottom:8px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
.geo>h2 .gt{{font-size:12px;color:var(--mut);font-weight:400}}
.art{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:14px 0}}
.ahead{{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:8px}}
.pmeta{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
.plat{{font-weight:800;font-size:13px;background:rgba(59,157,255,.12);color:var(--acc2);padding:3px 10px;border-radius:8px}}
.tag{{font-size:10.5px;font-weight:700;padding:2px 8px;border-radius:20px}}
.tag.df{{background:rgba(52,211,153,.15);color:var(--good)}}.tag.nf{{background:rgba(133,149,173,.15);color:var(--mut)}}
.wc{{color:var(--mut);font-size:11.5px}}
.done{{font-size:12.5px;color:var(--mut);cursor:pointer;user-select:none}}.done input{{vertical-align:-1px;margin-right:4px}}
.art.posted{{opacity:.55}}.art.posted .body{{filter:grayscale(.3)}}
.trow{{display:flex;align-items:flex-start;gap:10px;margin:6px 0 2px}}
.ttl{{font-size:17px;font-weight:700;line-height:1.3;flex:1}}
.byl{{color:var(--mut);font-size:12.5px;margin-bottom:10px}}.byl .hint{{color:#5f7186;font-style:italic}}
.body{{background:var(--card2);border:1px solid var(--line);border-radius:10px;padding:12px 15px;font-size:14px;max-height:230px;overflow:auto}}
.body p{{margin:0 0 10px}}.body p:last-child{{margin:0}}.body a{{color:var(--acc);text-decoration:underline}}
.mdesc{{background:var(--card2);border:1px solid var(--line);border-radius:9px;padding:9px 12px;font-size:12.5px;color:var(--mut);margin:0 0 10px}}.mdesc b{{color:var(--txt)}}
.imgblock{{display:flex;gap:12px;align-items:center;background:var(--card2);border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin:0 0 10px}}
.imgblock img{{width:120px;height:80px;object-fit:cover;border-radius:8px;flex:0 0 auto}}
.imgc{{display:flex;flex-direction:column;gap:6px;align-items:flex-start}}.imgc .il{{font-size:12px;color:var(--mut)}}.imgc .mini{{margin-left:0}}
.actions{{margin:10px 0 6px}}
.cbtn{{background:linear-gradient(135deg,var(--acc),#12a98a);color:#04241d;border:0;border-radius:9px;padding:9px 16px;font-weight:700;font-size:13px;cursor:pointer}}
.cbtn:hover{{filter:brightness(1.08)}}
.mini{{background:var(--card2);border:1px solid var(--line);color:var(--mut);border-radius:7px;padding:3px 9px;font-size:11px;cursor:pointer;margin-left:8px;white-space:nowrap}}
.mini:hover{{color:var(--txt);border-color:var(--acc)}}
.links{{margin-top:12px}}.links td{{vertical-align:top}}.links .anc{{width:55%}}.links .url code{{color:var(--acc);font-size:12px;word-break:break-all}}
.copied{{color:var(--good)!important;border-color:var(--good)!important}}
.foot{{color:var(--mut);font-size:12px;margin-top:34px;border-top:1px solid var(--line);padding-top:14px}}
.prog{{font-weight:700;color:var(--acc)}}
</style></head><body><div class="wrap">
<h1>❄️ Coolizi — Backlink Task Board</h1>
<div class="sub">18 ready-to-post articles · 6 geos × 3 platforms · target = the trycoolizi.com review pages · <span class="prog" id="prog">0/18 posted</span></div>

<div class="panel goal"><h3>🎯 What we're doing &amp; why</h3>
We're building backlinks to the <b>Coolizi review pages</b> (<code>trycoolizi.com/{{geo}}/</code>) to push them higher in Google for Coolizi searches. More ranking → more visitors on those pages → they click through to the CoolJet offer. <b>Every article is about Coolizi and links to the Coolizi review page</b> (not CoolJet directly — that's on purpose; the review page does the converting). Post them manually, spread out, from the right country.</div>

<div class="nav">{"".join(NAV)}</div>

<div class="panel"><h3>📋 This batch</h3>
<table><thead><tr><th>Platform</th><th>Link type</th><th>Articles</th><th>Spread</th></tr></thead><tbody>{sumrows}</tbody></table>
<p style="color:var(--mut);font-size:12.5px;margin:10px 0 0">Run out and want more? Rewrite the title + first paragraph and re-post to another platform: <b>Substack</b> or WordPress.com. <b>⚠ Skip Blogger</b> — it's bot-walled (phone/verification wall we couldn't get past). Telegraph, Write.as and Rentry are already covered automatically (see the <a href="posted.html">posted list</a>). Never post the same text twice.</p></div>

<div class="panel rules"><h3>✅ Rules (read once, follow every time)</h3><ul>
<li><b>1 article = 1 platform.</b> Never post the same text twice — it gets filtered as duplicate.</li>
<li><b>1 account = 1 country IP.</b> Post each geo from a <b>residential IP in that country</b> (use the Gonzo residential proxy, matched to the geo). Never log into the same account from two countries.</li>
<li><b>Fresh geo-matched persona per post.</b> Use the pen name given (or a similar local name). Don't reuse one account across platforms.</li>
<li><b>Exactly 2 links per article</b>, already written in. Keep the anchor text <b>as-is</b> — they're varied on purpose (don't make them all identical, and never "click here").</li>
<li><b>Drip, don't blast.</b> Max 2–3 posts per day across the whole batch. Spread over ~a week.</li>
<li><b>Always PUBLIC + indexable.</b> Do NOT tick any "hide from search engines" box — a backlink Google can't see is worthless.</li>
<li><b>Match the language.</b> German article → German account/IP only, etc.</li>
<li><b>Add the suggested image.</b> Every article has a suggested image below it — download it and upload it into your post. Articles with an image look real and rank better. One image per article; don't reuse the same image twice on the same platform.</li>
<li><b>Verify + screenshot.</b> After posting, open the live URL in a private window, confirm the links work, screenshot it, and tick "Posted" here.</li>
</ul></div>

<div class="panel"><h3>🛠️ How to post (per platform)</h3><div class="how">
<div class="h"><b>Google Sites</b> <span class="tag df">dofollow</span><ol><li>sites.google.com → blank site</li><li>Paste the title + article text</li><li>Highlight the anchor phrase → <b>Insert → Link</b> → paste the URL</li><li>Publish → make it public</li></ol></div>
<div class="h"><b>Medium</b> <span class="tag nf">nofollow</span><ol><li>New story</li><li>Paste title + text</li><li>Highlight phrase → <b>Ctrl/Cmd+K</b> → paste URL → Enter</li><li>Publish (public)</li></ol></div>
<div class="h"><b>Tumblr</b> <span class="tag nf">nofollow</span><ol><li>New text post</li><li>Paste title + text</li><li>Highlight phrase → link icon → paste URL</li><li>Post (public, allow indexing)</li></ol></div>
<div class="h"><b>Substack</b> <span class="tag df">dofollow</span><ol><li>substack.com → free publication (email only, <b>no phone</b>)</li><li>⚠ Use <b>New post → Text</b> (full-page editor) — <b>NOT</b> the "What's on your mind?" <b>Notes</b> box (Notes can't add real links). Desktop web only.</li><li>Paste the title + article text</li><li><b>Highlight the anchor phrase first</b>, then <b>Ctrl/Cmd+K</b> (or the 🔗 that pops up) → paste URL → Enter</li><li>Publish · audience = <b>Everyone</b></li></ol></div>
</div><p style="color:var(--mut);font-size:12px;margin:12px 0 0">nofollow links still count: they drive real referral clicks and make the backlink profile look natural. Keep a healthy mix.</p></div>

{"".join(CARDS)}

<div class="foot">Coolizi backlink board · articles are honest editorial / buyer-guide pieces (no fake "verified purchase" reviews or invented ratings — keeps the links safe and Google-friendly). Tick "Posted" as you go; progress saves in your browser. Questions → ping the team lead.</div>
</div>
<script>
(function(){{
  function flash(b){{var t=b.textContent;b.classList.add("copied");b.textContent="Copied ✓";setTimeout(function(){{b.classList.remove("copied");b.textContent=t;}},1300);}}
  function copy(text,b){{
    if(navigator.clipboard&&navigator.clipboard.writeText){{navigator.clipboard.writeText(text).then(function(){{flash(b);}},function(){{fallback(text,b);}});}}
    else fallback(text,b);
  }}
  function fallback(text,b){{var ta=document.createElement("textarea");ta.value=text;ta.style.position="fixed";ta.style.opacity="0";document.body.appendChild(ta);ta.focus();ta.select();try{{document.execCommand("copy");flash(b);}}catch(e){{}}document.body.removeChild(ta);}}
  document.querySelectorAll("[data-copy]").forEach(function(b){{b.addEventListener("click",function(){{copy(b.getAttribute("data-copy"),b);}});}});
  // posted-status tracking (localStorage)
  var total=document.querySelectorAll("[data-status]").length, prog=document.getElementById("prog");
  function upd(){{var n=document.querySelectorAll("[data-status]:checked").length;prog.textContent=n+"/"+total+" posted";}}
  document.querySelectorAll("[data-status]").forEach(function(c){{
    var k="czbl_"+c.getAttribute("data-status");
    try{{if(localStorage.getItem(k)==="1"){{c.checked=true;c.closest(".art").classList.add("posted");}}}}catch(e){{}}
    c.addEventListener("change",function(){{try{{localStorage.setItem(k,c.checked?"1":"0");}}catch(e){{}}c.closest(".art").classList.toggle("posted",c.checked);upd();}});
  }});
  upd();
}})();
</script></body></html>'''

with open(os.path.join(OUT,"index.html"),"w",encoding="utf-8") as f:
    f.write(HTML)
print("wrote index.html", len(HTML), "bytes ·", sum(v[1] for v in SUMMARY.values()), "articles")
