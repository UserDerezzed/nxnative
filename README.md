# nxnative

> [!NOTE]
> **This is the `oot-stack` branch of [UserDerezzed/nxnative](https://github.com/UserDerezzed/nxnative), not upstream.** It is [seedds/nxnative](https://github.com/seedds/nxnative) `main` (at [`1992edb8`](https://github.com/seedds/nxnative/commit/1992edb8)) with open community pull requests merged on top, mostly for The Legend of Zelda: Ocarina of Time on the Mac. None of these PRs is merged upstream yet, so expect rough edges; report problems with them on their PR, not as upstream issues. Everything below this note is upstream's README.
>
> **Ocarina of Time: performance and graphics**
> - [#1393](https://github.com/seedds/nxnative/pull/1393) `pool_skip_retired`: no out-of-GPU-memory at scene changes
> - [#1714](https://github.com/seedds/nxnative/pull/1714) `gpu_ts_hz`: wind and leaves move at the right speed (were 19.66× too fast)
> - [#1730](https://github.com/seedds/nxnative/pull/1730) contiguous gmem pool-run merging only (its archive hardening is superseded by main's PR 1735)
> - [#1731](https://github.com/seedds/nxnative/pull/1731) texture upgrades, BC render targets and retired descriptor bounds kept (adapted to main's copy absorption, PR 1310); with #2312, ported onto main's NVN resource owner (`dm/gfx/nvn/nvn_owner.m`)
> - [#1732](https://github.com/seedds/nxnative/pull/1732) updated prewarm manifest and shader list
> - [#1752](https://github.com/seedds/nxnative/pull/1752) raw global memory loads resolve their pool once (shader translator rebuilt and re-locked for it)
> - [#1824](https://github.com/seedds/nxnative/pull/1824) texel fetches clamped at the texture edge: no hard edge in the mist
> - [#1890](https://github.com/seedds/nxnative/pull/1890) experimental opt-in fractional timing for high-fps play
> - [#1468](https://github.com/seedds/nxnative/pull/1468) a long render pass starts on the GPU while it is still encoded (`DM_NVN_PASS_SPLIT`)
> - the main submission keeps up to 16 command allocators (was 8): the encode thread no longer waits for one about 5 times a frame (Hyrule Field at a 120 fps target 67.1 → 69.8 fps on an M3 Max)
> - [#1927](https://github.com/seedds/nxnative/pull/1927) `fps_hold` off: a late frame is shown late instead of held a second vsync
> - [#1942](https://github.com/seedds/nxnative/pull/1942) frame step does not step up on late frames with the GPU idle
> - [#2219](https://github.com/seedds/nxnative/pull/2219) no stretched horse / slingshot vertices or flickering ReDead faces: a Switch 2 game's uniform reads are not bounded by the binding's size (main's 256-byte rounding stays for Switch 1 games)
> - [#2226](https://github.com/seedds/nxnative/pull/2226) no holes in the flower bushes of Hyrule Castle's courtyard: an indirect dispatch does not join a copy encoder that holds work
> - [#2312](https://github.com/seedds/nxnative/pull/2312) render targets the game moved leave GPU memory (ghost serials go with their sharing entry, and an idle sweep)
> - [#2308](https://github.com/seedds/nxnative/pull/2308) large mesh stage memory in a device slice: the foliage mesh pass faster
> - [#2307](https://github.com/seedds/nxnative/pull/2307) native mesh pipelines built before their first draw (`DM_NVN_MESH_PREDICT`): fewer mid-play stalls
> - [#2260](https://github.com/seedds/nxnative/pull/2260) texture views cached by Metal texture, and the encode thread on for the game
> - [#2280](https://github.com/seedds/nxnative/pull/2280) 15 more task / mesh pipelines in the prewarm list, [#2324](https://github.com/seedds/nxnative/pull/2324) 171 more
> - [#2344](https://github.com/seedds/nxnative/pull/2344) area loads late in a session no longer freeze in runs of 200-670 ms frames (texture IDs' read marks go with an unread ID's next texture)
> - [#2408](https://github.com/seedds/nxnative/pull/2408) a sparse mapping rebuilds the texture tables only when it is new: no 150 ms-1 s stalls at area loads in long sessions
> - [#2341](https://github.com/seedds/nxnative/pull/2341) `replay_ahead`: a frame is translated before the game releases it (55-57 → 59.6-59.8 fps in its author's runs)
> - [#2402](https://github.com/seedds/nxnative/pull/2402) and [#2367](https://github.com/seedds/nxnative/pull/2367) the frame step leaves 20 fps where 30 fits, also after a load's late frames
> - [#2418](https://github.com/seedds/nxnative/pull/2418) Anisotropic filtering, 2x to 16x, a launcher choice (the game's own by default)
> - [#2433](https://github.com/seedds/nxnative/pull/2433) a loop exit's subgroup block stays in the iteration that left the loop (shader translator rebuilt for it)
> - [#2328](https://github.com/seedds/nxnative/pull/2328), [#2329](https://github.com/seedds/nxnative/pull/2329), [#2330](https://github.com/seedds/nxnative/pull/2330), [#2342](https://github.com/seedds/nxnative/pull/2342) small fixes: a pool buffer's release fence, the blend-zero word of a merged pass, the pool table words before a mid-submission commit, one upload source buffer
>
> **Ocarina of Time: cheats** (in the game window's cheat panel)
> - [#1718](https://github.com/seedds/nxnative/pull/1718) rupees and ammo, max hearts, Link speed ×1.5–×3, one-hit kill, no damage
> - [#1949](https://github.com/seedds/nxnative/pull/1949) free camera, [#1955](https://github.com/seedds/nxnative/pull/1955) god mode, [#1963](https://github.com/seedds/nxnative/pull/1963) map select
> - [#1960](https://github.com/seedds/nxnative/pull/1960) turning a cheat off undoes what it changed
> - [#2014](https://github.com/seedds/nxnative/pull/2014) cheat sections fold in the panel and become submenus in the menu
> - [#1662](https://github.com/seedds/nxnative/pull/1662) play the ocarina into the Mac's microphone (`DM_MIC=1`)
>
> **Switch 2 controllers and output**
> - [#2129](https://github.com/seedds/nxnative/pull/2129) a Controller menu and panel in the game window (⌘⇧P) test a stick's drift and save its calibration in the controller, Pro Controller 2 right stick included
> - [#1176](https://github.com/seedds/nxnative/pull/1176) HDR output
> - [#2422](https://github.com/seedds/nxnative/pull/2422) a low-latency Bluetooth link and a queue of their own: about 66 reports a second instead of 33 (the Controller panel's hooks run on the main queue)
>
> **Building and diagnostics**
> - [#366](https://github.com/seedds/nxnative/pull/366), [#1693](https://github.com/seedds/nxnative/pull/1693) faster shader builds (main has PR 2255's worker processes, which supersede 1693's batch queueing); [#2193](https://github.com/seedds/nxnative/pull/2193)'s other half: the prepare step builds its tasks in turn by vertex shader (main has its prebuild half); [#1463](https://github.com/seedds/nxnative/pull/1463) the shader split no longer hangs at 88 %; [#1691](https://github.com/seedds/nxnative/pull/1691) progress through the archive stages' silent tails
> - [#2432](https://github.com/seedds/nxnative/pull/2432) `shader_lib.py compress`: a shader library image stores its files compressed, about a third of the size
> - [#1720](https://github.com/seedds/nxnative/pull/1720) dropped task / mesh draws are reported; [#1751](https://github.com/seedds/nxnative/pull/1751) `DM_NVN_GPUPROF_GEOM` splits pass time into geometry and pixels
>
> The shader chain header is regenerated for the merged translator, so build from this branch as a whole rather than cherry-picking single PRs out of it.

Play your own Nintendo Switch and Switch 2 games natively on Apple silicon Macs, iPhone and iPad. One script packs your game into a Mac app or an unsigned IPA that you sideload.

It is not an emulator: the game's own code runs directly on the Apple chip, with Switch graphics rebuilt on Metal. Nothing from any game is in this repository, and the project is not affiliated with Nintendo or any game publisher.

[Games](#games) · [Community front ends](#community-front-ends) · [Requirements](#requirements) · [How to play](#how-to-play) · [Discussions](#discussions) · [For developers](#for-developers)

## Games

The full [tested games table](dm/games/README.md#games) includes original Switch games, tested builds, engines and graphics APIs. Each game's note records its tested platforms, progress and known issues.

These Switch 2 games have passed Mac gameplay testing. Build them from a [`.nup` file or a dump folder](#switch-2-games):

- [Donkey Kong Bananza](dm/games/040074A01BF12000/README.md)
- [Fire Emblem Fortune's Weave](dm/games/04007EF01F8AE000/README.md) — up to 120 fps
- [Hyrule Warriors: Age of Imprisonment](dm/games/04003F40232DE000/README.md)
- [Kirby Air Riders](dm/games/040077201BE50000/README.md)
- [Mario Kart World](dm/games/0400C3F00006E000/README.md)
- [Mario Tennis Fever](dm/games/0400D4201C6EA000/README.md)
- [Nintendo Switch Sports Resort](dm/games/04008E001F098000/README.md)
- [Pokémon Pokopia](dm/games/0400A3A01EE4C000/README.md)
- [PRAGMATA](dm/games/0400C76024710000/README.md)
- [Splatoon Raiders](dm/games/0400380020056000/README.md)
- [Star Fox](dm/games/0400E88025B1A000/README.md)
- [The Legend of Zelda: Ocarina of Time](dm/games/0400486024DEC000/README.md)
- [Yoshi and the Mysterious Book](dm/games/0400245021D2C000/README.md)

## Community front ends

Community projects build on nxnative with tools to turn your games into apps for your iPhone, iPad or Mac without the command line, and libraries to organize and launch them. They are separate projects: questions and bugs about them go to their own pages.

- [NX2Apple](https://github.com/LNPANDY/NX2Apple) — Mac builder with a shared iPhone/iPad game library.
- [NX Play](https://github.com/varyform/nx-native-wrapper) — Mac library with device installs and save sync.
- [NxNative Launcher](https://github.com/rennan101/nxnative_Launcher) — Mac launcher with guided builds and controller mapping.
- [LumaNX](https://github.com/Xc1Ym/LumaNX) — Mac game builder with IPA export.
- [GameCase](https://github.com/Tiaoge-tou/GameCase) — iOS game library based on LiveContainer.

## Requirements

- **Mac:** Apple silicon, macOS 26.6 or later. Building games requires Xcode 27.2.
- **iPhone:** A17 Pro chip or later, with iOS 26 or later.
- **iPad:** M1 chip or later, with iPadOS 26 or later.

The games' textures are BC-compressed, which older iPhones cannot read. Switch 2 builds are tested on the Mac; check each game's note for device-specific validation.

For a game without a profile, the script writes a survey and tries a provisional build with guessed settings. That build may not start; see [Port another game](docs/development.md#port-another-game).

## How to play

Switch 2 games are built from one `.nup` file or a folder of their files, not from NSPs, and are tested on the Mac only: see [Switch 2 games](#switch-2-games).

### Build from the command line

You need a Mac with macOS 26.6 or later, [Xcode](https://developer.apple.com/download/all/?q=Xcode%2027.2) 27.2, [Homebrew](https://brew.sh) and Python 3.12 or newer (an arm64 one, not an Intel Homebrew's). An iPhone build also needs Xcode's iOS platform (Xcode → Settings → Components).

The shaders are built with Xcode 27.2's Metal compiler. Select it before step 1: `sudo xcode-select -s /Applications/Xcode.app`. With several Xcode versions installed, name this one `Xcode-27.2.app` and select it with `sudo xcode-select -s /Applications/Xcode-27.2.app`.

**1. Install the tools** (only once), in Terminal:

```
xcodebuild -downloadComponent MetalToolchain
git clone https://github.com/seedds/nxnative.git && cd nxnative
brew install xcodegen zstd glslang
python3 -m pip install lz4 "capstone>=5,<6" fonttools nsz zbic "backports.zstd; python_version < '3.14'"
```

**2. Put your game in a folder**: the game, plus its update and DLC if you have them (`.nsp`, `.xci`, `.nsz` or `.xcz`):

```
~/Games/MarioWonder/
  Super Mario Bros. Wonder [010015100B514000][v0].nsp
  Super Mario Bros. Wonder [010015100B514800][v327680].nsp
```

**3. Build**, with your game folder and your `prod.keys`:

```
python3 scripts/build_ipa_from_nsp.py ~/Games/MarioWonder -k ~/keys/prod.keys
```

The IPA appears in the game's folder. The first build takes 30–60 minutes and needs free disk space of about twice the game's size plus 10 GB; building again is much faster.

To play on the Mac instead, add `--platform mac-app`: you get a Mac app of the game to open from Finder. All options: [The packing script in detail](docs/development.md#the-packing-script-in-detail).

### Install

Install the IPA on your iPhone or iPad with a sideloading tool such as AltStore, Sideloadly or LiveContainer. If your tool offers **Increased Memory Limit**, turn it on: the bigger games need it.

Game too big to install? Build again with `--romfs separate`, and run the command the script prints once to copy the game files to your phone ([Quick reinstalls](docs/development.md#quick-reinstalls)). With AltServer, also add `--shader-files`: it cannot install a file of 2 GiB or more.

Controls, saves and settings: [Playing](docs/playing.md).

### Switch 2 games

A Switch 2 game is built from one [NUP](https://github.com/a55uka/nup) container (a `.nup` file) or a folder of its files, not from NSPs. Neither needs `prod.keys`. A game this project has no profile for is surveyed and gets a provisional profile, as NSPs do ([Port another game](docs/development.md#port-another-game)), which may not boot. You get a Mac app; iPhone and iPad are untested.

**From a `.nup` file**, which holds the base game, its updates and DLC in one file. Give the file, or a folder that holds it:

```
python3 scripts/build_ipa_from_nsp.py ~/Games/DonkeyKongBananza.nup --platform mac-app
```

[Hyrule Warriors: Age of Imprisonment](dm/games/04003F40232DE000/README.md) is played this way: its 47 GB NUP unpacks in under five minutes. A NUP that carries the game's control data (its NACP) and icon gives the app the game's name and icon; otherwise the name comes from the game's profile and the app has no icon unless you give it one with `--icon <image>` (`ICON` in Spyder; a JPEG or PNG of any size).

A NUP without the base game also works, when its base package is empty or it has none and its updates are marked `standalone_update`: the update is taken as the whole game, and the script says so. If the game then stops on missing files, that update holds only what changed: pack a NUP with the base game. The newest update is selected by default; `--package v<N>` selects another version in the container. Such a container has no `v0` (base game) to select.

**From a folder of files**. The script expects this layout (`updates` and `dlc` are optional):

```
~/Games/DonkeyKongBananza/
  base/exefs/                     main, main.npdm, sdk, rtld
  base/romfs/
  updates/458752/exefs/           the update's version, as a decimal number
  updates/458752/romfs/           the patched RomFS, not a patch
  dlc/040074a01bf13001/0/romfs/   the DLC's title ID
```

```
python3 scripts/build_ipa_from_nsp.py ~/Games/DonkeyKongBananza --platform mac-app
```

An update's folder alone will do (no `base/`), and so will `exefs/` and `romfs/` directly in the folder, as `nup extract` writes them, which count as `base/`. The app has no icon, because the folder holds none; `--icon <image>` (`ICON` in Spyder) gives it one. To turn such a folder into a NUP: `nup pack ~/Games/DonkeyKongBananza game.nup`.

## Discussions

Questions, how a game runs on your Mac or iPhone, and ideas go in [Discussions](https://github.com/seedds/nxnative/discussions); [Issues](https://github.com/seedds/nxnative/issues) are for bugs, with the log. Ocarina of Time's performance (frame rate, resolution, which Macs hold 60 fps) is followed in [Ocarina of Time: state on main](https://github.com/seedds/nxnative/discussions/1789).

## For developers

[How it works](docs/development.md) · [Game notes](dm/games/README.md#games) · [Bring-up and debugging](docs/agents/README.md) · [Front ends](docs/frontends.md) · [Contributing](CONTRIBUTING.md)

## Acknowledgements

This project is built on other people's work ([licenses](dm/third_party/README.md)):

- **[d2r-mobile](https://github.com/jhaizhou-ops/d2r-mobile)** (MIT) developed this native-execution approach, for Diablo II: Resurrected. nxnative started as a copy of its generic parts: the NSO rewriter, the host that stands in for Horizon, the NVN-on-Metal layer and the iOS app shell. Fixes go both ways.
- **Ryujinx** (MIT): its shader translator (`Ryujinx.Graphics.Shader`, `Ryujinx.Common` and `Spv.Generator` 1.3.2, in `dm/third_party/ryujinx` with a few fixes listed in [its README](dm/third_party/ryujinx/README.md)) turns the games' shaders into SPIR-V. Its emulation of the kernel and system services is also a reference when the host's behaviour is in doubt.
- **[Atmosphère](https://github.com/Atmosphere-NX/Atmosphere)**: its kernel, mesosphère, is the reference for Horizon's synchronization semantics (address arbiter, condition variables).
- **[LibHac](https://github.com/Thealexbarney/LibHac)**: reads NSPs and layers updates over the base game in `dm/tools/nx_extract`.
- **[SPIRV-Cross](https://github.com/KhronosGroup/SPIRV-Cross)**: SPIR-V to Metal Shading Language.
- **[glslang](https://github.com/KhronosGroup/glslang)** compiles the GLSL of OpenGL games to SPIR-V for it.
- **[MacNativeGames](https://github.com/ly05010419/MacNativeGames)** (MIT): the GPU widening of 8-bit indices and in-pass clears in `dm/gfx/nvn/nvn_mtl.m`, and the visibility-counter lowering in the shader translator.

## License

MIT ([LICENSE](LICENSE)). Third-party code keeps its own license ([dm/third_party](dm/third_party/README.md)).
