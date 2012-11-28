"""
Contains method needed to build JSON files from SQLite files.
"""
from __future__ import absolute_import
import os, json
from pygdv.lib.jbrowse import *
import numpy as np
from bbcflib.btrack import track

headers = {True:  ['start', 'end', 'name', 'strand', 'subfeatures'],
           False: ['start', 'end', 'score', 'name', 'strand', 'attributes']}
subfeature_headers = {True:  ['start', 'end', 'score', 'name', 'strand', 'type', 'attributes'],
                      False: ['start', 'end']}
client_config = {True: {'labelScale':5, 'subfeatureScale':10, 
                        'featureCallback':'(function(feat, fields, div){if(fields.type){getFeatureStyle(feat[fields.type],div);}})'}, 
                 False: {'labelScale':5, 'subfeatureScale':10, 'featureCss':'"background-color: #0000FF;"'}}

_id_cols = ['id','gene_id','gene id','Id','identifier','Identifier','protein_id','name']
_name_cols = ['name', 'gene_name', 'gene name', 'gname', 'Name', 'product']

###################################################################################
#    ALGORITHM
###################################################################################

def _lazy_output(directory,t,chrom,extended=False):
    subfs = {}
    feats = []
    if extended:
        idxs = [t.fields.index('start'), t.fields.index('end'), 
                t.column_by_name(_id_cols), t.fields.index('strand')]
        if 'score' in t.fields: idxs.append(t.fields.index('score'))
        else: idxs.append(-1)
    else:
        idxs = [t.fields.index('start'), t.fields.index('end'),
                t.fields.index('score') if 'score' in t.fields else -1,
                t.column_by_name(_id_cols), t.fields.index('strand')]
    morxs = [i for i in range(len(t.fields)) if i not in idxs]
    for row in t.read(chrom,fields=t.fields):
        if extended: rid = row[idxs[2]]
        else: rid = row[idxs[3]]
        if rid in subfs:
            subfs[rid][1] = max(row[idxs[1]],subfs[rid][1])
            subfs[rid][-1].append([row[n] for n in morxs])
        else:
            feats.append(rid)
            subfs[rid] = [row[n] for n in idxs if n>=0]+[[]]
            subfs[rid][-1].append([row[n] for n in morxs])
    chunk_number = 0
    buffer = []
    first = None
    output_chunk = os.path.join(directory, "lazyfeatures-%s.json")
    NCList = []
    pos_list = []
    for feat_count, _f in enumerate(feats):
        _sf = subfs[_f]
        start = _sf[0]
        if first is None: first = start
        stop = _sf[1]
        if extended:
            _sf = [_sf[n] if m>=0 else 0.0 for n,m in enumerate(idxs)]\
                  +[dict((t.fields[m],x[n]) for n,m in enumerate(morxs))
                    for x in _sf[-1]]
        else:
            _sf = [_sf[n] if m>=0 else 0.0 for n,m in enumerate(idxs)]\
                  +[dict((t.fields[m],_sf[-1][0][n]) for n,m in enumerate(morxs))]
        buffer.append(_sf)
        pos_list.append((start,stop))
        if len(buffer) == CHUNK_SIZE:
            chunk_number += 1
            NCList.append([first, stop,{'chunk': str(chunk_number)}])
            with open(output_chunk%chunk_number, 'w') as f: json.dump(buffer,f)
            buffer = []
            first = None
    if first is not None:
        chunk_number += 1
        NCList.append([first, stop,{'chunk': str(chunk_number)}])
        with open(output_chunk%chunk_number, 'w') as fil: json.dump(buffer,fil)
    return NCList, feat_count+1, pos_list
    
###############################################################################

def _histogram_meta(chr_length, zooms, arrays, resource_url, output_directory):
    json_array = []
    url_template = os.path.join(resource_url, 'hist-%s-{chunk}.json')
    output = os.path.join(output_directory, 'hist-%s-%s.json')
    for nz, z in enumerate(zooms):
        length = (chr_length-1)/z+1
        array_param = {'basesPerBin': z, 
                       'arrayParams': {'length': length, 'chunkSize': CHUNK_SIZE-1, 
                                       'urlTemplate': url_template % z}}
        json_array.append(array_param)
        ar = arrays[nz]
        for chunk_nb, i in enumerate(xrange(0,ar.size,CHUNK_SIZE)):
            with open(output%(z, chunk_nb), 'w') as f:
                json.dump(ar[i:i+CHUNK_SIZE].tolist(),f)
    return json_array

