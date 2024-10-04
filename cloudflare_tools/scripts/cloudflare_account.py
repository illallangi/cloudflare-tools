import click
from json import dumps
from tabulate import tabulate

from more_itertools import one

from cloudflare_tools.account import CloudflareAccount


@click.group
@click.pass_context
@click.option(
    "--cloudflare-account-id",
    type=click.STRING,
    envvar="CLOUDFLARE_ACCOUNT_ID",
    help="Cloudflare Account ID",
    required=True,
)
@click.option(
    "--cloudflare-api-token",
    type=click.STRING,
    envvar="CLOUDFLARE_API_TOKEN",
    help="Cloudflare API Token",
    required=True,
)
def cli(
    ctx: click.Context,
    cloudflare_account_id: str,
    cloudflare_api_token: str,
):
    ctx.obj = {
        "CloudflareAccount": CloudflareAccount(
            api_token=cloudflare_api_token,
            account_id=cloudflare_account_id,
        ),
    }


@cli.command()
@click.pass_context
@click.option(
    "--json",
    is_flag=True,
)
def tunnels(
    ctx: click.Context,
    json: bool,
):
    data = ctx.obj["CloudflareAccount"].get_tunnels()

    if json:
        click.echo(
            dumps(
                [
                    {
                        **obj,
                    }
                    for obj in data
                ],
                indent=2,
            ),
        )
        return

    click.echo(
        tabulate(
            [
                {
                    "name": obj["name"],
                    "status": obj["status"],
                }
                for obj in data
            ],
            headers="keys",
        ),
    )


@cli.command()
@click.pass_context
@click.option(
    "--json",
    is_flag=True,
)
def ingresses(
    ctx: click.Context,
    json: bool,
):
    data = ctx.obj["CloudflareAccount"].get_ingresses()

    if json:
        click.echo(
            dumps(
                [
                    {
                        **obj,
                    }
                    for obj in data
                ],
                indent=2,
            ),
        )
        return

    click.echo(
        tabulate(
            [
                {
                    "tunnel": one(
                        tunnel
                        for tunnel in ctx.obj["CloudflareAccount"].get_tunnels()
                        if tunnel["id"] == obj["tunnel_id"]
                    )["name"],
                    "sort": obj["sort"],
                    "url": obj["url"],
                    "service": obj["service"],
                    "origin_request": dumps(obj["origin_request"]),
                }
                for obj in data
            ],
            headers="keys",
        ),
    )


if __name__ == "__main__":
    cli()
