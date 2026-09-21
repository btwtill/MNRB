# ROSE Editor — Development Roadmap

Status snapshot and forward plan, written 2026-09-01. This is a living document — update phase status as work lands, and adjust ordering if a dependency assumption turns out wrong.

## Architecture decision: staying Python

Considered converting the tool to a C++ Maya plugin. Decision: **stay Python**, because ROSE is a build-time rig compiler + authoring UI, not a runtime evaluator — every operation wires together native Maya nodes (`multMatrix`, `decomposeMatrix`, `composeMatrix`, constraints, etc.) at build time, and none of ROSE's own code runs per-frame during playback. That removes the main argument for C++ (per-frame evaluation speed), while a full port would cost significant rewrite effort, drop `importlib.reload`-speed iteration, and introduce Maya-version ABI fragility that Python doesn't have.

C++ stays on the table selectively: if a specific runtime bottleneck shows up later (e.g. a custom deformer/solver that must run every frame and can't be expressed as wired native nodes), write an isolated `MPxNode`/`MPxDeformerNode` for that one case, profiled and justified first — not a wholesale rewrite. This is the same pattern used by mGear, Advanced Skeleton, and most studio rigging pipelines.

## Phase 0 — Fix Node Editor UI regression (blocking)

The Node Editor tab renders incorrectly after the Maya-version port (PyQt6→PySide6, Maya 2023 → Maya 2027). Nothing downstream is reliably testable until the core editor looks and behaves correctly again.

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

## Phase 8 — Attribute Editor tab

Status: **built and in real-world use — good enough for now.** Reopen this section when enough adjustments have collected to be worth a pass.

Landed, as a **canvas** rather than the list this was originally scoped as. A list can only express control ← attribute; what was actually needed is a graph, because one attribute drives many, a driven attribute can drive further, and operators sit in between. It reuses the node editor a third time, the way the Pipeline tab does, with its own registry and a deliberately different look (pill-shaped nodes, category stripe, `attribute_Editor_UI/`).

- **Component side.** `ROSE_Attributes/` — an `attribute` class alongside `deform`/`control` with a derived stable id, declared per component in `initAttributes()` so the tab can list them before the rig has ever been built, and opt-in so a component's internal wiring stays private. The four hardcoded visibility attributes migrated onto it.
- **Graph.** Attribute nodes (input *and* output — an attribute can be either end), control nodes, a Scene Target node for driving an arbitrary `node.attribute` plug, and Reverse / Multiply / Condition / Clamp operators that become native Maya utility nodes. An edge into a control means proxy, an edge into an attribute means connect. Enforced rule: **a driven attribute must not also be proxied onto a control**, since the incoming connection owns the value and the animator's channel would silently refuse input.
- **Naming and limits.** Proxy names derive automatically as `<component prefix><attribute name>`, so several components' identically named attributes coexist on one control; typing a name makes it stick. Limits live on the source attribute — confirmed in Maya that a proxy inherits them and refuses a `setAttr` past the maximum — and rig-root attributes carry editable default/min/max/enum options.
- **Build.** Toolbar button, or the `Attributes` pipeline step (operation code 3), which must sit after Control Rig since the controls and attributes it needs are made by that build.

## Known bugs (unscheduled, fix as they surface)

*None open.*

Recently fixed and worth remembering:
- **Skinning tab opened empty after a restart, with every deform marked new.** Nothing was actually deleted — the data was on disk the whole time. Each tab located its graph with `os.listdir(folder)[0]`, whose order is arbitrary. The moment any weights were stored, the skinning folder gained a `weights/` subdirectory, which listed *ahead* of the graph; the tab then tried to open a directory as its graph, hit `IsADirectoryError`, swallowed it in a bare `except`, and came up with no clusters and an empty `tracked_dict` — which is why every deform then read as newly added and went green. The real danger was the next save: an empty tab serialises to an empty project, so one Save would have made the loss genuine. Fixed in `rose_ui_utils.findProjectGraphFile()` (files only, `.json` only, prefers `<project>_graph.json`), used by all four tabs, plus a guard that refuses to save a tab whose load failed. Worth remembering as a shape: **a load that fails quietly plus a save that runs unconditionally is a data-loss bug**, even when neither half looks like one.


- **Shelf reload is automatic.** `ROSE_shelf/module_loading.py` was a hand-maintained list of ~100 `importlib.reload` calls in a hand-maintained order, and both properties bit: `skinning_Editor_UI/skinning_Editor_Scene` was never in it, so editing that file and hitting Reload did nothing, and wrong ordering left stale Enum classes (see above). It now drops every `MNRB.*` module out of `sys.modules` and imports the package again, discovering modules from disk. 372 lines → 113, ~0.02s, nothing to keep up to date. Two things that were not obvious:
  - **`pkgutil.walk_packages` finds almost nothing here.** ROSE's subdirectories carry no `__init__.py`, so they are namespace packages, and pkgutil does not descend into those — it reported 5 modules out of 111. The walk is done over the filesystem instead.
  - **The conf/registry cycle has exactly one safe entry point.** Each editor's conf ends with `from <its package> import *`, while the modules that reaches import back through the node base to read that same conf. Entered from a node module the cycle raises, and — worse — the siblings the failed cascade already imported stay bound to a conf that is then discarded, so their registrations never re-run against the live one and `ROSE_NODES` comes back with **1 of 4** node types instead of an error. `sortRegistryModulesFirst()` imports conf modules first, which is the one ordering the import machinery cannot work out for itself.

  Failed imports are now reported (`log.warning`, ungated) rather than silently leaving last session's code running.

- **Constraint system reworked into `ROSE_Constraints/`.** A `constraint` class alongside `deform`/`control`/`attribute`, with a `ConstraintType` (matrix / native) per component from the node properties and a `ConstraintKind` (parent / point / orient / scale / aim), so a component says *what* it wants constrained and never *how*. Switching the flag doesn't rebuild live — it raises `needs_rebuild` (amber bar, deliberately not the red invalid bar, which would disable the very build button needed). Six defects fixed on the way, each worth remembering:
  - **`jointOrient` is applied even with the channels at zero**, so a matrix-constrained joint lands rotated by its own orient unless the offset cancels the neutral local matrix. This is true in the no-offset case too — "no offset" means landing *on* the driver, not landing on it rotated.
  - **Since Maya 2020 a node's `parentMatrix` includes its own `offsetParentMatrix`**, so dividing the child's parent out with `child.parentInverseMatrix` feeds the driven plug back into itself. Use the DAG parent's `worldInverseMatrix`, skipped at the world root. The child's parent also has to divide out *in the network*, not folded into the constant — fold it in and it's right at build time and wrong the moment the driver moves.
  - **`importlib.reload` rebuilds each `Enum` class as a new object**, and Enum members hash and compare by *identity* — a module reloaded before its enum module keeps the old class, whose members compare unequal and miss every dict lookup. This raised `KeyError: <ConstraintKind.PARENT>` on the first build after a shelf Reload and silently sent every exposed attribute down the float branch. Guarded three ways: `ROSE_Data/rose_enum.py`'s `enumValue()`, constructors remapping incoming members through their `mapNameTo…` function, and the reload list loading types before their importers.
  - **A control's parent link can never be a native constraint.** A `parentConstraint` owns the child's translate/rotate, so the control stops being posable and snaps back whenever anything upstream re-evaluates. Those links pass `constraint_type = ConstraintType.MATRIX` explicitly, so native mode affects srt inputs, deform links and IK internals while controls keep their channels free.
  - **`connectDecomposeToSRT` drove the target's `rotateOrder` from the decompose's own unset input**, pinning everything connected that way to xyz.
  - **DG nodes survive deleting the component hierarchy**, so the matrix networks accumulated on every rebuild until they were tracked and cleared.

  Migration lesson: the first pass moved only `setMatrixParentWithOffset` and left `setLiveMatrixParentNoOffset` / `setMatrixParentNoOffset` building their own networks outside the class, which is what kept the original bug alive. Worth grepping for *every* helper of a kind before declaring a migration done.

- **Guides, deforms and controls duplicated on every undo/redo.** `ROSE_Node.deserialize()` rebuilt them from the saved data without clearing the existing lists first, and `guide()`/`deform()`/`control()` each append themselves on construction — so deserializing a node that already exists added a whole extra set. `NodeEditorSceneHistory.restoreHistory()` re-deserializes every node in the scene, so one undo doubled the lists, two tripled them, and the Skinning and Attribute tabs listed the same deform or control a dozen times over. Long-standing, not introduced by the tabs that surfaced it. Fixed by clearing the three lists at the top of `deserialize()`; the Maya objects are untouched, since the replacements resolve to the same names and derived ids.

## Backlog (not scheduled into a phase yet)

- **Tab-search to add/find nodes** in the Node Editor (type-to-search node creation, and a way to jump to an existing node by name) — quality-of-life on top of an already-functional editor, not an MVP blocker.
- **Create-new-node-type from the editor** — a UI-driven way to scaffold a new component node (generates a new file in `ROSE_Nodes/Nodes/` with the basic class/registration boilerplate already in place), instead of hand-writing one from scratch each time.
- **Custom node categories** — `ROSE_NODE_GROUPS` (`node_Editor_conf.py`) is currently a fixed dict; adding a new node type means editing that dict directly rather than being able to assign/create a category from the UI.

## Open questions

- ~~Confirm target Maya version(s) for the current UI regression (2025 vs. 2027 mentioned in different conversations).~~ **Resolved: Maya 2027, PySide6 6.8.3.** Only 2023 and 2027 are installed (`/Applications/Autodesk/`), and `maya2027`'s `mayapy` reports PySide6 6.8.3 — the 2025 figure was a stale assumption. Note the README still advertises "Tested Supported Maya Versions: __2023__", which predates the Qt6 port and is now wrong; worth correcting when the docs get a pass.

  Practical side effect: `mayapy` at `/Applications/Autodesk/maya2027/Maya.app/Contents/bin/mayapy` runs PySide6 headlessly with `QT_QPA_PLATFORM=offscreen`, which makes it cheap to check an API question (does this method exist, does this enum resolve, does this ownership rule hold) without opening Maya. Simulating full widget *behaviour* there is unreliable and not worth it.
