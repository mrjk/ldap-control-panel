import click
from textual_serve.server import Server


@click.command()
@click.option(
    "--host",
    default="localhost",
    help="Host for the web application"
)
@click.option(
    "--port",
    default=8000,
    type=int,
    help="Port for the web application"
)
# @click.option(
#     "--title",
#     default=None,
#     help="Title shown in the web app (defaults to command)"
# )
@click.option(
    "--public-url",
    default=None,
    help="Public URL if server is behind a proxy"
)
# @click.option(
#     "--statics-path",
#     default=None,
#     help="Path to statics folder"
# )
# @click.option(
#     "--templates-path",
#     default=None,
#     help="Path to templates folder"
# )
@click.option(
    "--debug",
    is_flag=True,
    help="Enable textual devtools"
)
def serve(
    # command: str,
    host: str,
    port: int,
    # statics_path: str | None,
    # templates_path: str | None,
    debug: bool,
    public_url: str | None = None,
    title: str | None = "LDAP Control Panel",
) -> None:
    """Serve the LDAP IDP Textual app via web interface."""

    # if not public_url:
    #     public_url = f"http://{host}:{port}"

    server = Server(
        "python -m ldap_idp.main",
        host=host,
        port=port,
        title=title,
        public_url=public_url,
        # statics_path=statics_path,
        # templates_path=templates_path,
    )
    
    click.echo(f"Starting server at http://{host}:{port} ({public_url})")
    server.serve(debug=debug)



if __name__ == "__main__":
    serve()
