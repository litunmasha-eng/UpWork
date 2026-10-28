import json,sys
t=json.load(open(sys.argv[1]))
words=[];cur=None
for tok,ts in t:
  if tok.startswith(' ') or cur is None:
    if cur: words.append(cur)
    cur={'text':tok.strip(),'start':ts}
  else: cur['text']+=tok
if cur: words.append(cur)
words=[w for w in words if w['text']]
for i,w in enumerate(words):
  w['end']=words[i+1]['start'] if i+1<len(words) else w['start']+0.5
json.dump(words,open(sys.argv[2],'w'),ensure_ascii=False,indent=0)
for w in words: print(f"{w['start']:6.2f} {w['text']}")
