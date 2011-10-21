'''
Contains method needed to build JSON files from SQLite files.
'''
import os, sqlite3, json, math
from pygdv.lib.jbrowse import higher_zoom, TYPE, zooms, JSON_HEIGHT, SUBLIST_INDEX, CHUNK_SIZE, LAZY_INDEX, ARROWHEAD_CLASS, CLASSNAME, HIST_CHUNK_SIZE
import numpy as np


#####################################################################
#    QUANTITATIVE DATA
#####################################################################

def _prepare_quantitative_json(tile_width, min, max, sha1, chromosome):
    '''
    Prepare the JSON output for a chromosome.
    '''
    
    data = {}
    data['tileWidth'] = tile_width
    data['min'] = min
    data['max'] = max
    data['zoomLevels'] = _prepare_zoom_levels(sha1, chromosome)
    return data
    
def _prepare_zoom_levels(sha1, chromosome):
    '''
    Prepare the zoom levels for a chromosome
    '''
    array = []
    for zoom in zooms:
        data = {}
        data['urlPrefix'] = os.path.join(sha1, '%s_%s.db' % (chromosome, zoom)) 
        data['height'] = JSON_HEIGHT
        data['basesPerTile'] = str(zoom * 100)
        array.append(data)
    return array
    
#######################################################################
#    QUALITATIVE
#######################################################################


def _prepare_track_data(headers, subfeature_headers, sublist_index, lazy_index, 
                       histogram_meta, hist_stats, subfeature_classes, feature_NCList, 
                       client_config, feature_count, key, arrowhead_class, type, 
                       label, lasyfeature_url_template, classname):
    '''
    Prepare the track data for qualitative tracks.
    '''
    data = {}
    data['headers'] = headers
    data['subfeatureHeaders'] = subfeature_headers
    data['subListIndex'] = sublist_index
    data['lazyIndex'] = lazy_index
    data['histogramMeta'] = histogram_meta
    data['histStats'] = hist_stats
    data['subFeatureClasses'] = subfeature_classes
    data['featureNCList'] = feature_NCList
    data['clientConfig'] = client_config
    data['featureCount'] = feature_count
    data['key'] = key
    data['arrowheadClass'] = arrowhead_class
    data['type'] = type
    data['label'] = label
    data['lazyfeatureUrlTemplate'] = lasyfeature_url_template
    data['className'] = classname
    return data
    
_basic_headers = ['start', 'end', 'score', 'name', 'strand', 'attributes']

_extended_headers = ['start', 'end', 'name', 'strand', 'subfeatures']

_basic_subfeature_headers = ['start', 'end']

_extended_subfeature_headers = ['start', 'end', 'strand', 'type']
    
_basic_client_config = {'labelScale':5, 'subfeatureScale':10, 'featureCss':'"background-color: #0000FF;"'}

_extended_client_config = {'labelScale':5, 'subfeatureScale':10, 
        'featureCallback':'(function(feat, fields, div){if(fields.type){getFeatureStyle(feat[fields.type],div);}})'}

def _prepare_array_param(length, chunck_size, url_template):
    data = {}
    data['length'] = length 
    data['chunkSize'] = chunck_size
    data['urlTemplate'] = url_template
    return data

def _prepare_histogram_meta(bases_per_bin, array_param):
    data = {}
    data['basesPerBin'] = bases_per_bin
    data['arrayParams'] = array_param
    return [data]

def _prepare_hist_stats(bases, mean, max):
    data = {}
    data['bases'] = bases
    data['mean'] = mean
    data['max'] = max
    return data

    
###################################################################################################
#    ALGORITHM
###################################################################################################





_basic_fields = ('start', 'end', 'score', 'name', 'strand', 'attributes')

_extended_fields = ('start', 'end', 'score', 'name', 'strand', 'attributes', 'type', 'id')

def _get_basic_features(connection, chromosome):
    '''
    Get the features on a chromosome.
    @param chromosome : the chromosome
    @return a Cursor Object
    '''
    cursor = connection.cursor()
    cursor.execute('pragma table_info(?)', chromosome)
    fields = [row[1] for row in cursor]
    cursor.close()
    
    
    select_fields = []
    for f in _basic_fields:
        if f in fields:
            select_fields.append(f)
        else :
            select_fields.append('')
            
            cursor = connection.cursor()
    return cursor.execute('select %s from ? order by start, end;' % (', '.join([field for field in select_fields])) , chromosome)


def _get_extended_features(connection, chromosome):
    '''
    Get the features on a chromosome.
    @param chromosome : the chromosome
    @return a Cursor Object
    '''
    cursor = connection.cursor()
    cursor.execute('pragma table_info(?)', chromosome)
    fields = [row[1] for row in cursor]
    cursor.close()
    
    
    select_fields = []
    for f in _extended_fields:
        if f in fields:
            select_fields.append(f)
        else :
            select_fields.append('')
            
            cursor = connection.cursor()
    return cursor.execute('select %s from ? order by id, start, end;' % (', '.join([field for field in select_fields])) , chromosome)
    


