'''
Contains method needed to build JSON files from SQLite files.
'''
from __future__ import absolute_import
import os, sqlite3, json, math
#from lib.jbrowse import higher_zoom, TYPE, zooms, JSON_HEIGHT, SUBLIST_INDEX, CHUNK_SIZE, LAZY_INDEX, ARROWHEAD_CLASS, CLASSNAME, HIST_CHUNK_SIZE
from pygdv.lib.jbrowse import higher_zoom, TYPE, zooms, JSON_HEIGHT, SUBLIST_INDEX, CHUNK_SIZE, LAZY_INDEX, ARROWHEAD_CLASS, CLASSNAME
import numpy as np
import track

#####################################################################
#    QUANTITATIVE DATA
#####################################################################

def _prepare_quantitative_json(tile_width, _min, _max, sha1, chromosome):
    '''
    Prepare the JSON output for a chromosome.
    '''
    
    data = {}
    data['tileWidth'] = tile_width
    data['min'] = _min
    data['max'] = _max
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
                       client_config, feature_count, key, arrowhead_class, _type, 
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
    data['type'] = _type
    data['label'] = label
    data['lazyfeatureUrlTemplate'] = lasyfeature_url_template
    data['className'] = classname
    return data
    
_basic_headers = ['start', 'end', 'score', 'name', 'strand', 'attributes']
_basic_client_config = {'labelScale':5, 'subfeatureScale':10, 'featureCss':'"background-color: #0000FF;"'}
_basic_subfeature_headers = ['start', 'end']
_basic_fields = ('start', 'end', 'score', 'name', 'strand', 'attributes')


_extended_headers = ('start', 'end', 'name', 'strand', 'subfeatures')
_subfeature_headers = ('start', 'end', 'score', 'name', 'strand', 'type', 'attributes')
_extended_fields = ('start', 'end', 'score', 'name', 'strand', 'type', 'attributes', 'id')




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
    return data

def _prepare_hist_stats(bases, mean, _max):
    data = {}
    data['bases'] = bases
    data['mean'] = mean
    data['max'] = _max
    return data

    
###################################################################################################
#    ALGORITHM
###################################################################################################


        
        
def _generate_nested_extended_features(cursor, keep_field, count_index, subfeatures_index,
                                       start_index, end_index, name_index, strand_index):
    '''
    Generate features that has to be written in JSON
    :param: cursor - the SQL cursor
    :param: *_index : the index of the ``*`` param in the cursor
    :param: keep_field - the number of fields (it will take the firsts ``field number`` from the feature) 
    of the subfeature
    '''
    stack = []
    prev_feature = None

    nb_feature = 1
    ## 'generate nested features'
    for row in cursor:
        feature = [row[start_index], row[end_index], row[name_index], row[strand_index]]
        count = row[count_index]
        # add the sub-features
        feature.append(json.loads(row[subfeatures_index]))
        
        nb_feature += count
        # exclude the first loop        
        if prev_feature is not None:
            # nest features with an inferior `end`
            if feature[end_index] < prev_feature[end_index]:
                stack.append(prev_feature)
            else :
                # nest the feature in the stack
                while stack :
                    tmp_feature = stack.pop()
                    _nest(tmp_feature, prev_feature, subfeatures_index, keep_field)
                    nb_feature += 1
                    prev_feature = tmp_feature
                    if feature[end_index] < prev_feature[end_index]:
                        stack.append(prev_feature)
                        break
                else:
                    # the stack is empty
                    yield prev_feature, nb_feature
                    nb_feature = 1
      
        prev_feature = feature
    if prev_feature is not None:    
        yield prev_feature, nb_feature
    
    
def _generate_nested_features(cursor, keep_field, start_index, end_index):
    '''
    Generate features that has to be written in JSON
    '''
    field_number_list = range(keep_field)
    for row in cursor:
        feature = [row[i] for i in field_number_list]
        yield feature, 1
        

        
        
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
    tmp = math.ceil(chr_length/float(loop))
    nb = higher_zoom - tmp % higher_zoom + tmp

    #nb = math.ceil(chr_length/float(loop))
    array = np.zeros(nb)
    
    for row in cursor:
        start = row['start']
        start_pos = _get_array_index(start, loop)
        end = row['end']
        end_pos = _get_array_index(end, loop)
        array[start_pos:end_pos+1]+=1
    return array

    
