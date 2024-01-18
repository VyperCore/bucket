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
    sql_files = []
    for sql_path in sql_paths:
        if sql_path.is_dir():
            sql_files += sql_path.iterdir()
        else:
            sql_files.append(sql_path)

    merged_reading = None
    for sql_file in sql_files:
        sql_accessor = SQLAccessor.File(sql_file)
        reading_iter = iter(sql_accessor.read_all())
        if merged_reading is None:
            if (first_reading := next(reading_iter, None)) is None:   
                continue
            merged_reading = MergeReading(first_reading)
        merged_reading.merge(*reading_iter)

    output_accessor = SQLAccessor.File(output)
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
def read(sql_path: Path, axes: bool, goals: bool, points: bool, summary: bool):
    writer = ConsoleWriter(axes=axes, goals=goals, points=points, summary=summary)
    for reading in SQLAccessor.File(sql_path).read_all():
        writer.write(reading)

if __name__ == '__main__':
    cli()
