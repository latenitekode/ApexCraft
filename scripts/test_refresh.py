"""Regression fixtures for typed cosmetic extraction (no live network)."""
import unittest
from bs4 import BeautifulSoup
from refresh import parse_wiki, identity, legacy_type

def gallery(name,price='1,200',currency='Crafting Metals'):
 return f'<ul class="gallery"><li class="gallerybox"><div class="thumb"><img src="/images/{name.replace(" ","_")}.png"></div><div class="gallerytext"><p>{name}<br><img alt="{currency}" src="/currency.png">{price}</p></div></li></ul>'

class CosmeticTests(unittest.TestCase):
 def test_sections(self):
  html='<h2>Cosmetic items</h2><div class="mw-heading"><h3>Skins</h3></div><h4>Legendary</h4>'+gallery('Above The Law')+'<h3>Banner Frames</h3>'+gallery('Big Finish')+'<h3>Banner Poses</h3>'+gallery('Armed and Dangerous','400')+'<h3>Holosprays</h3>'+gallery('Fire Starter')+'<h3>Finishers</h3>'+gallery('Renewed Hostility')+'<h3>Emotes</h3>'+gallery('Guitar Tuner')+gallery('Coin-only','1,200','Apex Coins')+'<h3>Unknown category</h3>'+gallery('Not a cosmetic')+'<h2>Gallery</h2>'+gallery('Concept art')
  rows=parse_wiki(BeautifulSoup(html,'html.parser'),'Mad Maggie','Legend','https://apexlegends.wiki.gg/wiki/Mad_Maggie')
  self.assertEqual({r['name']:r['cosmetic'] for r in rows},{'Above The Law':'Skin','Big Finish':'Banner Frame','Armed and Dangerous':'Banner Pose','Fire Starter':'Holospray','Renewed Hostility':'Finisher','Guitar Tuner':'Emote'})
 def test_weapon_skins(self):
  html='<h2>Skins</h2>'+gallery('Supernova')+'<h2>Other</h2>'+gallery('Not a skin')
  rows=parse_wiki(BeautifulSoup(html,'html.parser'),'VK-47 Flatline','Weapon','https://apexlegends.wiki.gg/wiki/VK-47_Flatline')
  self.assertEqual([(r['name'],r['cosmetic']) for r in rows],[('Supernova','Skin')])
 def test_identity_and_legacy(self):
  row={'kind':'Legend','owner':'Mad Maggie','name':'Same name','cosmetic':'Skin'}
  self.assertNotEqual(identity(row),identity(dict(row,cosmetic='Holospray')))
  self.assertIsNone(legacy_type({'source':'https://apexlegends.wiki.gg/wiki/Mad_Maggie','verifiedAt':'2026-11-25'}))
if __name__=='__main__':unittest.main()
