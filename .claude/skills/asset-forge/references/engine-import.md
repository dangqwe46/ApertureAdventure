# Getting generated assets into the engine

## Godot 4
- **.glb**: drop into `assets/art/models/`. Godot imports it as a scene. Part
  names become node names, so `$lid_pivot.rotation.x` animates the chest lid.
  For web builds (Compatibility renderer) keep materials simple; emissive works,
  transparency costs more.
- **Sprite sheets**: import with Filter **Nearest** for pixel art (Project
  Settings > Rendering > Textures > Default Texture Filter = Nearest for an
  all-pixel game). Build `SpriteFrames` from the sheet using the `.json`'s
  frame size and fps hint.
- **SVG**: imports directly; raise the import `scale` for crisp large UI.
- **Textures**: Repeat enabled for seamless textures; mark `_n.png` files as
  normal maps (import as "Normal Map" or assign to the material's Normal slot).
- **Audio**: WAV and OGG both import. Enable **Loop** in the import dock for
  music loops (OGG: loop flag; WAV: Loop Mode = Forward).

## Unity
- **.glb** needs a glTF importer package (glTFast or UnityGLTF) installed.
- Sprites: Texture Type Sprite, Sprite Mode Multiple, slice by cell size from
  the `.json`; Filter Mode Point and Compression None for pixel art.
- Audio: WAV / OGG import directly; tick Loop on the AudioSource for music.

## Three.js / web
- `GLTFLoader` loads the .glb directly; textures load as normal images.

## Folder layout (matches CCGS `/asset-audit` for Godot)
```
assets/art/models/      prop_*.glb, env_*.glb, char_*.glb, weapon_*.glb
assets/art/sprites/     char_*.png + .json
assets/art/ui/          ui_*.svg / .png
assets/art/textures/    tex_*_256.png (+ _n.png)
assets/audio/sfx/       sfx_*_01.ogg
assets/audio/music/     music_*_loop.ogg
design/assets/recipes/  the JSON recipes (source of truth; regenerate any time)
```
Unity projects put the same folders under `Assets/`.