def _nest(feature, to_nest, index, keep_field):

    '''
    Nest a feature into another one.
    :param: feature : the feature to nest in
    :param: to nest : the feature to nest
    :param: index : at which index are the nested features
    :param: keep_field : the number of fields to keep on the feature
    '''
    if len(feature) == index + 1 :
        nested = feature[index]
        nested.append(to_nest[0:keep_field])
        feature[index] = nested
    else : 
        nested = []
        nested.append(to_nest[0:keep_field])
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
    first = None
    for feat, nb in feature_generator:
        start = feat[0]
        if first is None : first = start
        stop = feat[1]
        if start > stop :
            raise Exception("You cannot have a feature ending before starting %s " % feat)
        chunk_size+= nb
        buffer_list.append(feat)
        if chunk_size >= CHUNK_SIZE :
            nb_feature = chunk_size
            chunk_size = 0
            chunk_number += 1
            yield first, stop, chunk_number, buffer_list, nb_feature
            buffer_list = []
            first = None
    if first is not None:
        chunk_number += 1
        yield first, stop, chunk_number, buffer_list, chunk_size
        
#########################################################################
def write_histogram_meta(chr_length, threshold, array, resource_url, output_directory, zooms):
    
    json_array = []
    for z in zooms:
        
       
        bins = threshold * z 
        ###JSON
        length = int(math.ceil(chr_length / bins)) 
        
        url_template = os.path.join(resource_url, 'hist-%s-{chunk}.json' % bins)
        array_param = _prepare_histogram_meta(bins, _prepare_array_param(length, CHUNK_SIZE - 1, url_template))
        json_array.append(array_param)
        
        ###WRITE ARRAY
        _write_histo_stats(_generate_hist_outputs(array, bins, length), bins, output_directory)
        
        if bins * 100 > chr_length : break
            
        
    return json_array


def _histogram_meta(chr_length, threshold, resource_url):
    '''
    Output the histogram meta parameter.
    @param chr_length : the chromosome length
    @param threshold : the threshold defined
    @param resource_url : the url where to fetch the resources
    '''
    
    array = []
    t = int(threshold * 0.1)
    length = int(math.ceil(chr_length / t)) 
    url_template = os.path.join(resource_url, 'hist-%s-{chunk}.json' % t)
    array_param = _prepare_array_param(length, CHUNK_SIZE - 1, url_template)
    array.append(array_param)
    
    length = int(math.ceil(chr_length/threshold)) 
    url_template = os.path.join(resource_url, 'hist-%s-{chunk}.json' % threshold)
    array_param = _prepare_array_param(length, CHUNK_SIZE - 1, url_template)
    array.append(array_param)
    
    t = int(threshold * 100)
    length = int(math.ceil(chr_length / t )) 
    url_template = os.path.join(resource_url, 'hist-%s-{chunk}.json' % t)
    array_param = _prepare_array_param(length, CHUNK_SIZE - 1, url_template)
    array.append(array_param)
    
    
    return _prepare_histogram_meta(threshold, array)
#######################################################################       

def _write_histo_stats(generator, threshold, output):
    '''
    Write the files hist-{threshold}-{chunk}.jsont.cursor
    '''
    # write
    chunk_nb = -1
    for array in generator:
        chunk_nb += 1
        with open(os.path.join(output, 'hist-%s-%s.json' % (threshold, chunk_nb)), 'w', -1) as f:
            f.write(json.dumps(array.tolist()))
             
     
    

    
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


def _generate_hist_outputs(array, bins, array_length):
    '''
    Generate the hist-output.
    '''
    for i in xrange(1, array_length, bins):
        yield array[i:i + bins]


def _threshold(chr_length, feature_count):
    '''
    Get the threshold : when the view switch from feature to histogram
    @param chr_length : the chromosome's length
    @param feature_count : the total number of features
    @return the threshold
    '''
    t = (chr_length * 2.5) / feature_count
    prev_zoom = zooms[0]
    for zoom in zooms:
        if zoom > t:
            return prev_zoom
        prev_zoom = zoom
    return zooms[-1]


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
    with track.load(database_path, 'sql', readonly=False) as t :
        for chr_name in t:
            chr_length = t.chrmeta[chr_name]['length']
            out = os.path.join(output_path, chr_name)
            os.mkdir(out)
            lazy_url = os.path.join(out_browser_url, chr_name, 'lazyfeatures-{chunk}.json')
            _jsonify(t, name, chr_length, chr_name, os.path.join(out_public_url, chr_name), lazy_url, out, extended)
    return 1

