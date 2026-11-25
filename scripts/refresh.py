"""Expand the catalog from explicit Crafting Metals labels, retaining the starter on failures.
Requires requests and beautifulsoup4. Run from any directory.
"""
import json,re,time,sys
from pathlib import Path
from urllib.parse import urljoin,quote
from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup
CAT=Path(__file__).resolve().parents[1]/'catalog.js'
COSTS={30:'Common',60:'Rare',400:'Epic',800:'Epic',1200:'Legendary',2400:'Legendary',120:'Rare'}
LEGENDS='Alter|Ash|Axle|Ballistic|Bangalore|Bloodhound|Catalyst|Caustic|Conduit|Crypto|Fuse|Gibraltar|Horizon|Lifeline|Loba|Mad Maggie|Mirage|Newcastle|Octane|Pathfinder|Rampart|Revenant|Seer|Sparrow|Valkyrie|Vantage|Wattson|Wraith'.split('|')
WEAPONS='HAVOC Rifle|VK-47 Flatline|Hemlok Burst AR|R-301 Carbine|Nemesis Burst AR|Alternator SMG|Prowler Burst PDW|R-99 SMG|Volt SMG|C.A.R. SMG|Devotion LMG|L-STAR EMG|M600 Spitfire|Rampage LMG|G7 Scout|Triple Take|30-30 Repeater|Bocek Compound Bow|Charge Rifle|Longbow DMR|Kraber .50-Cal Sniper|Sentinel|EVA-8 Auto|Mastiff Shotgun|Mozambique Shotgun|Peacekeeper|RE-45 Auto|P2020|Wingman'.split('|')
SESSION=requests.Session()
SESSION.headers['User-Agent']='ApexCraftFanCatalog/1.0 (public fan catalog; reads crafting labels)'
def fetch(url):
 r=SESSION.get(url,timeout=20);r.raise_for_status();return BeautifulSoup(r.text,'html.parser')
def clean(s):return re.sub(r'\s+',' ',s).strip()
def slug(s):return re.sub(r'[^a-z0-9]+','-',s.lower().replace("'",'')).strip('-')
def number(s):
 m=re.search(r'(?<![\d,])(2,400|2400|1,200|1200|800|400|120|60|30)(?![\d,])',s)
 return int(m.group().replace(',','')) if m else None
def text(el):return clean(el.get_text(' ',strip=True))
def imgurl(img,base):
 src=img.get('data-src') or img.get('data-lazy-src') or img.get('src') or ''
 return urljoin(base,src) if src and not src.startswith('data:') else ''
# Classification is based on source section, never rarity, price or artwork.
TYPES={'skins':'Skin','legend skins':'Skin','weapon skins':'Skin','banner frames':'Banner Frame','banner poses':'Banner Pose','holosprays':'Holospray','finishers':'Finisher','emotes':'Emote','skydive emotes':'Skydive Emote','trackers':'Tracker','stat trackers':'Tracker','charms':'Charm','weapon charms':'Charm','stickers':'Sticker'}
def record(owner,kind,name,cost,image,source,themed=False,cosmetic='Skin'):
 return dict(owner=owner,kind=kind,cosmetic=cosmetic,name=name,cost=cost,rarity=COSTS[cost],image=image,fallback='',source=source,themed=themed)
def identity(r):return (r['kind'],r['owner'],r['cosmetic'],r['name'].casefold())
def legacy_type(r):
 if r.get('cosmetic') in set(TYPES.values()):return r['cosmetic']
 if r.get('verifiedAt') and r.get('source','').startswith('https://apexdb.gg/skins/'):return 'Skin'
 return None
def classify_section(stack,kind):
 for _,heading in reversed(stack):
  if heading in ('legendary','epic','rare','common'):continue
  c=TYPES.get(heading)
  if not c:return None
  if kind=='Weapon' and c not in ('Skin','Charm','Sticker'):return None
  return c
 return None
def section_items(soup,kind):
 stack=[]
 for el in soup.find_all(['h2','h3','h4','h5','h6','li','tr','div']):
  if re.fullmatch(r'h[2-6]',el.name):
   level=int(el.name[1]);h=el.select_one('.mw-headline') or el
   heading=re.sub(r'\s*\[edit\]\s*$','',text(h),flags=re.I).strip().casefold()
   stack=[(n,t) for n,t in stack if n<level];stack.append((level,heading));continue
  is_item=el.name=='tr' or 'gallerybox' in el.get('class',[]) or 'wikia-gallery-item' in el.get('class',[])
  if not is_item:continue
  cosmetic=classify_section(stack,kind)
  if cosmetic:yield el,cosmetic
