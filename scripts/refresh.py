"""Expand the catalog from explicit Crafting Metals labels, retaining the starter on failures.
Requires requests and beautifulsoup4. Run from any directory.
"""
import json,re,time,sys
from pathlib import Path
from urllib.parse import urljoin,quote
from datetime import date
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
def record(owner,kind,name,cost,image,source,themed=False):
 return dict(owner=owner,kind=kind,name=name,cost=cost,rarity=COSTS[cost],image=image,fallback='',source=source,themed=themed)
def apexdb(owner):
 url='https://apexdb.gg/skins/'+slug(owner)+'/'
 soup=fetch(url);out=[]
 for im in soup.select('img[alt]'):
  alt=im.get('alt','');suffix=' '+owner+' skin'
  if not alt.lower().endswith(suffix.lower()):continue
  name=alt[:-len(suffix)].strip();price=None
  for el in list(im.parents)[:5]:
   if el.name in ['main','section','body','html'] or len(el.select('img[alt]'))!=1:break
   t=text(el);m=re.search(r'(\d[\d,]*)\s+Crafting Metals',t,re.I)
   if m and name.lower() in t.lower():price=int(m[1].replace(',',''));break
  if price not in COSTS:continue
  if re.search(r'collection event|battle pass|legend tokens|store sale',t,re.I):continue
  image=imgurl(im,url)
  if image:out.append(record(owner,'Legend',name,price,image,url,bool(re.search(r'themed event',t,re.I))))
 return out
def metal_marker(el):
 return bool(re.search(r'crafting[ _-]*(metal|material)',text(el),re.I) or any(re.search(r'crafting[ _-]*(metal|material)',str(i.get('alt',''))+' '+str(i.get('src',''))+' '+str(i.get('title','')),re.I) for i in el.select('img')))
def wiki(owner,kind):
 url='https://apexlegends.wiki.gg/wiki/'+quote(owner.replace(' ','_'))
 try:
  r=SESSION.get('https://apexlegends.wiki.gg/api.php',params={'action':'parse','page':owner,'prop':'text','format':'json','formatversion':2},timeout=20);r.raise_for_status();soup=BeautifulSoup(r.json()['parse']['text'],'html.parser')
 except Exception:soup=fetch(url)
 out=[]
 for item in soup.select('li.gallerybox, .wikia-gallery-item, tr'):
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
  if image:out.append(record(owner,kind,name,price,image,url,bool(re.search('themed|event',t,re.I))))
 return out
def main():
 old=json.loads(CAT.read_text(encoding='utf-8').split('=',1)[1].strip().rstrip(';'))
 records={(r['kind'],r['owner'],r['name'].casefold()):r for r in old['rows']};success=[];errors=[]
 for kind,owners in [('Legend',LEGENDS),('Weapon',WEAPONS)]:
  for owner in owners:
   got=[]
   for fn in ([apexdb,lambda n:wiki(n,kind)] if kind=='Legend' else [lambda n:wiki(n,kind)]):
    try:got.extend(fn(owner))
    except Exception as e:print(owner,str(e)[:150],file=sys.stderr)
    time.sleep(.35)
   if not got:errors.append(owner);continue
   success.append(owner)
   for r in got:
    k=(r['kind'],r['owner'],r['name'].casefold())
    if k not in records:records[k]=r
    elif r.get('image'):records[k]['image']=r['image']
   print(owner,len(got))
 if not success:
  print('No sources yielded explicit crafting data; retaining existing catalog.',file=sys.stderr);return
 result={'updated':str(date.today()),'mode':'Expanded community catalog','coverage':f'Imported data for {len(success)} of {len(LEGENDS)+len(WEAPONS)} categories. {len(errors)} unavailable or unparsed; retained existing entries. Verify prices in-game.','rows':list(records.values()),'unparsed':errors}
 tmp=CAT.with_suffix('.tmp');tmp.write_text('window.FORGE_CATALOG = '+json.dumps(result,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8');tmp.replace(CAT)
 print('Total:',len(records),'Unparsed:',', '.join(errors))
if __name__=='__main__':main()
