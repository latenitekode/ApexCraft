# ApexCraft
A lightweight, unofficial Apex Legends Crafting Metals skin browser. Made by sha6a6.

## Publish on GitHub Pages
Open **Settings → Pages → Build and deployment → Source → GitHub Actions**. Then open the Actions tab, select **Publish ApexCraft**, and run the workflow on main. Leave **refresh** unchecked for a quick starter deployment, or enable it to attempt importing more skins. The expected URL is https://latenitekode.github.io/ApexCraft/ after successful deployment.

Alternatively, choose **Deploy from a branch**, select **main / (root)** and save for the starter catalog only (no importer required).

## Catalog
The initial 57 records cover Revenant, Caustic, Catalyst, Flatline, and EVA-8. This is a partial reference catalog, not a verified live in-game inventory. External preview links can fail or change. The importer reads explicit crafting prices from ApexDB and the Apex Legends Wiki; it does not infer craftability solely from rarity. Live import coverage depends on source availability and markup. Check in-game before spending metals.

Run locally with Python 3.10+:
```sh
python -m pip install requests beautifulsoup4
python scripts/refresh.py
python -m http.server 8000
```
Open http://localhost:8000. The workflow publishes its expanded catalog as a Pages artifact without changing the tracked starter file.

## Features
Legend and weapon categories, rarity and affordability filters, sorting, image previews, YouTube showcase searches, wishlist totals, local persistence, mobile-friendly static UI.

## Credits
Apex Legends artwork is owned by its respective rights holders. Community data and external previews are attributed to [ApexDB](https://apexdb.gg/skins/) and the [Apex Legends Wiki](https://apexlegends.wiki.gg/wiki/Main_Page). Follow source licensing terms when redistributing their content. Not affiliated with EA or Respawn.
