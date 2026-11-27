// A small DOM double verifies list identity without network/image dependencies.
const {readFileSync}=require('node:fs');const vm=require('node:vm');const assert=require('node:assert/strict');
class Element{constructor(){this.children=[];this.value='';this.checked=false;this.dataset={};}append(...xs){this.children.push(...xs)}replaceChildren(...xs){this.children=xs}setAttribute(){}addEventListener(){}querySelectorAll(){return []}}
const elements=new Map();const get=id=>{if(!elements.has(id))elements.set(id,new Element());return elements.get(id)};get('sort').value='name';
const rows=Array.from({length:80},(_,i)=>({name:`Skin ${String(i).padStart(2,'0')}`,owner:'Test',cosmetic:'Skin',kind:'Weapon',rarity:'Rare',cost:30,image:'',source:'https://example.com',verification:'source'}));
const context=vm.createContext({window:{FORGE_CATALOG:{rows}},document:{getElementById:get,createElement:()=>new Element()},localStorage:{getItem:()=>null,setItem(){}},Option:class extends Element{},URL,location:{href:'https://example.com'},console});
vm.runInContext(readFileSync(require('node:path').join(__dirname,'../app.js'),'utf8'),context);
const first=[...get('grid').children];assert.equal(first.length,36);
get('more').onclick();assert.equal(get('grid').children.length,72);first.forEach((node,i)=>assert.equal(get('grid').children[i],node));
get('more').onclick();assert.equal(get('grid').children.length,80);assert.equal(get('more').hidden,true);
get('search').value='Skin 79';vm.runInContext('render()',context);assert.equal(get('grid').children.length,1);assert.notEqual(get('grid').children[0],first[0]);
get('search').value='no match';vm.runInContext('render()',context);assert.equal(get('grid').children.length,0);assert.equal(get('empty').hidden,false);
console.log('PASS: append preserves 36 existing cards, final batch, search replacement, and empty results');
