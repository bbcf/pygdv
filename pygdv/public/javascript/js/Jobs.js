function JobPane(){};


JobPane.prototype.init_panel = function(DomNode, DijitNode){
    var cont = dojo.create('div', {}, DomNode);
    var job_container = new dijit.layout.ContentPane({
	title: "Jobs",
	id:'tab_jobs'
    }, cont);
    DijitNode.addChild(job_container);
    
    this.jobs = job_container;
    
    
    //init jobs                                                                                                      
    var jobs = init_jobs;
    var jobs_table = dojo.create("table", {id:"jobs_table", className: 'pane_table',}, cont);
    var jbl = jobs.length;
    var ctx = this;
    for(var i=0; i<jbl; i++){
	var job = jobs[i];
	var tr = dojo.create("tr", {}, jobs_table);
	var m = dojo.create("table", {className: 'pane_element'}, tr);
	var tr = dojo.create("tr", {}, m);
	var td = dojo.create("td", {className: 'pane_unit', innerHTML: job.name, title: job.desc}, tr);
	var td = dojo.create("td", {className: 'pane_unit'}, tr);
	td.appendChild(ctx.job_output(job));
    }
};

/**
* Return the right display for the job output
*/
JobPane.prototype.job_output = function(job){
    var job_output = job.out;
    switch(job_output){
    case 'job_image': return dojo.create('a', {target:'_blank', href: _GDV_JOB_URL + '/result?id=' + job.id, innerHTML:'view output'});
    case 'job_failure': return dojo.create('a', {target:'_blank', href: _GDV_JOB_URL + '/traceback?id=' + job.id, innerHTML:'failure'});
    case 'job_pendintg': return dojo.create('div', {innerHTML : 'Running', className : 'loading_gif'});
    default: return dojo.create('a', {target : '_blank', href : 'javascript:location.reload(true);'});
    }
};