def jsonify_quantitative(sha1, output_root_directory, database_path):
    output_path = os.path.join(output_root_directory, sha1)
    try :
        os.mkdir(output_path)
    except OSError: 
        pass
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute('select name from chrNames;')
    for row in cursor:
        chr_name = row[0]
        out = os.path.join(output_path, chr_name)
        try :
            os.mkdir(out)
        except OSError: 
            pass
        cur = conn.cursor()
        result = None
        try:
            result = cur.execute('select min(score), max(score) from "%s" ;' % chr_name).fetchone()
        except sqlite3.OperationalError as e:
            pass
        if result:
            data = _prepare_quantitative_json(200, result[0], result[1], sha1, chr_name)
            json_data = json.dumps(data)
            output = os.path.join(out, 'trackData.json')
            with open(output, 'w', -1) as f:
                f.write(json_data)
            cur.close()
        
    cursor.close()
    conn.close()
    return 1

def _gen_gen(t, chr_name,  gene_name_alias, gene_identifier_alias):
    prev_id = None
    l = []
    #for row in t.read(chr_name, ['start', 'end', 'score', 'name', 'strand', 'type', 'attributes', 'id'], cursor=True):
    for row in t.aggregated_read(chr_name, ('start', 'end', 'score', gene_name_alias, 'strand', 'type', gene_identifier_alias), order_by=gene_identifier_alias):
        
        idi = row[6]
        if prev_id is not None:
            if prev_id == idi :
                l.append(row[0:6] + row[7:])
            else :
                yield prev_id, json.dumps(l)
                l = []
                l.append(row[0:6] + row[7:])
        else :
            l.append(row[0:6] + row[7:])
        prev_id = idi
    if prev_id is not None:
        yield prev_id, json.dumps(l)
        
def _gen_gen2(t, chr_name,  gene_name_alias, gene_identifier_alias):
    for row in t.aggregated_read(chr_name, ('start', 'end', 'score', gene_name_alias, 'strand', 'type', gene_identifier_alias)):
        yield row

def _prepare_database(t, chr_name, gene_name_alias, gene_identifier_alias):
    '''
    Add a table that will reference all sub-features for a feature.
    :return: the table name to erase after
    '''
    
    
    table_name = 'tmp_%s' % chr_name
    t.cursor().execute('drop table if exists "%s";' % table_name)
    ##  'create table tmp_%s' % chr_name
    t.cursor().execute('create table "%s"(id text, subs text, foreign key(id) references "%s"(id));' % (table_name, chr_name))
    t.write(table_name, _gen_gen(t, chr_name, gene_name_alias, gene_identifier_alias) , ('id', 'subs'))
    table_name2 = 'tmp_%s2' % chr_name
    ##  'create table tmp_%s2' % chr_name
    t.cursor().execute('drop table if exists "%s";' % table_name2)
    t.cursor().execute('create table "%s"(start int, end int, score float, name text, strand int , type text, id text, attributes text);' % (table_name2))
    t.write(table_name2, _gen_gen2(t, chr_name, gene_name_alias, gene_identifier_alias) , ('start', 'end', 'score', 'name', 'strand', 'type', 'id', 'attributes'))
    
    return table_name, table_name2
    
    