#########################################################################


def _generate_nested_features(cursor, field_number):
    '''
    Generate features that has to be written in JSON
    '''
    stack = []
    prev_feature = None
    nb_feature = 1
    
    for row in cursor:
        feature = [row[i] for i in range(field_number)]
        
        if prev_feature is not None:
            if feature[1] < prev_feature[1]:
                stack.append(prev_feature)
            else :
                while stack :
                    tmp_feature = stack.pop()
                    _nest(tmp_feature, prev_feature)
                    nb_feature+=1
                    prev_feature = tmp_feature
                    if feature[1] < prev_feature[1]:
                        stack.append(prev_feature)
                        break
                else:
                    yield prev_feature, nb_feature
                    #result.append(prev_feature)
      
        prev_feature = feature
    yield prev_feature, nb_feature
        


        
########################################################################
      
def _get_array_index(position, loop):
    '''
    From a position, get the index of the array.
    '''
    return (position - 1)/loop

def _count_features(cursor, loop, chr_length):
    '''
    Generate a big array, that will contains the count of all features. Each index of 
    the array corresponding to a loop interval.
    The array length must be a multiple of the higher zoom level : 100000.
    '''        
    # build the big array
    print 'count features => chr_len : %s, loop : %s' % (chr_length, loop)
    tmp = math.ceil(chr_length/float(loop))
    nb = higher_zoom - tmp % higher_zoom + tmp

    #nb = math.ceil(chr_length/float(loop))
    array = np.zeros(nb)
    
    for row in cursor:
        start = row[0]
        start_pos = _get_array_index(start, loop)
        end = row[1]
        end_pos = _get_array_index(end, loop)
        array[start_pos:end_pos+1]+=1
    return array

###########################################################################
       
def _nest(feature, to_nest):
    '''
    Nest a feature into another one.
    '''
    if len(feature) == SUBLIST_INDEX + 1 :
        nested = feature[SUBLIST_INDEX]
    else : 
        nested = []
    nested.append(to_nest)
    feature.append(nested)


###############################################################################


def _generate_lazy_output(feature_generator):
    '''
    Build a generator that yield the feature NCList to write
    for each chunk, and the buffer to write in the file
    @param feature_generator :the generator of features
    @return start, stop, chunk_number, buffer, nb_features
    '''
    chunk_size = 0
    chunk_number = 0
    start = 0
    buffer_list = []
    for feat, nb in feature_generator:
        if start == 0:
            start=feat[0]
        stop = feat[1]
        
        chunk_size+= nb
        buffer_list.append(str(feat))
        if chunk_size >= CHUNK_SIZE :
            nb_feature = chunk_size
            chunk_size = 0
            chunk_number += 1
            buf = ','.join(buffer_list)
            buffer_list = []
            yield start, stop, chunk_number, buf, nb_feature
    yield start, stop, chunk_number, ','.join(buffer_list), chunk_size
        
        
#########################################################################
def _histogram_meta(chr_length, threshold, resource_url):
    '''
    Output the histogram meta parameter.
    @param chr_length : the chromosome length
    @param threshold : the threshold defined
    @param resource_url : the url where to fetch the resources
    '''
    
    length = int(math.ceil(chr_length/threshold)) 
    url_template = os.path.join(resource_url, 'hist-%s-{chunk}.json' % threshold)
    
    array_param = _prepare_array_param(length, CHUNK_SIZE - 1, url_template)
    
    return _prepare_histogram_meta(threshold, array_param)
#######################################################################       

def _write_histo_stats(generator, threshold, output):
    '''
    Write the files hist-{threshold}-{chunk}.json
    '''
     # write
    chunk_nb = 0
    for array in generator:
        chunk_nb += 1
        with open(os.path.join(output, 'hist-%s-%s.json' % (threshold, chunk_nb)), 'w', -1) as file:
             file.write(str(array))
             
     
    

    
def _calculate_histo_stats(array, threshold, chr_length):
    '''
    Calculate the histo stats to write in track data.
    @param array : the array containing count of features
    '''
    data = []
    for zoom in zooms:
        base = zoom * threshold;
        if base < chr_length :
            sum_array = array.reshape(array.size/zoom, zoom).sum(axis=1)
            stats = _prepare_hist_stats(base, sum_array.mean(), sum_array.max())
            data.append(stats)
    return data

def _generate_hist_outputs(array, chr_length):
    '''
    Generate the hist-output. 
    '''
    for i in range(1, chr_length, HIST_CHUNK_SIZE):
        yield array[i:i+HIST_CHUNK_SIZE]
    
    
    
def _threshold(chr_length, feature_count):
    '''
    Get the threshold : when the view switch from feature to histogram
    @param chr_length : the chromosome's length
    @param feature_count : the total number of features
    @return the threshold
    '''
    t = (chr_length *2.5 ) / feature_count;
    for zoom in zooms :
        if zoom>t : return zoom



    
    
