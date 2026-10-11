# `.adub` — AI Anime Dubbing Project Format

An open, model-independent project format for representing anime/video dialogue, narration, off-screen speech, background voices, inner thoughts, scene context, translations, generated voices, and synchronization data.

## Goals

- One interoperable project format shared by a transcriber, Hindi voice studio, and sync/dubbing editor.
- Keep observed facts separate from AI guesses and make uncertainty explicit.
- Preserve exact timing and overlapping speech.
- Keep the format independent of any AI provider, app framework, database, or UI theme.
- No accounts, authentication, API credentials, or database are part of the format.

## Package design

An `.adub` file is a ZIP archive with the `.adub` extension. Its required entry point is `project.json`.

Minimal package:

```text
episode.adub
└── project.json
```

Packages may include additional JSON and media assets:

```text
episode.adub
├── project.json
├── media/
│   ├── source-video.mp4          # optional; projects may reference an external file instead
│   └── audio/
│       ├── line-0001.wav
│       └── line-0002.wav
└── exports/
    └── transcript.srt            # optional convenience export
```

Applications must not assume optional files exist. Paths stored inside the package are relative POSIX paths (for example `media/audio/line-0001.wav`). Do not put API keys, passwords, or other credentials in a project file.

## Version 1 core

- `format`: must be `adub`
- `format_version`: semantic version string; this first draft uses `1.0.0`
- `project`: project metadata and source media reference
- `speakers`: speaker/character/narrator identities
- `scenes`: visual scene intervals and contextual observations
- `events`: timed audio/dialogue/narration/thought/sound events
- `tracks`: optional mix/timeline track definitions
- `assets`: optional media asset registry
- `extensions`: optional namespaced extra data

Read [SPECIFICATION.md](SPECIFICATION.md) for normative field definitions and [schema/adub-v1.schema.json](schema/adub-v1.schema.json) for a JSON Schema starter.

## Important behavior

- A speaker may be unknown: use `speaker_id: null` and record uncertainty rather than inventing an identity.
- A voice can be off-screen while still belonging to a known character.
- Multiple events may overlap in time. Consumers must preserve overlaps; do not flatten events into a single sequential subtitle list.
- `speech_kind` and `screen_presence` are separate. For example, narration may play while a character is visible.
- Visual identity and speaker identity links should be recorded as hypotheses with confidence, not absolute truth, unless manually confirmed.
- Times are seconds from the beginning of the source timeline, as decimal numbers.
- The schema validates structure, not whether AI inferences are correct.

## Status

This is an initial draft for review. Before declaring v1 stable, validate it against sample episodes and all three applications. Once stable, avoid changing existing field meanings; add compatible optional fields where possible.

## License

Released under the MIT License. See [LICENSE](LICENSE).
