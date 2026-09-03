# ROSE Editor — Development Roadmap

Status snapshot and forward plan, written 2026-09-01. This is a living document — update phase status as work lands, and adjust ordering if a dependency assumption turns out wrong.

## Architecture decision: staying Python

Considered converting the tool to a C++ Maya plugin. Decision: **stay Python**, because ROSE is a build-time rig compiler + authoring UI, not a runtime evaluator — every operation wires together native Maya nodes (`multMatrix`, `decomposeMatrix`, `composeMatrix`, constraints, etc.) at build time, and none of ROSE's own code runs per-frame during playback. That removes the main argument for C++ (per-frame evaluation speed), while a full port would cost significant rewrite effort, drop `importlib.reload`-speed iteration, and introduce Maya-version ABI fragility that Python doesn't have.

C++ stays on the table selectively: if a specific runtime bottleneck shows up later (e.g. a custom deformer/solver that must run every frame and can't be expressed as wired native nodes), write an isolated `MPxNode`/`MPxDeformerNode` for that one case, profiled and justified first — not a wholesale rewrite. This is the same pattern used by mGear, Advanced Skeleton, and most studio rigging pipelines.

## Phase 0 — Fix Node Editor UI regression (blocking)

The Node Editor tab renders incorrectly after the Maya-version port (PyQt6→PySide6, Maya 2023 → Maya 2025/2027 — version to be confirmed). Nothing downstream is reliably testable until the core editor looks and behaves correctly again.

Status: **done.** Root-caused and fixed: legacy `Qt.SHIFT`/`Qt.CTRL` enum usage broke edge-drag cancellation, node dragging, and rubber-band selection under PySide6/Qt6; node width/title sizing and socket positioning were static and drifted out of sync once made dynamic; the view didn't auto-center on open. Also landed alongside it: collapsible node display modes (`1`/`2`/`3`, matching Maya's own Node Editor convention) and a fix for shift-click additive selection only working on a node's title bar.

## Phase 1 — Plugin-node support (infrastructure)

Add support for node types that depend on a compiled Maya plugin (custom `MPxNode`/`MPxDeformerNode`), so the tool can:
- Declare required plugin(s) per node type (alongside the existing `operation_code` registration in `node_Editor_conf.py`).
- Check plugin availability (`cmds.pluginInfo(name, q=True, loaded=True)`) and surface missing plugins through the existing node validity system (`is_valid` / `updateActionButtons()` in `rose_node_base.py`), rather than failing silently at build time.

Why now: every subsequent phase adds more node types (Skinning components, Facial components). Building this once, before the registry grows, is cheaper than retrofitting validation onto many node classes later.

## Phase 2 — Finish the Skinning Editor tab

Status: **largely done, in real-world testing now.** Landed: `SkinningEditorCluster` backend (target-mesh binding, build with skip-missing, weight export/import via `deformerWeights`, hybrid id→name deform resolution that tolerates renames and static rebuilds without misfiring); full UI (draggable/reorderable component boxes, toolbar with build/select/remove all-or-selected, per-box weight store/apply/remove-with-confirmation and a stored/not-stored indicator); title-bar modified-star and the New/Open/Close unsaved-changes prompt now cover skin cluster edits, not just the node graph; Delete key now dispatches per-active-tab instead of always targeting the node graph (also fixed a latent crash in the Edit menu when opened while the Skin tab was active). The original diffing TODO (`# TODO: Check new list with previous list what was added and what was removed`) is resolved: the deform list now tracks added (green, persists until explicitly accepted)/removed (red, persists until explicitly cleared) state across refreshes and across save/reload, with a hybrid id→name match so a static rebuild doesn't falsely show every deform as removed-and-re-added.

Remaining before calling this phase closed: more real-world testing (this has had several rounds of "doesn't look right" fixes — colors, sizing, selection, stale-code confusion — worth a clean end-to-end pass), and deciding whether the facial/build-pipeline phases need anything from this tab's data model before it's touched again.

## Phase 3 — Build Pipeline tab (basic version)

