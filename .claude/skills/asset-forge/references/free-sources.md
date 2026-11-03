# When code-made assets are not enough

Some specs cannot be met honestly by code: realistic or organic characters,
skinned and animated rigs, painterly illustration, photo textures, voice acting,
orchestral music. Do not fake them with a weak procedural stand-in and call it
done. Report them as **NOT GENERATED - out of scope for code generation** and
offer these routes, which also cost nothing beyond the subscription:

- **Placeholder now**: make a clearly-named procedural stand-in
  (`*_placeholder.glb`, `temp_*`) so development continues. CCGS's
  `/launch-checklist` scans for `placeholder` / `temp_` / `WIP_` names, so it
  will not slip into a release unnoticed.
- **Free CC0 libraries** (no attribution required; confirm the licence on the
  page before using any asset):
  - Kenney (kenney.nl): 2D, 3D, UI, audio packs in consistent styles
  - Quaternius (quaternius.com): low-poly 3D, including rigged animated characters
  - Poly Haven (polyhaven.com): textures, HDRIs, realistic 3D models
  - OpenGameArt (opengameart.org): mixed licences - check each asset
- **An artist / composer** using the spec's generation prompt and description.

Record the licence and source URL of any downloaded asset next to it (for
example in `design/assets/asset-manifest.md`), so the release checklist can
verify it.
