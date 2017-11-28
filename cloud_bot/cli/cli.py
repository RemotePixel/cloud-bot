"""cloud_bot.cli.cli"""

import click
from cloud_bot.utils import create_img


@click.command(short_help="Create random cloud image")
@click.option('--full/--overview', default=False, help='')
@click.option('--bands', default=(5, 4, 3), help='')
@click.option('--cloud', default=60, help='')
def create(full, bands, cloud):
    """
    """
    if len(bands) != 3:
        raise Exception('Really? please try with 3 bands')

    scene, im, info = create_img(highres=full, bands=bands, min_cloud=cloud)
    outfile = f'./{scene}.jpg'
    with open(outfile, 'wb') as f:
        f.write(im.getvalue())
