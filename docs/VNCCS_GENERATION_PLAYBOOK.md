# VNCCS Generation Playbook

This is the operational runbook for generating and validating VNCCS characters on the local ComfyUI installation.

Use it when creating a new character, cloning an existing character, generating outfits, generating emotions, or automating those flows with an agent.

## 1. Runtime prerequisites

- Start ComfyUI Desktop and wait until the ComfyUI frontend is fully loaded.
- Do not assume port `8188`. Character Studio resolves the active local ComfyUI endpoint and exports it as `VNCCS_COMFY_URL`; an explicit `VNCCS_COMFY_URL` override wins. On 2026-09-20 the active Desktop instance is `http://127.0.0.1:8001` and runs with Manager enabled.
- Keep the ComfyUI frontend open for any workflow that contains **VNCCS Pose Studio**.
- Pose Studio renders images in the browser with WebGL and uploads them to the backend during execution.
- A backend-only/API run can fail with `Pose Studio did not receive images rendered by the browser widget` if no live frontend capture is available.
- Do not disable browser hardware acceleration/WebGL for Pose Studio workflows.

Canonical editable workflows live under:

`C:\Users\user\Documents\ComfyUI\user\default\workflows\VNCCS`

Installed source workflows live under:

`C:\Users\user\Documents\ComfyUI\custom_nodes\ComfyUI_VNCCS\workflows`

Do not edit installed source workflows for one-off runs. Work from a user workflow copy or a per-run copy.

## 2. Model policy

Treat ComfyUI `folder_paths` as the authoritative model inventory.

Before downloading or copying a model:

1. Check the primary ComfyUI model directories.
2. Check every directory registered through `extra_model_paths.yaml`.
3. Reuse a compatible installed model when one already exists.
4. Preserve canonical nested names such as `anima\qwen_3_06b_base.safetensors`.
5. If two registered models share the same basename, use the full canonical nested name.

For this machine, useful installed Qwen Image Edit 2511 choices include:

- Q4 GGUF: `models\unet\qwen-image-edit-2511-Q4_0.gguf`
- NVFP4: `models\diffusion_models\qwen_image_edit_2511_nvfp4.safetensors`

If Control Center is set to Q5 but Q5 is not installed, switch it to an installed compatible variant instead of downloading another copy just to satisfy the selector.

Anima assets are available through the configured extra model path. Known canonical names are:

- diffusion: `anima\anima-base-v1.0.safetensors`
- text encoder: `anima\qwen_3_06b_base.safetensors`
- VAE: `anima\qwen_image_vae.safetensors`

## 3. Standard pipeline

Use the workflows in this order:

1. `VNCCS_3.0_Step1_CharacterCreator.json` for a new character.
2. `VNCCS_3.0_Step1_CharacterCloner.json` instead of Creator when starting from an existing character image.
3. `VNCCS_3.0_Step2_CharacterClothes.json` after the base character exists.
4. `VNCCS_3.0_Step3_CharacterEmotions.json` after the character and desired costumes exist.
5. `VNCCS_MigrationAssistant.json` only when migrating older VNCCS data.

### Character discovery pre-stage

Use this before Character Creator/Cloner when the user does not already have a finished character description.

Supported intake modes:

1. **Generate visual samples** — create numbered candidate previews from broad constraints using curated/random traits, then ask the user only to choose a candidate number or reroll.
2. **Reference image** — analyze a supplied image and extract permanent character identity automatically.
3. **Guided plain-language choices** — map friendly choices such as hair length/color family, eye color family, build, and distinctive feature into generation-ready character data.
4. **Existing description** — preserve the current fast path.

For visual samples, use the production **VNCCS Character Studio** as the primary intake surface:

`/home/user/projects/temp/ai-apps/.personal-projects/chatgpt-plans/playbooks/vnccs-generation-wizard/vnccs-character-studio.sh`