def discover_legends():
 # Discover new Legend pages automatically; fallback roster is only used if discovery fails.
 url='https://apexdb.gg/skins/'
 soup=fetch(url)
 names=[]
 for a in soup.select('a[href]'):
  target=urljoin(url,a['href'])
  m=re.fullmatch(r'https://apexdb\.gg/skins/([a-z0-9-]+)/?',target)
  if not m:continue
  t=text(a)
  n=re.search(r'([A-Za-z][A-Za-z .\'-]*?)\s+skins\b',t,re.I)
  if n:
   name=n[1].strip()
   if name.lower()!='all' and name not in names:names.append(name)
 if not names:raise ValueError('Legend index did not yield categories')
 return names
def apexdb(owner):
 url='https://apexdb.gg/skins/'+slug(owner)+'/'
 soup=fetch(url);out=[]
 # The page explicitly reports how many skins are craftable. Require exact agreement
 # before permitting a category replacement (including removal of noncraftable skins).
 m=re.search(r'([\d,]+)\s+can be crafted with Crafting Metals',text(soup),re.I)
 if not m:raise ValueError('No craftable total on source page')
 expected=int(m[1].replace(',',''))
 for im in soup.select('img[alt]'):
  alt=im.get('alt','');suffix=' '+owner+' skin'
  if not alt.lower().endswith(suffix.lower()):continue
  name=alt[:-len(suffix)].strip();price=None
  for el in list(im.parents)[:5]:
   if el.name in ['main','body','html'] or len([i for i in el.select('img[alt]') if i.get('alt','').lower().endswith(suffix.lower())])!=1:break
   t=text(el);m=re.search(r'(\d[\d,]*)\s+Crafting Metals',t,re.I)
   if m and name.lower() in t.lower():price=int(m[1].replace(',',''));break
  if price not in COSTS:continue
  if re.search(r'collection event|battle pass|legend tokens|store sale',t,re.I):continue
  image=imgurl(im,url)
  if image:out.append(record(owner,'Legend',name,price,image,url,bool(re.search(r'themed event',t,re.I))))
 unique={r['name'].casefold():r for r in out}
 if len(unique)!=expected:raise ValueError(f'Parsed {len(unique)} of {expected} craftable skins')
 return list(unique.values())
def metal_marker(el):
 return bool(re.search(r'crafting[ _-]*(metal|material)',text(el),re.I) or any(re.search(r'crafting[ _-]*(metal|material)',str(i.get('alt',''))+' '+str(i.get('src',''))+' '+str(i.get('title','')),re.I) for i in el.select('img')))
def wiki(owner,kind):
 url='https://apexlegends.wiki.gg/wiki/'+quote(owner.replace(' ','_'))
 try:
  r=SESSION.get('https://apexlegends.wiki.gg/api.php',params={'action':'parse','page':owner,'prop':'text','format':'json','formatversion':2},timeout=20);r.raise_for_status();soup=BeautifulSoup(r.json()['parse']['text'],'html.parser')
 except Exception:soup=fetch(url)
 return parse_wiki(soup,owner,kind,url)
def parse_wiki(soup,owner,kind,url):
 out=[]
 for item,cosmetic in section_items(soup,kind):
  if item.name=='tr':
   cells=item.find_all('td',recursive=False)
   if len(cells)<3:continue
   caption=cells[1];costel=cells[-1];t=text(costel);name=text(caption)
   if not metal_marker(costel):continue
   images=cells[0].select('img')
  else:
   caption=item.select_one('.gallerytext, .lightbox-caption')
   if not caption:continue
   t=text(caption);costel=caption;images=item.select('.thumb img, .gallery-image img, img')
   if not metal_marker(costel):
    group=item.find_parent(['ul','div'],class_=re.compile('gallery',re.I))
    if group is None:continue
    heading=group.find_previous_sibling()
    if heading is None or len(text(heading))>80 or not metal_marker(heading):continue
    costel=heading
   chunks=[clean(x) for x in caption.stripped_strings if clean(x)]
   if not chunks:continue
   name=chunks[0]
  if re.search(r'collection event|battle pass|legend tokens|requires|needs |apex coins|default|reactive',t,re.I):continue
  price=number(text(costel))
  if price not in COSTS or not name or len(name)>100:continue
  name=re.sub(r'\s*\[\d+\]','',name).strip()
  im=next((i for i in images if not re.search(r'crafting|currency|coin|token|icon',str(i.get('alt',''))+' '+str(i.get('src','')),re.I)),None)
  if im is None:continue
  image=imgurl(im,url)
  if image:out.append(record(owner,kind,name,price,image,url,bool(re.search('themed|event',t,re.I)),cosmetic))
 return out
