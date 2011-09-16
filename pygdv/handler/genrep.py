from tg import app_globals as gl
from pygdv.model import DBSession, Sequence



def get_species():
    '''
    Get the species in GenRep
    '''
    organisms = gl.genrep.get_genrep_objects('organisms','organism')
    return [orga for orga in organisms]

def get_species_by_id(species_id):
    '''
    Get the species from GenRep with this id
    '''
    return gl.genrep.get_genrep_objects('organisms','organism',{'id':int(species_id)})[0]

def get_nr_assembly_by_id(nr_assembly_id):
    '''
    Get the the nr_assembly in GenRep
    '''
    return gl.genrep.get_genrep_objects('nr_assemblies','nr_assembly',{'id':int(nr_assembly_id)})[0]

def get_nr_assemblies_not_created_from_species_id(species_id):
    '''
    Get the assemblies in GenRep form the species specified
    minus those already created in GDV
    '''
    if not species_id:
        return []
    # get species
   # species = gl.genrep.get_genrep_objects('organisms','organism',{'species':species.species})[0s]
    # get genomes, filter by species
    genomes = gl.genrep.get_genrep_objects('genomes','genome',{'organism_id':int(species_id)})
    # get nr_assemblies
    nr_assemblies = gl.genrep.get_genrep_objects('nr_assemblies','nr_assembly')
    result = []
    # get nr_assemblies with same genome id as the species
    for genome in genomes :
        for nr_assembly in nr_assemblies :
            if genome.id == nr_assembly.genome_id :
                # look if the assembly not already created
                if not DBSession.query(Sequence).filter(Sequence.id == nr_assembly.id).first():
                    result.append(nr_assembly)
    return result