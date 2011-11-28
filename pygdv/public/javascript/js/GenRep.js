/**
* The general GenRep object used for queries.
*/
function GenRep(gv) {
    // Store the view
    this.gv = gv;
    // Hard coded URL
    this.url = 'http://bbcftools.vital-it.ch/genrep/';
}

/**
* Gets a GenRep URL
* @param{fn} the function to be executed with the data
* @param{path} the file path
* @example: b.view.genrep.get(function(a) {console.log("Result:", a)}, 'chromosomes.jsonp', {assembly_id: 11})
* @example: b.view.genrep.get(function(a) {console.log("Result:", a)}, 'chromosomes/11/bands.jsonp')
* @returns the complete url
*/
GenRep.prototype.get = function(fn, path, content) {
    if (!fn) {fn = function(data) {console.log(data);};}
    var ctx = this;
    dojo.io.script.get({
                url: this.url + path,
                jsonp: "callback",
                content: content,
                load: fn,
                error: ctx.error
    });
    return this.url + path;
};

GenRep.prototype.error = function(data){
    console.error(data);
};

/**
* Determines the currently view chromosome id (e.g. 3075)
* @param{fn} the function to be executed with the data
* @example: b.view.genrep.current_chr_id(function(id) {console.log("The id is:", id)})
* @returns nothing
*/
GenRep.prototype.current_chr_id = function(fn) {
    var assembly_id  = this.gv.nr_assembly_id;
    var chr_name  = b.refSeq['name'];
    this.chr_name_to_id(fn, assembly_id, chr_name);
};

/**
* Given an assembly id and a chromosome name, returns
* the chromosome identification number (e.g. 3075)
* @param{fn} the function to be executed with the data
* @param{assembly_id} the id of the assemlby (e.g. 11 for hg19)
* @param{chr_name} the chromsome name (e.g. 'chrX')
* @returns nothing
*/
GenRep.prototype.chr_name_to_id = function(fn, assembly_id, chr_name) {
    callback = dojo.hitch(this, function(data) {
        var chrom = this.filter_chrs(data, chr_name);
        var id = this.get_chr_id(chrom);
        fn(id);
    });
    this.get(callback, 'chromosomes.jsonp', {assembly_id: assembly_id});
};

/**
* Filters a list of chromosomes according to a name
* This function will check every possible synonym for every
* chromsome.
* @param{chroms} a list of Chromsome objects
* @param{input_name} the chr_name that ones needs (e.g. 'chrX')
* @returns a Chromosome object
*/
GenRep.prototype.filter_chrs = function(chroms, input_name) {
    for(var i=0; i<chroms.length; i++) {
        var chrom = chroms[i];
        var names = chrom['chromosome']['chr_names'];
        for(var j=0; j<names.length; j++) {
            var name = names[j];
            if (name['chr_name']['value'] == input_name) {
                return chrom;
            }
        }
    }
    return null;
};

/**
* Given a chromosome object, extracts the id
* @param{chrom} a Chromosome object
* @returns an integer representing the chromosome id (e.g. 3075)
*/
GenRep.prototype.get_chr_id = function(chrom) {
    if (chrom) return chrom['chromosome']['id'];
    else console.error('GenRep.get_chr_id : ' + chrom);
};

/**
* Gets the cytosomal bands of the current chromosome
* @param{fn} the function to be executed with the data
* @returns nothing
*/
GenRep.prototype.bands = function(fn) {
    callback = dojo.hitch(this, function(chr_id) {this.bands_by_chr(fn, chr_id);});
    this.current_chr_id(callback);
};

/**
* Gets the cytosomal bands of a specific chromosome
* @param{fn} the function to be executed with the data
* @param{chr_id} the chromosome identifier (e.g. 3075)
* @returns nothing
*/
GenRep.prototype.bands_by_chr = function(fn, chr_id) {
    callback = dojo.hitch(this, function(data) {fn(this.annotate_bands(data));});
    this.get(callback, 'chromosomes/' + chr_id + '/bands.jsonp');
};

/**
* Add some necessary information to the cyto bands
* such as which are the extreme and middle bands.
* @param{bands} a list of Band objects
* @returns a list of Band objects
*/
GenRep.prototype.annotate_bands = function(bands) {
    // Check that we have bands
    if (bands.length == 0) {return [];}
    // Default value
    dojo.forEach(bands, function(band) {band['band']['position'] = false;});
    // Extreme bands
    bands[0]['band']['position'] = 'left';
    bands[bands.length-1]['band']['position'] = 'right';
    // Middle bands
    for(var i=1; i<bands.length; i++) {
        var prev = bands[i-1];
        var next = bands[i];
        var prev_name = prev['band']['name'];
        var next_name = next['band']['name'];
        if (prev_name[0] == 'p' && next_name[0] == 'q') {
            prev['band']['position'] = 'right';
            next['band']['position'] = 'left';
        }
    }
    return bands;
};