def main():
 old=json.loads(CAT.read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
 now=datetime.now(timezone.utc).replace(microsecond=0).isoformat()
 # Exclude ambiguous legacy records; recover them through typed source checks.
 legacy=[r for r in old['rows'] if legacy_type(r) is None]
 records={}
 for r in old['rows']:
  c=legacy_type(r)
  if c:
   r=dict(r,cosmetic=c);records[identity(r)]=r
 previous={k:dict(r) for k,r in records.items()}
 for r in records.values():r.setdefault('verification','starter' if not r.get('verifiedAt') else 'source')
 old_status=old.get('categories',{})
 statuses=dict(old_status)
 try: discovered=discover_legends()
 except Exception as e:
  print('Legend discovery failed:',e,file=sys.stderr);discovered=[]
 legends=sorted(set(LEGENDS+discovered+[r['owner'] for r in old['rows'] if r['kind']=='Legend']))
 weapons=sorted(set(WEAPONS+[r['owner'] for r in old['rows'] if r['kind']=='Weapon']))
 success=[];errors=[]
 for kind,owners in [('Legend',legends),('Weapon',weapons)]:
  for owner in owners:
   category=kind+'|'+owner;got=[];complete=False
   if kind=='Legend':
    try:got=apexdb(owner);complete=True
    except Exception as e:print(owner,str(e)[:150],file=sys.stderr)
   try:
    wiki_rows=wiki(owner,kind)
    got.extend(r for r in wiki_rows if not complete or r['cosmetic']!='Skin')
   except Exception as e:print(owner,str(e)[:150],file=sys.stderr)
   time.sleep(.4)
   if not complete and not got:
    errors.append(owner);statuses[category]={**statuses.get(category,{}),'status':'unavailable','attemptedAt':now};continue
   success.append(owner)
   keys=set()
   for r in got:
    k=identity(r);keys.add(k)
    prior=previous.get(k)
    r['verifiedAt']=now;r['verification']='source'
    comparable=('cost','rarity','name','image','themed')
    if prior is None:r['change']='new';r['changedAt']=now
    elif any(prior.get(field)!=r.get(field) for field in comparable):r['change']='changed';r['changedAt']=now
    elif prior.get('changedAt'):r['change']=prior.get('change');r['changedAt']=prior['changedAt']
    records[k]=r
   if complete:
    for k in list(records):
     if k[:3]==(kind,owner,'Skin') and k not in keys:del records[k]
   # A partial wiki parse is positive evidence only. Never delete other records.
   statuses[category]={'status':'complete' if complete else 'partial','checkedAt':now,'attemptedAt':now,'count':len(keys)}
   print(owner,len(keys),'complete' if complete else 'partial')
 if not success:print('All source checks failed; preserving typed catalog and excluding ambiguous old rows.',file=sys.stderr)
 removed=[{'owner':r['owner'],'name':r['name'],'kind':r['kind'],'cosmetic':r['cosmetic']} for k,r in previous.items() if k not in records]
 # Preserve recent removals across otherwise unchanged refreshes.
 recent=old.get('recentRemovals',[])
 recent=[r for r in recent if r.get('at','')>=(datetime.now(timezone.utc)-timedelta(days=14)).isoformat()]
 recent.extend(dict(r,at=now) for r in removed)
 result={'updated':now if success else old.get('updated'),'checkedAt':now,'mode':'Community catalog' if success or old.get('mode')=='Community catalog' else 'Starter catalog','coverage':f'{len(success)} of {len(legends)+len(weapons)} categories retrieved this check; {len(errors)} unavailable. Partial and previously saved entries may be outdated. Verify in-game.','schema':2,'legacyExcluded':len(legacy) if legacy else old.get('legacyExcluded',0),'rows':sorted(records.values(),key=lambda r:identity(r)),'categories':statuses,'recentRemovals':recent,'unparsed':errors}
 tmp=CAT.with_suffix('.tmp');tmp.write_text('window.FORGE_CATALOG = '+json.dumps(result,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8');tmp.replace(CAT)
 print('Total:',len(records),'Removed:',len(removed),'Unavailable:',', '.join(errors))
if __name__=='__main__':main()
