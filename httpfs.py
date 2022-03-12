import click
import httpfs_methods


@click.command()
@click.option('-v', '--v', is_flag=True, help="Prints debugging messages. Enables a verbose output from the command-line.")
@click.option('-p', '--p', help="Specifies the port number that the server will listen and serve at. Default is 8080.")
@click.option('-d', '--d', help="Specifies the directory that the server will use to read/write requested files. "
                                "Default is the current directory when launching the application.")
def run_client(v, p, d):
    """
    Runs the httpfs server. It is a simple remote file server manager running on top of a HTTP server library.
    """
    port = 8080

    if p is None or p == "":
        port = 8080
    else:
        port = int(p)

    httpfs_methods.run_server('localhost', port, d, v)


if __name__ == '__main__':
    run_client()
