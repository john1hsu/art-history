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
| Planner | hourly | repo contents, all issues | 3 new issues labeled `planned` per run (stops at 100 waiting) |
| Builder | hourly | `planned` issues | branch + PR labeled `needs-review` (max 3 open PRs) |
| Reviewer | hourly | `needs-review` PRs | `approved` or `changes-requested` |
| Merger | hourly | `approved` / `changes-requested` PRs | merges, or revises; after 2 revision rounds → `blocked` |

Anything labeled `blocked` is waiting on a human.
