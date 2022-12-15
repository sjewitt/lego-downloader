var engine = {
    
	plandata : null,
    init : function(){

    	//NOTE The plans are loaded into mongo as a separate process
    	if($('#plans_list').length){
    		//bind handlers to links
    		$('#plans_show_stored > a').click(function(){
    			engine.getplandata({'show':'stored'});
    			return false;
    		});
    		$('#plans_show_not_stored > a').click(function(){
    			engine.getplandata({'show':'notstored'});
    			return false;
        	});
    		$('#plans_show_pending > a').click(function(){
    			engine.getplandata({'show':'pending'});
    			return false;
        	});
    		$('#plans_show_all > a').click(function(){
    			engine.getplandata({'show':'all'});
    			return false;
		    });
    		/*
    		 * use 
    		 *     engine.getplandata({'show':nnnnnn});
    		 * for getting a set directly from source
    		 */
    		 
    		 /** paginated endpoints */
    		 $('#startlinks > li').each(function(){
				console.log('appending handler to ', this)
				$(this).on('click',function(){
					console.log(this);
					engine.getplandata_paginated({'page_length':100, 'filter': $(this).attr('data-action')});
				});
			 });
			 $('#startlinks > li.active').click();
    	}
    },
    
    //check that the plans are loaded
    plansloaded : function(){
    	$.ajax({
            type: "GET",
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            url : "/api/plansloaded"
        }).done(function(data){
        	engine.planDataLoaded = data['planDataLoaded'];
            if(engine.planDataLoaded){
            	engine.getplandata({'setnumber':'showall'});	//in case I need to pass in a set number later
            }
        }).fail(function(jqxhr, status, e){ 
            console.log("err"); 
        });
    },
    
    //Load the plans into memory
    loadplans : function(filterObj){
    	
    	$.ajax({
            type: "GET",
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            url : "/api/loadplans"
        }).done(function(data){
        	engine.planDataLoaded = data['planDataLoaded'];
            
            //load the search/browse form
            if(engine.planDataLoaded){
            	engine.getplandata()
            }
            
        }).fail(function(jqxhr, status, e){ 
            console.log("err"); 
        }).done(function(){});
    },
    
    /*
     * display the plans
     */
    getplandata : function(params){
    	$.ajax({
            type: "GET",
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            url : "/api/getplandata?show=" + params.show
        }).done(function(data){
        	engine.planData = data;
        	var _out = "<table id='plans_listing'><thead><tr><th>Set number</th><th>Description</th><th>Notes</th><th>Actions</th><th></th></tr></thead>";
        	_out += "<tfoot><th>Set number</th><th>Description</th><th>Notes</th><th>Actions</th><th></th></tfoot><tbody>";
        	
        	//TODO: Exclude items that are flagged as unavailable (i.e. we have alrady tried to get the plan, but we got a response othter than 200OK) 
        	
//        	console.log(engine.planData.length);
            for(var a=0;a<engine.planData.length;a++){
//        	for(var a=0;a<10;a++){
//        		console.log(engine.planData[a])
            	if(engine.planData[a].SetNumber !== undefined){
            		
	            	var _desc = engine.planData[a].Description;
	            	//var _notes = engine.planData[a].Notes;
	            	if(_desc.length === 0){
	            		_desc = "[No description]";
	            	}
	            	/*if(_notes.length === 0){
	            		_notes = "[No notes]";
	            	}*/
	
	            	//detect the download status form the object. The downloaded flag will be checked at the python end.
	            	var _isFlaggedForDownload = engine.planData[a].download;
	            	var _isDownloaded = engine.planData[a].downloaded;
	            	
	            	var _downloadFlagIsChecked = '';
	            	if(_isFlaggedForDownload){
	            		_downloadFlagIsChecked = 'checked="checked"';
	            	}
	            	if(_isDownloaded){
	            		_downloadFlagIsChecked = 'disabled="disabled"';
	            	}
	            	
	            	/*Do as DOM elements - faster. Also - do some timing tests...*/
	            	var _isDownloadedMsg = '';
	            	if(_isDownloaded){
	            		_isDownloadedMsg = '[<a href="/api/getstoredplan?getlocal=' + engine.planData[a].key + '.pdf" target="_blank">open</a>]'; 
	            		_isDownloadedMsg += ' [<a href="/api/getstoredplan?action=download&getlocal=' + engine.planData[a].key + '.pdf">download</a>]'
	            		_isDownloadedMsg += ' [<span class="link" data-action="reset">Reset</span>]'  ///api/resetdownload
	            	}
	            	
	            	_out += '<tr data-plan-item="' + engine.planData[a].key + '"><td>' 
	            		+ engine.planData[a].SetNumber+'</td><td class="plan-handler" data-plan-field="Description"><span>' 
	            		+ _desc + '</span></td><td class="plan-handler" data-plan-field="Notes"><span>' 
	            		//+ _notes 
	            		+ '</span></td><td class="download_checkbox"><span class="plan_add"><input type="checkbox" value="' 
	            		+ engine.planData[a].key + '" ' + _downloadFlagIsChecked + '></span></td>'
	            		+ '<td>'+_isDownloadedMsg+'</td>'
	            		+ '</tr>';
	            
            	}
            }
            _out += '</table>';
            $('#plans_list').html(_out);
            $('#plans_listing').dataTable({
            	  "pageLength": 50
            });
            
            //see SO #30794672 - defer binding so that hidden elements are also flagged:
            $('table').on('click','td.download_checkbox',function(){

            	//send AJAX call to back end for this
            	engine.setDownloadFlag($(this).find('input').attr('value'),$(this).find('input').is(':checked'));
            });
            
            $('table').on('click','td.plan-handler > span',function(){
            	//generate a form element, with a blur handler to reset it (removing the input, re-showing the text with update? TO CONFIRM)
            	engine.getEditField($(this));
            });
            
            $('table').on('click','span.link',function(){
            	//generate a form element, with a blur handler to reset it (removing the input, re-showing the text with update? TO CONFIRM)
            	if($(this).attr('data-action') === "reset"){
            		engine.resetDownload($(this).parent().parent().attr('data-plan-item'));
            	}
            	//need to remove  the parent tr as well
            	$(this).parent().parent().remove()
            });            
        }).fail(function(jqxhr, status, e){ 
            console.log("err"); 
        });
    },

    getplandata_paginated : function(params){
    	let page_length=100;
    	let curr_page = 1;
    	let filter = 'all'
    	if(params['page_length']){
			page_length = parseInt(params['page_length']);
		}
		if(params['page_num']){
			curr_page = parseInt(params['page_num']);
		}
		if(params['filter']){
			filter = params['filter'];
		}
    	/** need page_length, curr_page and filter */
    	$.ajax({
            type: "GET",
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            url : "/api/paginated_plandata?page_length=" + page_length + "&page_num=" + curr_page + "&filter=" + filter
        }).done(function(data){
			console.log("/api/paginated_plandata?page_length=" + page_length + "&page_num=" + curr_page + "&filter=" + filter)
        	engine.planData = data;
        	// build as DOM properly
        	var _out = "<table><thead><tr><th>Set number</th><th>Description</th><th>Notes</th><th>Actions</th><th></th></tr></thead>";
        	_out += "<tfoot><th>Set number</th><th>Description</th><th>Notes</th><th>Actions</th><th></th></tfoot><tbody>";
        	
        	//TODO: Exclude items that are flagged as unavailable (i.e. we have alrady tried to get the plan, but we got a response othter than 200OK) 
            for(var a=0;a<engine.planData.entries.length;a++){
            	if(engine.planData.entries[a].SetNumber !== undefined){
	            	var _desc = engine.planData.entries[a].Description;
	            	if(_desc.length === 0){
	            		_desc = "[No description]";
	            	}

	            	//detect the download status form the object. The downloaded flag will be checked at the python end.
	            	var _isFlaggedForDownload = engine.planData.entries[a].download;
	            	var _isDownloaded = engine.planData.entries[a].downloaded;
	            	
	            	var _downloadFlagIsChecked = '';
	            	if(_isFlaggedForDownload){
	            		_downloadFlagIsChecked = 'checked="checked"';
	            	}
	            	if(_isDownloaded){
	            		_downloadFlagIsChecked = 'disabled="disabled"';
	            	}
	            	
	            	/*Do as DOM elements - faster. Also - do some timing tests...*/
	            	var _isDownloadedMsg = '';
	            	if(_isDownloaded){
	            		_isDownloadedMsg = '[<a href="/api/getstoredplan?getlocal=' + engine.planData.entries[a].key + '.pdf" target="_blank">open</a>]'; 
	            		_isDownloadedMsg += ' [<a href="/api/getstoredplan?action=download&getlocal=' + engine.planData.entries[a].key + '.pdf">download</a>]'
	            		_isDownloadedMsg += ' [<span class="link" data-action="reset">Reset</span>]'  ///api/resetdownload
	            	}
	            	
	            	_out += '<tr data-plan-item="' + engine.planData.entries[a].key + '"><td>' 
	            		+ engine.planData.entries[a].SetNumber+'</td><td class="plan-handler" data-plan-field="Description"><span>' 
	            		+ _desc + '</span></td><td class="plan-handler" data-plan-field="Notes"><span>' 
	            		+ '</span></td><td class="download_checkbox"><span class="plan_add"><input type="checkbox" value="' 
	            		+ engine.planData.entries[a].key + '" ' + _downloadFlagIsChecked + '></span></td>'
	            		+ '<td>'+_isDownloadedMsg+'</td>'
	            		+ '</tr>';
            	}
            }
            _out += '</table>';
            $('#plans_list').html(_out);
            $('#plans_listing').dataTable({
            	  "pageLength": 50
            });
            
            //see SO #30794672 - defer binding so that hidden elements are also flagged:
            $('table').on('click','td.download_checkbox',function(){

            	//send AJAX call to back end for this
            	engine.setDownloadFlag($(this).find('input').attr('value'),$(this).find('input').is(':checked'));
            });
            
            $('table').on('click','td.plan-handler > span',function(){
            	//generate a form element, with a blur handler to reset it (removing the input, re-showing the text with update? TO CONFIRM)
            	engine.getEditField($(this));
            });
            
            $('table').on('click','span.link',function(){
            	//generate a form element, with a blur handler to reset it (removing the input, re-showing the text with update? TO CONFIRM)
            	if($(this).attr('data-action') === "reset"){
            		engine.resetDownload($(this).parent().parent().attr('data-plan-item'));
            	}
            	//need to remove  the parent tr as well
            	$(this).parent().parent().remove()
            });  
            
            //paginator:
            let _paginator_location = document.getElementById('paginator') ;
            _paginator_location.innerHTML = "" 
            _paginator_location.appendChild(engine.getPaginationLinks(data.pagination_data))  
        }).fail(function(jqxhr, status, e){ 
            console.log("err"); 
        });
    },
    
    getPaginationLinks : function(data){
		let total_pages = Math.ceil(data.total / data.page_length);
		
		let _wrapper = document.createElement('ul');
		let _pagination_info = document.createElement('li');
		_pagination_info.setAttribute('class','paginator_info');
		_pagination_info.innerHTML = 'page ' + data.curr_page + ' of ' + total_pages + ' (of '+ data.total +' records)';
		
		//get prev or next page numbers
		let prevpagemany = data.curr_page > 0 ? data.curr_page - 15 : 0;
		let prevpageone = data.curr_page > 0 ? data.curr_page-1 : 0;
		let nextpageone = data.curr_page <= total_pages ? data.curr_page+1 :  total_pages; 
		let nextpagemany = data.curr_page <= total_pages ? data.curr_page + 15 :  total_pages;
		
		_back_one = this.getPaginationLink(data,prevpageone,'<',this.paginationHandler);
		_back_many = this.getPaginationLink(data,prevpagemany,'<<',this.paginationHandler);
		_fwd_one = this.getPaginationLink(data,nextpageone,'>',this.paginationHandler);
		_fwd_many = this.getPaginationLink(data, nextpagemany, '>>', this.paginationHandler);
		
		_wrapper.appendChild(_back_many);
		_wrapper.appendChild(_back_one);
		_wrapper.appendChild(_pagination_info);
		_wrapper.appendChild(_fwd_one);
		_wrapper.appendChild(_fwd_many);
		return(_wrapper);
	},
	
	/** build link, or just display elem, from link data */
	getPaginationLink : function(data, target_page,link_text,handler){
		let total_pages = Math.ceil(data.total / data.page_length);
		let _li = document.createElement('li');
		_li.setAttribute('data-targetpage',target_page);
		_li.setAttribute('data-total',data.total);
		_li.setAttribute('data-page_length',100);	//TODO: Set this programmatically
		_li.setAttribute('data-filter',data.filter_key);
		_li.appendChild(document.createTextNode(link_text));
		if(target_page > 0 && target_page < total_pages){
			_li.setAttribute('class','paginator');
			_li.addEventListener('click',handler);
		}

		console.log(_li)
		return(_li);
	},
	
	paginationHandler : function(){
		console.log('in pagination handler...');
		let args = {
			page_num:parseInt(this.getAttribute('data-targetpage')),
			filter:this.getAttribute('data-filter'),
			page_length:this.getAttribute('data-page_length'),
			total:this.getAttribute('data-total')
		}
		engine.getplandata_paginated(args);
	},
	
	
    resetDownload : function(key){
    	var _params = {'key':key};
    	$.ajax({
            type: "POST",  
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            data:JSON.stringify(_params),
            url : "/api/resetdownload"
        }).done(function(data){ });
    },
    
    setDownloadFlag : function(setnumber,flag){
    	$.ajax({
            type: "GET",  
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            url : "/api/flagdownload?setnumber=" + setnumber + "&flag=" + flag    //flag is boolean - enable/disable the download
        }).done(function(data){ });
    },
    
    /*
     * Construct an imput field with the current text:
     * 
     * params:
     * elem: DOM element that was clicked (should be a td)
     * 
     */
    getEditField : function(elem){
    	var _out = document.createElement('input');
        _out.setAttribute('type','text');
        _out.setAttribute("value", $(elem).text());
        $(_out).css({'width':'100%'});

        $(_out).blur(function(){
        	$(this).parent().find('span').css({'display':'inline'});
        	//send update AJAX request:
        	//key,identifier (class),value
        	engine.updateEntry( 
        			$(this).parent().parent().attr('data-plan-item'),
        		    $(this).parent().attr('data-plan-field'),
        		    $(this).val()
        		);
        	
        	//update text:
        	$(this).parent().find('span').text($(this).val());
	        $(this).remove();
        });

        $(elem).parent().append(_out);
        $(_out).focus();

    	$(elem).parent().find('span').css({'display':'none'});
    	return false;
    },
    
    updateEntry : function(key,field,val){
    	_update = {
    		'key':key,
    		'field':field,
    		'val':val
    	}
    	
    	$.ajax({
            type: "POST",
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            data:JSON.stringify(_update),
            url : "/api/updateplan",   //flag is boolean - enable/disable the download
        }).done(function(){ });
    },
    
    _getQSVal : function(url,param){
        var _params = decodeURI(url).split('?');
        var _out = '';
        if(_params.length === 2){
            var _bits = _params[1].split(/&/g);
            for(var b=0;b<_bits.length;b++){
                if(_bits[b].split(/=/)[0] === param){
                    //get rid of hash, if found:
                    _out = _bits[b].split(/=/)[1];
                    if(_out.indexOf('#') !== -1){
                        _out = _out.split(/#/)[0];
                    }
                    return(_out);
                }
            }
        }
        return(null);
    }

};

//ajax start/stop for progress icon
$(document).bind('ajaxStart', function(){
//    $("#ajax-loading").dialog({
//        'modal':true
//    });
}).bind('ajaxStop', function(){
//    $("#ajax-loading").dialog('close');
});
