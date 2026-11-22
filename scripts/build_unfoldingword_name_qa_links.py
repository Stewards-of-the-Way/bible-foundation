#!/usr/bin/env python3
"""Generate version-pinned SOTW name-to-Q&A links and cross-edition verse checks."""
import argparse, collections, hashlib, json, pathlib, re

DATA=pathlib.Path("data/unfoldingword/v91")
DEST=DATA/"names/qa-links/v1"
ED={"ASV1901":("asv","asv1901"),"KJV1769":("kjv","kjv1769"),"BSB":("bsb","bsb"),"WEBSTER1833":("webster","webster1833")}
PINS={"qa/index.json":"103d4d6c9c11de3418a075482aa9b3bb44e9298f","names/index.json":"e8aba2eb47739f26c02f1f7b7bd4e7098ce7481a"}
ALIASES={
"johnthebaptist":["John the Baptist"],"johntheapostle":["John the apostle","apostle John","John son of Zebedee"],
"jamesbrotherofjesus":["James brother of Jesus","James the brother of Jesus"],
"jamessonofalphaeus":["James son of Alphaeus","James the son of Alphaeus"],
"jamessonofzebedee":["James son of Zebedee","James the son of Zebedee"],
"mary":["Mary the mother of Jesus","Mary, the mother of Jesus"],"marysisterofmartha":["Mary sister of Martha","Mary the sister of Martha"],
"marymagdalene":["Mary Magdalene"],"josephot":["Joseph"],"josephnt":["Joseph"],
"zechariahot":["Zechariah"],"zechariahnt":["Zechariah"],"philip":["Philip"],"philiptheapostle":["Philip"],
"saul":["Saul"],"manasseh":["Manasseh"],"simeon":["Simeon"],
"kingdomofjudah":["kingdom of Judah"],"judea":["Judea"],"thegreatsea":["Great Sea","western sea"]
}
RESTRICT={"josephot":{"GEN","EXO"},"josephnt":{"MAT","LUK"},"zechariahot":{"EZR","NEH","ZEC"},
"zechariahnt":{"LUK"},"philip":{"ACT"},"philiptheapostle":{"MAT","MRK","LUK","JHN"},
"saul":{"1SA","2SA","1CH"},"manasseh":{"GEN","EXO","NUM","DEU","JOS","JDG","1CH"},
"simeon":{"GEN","EXO","NUM","JOS","1CH"},"dan":{"GEN","EXO","NUM","DEU","JOS"}}
CASE={"job","lot","dan","ham","ur","ai","og","asa","gad","eve","eli","amoz","gath"}
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def hashbytes(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def gitblob(p):
 b=p.read_bytes()
 return hashlib.sha1(("blob %d\0"%len(b)).encode()+b).hexdigest()
def emit(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,sort_keys=True,ensure_ascii=False,separators=(",",":"))+"\n",encoding="utf-8")
def aliases(slug,title):
 if slug in ALIASES:return ALIASES[slug]
 a=[]
 for item in title.split(","):
  v=item.strip()
  if not v or "(" in v or ")" in v:continue
  v=re.sub(r"^the\s+","",v,flags=re.I)
  if len(v)<2 or v.lower() in {"the","and","of","a","king","queen","father","mother","son","river","city","lake","sea"}:continue
  a.append(v)
 return list(dict.fromkeys(a))
def targets(t):
 if not isinstance(t,dict):return []
 b,c,v=t.get("book"),t.get("chapter"),t.get("verse")
 end=t.get("endVerse") or v
 if not(isinstance(b,str) and isinstance(c,int) and isinstance(v,int) and isinstance(end,int)
        and 1<=c<=150 and 1<=v<=end<=176):return []
 return [f"{b}.{c}.{n}" for n in range(v,end+1)]
