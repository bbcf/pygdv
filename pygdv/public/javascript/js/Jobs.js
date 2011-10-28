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
     * get the status of a job
     * and the result if there is success
     */
    get_job_status : function(job_id){
        var body = "id=job&action=status&job_id="+job_id;
        this.post_to_gdv(body);
    },
    
    /**
     * send a new selection job
     * @param {selection} - the selections
     */
    new_selection : function(selections){
        /* build description */
	var desc = '';
	dojo.forEach(selections, function(entry, index){
	    desc += '( ' + entry.get() + ' )';
	});
	/* build job */
	this.new_job('selection', desc, 'project_id=' + _gdv_info.project_id + '&s='+ dojo.toJson(selections));
    },

    /**
     * launch a new gfeatminer job
     * @param{project_id} the project id
     * @param{data} the data from the form
     */
    new_gfeatminer_job: function(project_id,data){
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
        console.log(body);
        var xhrArgs = {
            url: _POST_URL_GDV + '/url',
            postData: body,
            handleAs: "json",
            load: function(data) {
		this.update_job(data);
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
	/* get job or create it */
	var job_id = data['job_id'];
	var job = this.get_job(job_id);
	if (job){
	    job.name = data['name'];
	    job.description = data['description'];
	    job.status = data['status'];
	} else {
	    job = new GDVJob(
		job_id,
		data['name'], 
		data['description'],
		data['status'],
		'/status', 
		'job_id=' + data['job_id'], false)
	}
	
	this.put_job(job);
	
	this.check_job(job);
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
    put_job : function(job){
	this.jobs[job.id] = job;
    },
    /**
     * Will create and send a new job on GDV
     */
    new_job : function(name, description, url, body){
	body += '&job_name=' +name + 'job_description= ' + description;
	this.post_to_gdv(url, body);
	notify('job ' + job.name + ' launched (' + description +').');
    }, 
    

    /**
     * Will relaunch a status update for the job if needed
     * TODO : check if the job has to be updated relaunch it or just display it - how - ???
     */
    check_job : function(job){

    }
    /**
     * Display the jobs on the tab container
     * & start updating jobs that are running
     */
    display_jobs : function(){
        var jobs = this.jobs;
        var update=false;
        var ctx = this;
        dojo.forEach(jobs, function(job, i){
            if(job.failed){
		console.log(job);
		console.error(job.data);
            }
            else if(job.status == 'running'){
                update = true;
                ctx.get_job_status(job.job_id);
            }
            _tc.addJob(job);
        });
        if(update){
            var ctx = this;
            this.displayTimeout = setTimeout(function(){
		ctx.display_jobs()
            },_GDV_JOB_STATUS_WAIT);
        }
    },
    /**
     * Stop the update of the job display
     */
    stop_display : function(){
        clearTimeout(this.displayTimeout);
    }
});




/**
 * Add a method to array object, that it
 * could search & compare containing jobs
 * @return the index of the same job if contains, else -1
 */
Array.prototype.containsJob = function (job){
    var i;
    for (i = 0; i < this.length; i += 1){
	if(job.job_id===this[i].job_id){
            return i;
	}
    }
    return -1;
};








dojo.declare("GDVJob", null, {
    constructor: function(id, name, description, url, body_params, flag){
        this.launched = false;
	this.id = id;
	this.name = name;
	this.description = description;
	this.url = url;
	this.statue = 'running';
	if (flag){
	    this.body = body_params += '&job_name=' +name + 'job_description= ' + description;
	} else {
	    this.body = body_params;
	}
    }
});