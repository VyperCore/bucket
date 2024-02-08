from pathlib import Path
import click
from .rw import SQLAccessor, MergeReading, ConsoleWriter

@click.group()
def cli():
    pass

@cli.command()
@click.option('--sql-path', 'sql_paths',
              help='Path to an SQL db file, or a directory containing ONLY SQL db files',
              multiple=True,
              type=click.Path(exists=True, readable=True, path_type=Path, resolve_path=True))
@click.option('--output',
              help='Path to output the merged SQL db file',
              required=True,
              type=click.Path(path_type=Path))
def merge(sql_paths: tuple[Path], output: Path):
    output_accessor = SQLAccessor.File(output)
    merged_reading = SQLAccessor.merge_files(*sql_paths)
    if merged_reading:
        output_accessor.write(merged_reading)

@cli.command()
@click.option('--sql-path',
              help='Path to an SQL db file',
              required=True,
              type=click.Path(exists=True, readable=True, path_type=Path))
@click.option('--axes/--no-axes', default=False)
@click.option('--goals/--no-goals', default=False)
@click.option('--points/--no-points', default=False)
@click.option('--summary/--no-summary', default=True)
@click.option('--record', default=None, type=click.INT)
def read(sql_path: Path, axes: bool, goals: bool, points: bool, summary: bool, record: int|None):
    print(f"{record=}")
    writer = ConsoleWriter(axes=axes, goals=goals, points=points, summary=summary)
    if record is None:
        for reading in SQLAccessor.File(sql_path).read_all():
            writer.write(reading)
    else:
        reading = SQLAccessor.File(sql_path).read(record)
        writer.write(reading)


if __name__ == '__main__':
    cli()