The studio:
- collects broad human constraints rather than raw tags, including explicit sex (`Female` / `Male` / `Surprise me`) separately from presentation;
- generates deterministic candidate identities from the installed Portrait Master vocabulary;
- renders numbered previews through the real VNCCS `/vnccs/preview_generate` path using the same selected generation engine/model/sampler/CFG/LoRA/character settings that Production will execute;
- keeps comparison pose/expression/background/transient clothing neutral;
- keeps active discovery working state under `/tmp/vnccs-discovery/<run-id>/` and copies completed casting images/state durably to `output/VNCCS/CharacterDiscovery/<run-id>/`;
- lets the user select one take or reroll;
- analyzes the selected rendered take with WD EVA02 v3;
- applies a deterministic permanent-identity whitelist/denylist locally so clothing, underwear, pose, expression, background, injury/state, and similar transient tags are not baked into base identity;
- falls back to the deterministic candidate metadata only for permanent fields the rendered-image tagger did not resolve;
- collects poses/outfits/emotions and writes the authoritative `/tmp/<timestamp>-<character>.md` + `.json` brief for end-to-end execution;
- exposes real installed-workflow controls for generation/model/encoder/VAE selection, DMD/Age/five-slot LoRAs, Anima Turbo, resolution/sampler/scheduler/steps/CFG/seed behavior, Creator background/NSFW/prompts, full Pose Studio anatomy/camera/view/lighting, Clothes LoRA and garment fields, Emotion detector/SAM/device/detailer/inpaint settings, chroma/SAM3 detail recovery, SeedVR seed/batching/noise/attention/tile/cache output settings, and the separate VNCCS Control Center edit-model family used by Pose and Clothes generation;
- writes those controls under `workflow_options` in the structured brief so the runner and saved reusable workflows use the same settings rather than reverting to template defaults.

Keep the two model paths distinct. `workflow_options.generation` configures Character Creator/Emotion generation such as Anima or Illustrious. `workflow_options.control_center` configures the `VNCCS_ControlCenter` pipe used by Pose and Clothes editing. VNCCS Control Center merges its packaged catalog with compatible local models enumerated through ComfyUI `folder_paths`; registered `extra_model_paths` are therefore authoritative and models must not be copied into the default model tree just to make them selectable. Character Studio consumes that merged inventory, supports `QIE2511` and `Klein9b` editing, exposes compatible Anima/Illustrious generation models, disables missing catalog entries, and writes the selected family, model type/name, sampler, scheduler, steps, and CFG into the workflow's serialized Control Center state. For Klein9b, the native Control Center resolves the Klein Qwen text encoder, Flux 2 VAE, and Klein-specific VNCCS Pose/Clothes helper LoRAs.

If the studio is unavailable or a non-visual/terminal workflow is explicitly preferred, fall back to the helper/contact-sheet path.

For external reference images, prefer VNCCS Character Cloner `Analyze Captions` because it already returns structured character attributes. The verified local analysis stack includes VNCCS Qwen2.5-VL Q4 + F16 mmproj, Florence PromptGen Base/Large, WD EVA02 v3, JoyCaption beta-one, and TagFilter. QwenVL remains preferred for Cloner/reference-image structured extraction; use Florence/WD/TagFilter or JoyCaption selectively as complementary evidence rather than invoking every analyzer on every run.

Never require the user to know booru/Danbooru tag names.

Permanent identity includes hair, eyes, skin/face details, build/silhouette, fantasy anatomy, and stable identifying accessories. Pose, expression, temporary clothes, background, lighting, and camera are transient and belong to later VNCCS stages.

### End-to-end mode

Use end-to-end mode when the request says full process, complete pipeline, full chain, start to finish, or comes from the VNCCS generation wizard with `mode: end-to-end`.

For a Character Studio or terminal-wizard JSON brief, the primary executable path is:

```bash
/home/user/.agents/skills/vnccs-workflows/scripts/run_fullchain.py \
  --job /tmp/<timestamp>-<character>.json
```

Character Studio exposes the same runner as **Run full VNCCS chain** in Production.

The runner uses committed Creator, Clothes, and Emotions templates. It owns the headed `comfyui-vnccs` Pose Studio capture step, registers requested costumes, submits the proven API workflow shapes to ComfyUI, requires successful prompt history, verifies versioned outputs, creates contact sheets, and writes transient state under `/tmp/vnccs-fullchain/<execution-id>/`. It also archives `job.json`, `state.json`, and `RUN_REPORT.md` durably under `output/VNCCS/RunHistory/<character>/<run-id>/`.

For multi-pose generation, the runner resolves default poses from installed Pose Studio library assets and copies their actual skeletal state into the Creator workflow. Character Studio Define exposes the same installed library with previews/search/category filtering and writes explicit picks to `poses.assets`. Pose prompts remain separate text instructions. Do not create pose variants by cloning one pose and changing only `prompt`; that produces duplicate browser captures. The runner rejects duplicate skeletal states. A structured job may override defaults with `poses.assets`, where each entry identifies a Pose Studio asset by `name`, `category`, and optional `repository`. Execution capture IDs are fresh per headed-browser capture, and the backend treats that uploaded capture set as the authoritative execution snapshot with an expected count.

