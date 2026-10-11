# `.adub` Format Specification — Draft 1.0.0

**Status:** Draft; suitable for prototyping, not yet a frozen standard.

The keywords **MUST**, **SHOULD**, and **MAY** are used as requirements for compatible implementations.

## 1. Container

1. An `.adub` file MUST be a ZIP archive.
2. The archive MUST contain a UTF-8 JSON file named `project.json` at its root.
3. JSON MUST use UTF-8. Times MUST be seconds from the source video's timeline.
4. Paths to package assets MUST be relative POSIX paths and MUST NOT contain absolute paths or parent traversal (`..`).
5. An application MAY store the source video inside the archive. It MAY instead reference a source video outside the archive; the app should mark whether that external source is currently available.
6. Consumers SHOULD preserve unknown optional fields when editing and re-saving a project.

## 2. Root object

### Required
- `format`: string, exactly `adub`
- `format_version`: string, currently `1.0.0`
- `project`: project metadata object
- `speakers`: array of speaker objects
- `scenes`: array of scene objects
- `events`: array of timed events

### Optional
- `tracks`: timeline/mix track definitions
- `assets`: asset registry
- `extensions`: object for namespaced experimental data

## 3. Project metadata

`project` contains:
- `id`: stable project identifier
- `title`: human-readable title
- `duration_seconds`: duration of the source timeline, or `null` if unknown
- `source`: source media descriptor

`source`:
- `kind`: `video`, `audio`, or `unknown`
- `uri`: optional external URI/path, not necessarily portable
- `asset_path`: optional path to media stored inside the archive
- `media_available`: boolean or `null` if not checked
- `frame_rate`: optional numeric frame rate
- `width`, `height`: optional video dimensions

An application MUST NOT assume an external `uri` will work on another computer.

## 4. Speakers

Each speaker has:
- `id`: stable ID unique within the project
- `label`: display name, e.g. `Narrator`, `Character A`, `Unknown voice 1`
- `speaker_type`: `character`, `narrator`, `background_group`, `unknown`, or `other`
- `voice_description`: optional text description of the voice/personality
- `visual_identity`: optional link to a character identity/visual reference; not proof the character spoke
- `voice_profile_id`: optional voice profile assignment for dubbing
- `notes`: optional human-readable notes

Do not create a separate speaker for every line when evidence indicates the same speaker recurs. Conversely, do not merge speakers solely because they sound similar if evidence is weak.

## 5. Scenes

Each scene has:
- `id`: stable unique ID
- `start`, `end`: interval in seconds
- `description`: concise visual/context description
- `visible_speaker_ids`: speaker/character IDs visibly present, if known
- `visual_observations`: optional observations such as action, shot type, mouth movement, or on-screen text
- `confidence`: optional confidence in the scene interpretation, 0 to 1

Scene descriptions should summarize relevant context, not claim that a visible character is speaking without evidence.

## 6. Events

Each event has:
- `id`: stable unique ID
- `start`, `end`: event interval in seconds (`start` MUST be <= `end`)
- `event_type`: `speech`, `sound_effect`, `music`, `ambience`, or `other`
- `speech_kind`: for speech events, one of `dialogue`, `narration`, `inner_thought`, `background_dialogue`, `announcement`, `singing`, `uncertain`, or `other`
- `speaker_id`: speaker ID or `null` when unknown
- `screen_presence`: `on_screen`, `off_screen`, `voiceover`, `not_applicable`, or `unknown`
- `source_text`: original-language transcription, or `null` if non-speech/unintelligible
- `language`: BCP-47 language tag if known, e.g. `ja`, `en`, `hi`
- `translation`: optional object with `text`, `language`, and `adaptation_notes`
- `acting`: optional object with `emotion`, `delivery`, `intensity`, `direction`, and `review_required`
- `confidence`: optional object with `transcription`, `speaker`, `speech_kind`, and `screen_link` numeric values between 0 and 1
- `overlap_group`: optional string ID shared by events that overlap intentionally
- `source_audio`: optional asset path or source-audio segment reference
- `dub_audio`: optional generated audio asset reference
- `word_timings`: optional array of word/token timing objects
- `review_status`: `unreviewed`, `needs_review`, `confirmed`, or `rejected`
- `notes`: optional human-readable notes

The values in `speech_kind` and `screen_presence` are independent. Narration is commonly voiceover, but the format does not force that assumption. Background dialogue can be off-screen or on-screen.

### Word timing
Each word timing item may contain:
- `text`: word or token
- `start`, `end`: seconds
- `confidence`: optional number between 0 and 1

Word timings are optional; never fabricate them when the engine cannot provide them.

## 7. Voice profiles and generated audio

Voice profiles are referenced by `voice_profile_id` and MAY be described in an optional root-level `voice_profiles` array in future-compatible implementations. In this draft, implementations may also store profile definitions under `extensions` using a namespaced key, for example `extensions["org.example.voice_profiles"]`.

A generated audio file should be referenced by package-relative `dub_audio` or registered under `assets`. Each line may have multiple takes; implementations can place a list under a namespaced extension until a standard takes field is added.

A project file MUST NOT contain service API keys, passwords, access tokens, or private credentials.

## 8. Tracks and mixing

`tracks` is optional. Each track has `id`, `label`, `kind` (`dialogue`, `narration`, `music`, `effects`, `ambience`, or `other`), and optional `speaker_id`, `gain_db`, and `muted`.

Events can reference a `track_id`. Events with intersecting time intervals are allowed and SHOULD be played simultaneously unless explicitly muted or excluded by the editor.

## 9. Assets

Each asset has `id`, `path`, `media_type`, and optional `role`, `duration_seconds`, `sample_rate`, `channels`, `language`, and `notes`. `path` is relative to the package root. Asset metadata does not guarantee that a file is present; importers should report missing assets.

## 10. AI uncertainty and review

- Confidence values are estimates, not guarantees.
- `null` means unknown or unavailable; it MUST NOT be interpreted as false.
- If a voice cannot confidently be matched to a visible character, leave the screen link unknown and flag review.
- Keep manually confirmed information distinguishable from automatic inference. An implementation MAY add `origin: "manual" | "automatic" | "imported"` to observations in a later compatible revision.
- The format stores results and evidence; it does not itself perform transcription, scene understanding, translation, or lip-sync.

## 11. Compatibility

- Readers MUST reject or clearly report an unsupported major version.
- Readers SHOULD ignore unknown optional fields without losing them on save.
- New optional fields may be added in compatible minor revisions.
- Existing field meanings MUST NOT be silently changed after v1 is frozen.

## 12. Privacy, rights, and scope

The format has no account system, database, security subsystem, skin/theme system, or AI service dependency. These are outside its scope. Applications may independently perform basic archive/path validation when importing files. Users are responsible for having appropriate rights to media and voice assets they process.
