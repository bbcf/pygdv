from pygdv.model import DBSession, Sequence
from bbcflib import genrep
gr = genrep.GenRep()

def get_species():
    '''
    Get the species in GenRep
    '''
    organisms = gr.get_genrep_objects('organisms','organism')
    return [orga for orga in organisms]

def get_species_by_id(species_id):
    '''
    Get the species from GenRep with this id
    '''
    return gr.get_genrep_objects('organisms','organism',{'id':int(species_id)})[0]

def get_assembly_by_id(assembly_id):
    '''
    Get the the assembly in GenRep
    '''
    return gr.get_genrep_objects('assemblies','assembly',{'id':int(assembly_id)})[0]


def get_assemblies_not_created_from_species_id(species_id):
    '''
    Get the assemblies in GenRep form the species specified
    minus those already created in GDV
    '''
    if not species_id:
        return []
    genomes = gr.get_genrep_objects('genomes','genome',{'organism_id':int(species_id)})
    
    assemblies = gr.get_genrep_objects('assemblies', 'assembly', {'bbcf_valid' : True})
    
    result = []
    for genome in genomes :
        for assembly in assemblies :
            if genome.id == assembly.genome_id :
                if not DBSession.query(Sequence).filter(Sequence.id == assembly.id).first():
                    result.append(assembly)
    return result



def checkright(sequence, user):
    return True

