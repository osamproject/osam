import datetime
import json
import sys

import click
import numpy as np
import PIL.Image
import uvicorn

from samuel import _humanize
from samuel import _models
from samuel import _tabulate
from samuel import _types
from samuel import apis


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli():
    pass


@cli.command(help="Help about any command")
@click.argument("subcommand", required=False, type=str)
@click.pass_context
def help(ctx, subcommand):
    if subcommand is None:
        click.echo(cli.get_help(ctx))
        return

    subcommand_obj = cli.get_command(ctx, subcommand)
    if subcommand_obj is None:
        click.echo(f"Unknown subcommand {subcommand!r}", err=True)
        click.echo(cli.get_help(ctx))
    else:
        click.echo(subcommand_obj.get_help(ctx))


@cli.command(help="List models")
def list():
    rows = []
    for model in _models.MODELS:
        size = model.get_size()
        modified_at = model.get_modified_at()

        if size is None or modified_at is None:
            continue

        rows.append(
            [
                model.name,
                model.get_id(),
                _humanize.naturalsize(size),
                _humanize.naturaltime(datetime.datetime.fromtimestamp(modified_at)),
            ]
        )
    print(_tabulate.tabulate(rows, headers=["NAME", "ID", "SIZE", "MODIFIED"]))


@cli.command(help="Pull a model")
@click.argument("model_name", metavar="model", type=str)
def pull(model_name):
    for cls in _models.MODELS:
        if cls.name == model_name:
            break
    else:
        click.echo(f"Model {model_name} not found.", err=True)
        sys.exit(1)

    click.echo(f"Pulling {model_name!r}...", err=True)
    cls.pull()
    click.echo(f"Pulled {model_name!r}", err=True)


@cli.command(help="Remove a model")
@click.argument("model_name", metavar="model", type=str)
def rm(model_name):
    for cls in _models.MODELS:
        if cls.name == model_name:
            break
    else:
        click.echo(f"Model {model_name} not found.", err=True)
        sys.exit(1)

    click.echo(f"Removing {model_name!r}...", err=True)
    cls.remove()
    click.echo(f"Removed {model_name!r}", err=True)


@cli.command(help="Start server")
@click.option("--reload", is_flag=True, help="reload server on file changes")
def serve(reload):
    click.echo("Starting server...", err=True)
    uvicorn.run("samuel._server:app", host="127.0.0.1", port=11368, reload=reload)


@cli.command(help="Run a model")
@click.argument("model_name", metavar="model", type=str)
@click.option(
    "--image",
    "image_path",
    type=click.Path(exists=True),
    help="image path",
    required=True,
)
@click.option("--prompt", type=json.loads, help="prompt")
def run(model_name, image_path, prompt):
    try:
        response = apis.generate_mask(
            request=_types.GenerateMaskRequest(
                model=model_name,
                image=np.asarray(PIL.Image.open(image_path)),
                prompt=prompt,
            )
        )
    except ValueError as e:
        click.echo(e, err=True)
        sys.exit(1)
    click.echo(response.model_dump_json())


if __name__ == "__main__":
    cli()
