import os
from pygdv.lib.jbrowse import TYPE, zooms, JSON_HEIGHT, SUBLIST_INDEX, CHUNK_SIZE, LAZY_INDEX, ARROWHEAD_CLASS, CLASSNAME


#####################################################################
#    QUANTITATIVE DATA
#####################################################################

def _prepare_qualitative_json(tile_width, min, max, sha1, chromosome):
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
        data['basesPerTile'] = zoom*100
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
        'featureCallback':'(function(feat, fields, div){if(fields.type){getFeatureStyle(feat[fields.type],div)}})'}

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
    return data

def _prepare_hist_stats(bases, min, max):
    data = {}
    data['bases'] = bases
    data['min'] = min
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


def _generate_basic_json(cursor):
    '''
    Generate features that has to be written in JSON
    '''
    stack = []
    prev_feature = None
    nb_feature = 1
    
    for row in cursor:
        feature = [row[0], row[1], row[2], row[3], row[4], row[5]]
        
        if prev_feature is not None:
            if feature['end'] < prev_feature['end']:
                stack.append(prev_feature)
            else :
                while stack :
                    tmp_feature = stack.pop()
                    _nest(tmp_feature, prev_feature)
                    nb_feature+=1
                    prev_feature = tmp_feature
                    if feature['end'] < prev_feature['end']:
                        stack.append(prev_feature)
                        break
                else:
                    yield prev_feature, nb_feature
                    #result.append(prev_feature)
      
        prev_feature = feature
    yield prev_feature, nb_feature
        

def _generate_features(cursor, field_number):
    stack = []
    prev_feature = None
    nb_feature = 1
    
    for row in cursor:
        feature = [row[i] for i in range(field_number)]
        
        if prev_feature is not None:
            if feature['end'] < prev_feature['end']:
                stack.append(prev_feature)
            else :
                while stack :
                    tmp_feature = stack.pop()
                    _nest(tmp_feature, prev_feature)
                    nb_feature+=1
                    prev_feature = tmp_feature
                    if feature['end'] < prev_feature['end']:
                        stack.append(prev_feature)
                        break
                else:
                    yield prev_feature, nb_feature
                    #result.append(prev_feature)
      
        prev_feature = feature
    yield prev_feature, nb_feature  
        
        
        
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


def _generate_lazy_output(feature_generator, field_number):
    '''
    Build a generator that yield the feature NCList to write
    for each chunk, and the buffer to write in the file
    @param feature_generator :the gererator of features
    @param field_number : the number of fields in the feature
    @return start, stop, chunk_number, buffer
    '''
    chunk_size = 0
    chunk_number = 0
    start = 0
    buffer_list = []
    for feat, nb in feature_generator:
        if start == 0:
            start=feat['start']
        stop = feat['stop']
        
        chunk_size+= nb
        buffer_list.append(','.join([feat[i] for i in range(field_number)]))
        if chunk_size >= CHUNK_SIZE :
            chunk_size = 0
            chunk_number += 1
            buffer_list = []
            yield start, stop, chunk_number, ','.join(buffer_list)
    yield start, stop, chunk_number, buffer
        
        
        
    


def jsonify(name, extended = False):
    '''
    Make a JSON representation of the database.
    @name : name of the track
    @param extended : if the format is extended
    '''
   
    if extended :
        field_number = 5
        headers = _extended_headers
        subfeature_headers = _extended_subfeature_headers
        client_config = _extended_client_config
    else :
        field_number = 7
        headers = _basic_headers
        subfeature_headers = _basic_subfeature_headers
        client_config = _basic_client_config

    cursor = None
    lazy_feats = _generate_lazy_output(_generate_features(cursor, field_number), field_number)
    NCList = []
    for start, stop, chunk_number, buffer in lazy_feats:
         NCList.append([start, stop,{'chunk' : chunk_number}])
         last_chunk_number = chunk_number
         #TODO write in output
    feature_NCList = str(NCList)
    feature_count = last_chunk_number * CHUNK_SIZE
    cursor.close()
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
                               lasyfeature_url_template, 
                               CLASSNAME
                                )
    