/*
 * Jobs : contains methods to launch & update jobs
 * launched to GDV
 *
 *
 */

dojo.declare("ch.epfl.bbcf.gdv.JobHandler",null,{
    constructor: function(args){
        dojo.mixin(this, args);
        this.jobs = [];
        this.init_jobs();
	
    },
    init_jobs : function(){
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
     */
    new_selection : function(project_id,nrassemblyid,selections,selection_name){
        var body = "id=job&action=new_selection&project_id="+project_id+"&nrass="+nrassemblyid+"&selections="+selections+"&data="+selection_name;
        _tc.container.selectChild("tab_jobs");
        this.post_to_gdv(body,true);
	
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
    post_to_gdv : function(body,tag){
        console.log(body);
        var xhrArgs = {
            url: _POST_URL_GDV,
            postData: body,
            handleAs: "json",
            load: function(data) {
		console.log(data);
		_jh.add_job(data);
		if(tag){
		    _jh.display_jobs();
		}
            },
            error: function(data){
		console.error('failed : ');
		console.log(data);
            }
        }
        dojo.xhrPost(xhrArgs);
    },
    /**
     * Add a job to the job handler
     *@param{job} the job
     */
    add_job : function(job){
        var jobs = this.jobs;
        var index = jobs.containsJob(job);
        if(!(index>-1)){
            jobs.push(job);
        } else {
            jobs.splice(index,1,job);
        }
        this.jobs=jobs;
    },
    
    
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
            else if(job.status=='running'){
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