def _jsonify(t, name, chr_length, chr_name, url_output, lazy_url, output_directory, extended):
    '''
    Make a JSON representation of the chromosome.
    @param connection : the connection to the sqlite database
    @param output_directory : where files will be write
    @param url_output : url access to the ressources
    '''
    
    gene_name_alias =  t.find_column_name(['name', 'gene_name', 'gene name', 'gname', 'Name', 'product'])
    att_name = '%s' % gene_name_alias
    if gene_name_alias == '':
        att_name = 'name'
            
    if extended :
        gene_identifier_alias =  t.find_column_name(['id', 'gene_id', 'gene id', 'Id', 'identifier', 'Identifier', 'protein_id'])
        headers = _extended_headers
        subfeature_headers = _subfeature_headers

        
        client_config = _extended_client_config
        ##  'preparedb'
        table_name , table_name2 = _prepare_database(t, chr_name, att_name, gene_identifier_alias)
        
        #t.cursor.execute('select min(t1.start), max(t1.end), t1.score, t1.name, t1.strand, t1.type, t1.attributes, t1.id, count(t1.id), t2.subs from "%s" as t1 inner join "%s" as t2 on t1.id = t2.id group by t1.id order by t1.start asc, t1.end asc ;' % (chr_name, table_name))
        cursor = t.cursor().execute('select min(t1.start), max(t1.end), t1.score, t1.name, t1.strand, t1.type, t1.attributes, t1.id, count(t1.id), t2.subs from "%s" as t1 inner join "%s" as t2 on t1.id = t2.id group by t1.id order by t1.start asc, t1.end asc ;' % (table_name2, table_name))
        
        ## ' calculate lazy features'
        lazy_feats = _generate_lazy_output(
                    _generate_nested_extended_features(cursor, keep_field=7, count_index=8, 
                                    subfeatures_index=9, start_index=0, end_index=1, name_index=3, strand_index=4))
        
    else :
        headers = _basic_headers
        subfeature_headers = _basic_subfeature_headers
        client_config = _basic_client_config
        ## ' calculate lazy features'
        
        gen =  t.aggregated_read(chr_name, ('start', 'end', 'score', att_name, 'strand'), order_by='start asc, end asc');
        #cursor = t.cursor().execute('select t1.start, t1.end, t1.score, %s , t1.strand, t1.attributes from "%s" as t1 order by t1.start asc, t1.end asc ;' % (att_name, chr_name) )
        
        lazy_feats = _generate_lazy_output(
                            _generate_nested_features(gen, keep_field=6, start_index=0, end_index=1))
   
   
    ## 'NCLIST'
    NCList = []
    feature_count = 0
    for start, stop, chunk_number, buff, nb_feats in lazy_feats:
        NCList.append([start, stop,{'chunk' : str(chunk_number)}])
        feature_count += nb_feats
        output_chunk = os.path.join(output_directory, 'lazyfeatures-%s.json' % chunk_number)
        with open(output_chunk, 'w', -1) as fil:
            fil.write(json.dumps(buff))
    
    if extended :
        
        ## 'erase table'
        ## 'drop table %s'% table_name
        t._cursor.execute('drop table "%s";' % table_name)
        
        ## 'drop table %s'% table_name2
        t._cursor.execute('drop table "%s";' % table_name2)
        t.vacuum()
        #t.cursor.execute('vacuum')
        ## 'dropped'
            
    if feature_count == 0 : feature_count = 1
    
    ## ' threshold %s, %s ' % (chr_length, feature_count)
    threshold = _threshold(chr_length, feature_count)
    
    ## ' histogram meta %s, %s, %s' % (chr_length, threshold, url_output)
    
    
    cursor = t.cursor().execute("select * from '%s' ;" % (chr_name))
    array = _count_features(cursor, threshold, chr_length)
    
    ## ' hists stats'
    hist_stats = _calculate_histo_stats(array, threshold, chr_length)

    histogram_meta = write_histogram_meta(chr_length, threshold, array, url_output, output_directory, zooms)
    
    data = _prepare_track_data(
                               headers, 
                               subfeature_headers, 
                               SUBLIST_INDEX, 
                               LAZY_INDEX, 
                               histogram_meta, 
                               hist_stats, 
                               'subfeatureClasses', 
                               NCList,
                               client_config,
                               feature_count, 
                               name, 
                               ARROWHEAD_CLASS, 
                               TYPE, 
                               name, 
                               lazy_url, 
                               CLASSNAME
                               )
    
    
    
    ## ' convert to json'
    json_data = json.dumps(data)
    ## ' write track data'
    track_data_output = os.path.join(output_directory, 'trackData.json')
    with open(track_data_output, 'w', -1) as f:
            f.write(json_data)

    return 1









if __name__ == '__main__':
    import shutil
    out_dir = '/home/yo/Desktop/tests'
    try: 
        shutil.rmtree(out_dir)
    except OSError:
        pass
    sha1 = 'nosha1'
    os.mkdir(out_dir)
    db = '/web/ass/tair10_m.sql'


    jsonify(db, 'aname', sha1, out_dir, 'public_url', 'browser_url', True)
   
