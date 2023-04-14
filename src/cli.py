import functools
import os

import click

from src.apis.jina_cloud import jina_auth_login
from src.options.configure.key_handling import set_api_key


def exception_interceptor(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise type(e)(f'''
{str(e)}

😱😱😱 Sorry for this experience. Could you please report an issue about this on our github repo? We'll try to fix it asap.
''') from e
    return wrapper

def path_param(func):
    @click.option('--path', required=True, help='Path to the generated microservice.')
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        path = os.path.expanduser(kwargs['path'])
        path = os.path.abspath(path)
        kwargs['path'] = path
        return func(*args, **kwargs)
    return wrapper


@click.group(invoke_without_command=True)
@click.pass_context
@exception_interceptor
def main(ctx):
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
    jina_auth_login()


@main.command()
@click.option('--description', required=True, help='Description of the microservice.')
@click.option('--test', required=True, help='Test scenario for the microservice.')
@path_param
def generate(
        description,
        test,
        path,
):
    from src.options.generate.generator import Generator
    path = os.path.expanduser(path)
    path = os.path.abspath(path)
    if os.path.exists(path):
        if os.listdir(path):
            click.echo(f"Error: The path {path} you provided via --path is not empty. Please choose a directory that does not exist or is empty.")
            return
    generator = Generator()
    generator.generate(description, test, path)

@main.command()
@path_param
def run(path):
    from src.options.run import Runner
    path = os.path.expanduser(path)
    path = os.path.abspath(path)
    Runner().run(path)


@main.command()
@path_param
def deploy(path):
    from src.options.deploy.deployer import Deployer
    path = os.path.expanduser(path)
    path = os.path.abspath(path)
    Deployer().deploy(path)

@main.command()
@click.option('--key', required=True, help='Your OpenAI API key.')
def configure(key):
    set_api_key(key)


if __name__ == '__main__':
    main()
