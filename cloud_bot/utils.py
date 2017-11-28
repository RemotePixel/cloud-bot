"""cloud_bot.utils: utility function"""

import os
import re
import json
import time
import random
import datetime
from io import BytesIO
from functools import partial
from concurrent import futures
from urllib.request import urlopen

from PIL import Image

import numpy as np

from mapbox import Geocoder

import rasterio
import mercantile
from rasterio.vrt import WarpedVRT
from rasterio.enums import Resampling
from rasterio.plot import reshape_as_image
from rio_toa.reflectance import reflectance

from rio_tiler.utils import landsat_parse_scene_id, linear_rescale, landsat_get_mtl

sat_api = 'https://api.developmentseed.org/satellites/?'


LANDSAT_BUCKET = 's3://landsat-pds'


def random_date():
    """
    """
    start = datetime.datetime.strptime('2013-04-01', '%Y-%m-%d')
    now = datetime.datetime.now()
    end = now - datetime.timedelta(days=1)
    return start + datetime.timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())),)


def band_worker(band, landsat_address, meta, bounds=None):
    """
    """

    address = f'{landsat_address}_B{band}.TIF'

    sun_elev = meta['IMAGE_ATTRIBUTES']['SUN_ELEVATION']
    multi_reflect = meta['RADIOMETRIC_RESCALING'][f'REFLECTANCE_MULT_BAND_{band}']
    add_reflect = meta['RADIOMETRIC_RESCALING'][f'REFLECTANCE_ADD_BAND_{band}']

    ovrSize = 1024

    with rasterio.open(address) as src:

        if bounds:
            w, s, e, n = bounds
            with WarpedVRT(src,
                           dst_crs='EPSG:3857',
                           resampling=Resampling.bilinear,
                           src_nodata=0,
                           dst_nodata=0) as vrt:
                                window = vrt.window(w, s, e, n, precision=21)
                                matrix = vrt.read(window=window,
                                                  boundless=True,
                                                  resampling=Resampling.bilinear,
                                                  out_shape=(ovrSize, ovrSize),
                                                  indexes=1).astype(src.profile['dtype'])

        else:
            matrix = src.read(indexes=1,
                              out_shape=(ovrSize, ovrSize),
                              resampling=Resampling.bilinear).astype(src.profile['dtype'])

        matrix = reflectance(matrix, multi_reflect, add_reflect, sun_elev, src_nodata=0)
        imgRange = np.percentile(matrix[matrix > 0], (2, 98)).tolist()
        matrix = np.where(matrix > 0,
                          linear_rescale(matrix, in_range=imgRange, out_range=[1, 255]),
                          0).astype(np.uint8)

    return matrix


def get_place(lat, lon):
    """Get the region name of the center lat/lon
    """
    geocoder = Geocoder()
    geocoder = Geocoder(access_token=os.environ['MapboxAccessToken'])
    place = 'Somewhere over the clouds!'
    try:
        response = geocoder.reverse(lon=lon, lat=lat, types=['region'])
        if response.status_code == 200:
            features = response.geojson()['features']
            place = features[0].get('place_name')
        return place
    except:
        return place


def create_img(highres=None, bands=[5, 4, 3], min_cloud=60):
    """
    """
    max_i = 5
    i = 0

    while True:
        date_image = random_date().strftime('%Y-%m-%d')
        query = f'{sat_api}satellite_name=landsat-8&date={date_image}&cloud_from={min_cloud}&limit=2000'
        response = json.loads(urlopen(query).read())
        if response.get('errorMessage'):
            raise Exception('What is wrong with you dude')

        if response.get('meta').get('found') == 0:
            continue

        scenes = response.get('results', [])
        index = random.randrange(0, len(scenes))
        scene = scenes[index]

        date = time.strptime(scene['date'], '%Y-%m-%d')
        aws_id = re.sub(r'LGN0[0-9]', 'LGN00', scene['scene_id']) \
            if date < time.strptime('2017-05-01', '%Y-%m-%d') else scene['LANDSAT_PRODUCT_ID']

        lat = scene['sceneCenterLatitude']
        lng = scene['sceneCenterLongitude']

        try:
            if highres:
                tile = mercantile.tile(lng, lat, 9, truncate=True)
                bounds = mercantile.xy_bounds(tile)
            else:
                bounds = None

            scene_params = landsat_parse_scene_id(aws_id)
            meta_data = landsat_get_mtl(aws_id).get('L1_METADATA_FILE')
            landsat_address = f'{LANDSAT_BUCKET}/{scene_params["key"]}'

            _worker = partial(band_worker, landsat_address=landsat_address, meta=meta_data, bounds=bounds)
            with futures.ThreadPoolExecutor(max_workers=3) as executor:
                out = np.stack(list(executor.map(_worker, bands)))

            out = reshape_as_image(out)
            img = Image.fromarray(out, mode='RGB')

            im = BytesIO()
            img.save(im, 'jpeg', subsampling=0, quality=100)
            im.seek(0)
        except:
            print(f'{aws_id}: NOPE!')
            i += 1
            if i >= max_i:
                raise Exception('What is wrong with you dude')

            continue

        info = {
            'lat': lat,
            'lng': lng,
            'name': get_place(lat, lng)}

        return aws_id, im, info
