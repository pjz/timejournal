import os
import re
import sys
import shutil
import logging
from types import SimpleNamespace
from datetime import datetime
from pathlib import Path

import click

logger = logging.getLogger(__file__)


def _cur_entry_name() -> str:
    return datetime.now().strftime("%Y%m%d")


def _base_journal_path() -> Path:
    default: str = os.path.expanduser("~/.config/tj")
    base = Path(os.environ.get('TJ_DIR') or default)
    if not base.is_dir():
        if base.exists():
            print(f"Error: {base} exists but isn't a directory.")
            sys.exit(1)
        base.mkdir(parents=True, exist_ok=True)
    return base


def current_journal_path() -> Path:
    """
    return the Path of the journal for this moment in time
    """
    base, cur = _base_journal_path(), _cur_entry_name()
    entries = list(base.glob(cur + "*.md"))
    if not entries:
        return base / (cur + ".md")
    logger.debug("Current journal path found entries: %r", entries)
    latest = sorted(entries)[-1]
    return latest


def cd_basedir():
    '''
    chdir to the basedir to help $EDITORs
    '''
    os.chdir(current_journal_path().parent)


def next_journal_path() -> Path:
    """
    return the Path of a new journal entry
    """
    base, cur = _base_journal_path(), _cur_entry_name()
    entries = base.glob(cur + "*.md")
    if not entries:
        return base / (cur + ".md")
    latest: Path = sorted(entries)[-1]
    head, _md = latest.name.rsplit('.', 1)
    i = 0
    if '.' in head:
        head, i = head.rsplit('.', 1)
        i = int(i)
    i += 1
    return base / f'{head}.{i:05}.md'


def edit_journal(context, filename: Path | str) -> None:
    '''internal common code for comp/repl/dist/medit'''
    cd_basedir()
    editor = context.obj.editor
    template = context.obj.template
    if template and not Path(filename).exists():
        shutil.copyfile(template, filename)
    try:
        _ = os.system(f"{editor} {filename}")
    except Exception as e:
        print(f"Exception editing {filename}: {e}", file=sys.stderr)


@click.group
@click.option('--editor', help='Editor to use when editing entries (or set TJ_EDITOR, VISUAL, or EDITOR)')
@click.option('--debug/--no-debug', default=False, help='Enable global debugging (or set TJ_DEBUG)')
@click.option('--entryspec', default="%Y%m%d", help='Entry filename spec (or set TJ_ENTRYSPEC) using python strftime', show_default=True)
@click.pass_context
def cli(ctx, editor, debug, entryspec):
    """
    TJ - the Time Journal
    Helps keep journal entries with time-based names.
    For now they're hard-coded to YYYYmmdd
    """
    ctx.ensure_object(SimpleNamespace)

    env = os.environ
    ctx.obj.editor = editor or env.get('VISUAL') or env.get('EDITOR')

    ctx.obj.debug = debug
    if debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)

    # override this global so it's easily available to all commands
    def _make_entry_name() -> str:
        return datetime.now().strftime(entryspec)
    global _cur_entry_name
    _cur_entry_name = _make_entry_name

    ctx.obj.template = None

@cli.command()
@click.option('-e', '--editor', help="Editor to use")
@click.pass_context
def new(ctx):
    """
    Force the creation of a new journal entry.
    If there's already one for this time period, a .XXXXX suffix will be added to the date
    """
    edit_journal(ctx, next_journal_path())


@cli.command()
@click.pass_context
def edit(ctx):
    """
    Edit the current (aka latest) journal entry.  If no current entry exists, create an empty one and edit that.
    """
    cur: Path = current_journal_path()
    edit_journal(ctx, cur)


HEADER_PATTERN = re.compile(r'^\s*(#+)\s*(.*)\s*#*\s*$')


def headers_and_match(text: str, matcher: re.Pattern) -> list[str]:

    result = []
    headers = [''] * 100
    for line in text.splitlines():
        s = HEADER_PATTERN.match(line)
        if s:
            depth, header = len(s.group(1)), s.group(2)
            headers[depth] = header
        elif matcher.search(line):
            result.extend([h for h in headers if h])
            result.append(line)

    return result


@cli.command()
@click.option('-l', '--listfiles', is_flag=True, help="Show just the list of matching files")
@click.option('-s', '--sections', is_flag=True, help="Show the section headers up to each match")
@click.argument('keyword', nargs=-1, required=True)
def search(keyword, listfiles, sections):
    """
    Search journal for keywords.  By convention tags are '@tagname'.
    For now just prints out the matching filenames.
    Later, should show the nested headers down to where the match is, and some lines of context.
    """

    entries = _base_journal_path().rglob('*.md')

    kw_re = '(' + '|'.join(keyword) + ')'
    kw_pattern = re.compile(kw_re)

    for entryfile in entries:
        with open(entryfile) as f:
            text = f.read()
            if not kw_pattern.search(text):
                continue
            if listfiles:
                print(entryfile)
            elif sections:
                print(*headers_and_match(text, kw_pattern))



@cli.command()
@click.pass_context
def basedir(ctx):
    """
    Print out the journal directory
    """
    basedir: Path = current_journal_path().parent
    print(basedir)


def main():
    cwd = Path.cwd()
    cli(auto_envvar_prefix='TJ')
    os.chdir(cwd)


if __name__ == '__main__':
    main()
