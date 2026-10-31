# Art History

A growing, cited collection of articles on art history — movements, artists, works, techniques, and the ideas that connect them.

## Structure

```
articles/
  movements/      # e.g. impressionism.md, bauhaus.md
  artists/        # e.g. artemisia-gentileschi.md
  works/          # e.g. las-meninas.md
  techniques/     # e.g. sfumato.md, lost-wax-casting.md
  themes/         # cross-cutting ideas: patronage, iconography, the gaze
index.md          # table of contents, grouped by category
```

## Article conventions

Every article:

- Is original prose (no copied passages from any source).
- Starts with YAML front matter: `title`, `category`, `period`, `related` (list of other article slugs), `sources`.
- Ends with a **Sources** section listing at least two reputable references (museum sites, university presses, peer-reviewed journals, major encyclopedias) with URLs.
- Links to related articles with relative Markdown links so the collection reads as a knowledge graph.
- Is a single new topic — check `index.md` before writing to avoid duplicates.

## How this repo is maintained

Four scheduled Claude jobs run the pipeline. Labels are the state machine:

| Job | Runs | Reads | Writes |
|---|---|---|---|
| Planner | hourly | repo contents, all issues | 1 new issue labeled `planned` per run |
| Builder | hourly | `planned` issues | up to 2 PRs labeled `needs-review` per run (max 6 open PRs) |
| Reviewer | hourly | `needs-review` PRs | up to 4 per run → `approved` or `changes-requested` |
| Merger | hourly | `approved` / `changes-requested` PRs | up to 4 per run: merges, or revises; after 2 revision rounds → `blocked` |

Anything labeled `blocked` is waiting on a human.
