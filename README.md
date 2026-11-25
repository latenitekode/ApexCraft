# ApexCraft v1.1
Unofficial Apex Legends Crafting Metals skin browser. Made by sha6a6.

## Pages deployment
Set [Settings → Pages](https://github.com/latenitekode/ApexCraft/settings/pages) → Source to **GitHub Actions**. On the [Actions tab](https://github.com/latenitekode/ApexCraft/actions), select **Publish ApexCraft** and run on main with refresh enabled (default). Expected URL: https://latenitekode.github.io/ApexCraft/.

The workflow checks upstream on pushes, daily at 03:23 UTC (09:23 Bangladesh time; GitHub may delay scheduled runs), and on demand. It commits the latest snapshot back to main, then deploys static files. Repository Actions must allow the workflow token to write contents and Pages deployments; protected branches may block snapshot commits. GitHub may disable scheduled workflows after 60 days of repository inactivity. Branch-only Pages deployment does not execute the importer.

## Data refresh
- Discover Legend categories from ApexDB's current skin index and retain the fallback roster.
- Accept explicit Crafting Metals prices only; exclude event-only, token, coin and Battle Pass entries.
- Replace a Legend category only if the parsed craftable count exactly equals its source's declared total. Otherwise attempt a conservative Wiki import.
- Partial Wiki results add or update positively identified entries only, never delete unseen entries.
- Preserve previous records if a source fails; record separate check and retrieval times, complete/partial/unavailable categories, and recent removals.
- Compare prices, rarity, artwork URL, name and themed status. New/changed labels persist for 14 days and describe catalog indexing, not game release dates.
- The original 57 starter records are not fully verified; they are labeled accordingly until confirmed by a source. Complete live coverage and external artwork reliability are not guaranteed. Community sources may lag the game. Confirm availability in-game before spending.

## Local development
Python 3.10+:
```sh
python -m pip install requests beautifulsoup4
python scripts/refresh.py
python -m http.server 8000
```
Open http://localhost:8000. No paid backend or API key required.

## Interface
SkinVault-inspired automatic data pipeline and MeterLeaf-inspired responsive layout. Search, Legend/weapon categories, rarity and affordability filters, recent updates, preview dialog, YouTube showcase links, wishlist and local balance. No animations or framework dependencies. Desktop, tablet, portrait and narrow-phone layouts use fluid grid and touch-friendly controls.

## Attribution
Cosmetic data: [ApexDB](https://apexdb.gg/skins/) and [Apex Legends Wiki](https://apexlegends.wiki.gg/wiki/Main_Page). ApexDB attributes its Wiki-derived data to CC BY-SA 3.0; adapted community data is attributed and shared under [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) where applicable. Game artwork belongs to its respective rights holders and is displayed via external URLs, not granted a new license. Not affiliated with EA or Respawn. Project code is separate from third-party data.
