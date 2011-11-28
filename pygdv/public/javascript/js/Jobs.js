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
	this.init_old_jobs();
    },
    
    
    init_old_jobs : function(){
        var jobs = dojo.byId('init_jobs').innerHTML;
        if(jobs){
            //console.log(jobs);
	    var json_jobs = dojo.fromJson(jobs);
            var ctx=this;
            dojo.forEach(json_jobs, function(entry, i){
                ctx.update_job(entry);
            });
        }
    },

    
    /**
     * send a new selection job
     * @param {selection} - the selections
     */
    new_selection : function(selections){
	var sorted = {};
        /* build description & sort the marquees like {chr : [marquees]}*/
	var desc = '';
	var cur_chr;
	dojo.forEach(selections, function(entry, index){
	    cur_chr = entry['chr'];
	    if (!(cur_chr in sorted)) sorted[cur_chr] = [];
	    sorted[cur_chr].push({'start' : entry.start, 'end' : entry.end});
	    desc += '( ' + entry.display() + ' )';
	});
	/* build job */
	//console.log('new sel');
	this.new_job('selection', desc, '/new_selection', 
		     'project_id=' + _gdv_info.project_id + '&s='+ dojo.toJson(sorted));
    },

    /**
     * launch a new gfeatminer job
     * @param{project_id} the project id
     * @param{data} the data from the form
     */
    new_gfeatminer_job: function(data){
      	var name = 'gfeatminer';
	var desc = 'job'
	if('characteristic' in data) desc = data['characteristic'];
	if('operation_type' in data) name = data['operation_type'];
	
	this.new_job(name, desc, '/new_gfeatminer_job',
		     'project_id=' + _gdv_info.project_id + '&data='+ dojo.toJson(data));
        	
    },
    
    /**
     * Post the body to GDV
     * @param{body} - the body to post
     */
    post_to_gdv : function(url, body){
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
	//console.log('update jobs');
	//console.log(data);
	/* Get job or create it */
	if(data && 'job_id' in data){
	    var job_id = data['job_id'];
	    var job = this.get_job(job_id);
	    
	    if (job){
		/* update fields */
		dojo.mixin(job, data);
	    } else {
		/* create new */
		data['url'] = '/status';
		data['body'] = 'job_id=' + data['job_id'];
		job = new GDVJob(data, false);
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
	//notify('job ' + name + ' launched (' + description +').');
    }, 
    

    /**
     * Will relaunch a status update for the job if needed
     * TODO : check if the job has to be updated relaunch it or just display it - how - ???
     */
    check_job : function(job){
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
	    this.body = this.body += '&job_name=' + name + '&job_description= ' + description;
	} 
    }
});

