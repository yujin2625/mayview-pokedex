# Mayview Guides

Static guide pages for the **Mayview (with Cobblemon)** Minecraft modpack (Cobblemon 1.7.3, NeoForge 1.21.1).

- **Pokédex:** `pokedex/index.html`. 1,025 Pokémon, bilingual (EN/KO), with in-game model renders, wild spawns, raid dens, evolutions, breeding partners, shiny odds, stars and custom lists (saved in the browser).
- **Breeding guide:** `breeding.html`. How Cobbreeding is configured in this pack.

Published with GitHub Pages from the `main` branch root.

## Rebuilding the Pokédex

`pokedex/index.html` is generated. Edit `pokedex/template.html`, then run:

```
python _tools/build_page.py
```

This inlines `pokedex/data/*.json` and the Galmuri font into `pokedex/index.html`. The data and sprite atlases come from the scripts in `_tools/` (`build_data.py`, `build_jobs.py`, `render.html` + `server.py`, `build_atlas.py`). They read game files extracted from the modpack, and their paths point at the original workspace, so adjust them before running.

Form-change notes (the "How to get each form" list on the Forms tab) come from `_tools/form_changes.py`. It reads the Mega Showdown, Cobblemon and ATM x MSD files straight from the instance and rewrites `pokedex/data/pokedex.json`. Run it after `build_data.py` and before `build_page.py`.

## Credits

- Pokémon and Pokémon names © Nintendo / Creatures Inc. / GAME FREAK inc. This is an unofficial fan project, not affiliated with or endorsed by Nintendo, The Pokémon Company, GAME FREAK or the Cobblemon team.
- Models, textures and data come from Cobblemon and the mods and resource packs bundled in the Mayview modpack, rendered for reference. All game assets (sprites in `pokedex/sprites`, `pokedex/data/thumbs.json`) remain the property of their respective owners and will be removed on request.
- Font: [Galmuri](https://github.com/quiple/galmuri) by Lee Minseo, SIL Open Font License 1.1 (`pokedex/fonts/OFL.md`). DotGothic16 and Silkscreen are loaded from Google Fonts.

## License

The code in this repository is licensed under [PolyForm Noncommercial 1.0.0](LICENSE.md): noncommercial use, modification and redistribution are allowed, commercial use is not, and redistributions must keep the `Required Notice` line and the license terms. Game assets (Pokémon sprites, models, textures and data) are not covered by this license; see Credits above.
