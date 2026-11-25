# ApexCraft

**Your cosmetic locker.** A lightweight, unofficial Apex Legends catalog for discovering cosmetics unlockable with Crafting Metals.

[Open ApexCraft](https://latenitekode.github.io/ApexCraft/) · [Developer portfolio](https://shabab.eu.cc/) · [Catalog updates & deployment](https://github.com/latenitekode/ApexCraft/actions)

![Version](https://img.shields.io/badge/version-1.3-d64b40?style=flat-square) ![Frontend](https://img.shields.io/badge/frontend-HTML%20%2F%20CSS%20%2F%20JS-28252b?style=flat-square) [![Catalog workflow](https://github.com/latenitekode/ApexCraft/actions/workflows/pages.yml/badge.svg)](https://github.com/latenitekode/ApexCraft/actions/workflows/pages.yml)

## Features

- Browse Legend skins, weapon skins, holosprays, profile banners and other supported craftable cosmetics independently.
- Combine search, Legend/weapon, cosmetic type, rarity and affordability filters.
- Inspect artwork directly in the catalog and enlarge previews without leaving the website.
- Open a YouTube showcase search for the exact cosmetic, owner and type.
- Track a Crafting Metals balance, save a wishlist and see its combined crafting cost.
- Discover newly indexed and changed cosmetics in the Recent updates tab.
- View catalog retrieval dates, source coverage and recent removals.
- Apex-inspired angular collectible cards, rarity-colored accents and responsive desktop, tablet, portrait and mobile layouts.

No login, paid API, frontend framework or animation library is required. Balance and wishlist preferences are stored locally in the browser.

## Cosmetic categories

| Category | Includes |
| --- | --- |
| Legend skins | Character outfits |
| Weapon skins | Weapon appearances |
| Holosprays | Holographic sprays |
| Profile banners | Banner frames and banner poses |
| Other cosmetics | Finishers, emotes, skydive emotes, trackers, charms and stickers, where indexed |

The catalog treats cosmetic type and Legend/weapon ownership as separate fields. Rarity alone does not establish crafting eligibility. For example, Mad Maggie's Above The Law, Big Finish and Fire Starter belong to distinct cosmetic categories.

## How the catalog stays updated

A Python importer retrieves public community data from [ApexDB](https://apexdb.gg/skins/) and the [Apex Legends Wiki](https://apexlegends.wiki.gg/wiki/Main_Page). GitHub Actions checks sources on pushes, manual runs and daily at **03:23 UTC / 09:23 Bangladesh time** (scheduled runs may be delayed).

1. Discover Legend categories from ApexDB and retain the fallback Legend/weapon roster.
2. Accept explicit crafting-price evidence. Ignore unknown cosmetic sections and recognized store-only, token and Battle Pass entries.
3. Classify Wiki records by source headings rather than guessing from artwork or price.
4. Reconcile complete skin-only source checks; partial Wiki retrievals add or update positively identified records without deleting unseen records.
5. Preserve previously typed records when retrieval fails and record coverage and timestamps. Exclude ambiguous untyped legacy records until re-indexed.
6. Validate catalog identities and run regression checks before publishing. Save the latest snapshot back to the repository.

The Recent updates view displays changes for 14 days. These are **catalog indexing changes**, not necessarily new in-game releases. Community sources can lag behind the game; some previews may be unavailable, and exhaustive coverage is not guaranteed. Confirm crafting eligibility and price in-game before spending.

## Run locally

To browse the existing catalog, only a local static HTTP server is needed:

```sh
git clone https://github.com/latenitekode/ApexCraft.git
cd ApexCraft
python -m http.server 8000
```

Open [localhost:8000](http://localhost:8000/).

To refresh the catalog and run the parser tests (Python 3.10+):

```sh
python -m pip install requests beautifulsoup4
python -m unittest discover -s scripts -p "test_*.py"
python scripts/refresh.py
```

Optional JavaScript syntax validation (Node.js):

```sh
node --check app.js
node --check catalog.js
```

## Deployment

The website is designed for free GitHub Pages hosting. Set **Settings → Pages → Source → GitHub Actions**, then run **Publish ApexCraft** from the Actions tab with refresh enabled. The workflow validates and packages the static website, persists the refreshed snapshot, and deploys when Pages is configured. If Pages is not initialized, the catalog build can still succeed and provide a static-site artifact.

The workflow needs repository contents write access for snapshot commits, and Pages write plus OIDC permissions for deployment. Protected branches may restrict snapshot commits. GitHub may disable scheduled workflows on inactive public repositories. A branch-only Pages setup does not run the importer by itself.

## Repository structure

```text
index.html                    Responsive interface and styles
app.js                        Search, filters, previews and wishlist
catalog.js                    Generated cosmetic catalog snapshot
scripts/refresh.py            Community-source importer
scripts/test_refresh.py       Classification regression tests
.github/workflows/pages.yml    Refresh, validation and Pages deployment
```

## Credits

Designed and developed by **[Shabab Hussain Siam](https://shabab.eu.cc/)** (sha6a6).

The lightweight catalog workflow takes inspiration from [SkinVault](https://skin-vault-valorant.vercel.app/), with responsive design principles from MeterLeaf and an Apex-inspired field-ledger visual theme.

Cosmetic metadata and previews are sourced from [ApexDB](https://apexdb.gg/skins/) and the [Apex Legends Wiki](https://apexlegends.wiki.gg/wiki/Main_Page). ApexDB attributes its Wiki-derived data to CC BY-SA 3.0; adapted community data is attributed and shared under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) where applicable. Third-party artwork remains the property of its respective rights holders and is displayed through external preview URLs. Project code is separate from third-party data.

ApexCraft is an independent fan project and is not affiliated with, endorsed by or sponsored by Electronic Arts or Respawn Entertainment.
