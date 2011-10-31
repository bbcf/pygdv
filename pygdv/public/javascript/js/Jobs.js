/*
 * Jobs : contains methods to launch & update jobs
 * launched to GDV
 *
 *
 */

dojo.declare("ch.epfl.bbcf.gdv.JobHandler",null,{
    constructor: function(args){
        dojo.mixin(this, args);
        this.jobs = {};
	//this.init_old_jobs();
    },
    
    
    init_old_jobs : function(){
        var jobs = dojo.byId('init_jobs').innerHTML;
        if(jobs){
            var json_jobs = dojo.fromJson(jobs);
            var ctx=this;
            dojo.forEach(json_jobs, function(entry, i){
                ctx.add_job(entry);
            });
        }
    },

    
    /**
     * send a new selection job
     * @param {selection} - the selections
     */
    new_selection : function(selections){
        /* build description */
	var desc = '';
	dojo.forEach(selections, function(entry, index){
	    desc += '( ' + entry.display() + ' )';
	});
	/* build job */
	//console.log('new sel');
	this.new_job('selection', desc, '/new_selection', 
		     'project_id=' + _gdv_info.project_id + '&s='+ dojo.toJson(selections));
    },

    /**
     * launch a new gfeatminer job
     * @param{project_id} the project id
     * @param{data} the data from the form
     */
    new_gfeatminer_job: function(project_id,data){
        //console.log('new gm');
	var body = "id=job&action=gfeatminer&project_id="+project_id+"&data="+dojo.toJson(data);
        _tc.container.selectChild("tab_jobs");
        //console.log(data);
        this.post_to_gdv(body);
	
    },
    
    /**
     * Post the body to GDV
     * @param{body} - the body to post
     */
    post_to_gdv : function(url, body){
	//console.log('ptgdv');
	var ctx = this;
        var xhrArgs = {
            url: _GDV_WORKER_URL + url,
            postData: body,
            handleAs: "json",
            load: function(data) {
		ctx.update_job(data);
	    },
            error: function(data){
		console.error('failed : ');
		console.log(data);
            }
        }
        dojo.xhrPost(xhrArgs);
    },


    
    /**
     * Response send by GDV back to the view
     */
    update_job : function(data){
	//console.log('update job');
	//console.log(data);
	/* get job or create it */
	if(data && 'job_id' in data){
	    var job_id = data['job_id'];
	    var job = this.get_job(job_id);
	    
	    if (job){
		/* update fields */
		dojo.mixin(job, data)
	    } else {
		/* create new */
		data['url'] = '/status',
		job = new GDVJob(data, false)
	    }
	    this.to_buffer(job);
	    this.check_job(job);
	    
	}
    },

    /**
     * Return a job by it's id
     */
    get_job : function(job_id){
	return this.jobs[job_id];
    },
    /**
     * Put the job in the buffer
     */
    to_buffer : function(job){
	this.jobs[job.job_id] = job;
    },
    /**
     * Will create and send a new job on GDV
     */
    new_job : function(name, description, url, body){
	//console.log('new_job');
	body += '&job_name=' + name + '&job_description= ' + description;
	this.post_to_gdv(url, body);
	notify('job ' + name + ' launched (' + description +').');
    }, 
    

    /**
     * Will relaunch a status update for the job if needed
     * TODO : check if the job has to be updated relaunch it or just display it - how - ???
     */
    check_job : function(job){
	//console.log('check job');
	//console.log(job);
	var ctx = this;
	if (job.status == 'RUNNING' || job.status == 'running' || 
	    job.status == 'pending' || job.status == 'PENDING'){
	    var ctx = this;
	    setTimeout(function(){
		ctx.post_to_gdv(job.url, job.body);
	    }, _GDV_JOB_STATUS_WAIT);
	}
	/* add the job to the tab_container */
	_tc.addJob(job);
    }
});




dojo.declare("GDVJob", null, {
    constructor: function(args, flag){
        dojo.mixin(this, args)
	this.launched = false;
	if (flag){
	    this.body = this.body += '&job_name=' +name + '&job_description= ' + description;
	} 
    }
});