Runs are convergent. If base, poses, an outfit, or requested emotion artifacts already exist and verify correctly, the runner skips that completed stage unless forced. Use `--force` for the whole run or repeat `--force-stage` with `base`, `poses`, `clothes:<outfit>`, or `emotions:<outfit>`. Upstream force requests include dependent downstream stages automatically. Character Studio exposes the same policy through Production's **Regenerate existing outputs** and Library's per-stage buttons. Restart the same JSON brief after an interruption instead of rebuilding state manually.

To keep the generated workflows for later manual editing/reuse, enable **Save reusable Creator, Clothes, and Emotions workflows to my ComfyUI user workflows** in Character Studio Production or run with `--save-user-workflows`. The runner saves normal UI workflows under `C:\Users\user\Documents\ComfyUI\user\default\workflows\VNCCS\Saved Runs\<character>\<run-id>\`, preserving the run's character, poses, costume settings, and requested emotions. These files must reopen directly in ComfyUI without relying on agent state or the last active browser character.

Saved user workflows are permanent until the user deletes them manually. Generated character assets/sheets, `output/VNCCS/CharacterDiscovery`, and `output/VNCCS/RunHistory` are also durable. Character Studio may prune only completed working data under `/tmp/vnccs-discovery/` and `/tmp/vnccs-fullchain/` when the user presses the Production cleanup button. Cleanup must preserve active/current runs and must never delete durable output/history/workflow trees.

In this mode, the generation agent must:

1. Run Character Creator or Character Cloner according to the request.
2. Verify the base-character and requested pose outputs before advancing.
3. Run Clothes for every requested outfit.
4. Verify each outfit before advancing to emotions.
5. Run Emotions for every requested outfit/emotion combination.
6. Continue automatically between successful stages instead of returning control after each workflow.
7. Stop only for an unrecoverable blocker, missing required user input, or an explicitly requested human checkpoint.
8. Finish by reporting the stages executed, models actually used, output counts, and exact output directories.

Wizard-generated choices are already-resolved requirements. Do not ask the user to repeat choices present in the brief.

### Character Studio Output Library

Use Character Studio's **Library** to inspect durable outputs after generation. The catalog is derived from the filesystem, not a separate database. It includes character sprites/faces/sheets, durable discovery takes, durable run records, and saved reusable workflows. Search/filter current outputs or include historical versions as needed. Use Library actions to open output/report/workflow folders, view reports, load a saved workflow into the managed ComfyUI tab, or regenerate an entire archived run or one stage from its durable `job.json`. When the native VNCCS generator cache for that stage is available, Library can also regenerate one cached pose, clothes-neutral output, or emotion output without rerunning the whole stage. Production exposes live stage progress and fresh output previews.

Pruning `/tmp` must not remove anything required by Library regeneration.

### Character Creator

1. Open `VNCCS_3.0_Step1_CharacterCreator` in the ComfyUI frontend.
2. In **VNCCS Control Center**, select an installed model variant.
3. In **VNCCS Character Creator V2**, create or select the character.
4. Choose Illustrious or Anima and confirm generation settings.
5. Use **GENERATE PREVIEW** until the base appearance is correct.
6. Configure **VNCCS Pose Studio** with the body proportions and poses you want.
7. Confirm Pose Studio has visibly initialized in the browser before running.
8. Configure Character Generator upscaling/background removal only as needed.
9. Press **Run** from the frontend.
10. Keep the browser tab open until the workflow completes.

### Character Cloner

Use the Cloner when the starting point is an existing image.

- Prefer a clear, high-quality, full-body source image.
- Analyze or enter character tags.
- Check inferred character details before generation.
- Configure Pose Studio exactly as for Character Creator.
- Choose a background color that does not conflict with important hair, eye, or clothing colors.
- Run from the frontend and keep the Pose Studio browser context alive.

### Clothes

1. Open `VNCCS_3.0_Step2_CharacterClothes`.
2. Select the existing VNCCS character.
3. Create a named costume.
4. Describe clothing manually, use Clothes Wizard, or clone clothes from an image.
5. Put persistent face details such as glasses in the face field and hats/headwear in the head field.
6. Generate a preview first.
7. Configure Pose Studio if the workflow uses it.
8. Run from the frontend.
9. Repeat with a new costume name for additional outfits.

### Emotions

1. Open `VNCCS_3.0_Step3_CharacterEmotions`.
2. Select the character and one or more costumes.
3. Start with a small emotion set while tuning settings.
4. Choose the generation model.
5. Tune Face Detailer Denoise: higher values increase expression strength but can reduce identity consistency.
6. Run the workflow.
7. Expand to the full emotion set only after the test results look correct.

## 4. Output map

All character outputs are rooted at:

`C:\Users\user\Documents\ComfyUI\output\VNCCS\Characters\<CharacterName>\`

Important locations:

- Base/final neutral sprites: `Sprites\Naked\Neutral\`
- Costume sprites: `Sprites\<CostumeName>\Neutral\`
- Emotion sprites: `Sprites\<CostumeName>\<EmotionName>\`
- Emotion face crops: `Faces\<CostumeName>\<EmotionName>\`
- Character config: `<CharacterName>_config.json`
- Preview image: `cache\preview.png`
- Costume preview: `cache\preview_<CostumeName>.png`
- Contact sheets: `Sheets\Naked\Neutral\sheet_neutral.png` and `Sheets\<CostumeName>\Contact\sheet_contact.png`
- Durable casting archive: `..\..\CharacterDiscovery\<run-id>\`
- Durable full-chain history: `..\..\RunHistory\<character>\<run-id>\`
- Per-run/intermediate pose stages: `cache\poses\<node-id>\`

Inside a pose cache directory, common artifacts include:

- `pose_generation_XX.png`: generated pose result before later stages
- `upscaler_XX.png`: upscaled pose stage
- `bg_remove_XX.png`: background-removed stage
- `_stage_cache\`: serialized intermediate tensors/state used by VNCCS

Pose Studio's editable pose definitions live in the workflow/widget state. The final rendered character poses are the PNG assets written to the sprite and cache directories above.

## 5. Verification checklist

A generation is complete only when all applicable checks pass:

- ComfyUI history reports `execution_success`.
- No active or pending queue item remains.
- Expected sprite count exists in the character output directory.
- Generated PNGs are non-empty and visually inspectable.
- Character configuration exists and references the intended character/costume.
- Pose Studio workflows show successful browser-side capture upload during execution.
- No workaround model download or duplicate was created when a compatible installed model already existed.

For Pose Studio runs, successful frontend sync normally includes HTTP 200 requests to:

- `/vnccs/pose_captures_upload`
- `/vnccs/pose_sync/upload_capture`

## 6. Failure recovery

### Pose Studio says it did not receive browser-rendered images

Cause: the backend executed without usable browser/WebGL capture state.

Recovery:
1. Start ComfyUI Desktop.
2. Open the exact workflow in the frontend.
3. Wait for Pose Studio to initialize.
4. Keep the tab open.
5. Run from that frontend.

Do not attempt to fix this error by moving or downloading models.

### Control Center says a model is not downloaded

1. Check whether the selected variant actually exists.
2. Check all registered extra model paths.
3. If an equivalent compatible model is already installed, select that installed variant.
4. Only download when the required model is genuinely absent.

Example: if Q5 is selected but only Q4 is installed, switch the selector to Q4 rather than treating the workflow as broken.

### A bare Anima filename is rejected

Use the canonical nested ComfyUI name returned by `folder_paths`, for example:

`anima\qwen_3_06b_base.safetensors`

Do not recreate a duplicate at the ComfyUI model root just to satisfy a stale basename.

### Step 2 or Step 3 fails even though the workflow validates

Workflow validation does not guarantee character state exists.

- Step 2 requires an existing generated VNCCS character.
- Step 3 requires an existing character and the target costume state.

### Sheets directory is empty

An empty `Sheets` directory does not by itself mean generation failed. VNCCS can successfully produce individual sprites, faces, and cached pose stages without compiling a sheet in that run.

## 7. Agent execution

For automated runs:

1. Create a per-run workflow copy.
2. Validate before editing.
3. Discover stable workflow slots instead of hand-editing arbitrary JSON.
4. Parse and re-serialize JSON-string widgets such as `widget_data` and `pose_data`.
5. Validate again after overrides.
6. For Pose Studio workflows, drive the run through the headed ComfyUI frontend or otherwise ensure the browser capture sync is active.
7. For workflows without a browser-rendered dependency, backend/API execution is acceptable.
8. Inspect ComfyUI history and the VNCCS output tree before declaring success.
9. Preserve user/runtime data, including PoseLibrary and character output state.

The goal is a reproducible pipeline: reuse installed assets, keep workflow state explicit, generate through the correct frontend/backend path, and verify the actual files produced.
