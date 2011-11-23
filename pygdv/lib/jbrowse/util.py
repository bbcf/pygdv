from tg import app_globals as gl
from bbcflib.genrep import GenRep
from pygdv.lib.jbrowse import SEQUENCE_CHUNK_SIZE
from pygdv.model import Track
import json
'''
Contains utility methods for buildings JSON informations that the browser need.
'''


def track_info(tracks):
    '''
    Build ``trackInfo`` variable.
    '''
    list = []
    ##TODO add DNA track
    l = [track.parameters.jb_dict for track in tracks]
    return [track.parameters.jb_dict for track in tracks]
        
        
        
        
def ref_seqs(sequence_id):
    '''
    Build the ``refSeqs`` variable.
    @param sequence_id : the assembly_id in GenRep.
    '''
    gl = GenRep()
    chromosomes = gl.get_chromosomes_from_assembly_id(sequence_id)
    return [_chromosome_output(chr) for chr in chromosomes]
    
    
    
def browser_parameters(data_root, style_root, image_root, tracks_names):
    '''
    Build the browser parameters needed by the view.
    :param: data_root : path to the root directory of the data.
    :param: style_root : path to the root directory containing stylesheet.
    :param: tracks_names : all tracks name put one after another.
    '''
    return "{'containerID' : 'GenomeBrowser', 'refSeqs' : refSeqs, 'browserRoot' : '%s','dataRoot' : '%s', 'imageRoot' : '%s', 'styleRoot' : '%s', trackData : trackInfo, 'defaultTracks' : '%s'}" % (data_root, data_root, image_root, style_root, tracks_names)


def features_style(tracks):
    '''
    Build the body of the switch statement in the javascript to fit the right style to the right feature.
    :param: tracks . the tracks
    '''
    #toDO
    return '''case 'exon': case 'intron': default: div.style.height='10px';div.style.marginTop='-4px';div.style.zIndex='30';break'''
    
def _chromosome_output(chromosome):
    '''
    Get the chromosome output for the browser.
    :param: chromosome : the chromosome
    '''
    #print '[WARNING] : here is used the chromosome "name" & not the "chr_name"'
    return {"length" : chromosome.length,
            "name" : chromosome.chr_name,
            "seqDir": 'TODO',
            "start": 0,
            "end": chromosome.length,
            "seqChunkSize" : SEQUENCE_CHUNK_SIZE}

    