Status: **largely done, in real-world testing now.** Landed: a third canvas tab (Control Rig / Skinning step nodes, sequence-socket edges, topological `buildFullPipeline()`, per-step enable/disable via the `M` key, non-collapsible title-only visuals); an Output Path step that exports the build (persisted output directory, browse button) with the last-remaining one protected from deletion while extras are freely deletable; the Skinning step now reparents every skinned mesh into a `<rig_name>_geometry_hrc` group under the main rig hierarchy as part of a pipeline run (not the Skinning tab's own build button), and the Output Path step exports only that rig hierarchy (`exportSelected`, not the whole scene) so guides/helper nodes never end up in the shipped `.mb`. Delete-key/Edit-menu dispatch and undo history are wired up for the tab, matching the other two.

Remaining before calling this phase closed: a clean end-to-end real-world pass (same as Phase 2 — this had several rounds of "doesn't work yet" fixes for Delete-key wiring, a shared-code `display_mode` crash, and orphaned editor windows from testing); deciding whether Package Output needs anything beyond scene export (plugin-copying, texture-repathing) once Phase 1 exists to inform that.

## Phase 4 — Facial rig tab

Largest net-new scope. Likely needs its own component subtypes (corrective joints, blendshape-driven components, possibly dedicated facial guide types). Benefits from Phases 1–3 already existing: plugin support for any custom facial-solver nodes, the Skinning tab as a proven second-tab template, and the Build Pipeline tab to slot facial build steps into a full-rig run.

## Phase 5 — Custom Rig UI tab (companion script generator)

Lets a user design a custom rig-control UI inside ROSE, which the build pipeline exports as a **self-contained companion Python script** — an animator runs it directly to open the rig's UI, with no ROSE installation required at runtime. Design implication for earlier phases: the generator should only need hardcoded control names / serialized layout data, not live ROSE internals — worth keeping in mind while shaping the Controls/serialization layer in Phases 2–4 so this stays a straightforward export rather than a refactor.

## Phase 6 — Control Shapes Layers tab

Its own tab for authoring and managing control curve shapes as swappable layers — not yet scoped in detail. `ROSE_Names.rig_hierarchy_shapes_suffix` (`_shapes_hrc`) is already reserved for this, the same way `_geometry_hrc` sat unused until the Pipeline tab's Skinning step wired it up this session, so the naming slot is ready whenever this phase starts. Likely benefits from the Pipeline tab existing already, as a "shape layer" build/apply step is a natural fit for that orchestration model once this tab's data model is defined.

## Phase 7 — Curve Net Deformation tab

Its own tab for building and controlling a curve-net-based mesh deformation system — not yet scoped in detail (net topology, drive/follow relationships, and how it plugs into the Skinning/Pipeline build chain are all open design questions). Greenfield: no reserved naming or partial infrastructure exists for this yet, unlike Phase 6.

## Backlog (not scheduled into a phase yet)

- **Tab-search to add/find nodes** in the Node Editor (type-to-search node creation, and a way to jump to an existing node by name) — quality-of-life on top of an already-functional editor, not an MVP blocker.
- **Attribute system for components** — a more general way for a component node to expose typed attributes beyond the current fixed guide/deform/control-size sliders.
- **Rename `MNRB` → `ROSE`** — **done.** Every subfolder, file, class, function, variable, and UI-visible string is now ROSE-branded. The root project folder itself intentionally stays named `MNRB`, since Maya's `import MNRB...` resolution depends on that folder name and changing it would break the tool's own installation path for existing setups; everything under it (`MNRB/ROSE_UI/`, `MNRB/ROSE_naming/`, etc.) is ROSE.
- **Centralized debug-logging class**, replacing the scattered `if CLASS_DEBUG: print(...)` calls throughout the codebase, so debug output can be toggled/filtered in one place instead of per-module flags — the repeated `print()` calls have a real runtime cost when left on. Optimization, not urgent.
- **Create-new-node-type from the editor** — a UI-driven way to scaffold a new component node (generates a new file in `ROSE_Nodes/Nodes/` with the basic class/registration boilerplate already in place), instead of hand-writing one from scratch each time.
- **Rotation order selection** in the node properties panel — currently not exposed as a control anywhere.
- **Rework the node validity indicator** — currently the small triangular icon in the node's title-bar corner (`node_Editor_QGraphicNode.py`'s `paint()`); move it to a line/bar under the title instead, likely more legible at a glance and across zoom levels.
- **Custom node categories** — `ROSE_NODE_GROUPS` (`node_Editor_conf.py`) is currently a fixed dict; adding a new node type means editing that dict directly rather than being able to assign/create a category from the UI.

## Open questions

- Confirm target Maya version(s) for the current UI regression (2025 vs. 2027 mentioned in different conversations) — affects which Qt/PySide behavior is actually being debugged.
