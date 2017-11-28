"""cloud_bot.cli.cli"""

import click
from cloud_bot.utils import create_img


@click.command(short_help="Create random cloud image")
@click.option('--full/--overview', default=False, help='')
@click.option('--bands', default=(5, 4, 3), help='')
def create(full, bands):
    """
    """
    if len(bands) != 3:
        raise Exception('Really? please try with 3 bands')

    scene, im = create_img(highres=full, bands=bands)
    outfile = f'./{scene}.jpg'
    with open(outfile, 'wb') as f:
        f.write(im.getvalue())
