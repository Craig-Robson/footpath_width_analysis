import time
import centerline
import centerline.exceptions
import pandas as pd
import geopandas as gpd
import shapely.wkt


from centerline.geometry import Centerline
from shapely.geometry import LineString
from shapely.geometry import Point, MultiPoint, MultiLineString
from shapely.ops import linemerge, nearest_points


class ProcessingMethod:

    def __init__(self):
        """"""

    @staticmethod
    def remove_short_lines(line):

        if line.type == 'MultiLineString':

            passing_lines = []

            for i, linestring in enumerate(line):

                other_lines = MultiLineString([x for j, x in enumerate(line) if j != i])

                p0 = Point(linestring.coords[0])
                p1 = Point(linestring.coords[-1])

                is_deadend = False

                if p0.disjoint(other_lines): is_deadend = True
                if p1.disjoint(other_lines): is_deadend = True

                if not is_deadend or linestring.length > 5:
                    passing_lines.append(linestring)

            return MultiLineString(passing_lines)

        if line.type == 'LineString':
            return line

    @staticmethod
    def interpolate_by_distance(linestring, distance=1):
        count = round(linestring.length / distance) + 1

        if count == 1:
            # grab mid-point if it's a short line
            return [linestring.interpolate(linestring.length / 2)]
        else:
            # interpolate along the line
            return [linestring.interpolate(distance * i) for i in range(count)]

    @staticmethod
    def explode_to_segments(df):
        data = {'geometry': [], 'width': []}

        for i, row in df.iterrows():

            for segment, distance in zip(row.segments, row.avg_distances):
                data['geometry'].append(segment.buffer(distance))
                data['width'].append(distance * 2)

        df_segments = pd.DataFrame(data)
        df_segments = gpd.GeoDataFrame(df_segments, crs=df.crs, geometry='geometry')
        return df_segments

    @staticmethod
    def explode_to_segments_(df):
        data = {'geometry': [], 'width': []}

        for i, row in df.iterrows():
            for segment, distance in zip(row.segments, row.avg_distances):
                data['geometry'].append(segment)
                data['width'].append(distance * 2)

        df_segments = pd.DataFrame(data)
        df_segments = gpd.GeoDataFrame(df_segments, crs=df.crs, geometry='geometry')
        return df_segments


def get_segments(line):
    if line.type == 'MultiLineString':
        line_segments = []
        for linestring in line.geoms:
            line_segments.extend(linestring_to_segments(linestring))
        return line_segments

    elif line.type == 'LineString':
        return linestring_to_segments(line)
    else:
        return []


def linestring_to_segments(linestring):
    return [
        LineString([linestring.coords[i], linestring.coords[i + 1]])
        for i in range(len(linestring.coords) - 1)
    ]


def get_avg_distances(row):
    avg_distances = []

    boundary = polygon_to_multilinestring(row.geometry)

    for segment in row.segments:
        points = interpolate(segment)

        distances = []

        for point in points:
            p1, p2 = nearest_points(boundary, point)
            distances.append(p1.distance(p2))

        avg_distances.append(sum(distances) / len(distances))

    return avg_distances


def polygon_to_multilinestring(polygon):
    return MultiLineString([polygon.exterior] + [line for line in polygon.interiors])


def interpolate(line):
    if line.type == 'MultiLineString':
        all_points = []

        for linestring in line:
            all_points.extend(ProcessingMethod.interpolate_by_distance(linestring))

        return all_points

    if line.type == 'LineString':
        return ProcessingMethod.interpolate_by_distance(line)


def gen_centerlines(df, interpolation_distance=0.5):
    """
    """
    centerlines = []

    for i, row in df.iterrows():
        cl = Centerline(row.geometry, interpolation_distance=interpolation_distance)
        centerlines.append(cl)

    return centerlines


def process(df):
    """
    Run processing
    """
    start = time.process_time()
    df['centerlines'] = gen_centerlines(df)
    print('Generated centerlines. Took %s' % (time.process_time() - start))
    df.centerlines = df.centerlines.apply(linemerge)
    print('Done linemerge')
    df.centerlines = df.centerlines.apply(ProcessingMethod.remove_short_lines)
    print('Done remove short lines')
    df.centerlines = df.centerlines.apply(lambda line: line.simplify(1, preserve_topology=True))
    print('Done simplify')
    df['segments'] = df['centerlines'].apply(get_segments)
    print('Done get segments')
    df['avg_distances'] = df.apply(get_avg_distances, axis=1)
    print('Done get avg distances')
    dfc = df.set_geometry('centerlines')
    df_segments = ProcessingMethod.explode_to_segments(df)
    dfc_segments = ProcessingMethod.explode_to_segments_(dfc)
    print('Completed processing. Took %s' % (time.process_time() - start))

    return df_segments, dfc_segments