#######################################################################       

def jsonify(database_path, name, sha1, output_root_directory, 
            public_url, browser_url, extended=False):
    """
    Make a JSON representation of the database.
    @param database_path : the path to the sqlite database
    @param name : the name of the track
    @param sha1 : the sha1 sum of the file
    @param public_url : he base url where the file can be fetched from external request
    @param browser_url : he base url where the file can be fetched from internal request
    @param output_root_directory : the base system path where to write the output
    @param extended : if the format is ``basic`` or ``extended``
    """
    out = os.path.join(output_root_directory, sha1, '%s')
    os.mkdir(out % '')
    lazy_url = os.path.join(browser_url, sha1,'%s','lazyfeatures-{chunk}.json')
    pub_url = os.path.join(public_url, sha1, '%s')
    with track(database_path) as t:
        for chr_name, chr_info in t.chrmeta.iteritems():
            os.mkdir(out %chr_name)
            _jsonify(t, name, chr_info['length'], chr_name, 
                     pub_url%chr_name, lazy_url%chr_name, out%chr_name, extended)
    return 1

def jsonify_quantitative(sha1, output_root_directory, database_path):
    out = os.path.join(output_root_directory, sha1, '%s')
    try :
        os.mkdir(out % '')
    except OSError: 
        pass

    t = track(database_path)
    for chr_name in t.chrmeta:
        try :
            os.mkdir(out %chr_name)
        except OSError: 
            pass
        path = os.path.join( sha1, chr_name+"_%s.db" )
        _min, _max = t.get_range(selection=chr_name,fields=['score'])
        if _min and _max:
            zl = [{'urlPrefix': path %z, 'height': JSON_HEIGHT,
                   'basesPerTile': str(z*100)} for z in zooms]
            with open(os.path.join( out %chr_name, 'trackData.json' ), 'w') as f:
                json.dump({'tileWidth': 200, 'min': _min, 'max': _max, 'zoomLevels': zl}, f)
    return 1

def _jsonify(t, name, chr_length, chr_name, url_output, lazy_url, output_directory, extended):
    """
    Make a JSON representation of the chromosome.
    @param connection : the connection to the sqlite database
    @param output_directory : where files will be write
    @param url_output : url access to the ressources
    """
    NCList, feature_count, pos_list = _lazy_output(output_directory, t, chr_name, extended)
    thr = chr_length*5/2
    for nt, threshold in enumerate(zooms):
        if threshold*feature_count > thr: break
    Nth = (chr_length-1)/threshold+1
    arrays = [np.zeros(Nth-1)]
    for zz in zooms[nt+1:]:
        Nzz = (chr_length-1)/zz+1
        arrays.append(np.zeros(Nzz))
    while (pos_list):
        row = pos_list.pop()
        for nz,zz in enumerate(zooms[nt:]):
            start_pos = row[0]/zz
            end_pos = (row[1]-1)/zz+1
            arrays[nz][start_pos:end_pos]+=1
    hist_stats = []
    for nz, zoom in enumerate(zooms[nt:]):
        hist_stats.append({'bases': zoom, 'mean': arrays[nz].mean(), 'max': arrays[nz].max()})

    histogram_meta = _histogram_meta(chr_length, zooms[nt:], arrays, url_output, output_directory)
    data = {'headers': headers[extended], 'subfeatureHeaders': subfeature_headers[extended], 
            'subListIndex': SUBLIST_INDEX, 
            'lazyIndex': LAZY_INDEX, 'histogramMeta': histogram_meta, 'histStats': hist_stats,
            'subFeatureClasses': 'subfeatureClasses', 'featureNCList': NCList, 
            'clientConfig': client_config[extended], 'featureCount': feature_count, 
            'key': name, 'arrowheadClass': ARROWHEAD_CLASS, 'type': TYPE, 
            'label': name, 'lazyfeatureUrlTemplate': lazy_url, 'className': CLASSNAME}
    track_data_output = os.path.join(output_directory, 'trackData.json')
    with open(track_data_output, 'w') as f: json.dump(data,f)
    return 1

if __name__ == '__main__':
    import shutil
    out_dir = '/scratch/cluster/monthly/jrougemo/libv2/temp'
    sha1 = 'nosha3'
    db = '/db/genrep/nr_assemblies/annot_tracks/bb27b89826b88823423282438077cdb836e1e6e5.sql'
    jsonify(db, 'aname', sha1, out_dir, 'public_url', 'browser_url', True)