def jsonify(database_path, name, sha1, output_root_directory, public_url, browser_url, extended = False):
    '''
    Make a JSON representation of the database.
    @param database_path : the path to the sqlite database
    @param name : the name of the track
    @param sha1 : the sha1 sum of the file
    @param public_url : he base url where the file can be fetched from external request
    @param browser_url : he base url where the file can be fetched from internal request
    @param output_root_directory : the base system path where to write the output
    @param extended : if the format is ``basic`` or ``extended``
    '''
    # configure outputs
    output_path = os.path.join(output_root_directory, sha1)
    out_public_url = os.path.join(public_url, sha1)
    out_browser_url = os.path.join(browser_url, sha1)
    os.mkdir(output_path)
    
    
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute('select * from chrNames;')
    
    for row in cursor:
        chr_name = row[0]
        chr_length = row[1]
        out = os.path.join(output_path, chr_name)
        os.mkdir(out)
        lazy_url = os.path.join(out_browser_url, chr_name, 'lazyfeatures-{chunk}.json')
        _jsonify(conn, name, chr_length, chr_name, os.path.join(out_public_url, chr_name), lazy_url, out, extended)
    cursor.close()
    conn.close()
    return 1

def jsonify_quantitative(sha1, output_root_directory, database_path):
    output_path = os.path.join(output_root_directory, sha1)
    try :
        os.mkdir(output_path)
    except OSError: 
        pass
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute('select * from chrNames;')
    for row in cursor:
        chr_name = row[0]
        chr_length = row[1]
        out = os.path.join(output_path, chr_name)
        try :
            os.mkdir(out)
        except OSError: 
            pass
        cur = conn.cursor()
        result = cur.execute('select min(score), max(score) from "%s" ;' % chr_name).fetchone()
        data = _prepare_quantitative_json(200, result[0], result[1], sha1, chr_name)
        json_data = json.dumps(data)
        output = os.path.join(out, 'trackData.json')
        with open(output, 'w', -1) as file:
            file.write(json_data)
        cur.close()
    cursor.close()
    conn.close()
    return 1
    
def _jsonify(connection, name, chr_length, chr_name, url_output, lazy_url, output_directory, extended):
    '''
    Make a JSON representation of the chromosome.
    @param connection : the connection to the sqlite database
    @param output_directory : where files will be write
    @param url_output : url access to the ressources
    '''
    
    ##' init standard fields'
    if extended :
        field_number = 7
        headers = _extended_headers
        subfeature_headers = _extended_subfeature_headers
        client_config = _extended_client_config
    else :
        field_number = 5
        headers = _basic_headers
        subfeature_headers = _basic_subfeature_headers
        client_config = _basic_client_config

    ##' calculate lazy features'
    cursor = connection.cursor()
    cursor.execute("select * from '%s' ;" % chr_name)
    lazy_feats = _generate_lazy_output(_generate_nested_features(cursor, field_number))
    NCList = []
    feature_count = 0
    for start, stop, chunk_number, buffer, nb_feats in lazy_feats:
        NCList.append([start, stop,{'chunk' : str(chunk_number)}])
        last_chunk_number = chunk_number
        feature_count += nb_feats
        ##' write in output'
        output_chunk = os.path.join(output_directory, 'lazyfeatures-%s.json' % chunk_number)
        with open(output_chunk, 'w', -1) as file:
            file.write(buffer)
             
    cursor.close()
    feature_NCList = str(NCList)
    
    if feature_count == 0 : feature_count = 1
    
    ##' threshold'
    threshold = _threshold(chr_length, feature_count)
    
    ##' histogram meta'
    histogram_meta = _histogram_meta(chr_length, threshold, url_output)
    
    ##' count array'
    cursor = connection.cursor()
    cursor.execute("select * from '%s' ;" % (chr_name))
    array = _count_features(cursor, threshold, chr_length)
    cursor.close()
    
    ##' hists stats'
    hist_stats = _calculate_histo_stats(array, threshold, chr_length)
    
    ##' write hist in output' 
    _write_histo_stats(_generate_hist_outputs(array, chr_length), threshold, output_directory)
    
    
    data = _prepare_track_data(
                               headers, 
                               subfeature_headers, 
                               SUBLIST_INDEX, 
                               LAZY_INDEX, 
                               histogram_meta, 
                               hist_stats, 
                               'subfeatureClasses', 
                               feature_NCList,
                               client_config,
                               feature_count, 
                               name, 
                               ARROWHEAD_CLASS, 
                               TYPE, 
                               name, 
                               lazy_url, 
                               CLASSNAME
                               )
    
    
    
    ##' convert to json'
    json_data = json.dumps(data)
    ##' write track data'
    track_data_output = os.path.join(output_directory, 'trackData.json')
    with open(track_data_output, 'w', -1) as file:
            file.write(json_data)

    return 1


