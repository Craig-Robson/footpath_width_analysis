import requests, configparser, json
import geopandas as gpd
from os import path
from functions import process


def read_config():
    """
    Read in config file with API url, username and password
    """
    cfg = configparser.ConfigParser()
    cfg.read('api_config.ini')
    return {'url': cfg['API']['url'],
            'username': cfg['API']['username'],
            'password': cfg['API']['password']}


def get_data(area_scale='oa', area_code='E00042673'):
    """
    Pull data from NISMOD-DB API and save as geojson file.
    """
    file_name = 'data.geojson'
    output_dir = './'

    api_details = read_config()
    classification_codes = '10123, 10172, 10183'
    response = requests.get('%s/data/mastermap/areas?export_format=geojson&scale=oa&area_codes=E00042673&classification_codes=%s' %(api_details['url'], classification_codes), auth=(api_details['username'], api_details['password']))
    #response = requests.get('%s/data/mastermap/areas?export_format=geojson&scale=lad&area_codes=E08000021&classification_codes=%s' % (api_details['url'], classification_codes), auth=(api_details['username'], api_details['password']))
    #response = requests.get(
    #    '%s/data/mastermap/areas?export_format=geojson-zip&scale=lad&area_codes=E08000021&classification_codes=%s' % (
    #    api_details['url'], classification_codes), auth=(api_details['username'], api_details['password']))
    #print('Got data')
    #z = zipfile.ZipFile(io.BytesIO(response.content))
    #z.extractall('./data.geojson')
    if response.status_code != 200:
        print('API returned status code %s, failing in the process.' %response.status_code)
        exit()

    data = json.loads(response.text)
    print('Number of features:', len(data['features']))
    with open(path.join(output_dir, file_name), 'w') as data_file:
        json.dump(data, data_file)

    return path.join(output_dir, file_name)


def import_file(file_name):
    """
    Convert a .geojson file, or similar, into a geo-dataframe
    """
    df = gpd.read_file(file_name, encoding='UTF-8')
    return df


def create_df(json_data):
    """
    Convert raw geojson into a geo-datafrane
    """
    return gpd.read_geojson(json_data)


##############################################


df = get_data()
df_1, df_2 = process(import_file(df))

