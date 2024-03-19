# Time Journal (aka tj)

...it came to me in a dream...

...well, okay, not a dream, but I was definitely falling asleep at the time.  Noting that jrnl wasn't quite right, that zettlekasten had some good ideas, and that the simplicity of an ancient perl script called pjphone was quite nice.

Alas, the simplicity didn't survive so well, but hopefully this is an improvement on jrnl, and can be used for zettlekasten.

## Installation

`pip install timejournal` should work eventually.  For now you might need to do `pip install git+https://github.com/pjz/timejournal.git`

## Usage

It's written using [click], with lots of docstrings, so `tj --help` should get you quite far.

# TODO:

  * [ ] dynamic templates to substitute in the entryname, as well as ... ?
  * search infra
      * [ ] `reindex` command to (re)build a full-text index on specified file (or all)
      * [ ] `autoindex` flag to automatically add `new`/`edit`ed entries to the index
      * [ ] have `search` use the index
  * search output
      * [x] matching filenames
      * [ ] N context lines on each side (default: 1 or 2)
      * [ ] headers upward through the tree
        * [ ] ..and full containing section
      * [ ] `--latest` show only latest (default 10) matches
  * `tags` command to list all tags

---
[click]: https://click.palletsprojects.com