def edition_verses(vendor,rel):
 base=vendor/rel[0]/"data"/rel[1]
 if not base.is_dir():raise RuntimeError("Missing edition repository "+str(base))
 ids=set();chapters=0
 for p in base.glob("*/chapters/*.json"):
  book=load(p)
  if book.get("edition_id") not in ED:raise RuntimeError("Unexpected edition "+str(p))
  if not isinstance(book.get("chapter"),int):raise RuntimeError("Invalid chapter "+str(p))
  chapters+=1
  for verse in book.get("verses",[]):
   vid=verse.get("id")
   if isinstance(vid,str):ids.add(vid)
 if chapters<1000 or len(ids)<30000:raise RuntimeError(f"Incomplete {base} ({chapters} chapters, {len(ids)} verses)")
 return ids,chapters
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--root",default=".")
 ap.add_argument("--vendor",default="vendor/uw-editions")
 args=ap.parse_args()
 root=pathlib.Path(args.root);base=root/DATA;out=root/DEST
 if out.exists() and any(out.iterdir()):raise RuntimeError("Refusing overwrite of nonempty target")
 for name,expected in PINS.items():
  if gitblob(base/name)!=expected:raise RuntimeError("Source pin mismatch "+name)
 qi=load(base/"qa/index.json");ni=load(base/"names/index.json")
 visibility_path=base/"names/review/v1/reader-eligibility.json";vis=load(visibility_path)
 if qi["total"]!=12139 or ni["count"]!=355 or vis["schema"]!="sotw-unfoldingword-name-visibility/1.0.0":
  raise RuntimeError("Schema or source counts changed")
 if vis["source"]["sourceIndexGitBlob"]!=PINS["names/index.json"]:raise RuntimeError("Eligibility pin mismatch")
 ok=set(vis["eligibleIds"]);no=set(vis["excludedIds"]);allnames={n["id"] for n in ni["entries"]}
 if len(ok)!=332 or len(no)!=23 or ok&no or ok|no!=allnames:raise RuntimeError("Inconsistent exclusion coverage")
 qa=[];known=set();bybook=collections.defaultdict(list)
 for b in qi["books"]:
  book=load(base/"qa/books"/(b["book"]+".json"))
  if book["count"]!=b["count"]:raise RuntimeError("Q&A book count mismatch")
  for q in book["records"]:
   if q["id"] in known:raise RuntimeError("Duplicate Q&A")
   known.add(q["id"]);qa.append(q);bybook[q["book"]].append(q)
 if len(qa)!=12139:raise RuntimeError("Incomplete Q&A")
 results=[];used=set();types=collections.Counter()
 for name in ni["entries"]:
  if name["id"] in no:continue
  sl=name["slug"];patterns=[(word,re.compile(r"(?<![\w])"+re.escape(word)+r"(?![\w])",0 if sl in CASE else re.I)) for word in aliases(sl,name["title"])]
  links=[]
  for bk,questions in bybook.items():
   if sl in RESTRICT and bk not in RESTRICT[sl]:continue
   for q in questions:
    qhits=[label for label,rx in patterns if rx.search(q["question"])]
    ahits=[label for label,rx in patterns if rx.search(q["answer"])]
    if not qhits and not ahits:continue
    kind="QUESTION_EXPLICIT" if qhits else "ANSWER_EXPLICIT"
    links.append({"qaId":q["id"],"book":bk,"reference":q["reference"],
      "scriptureTargets":q["scriptureTargets"],"matchType":kind,"matchedName":(qhits or ahits)[0]})
    used.add(q["id"]);types[kind]+=1
  links.sort(key=lambda x:(x["book"],x["scriptureTargets"][0]["chapter"],x["scriptureTargets"][0]["verse"],x["qaId"]))
  results.append({"id":name["id"],"slug":sl,"title":name["title"],"qaCount":len(links),
    "questionExplicitCount":sum(x["matchType"]=="QUESTION_EXPLICIT" for x in links),
    "answerExplicitCount":sum(x["matchType"]=="ANSWER_EXPLICIT" for x in links),
    "path":"by-name/"+sl+".json"})
  emit(out/"by-name"/(sl+".json"),{"schema":"sotw-name-qa-links/1.0.0","sourceNameId":name["id"],
    "title":name["title"],"qaCount":len(links),"links":links,
    "meaning":"Original authored Q&A explicitly mentions this name in question or answer, not a source-asserted identity connection."})
 if len(results)!=332:raise RuntimeError("Excluded articles in output")
 refs=[];unresolved=[];qt=0;name_reference_count=0
 for q in qa:
  for t in q["scriptureTargets"]:
   qt+=1;r=targets(t)
   if not r:unresolved.append({"kind":"QA","id":q["id"],"target":t})
   refs.extend(r)
 if qt!=12141:raise RuntimeError("Q&A references changed")
 for n in ni["entries"]:
  if n["id"] not in ok:continue
  obj=load(base/"names/entries"/(n["slug"]+".json"))
  for r in obj["bibleReferences"]:
   name_reference_count+=1
   found=targets(r.get("scriptureTarget"))
   if not found:unresolved.append({"kind":"NAME","id":n["id"],"label":r.get("label")})
   refs.extend(found)
 unique=sorted(set(refs))
 if len(unique)<5000:raise RuntimeError("Too few verse IDs to audit")
 availability={};exceptions={}
 for name,directory in ED.items():
  have,chapters=edition_verses(root/args.vendor,directory)
  missing=[x for x in unique if x not in have]
  availability[name]={"chaptersInspected":chapters,"publishedVerseIDs":len(have),"checkedTargetIDs":len(unique),
     "availableTargets":len(unique)-len(missing),"unavailableTargets":len(missing)}
  exceptions[name]=missing
 emit(out/"reader-verse-availability.json",{
  "schema":"sotw-v91-name-qa-verse-availability/1.0.0",
  "checkedSource":"Four published SOTW Bible edition chapter JSON collections",
  "editionChecks":availability,"unavailableScopesByEdition":exceptions,"unresolvedSourceReferences":unresolved,
  "consumerRule":"Use translation selected in Reader at click time. Render only resolved canonical BOOK.CHAPTER.VERSE scopes not listed as unavailable in that edition. Missing/invalid availability file must fail closed.",
  "readerRoutes":{"sotw":"/historical-commentary-resources/mobile-bible-sotw/",
       "cgbc":"/historical-commentary-resources/mobile-bible-beta/"},
  "readerQueryKeys":["book","chapter","verse","translation"]})
 counts={"sourceNameArticles":355,"excludedNameArticles":23,"eligibleNameArticles":332,
   "namesWithQALinks":sum(x["qaCount"]>0 for x in results),
   "namesWithoutExplicitQALinks":sum(x["qaCount"]==0 for x in results),
   "sourceQARecords":12139,"distinctRelatedQA":len(used),"relationships":sum(x["qaCount"] for x in results),
   "questionsExplicit":types["QUESTION_EXPLICIT"],"answersExplicit":types["ANSWER_EXPLICIT"],
   "qaScriptureTargets":qt,"nameSourceReferencesChecked":name_reference_count,
   "uniqueVerseIDsChecked":len(unique),"unresolvedSourceReferences":len(unresolved)}
 emit(out/"index.json",{"schema":"sotw-name-qa-index/1.0.0","version":"1","sourceVersions":{"qa":"en_tq v91","names":"en_tw v91"},
   "sourceGitBlobPins":PINS,"eligibilityGitBlob":gitblob(visibility_path),
   "counts":counts,"entries":results,"qaTextIsIndependent":True,
   "excludedNameRecordsNeverIncluded":True,"status":"PUBLISHED_DATA_NOT_READER_UI_INSTALLED"})
 emit(out/"audit.json",{"schema":"sotw-name-qa-links-audit/1.0.0","counts":counts,"editions":availability,
   "unresolvedOriginalSourceReferences":unresolved,"excludedNameIds":sorted(no),
   "unmatchedEligibleNameIds":sorted(x["id"] for x in results if not x["qaCount"]),
   "rule":"Explicit name match only, with aliases and disambiguation for common names. No inferred verse-only identity."})
 (out/"README.md").write_text(
  "# SOTW unfoldingWord v91 People and Places Q&A associations\n\n"
  "Derived navigational associations only; source Q&A and name article wording remain unchanged. "
  "Original Q&A IDs point to qa/books/{BOOK}.json. QUESTION_EXPLICIT is a direct name mention in the question; "
  "ANSWER_EXPLICIT means a direct name mention only in the answer. Do not treat associations as historical proof.\n\n"
  "Before showing any name profile, enforce names/review/v1/reader-eligibility.json. "
  "Its 23 excluded IDs MUST NOT appear in search, profiles, Q&A related-topic links, or recommendations. "
  "Fail closed if eligibility file or source pin mismatches.\n\n"
  "For Scripture links, use canonical book/chapter/verse targets, check reader-verse-availability.json "
  "for the currently selected edition, then form the existing Reader URL using translation at click time. "
  "Never hard-code a Bible translation or substitute a missing verse. Retain source range labels. "
  "This dataset publication does not re-enable the retired People/Places UI.\n",encoding="utf-8")
 files=sorted(x for x in out.rglob("*") if x.is_file() and x.name!="manifest.json")
 emit(out/"manifest.json",{"schema":"sotw-name-qa-links-manifest/1.0.0","counts":counts,
   "editionAvailability":availability,
   "files":[{"path":x.relative_to(out).as_posix(),"sha256":hashbytes(x),"bytes":x.stat().st_size} for x in files]})
 print(json.dumps({"counts":counts,"editions":availability},indent=2))
if __name__=="__main__":main()
