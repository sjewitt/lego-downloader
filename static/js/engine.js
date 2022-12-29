var engine = {

	plandata : null,
    init : function(page){
		switch(page){
			case 'index':
				/** we want to set the default, or currently selected, page length back to the dropdown as well as apply the click handler if we
				want to reset it...*/
				this.setCurrentPageLength();
				this.setPageLengthButtonHandler();
				this.setJumpToPageButtonHandler();
		    	//NOTE The plans are loaded into mongo as a separate process
		    	if($('#plans_list').length){
		    		 /** paginated endpoints */
		    		 $('#startlinks > li').each(function(){
						$(this).on('click',function(){
							engine.getplandata_paginated({'filter': $(this).attr('data-action')});
							engine.toggleMenuHighlight(this);
						});
					 });
					 $('#startlinks > li.active').click();
					 
					 /** add handler to set # filter */
					document.getElementById('set_num_filter').addEventListener('keyup',function(){
						fetch('/api/set_set_filter?set_filter=' + this.value)
							.then((response) => response.json())
							.then(function(data){
								/** find the highlighted menu, and click that */
								document.querySelector('#startlinks > li.active').click();
							});
					});
		    	};
		    	/** have we been sent a URL parameter from - eg a manual upload? */
				let view = this._getQSVal(document.location.href,'filter');
				console.log('#startlinks > li[data-action="' + view+ '"]');
				$('#startlinks > li[data-action="' + view+ '"]').click();
			break;

			case 'manage':
				/** load handlers for manage page */
				this.getPreviousFetches('previous_fetches');
				$('#managelinks > li')
					.each(function(){
						$(this).on('click',function(){
							engine.toggleMenuHighlight(this);
						});
					 });
		    	document.getElementById('manage_load_plans').addEventListener('click',function(){
					engine.loadplans();
				});			
			break;

			default:
		}
    },

	getPreviousFetches : function(target_id){
		let previous_fetches = document.getElementById(target_id);
		
		fetch('/api/previous_fetches')
			.then((response) => response.json())
			.then(function(data){
				/** find the highlighted menu, and click that */
				let _table = engine.getDOMElement('table',[]);
				let _thead = engine.getDOMElement('thead',[]);
				let _tfoot = engine.getDOMElement('tfoot',[]);
				let _tr = engine.getDOMElement('tr',[]);
				let _th1 = engine.getDOMElement('th',[]);
				let _th2 = engine.getDOMElement('th',[]);
				let _th3 = engine.getDOMElement('th',[]);
				let _th4 = engine.getDOMElement('th',[]);
				
				_th1.appendChild(document.createTextNode('Timestamp'));
				_th2.appendChild(document.createTextNode('Total processed'));
				_th3.appendChild(document.createTextNode('Total added'));
				_th4.appendChild(document.createTextNode('Error count'));
				
				_tr.appendChild(_th1);
				_tr.appendChild(_th2);
				_tr.appendChild(_th3);
				_tr.appendChild(_th4);
				
				_thead.appendChild(_tr);
				_tfoot.appendChild(_tr.cloneNode(true));	//see https://developer.mozilla.org/en-US/docs/Web/API/Node/cloneNode
				
				let _tbody = engine.getDOMElement('tbody',[]);
				for(entry of data){
					let _tr = engine.getDOMElement('tr',[]);
					/** basic output */
					let _td1 = engine.getDOMElement('td',[]);
					let _td2 = engine.getDOMElement('td',[]);
					let _td3 = engine.getDOMElement('td',[]);
					let _td4 = engine.getDOMElement('td',[]);
					
					_td1.appendChild(document.createTextNode(entry['timestamp']));
					_td2.appendChild(document.createTextNode(entry['data']['num_processed']));
					_td3.appendChild(document.createTextNode(entry['data']['num_added']));
					_td4.appendChild(document.createTextNode(entry['error_count']));
					
					_tr.appendChild(_td1);
					_tr.appendChild(_td2);
					_tr.appendChild(_td3);
					_tr.appendChild(_td4);
					_tbody.appendChild(_tr);
				}
				_table.appendChild(_thead);
				_table.appendChild(_tbody);
				_table.appendChild(_tfoot);
				previous_fetches.innerHTML = '';
				previous_fetches.appendChild(_table);
			});
	},
    
    setPageLengthButtonHandler : function(){
		let set_page_length = document.getElementById('set_page_length_btn');
		set_page_length.addEventListener('click',function(evt){
			let page_length_selector = document.getElementById('set_page_length');
			fetch('/api/set_page_length?page_length=' + page_length_selector.value)
				.then((response) => response.json())
				.then(function(data){
					/** find the highlighted menu, and click that */
					document.querySelector('#startlinks > li.active').click();
				});
		});
	},
	
	setJumpToPageButtonHandler : function(){
		let jump_to_page = document.getElementById('jump_to_btn');
		/** get the jump params from the paginator */
		jump_to_page.addEventListener('click',function(){
			let page_to_load = document.getElementById('jump_to').value;

			let params = {};
			params.page_num = parseInt(page_to_load);
			engine.getplandata_paginated(params);
		})
	},
    
    setCurrentPageLength : function(){
		//use fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
		// see also https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions
		fetch('/api/get_page_length')
			.then(function(response){
				return(response.json())
			})
			.then(function(data){
				let page_length_selector = document.getElementById('set_page_length');
				for (option of page_length_selector.children){
					option.removeAttribute('selected');
					if(option.value === data.page_length.toString()){
						option.setAttribute('selected','selected');
					}
				}
			})	
	},
    
    toggleMenuHighlight : function(elem){
		for(item of elem.parentNode.children){
			item.classList.remove('active');
			if(item === elem){
				item.classList.add('active')
			}
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
    
    loadplans : function(){
		let progress = document.getElementById('manage_content');
		let _pending = this.getDOMElement('div',[]);
		let _spinner = this.getDOMElement('img',[{'attr':'src','val':'/static/images/load-loading.gif'}]);
		_pending.appendChild(_spinner);
		_pending.appendChild(document.createTextNode('retrieving...'));
		progress.appendChild(_pending);
		fetch('/api/loadplans')
			.then(function(response){
				return(response.json());
			})
			.then(function(data){
				/** process return data to database (so we have a record of each update) and process display */
				progress.innerHTML = '';
				let _done = engine.getDOMElement('div',[]);
				_done.appendChild(document.createTextNode('Done!'));
				progress.appendChild(_done);
				engine.getPreviousFetches('previous_fetches');
			})
	},
    
    //Load the plans into memory
    loadplansXXXX : function(filterObj){
    	
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
    

    getplandata_paginated : function(params){
    	let curr_page = 1;
    	let filter = 'all';
    	let set = null;
    	if(params['page_length']){
			page_length = parseInt(params['page_length']);
		}
		if(params['page_num']){
			curr_page = parseInt(params['page_num']);
		}
		if(params['filter']){
			filter = params['filter'];
		}
		if(params['set']){
			set = params['set'];	//a regex filter anchored at start for set number
		}
		let list_url = "/api/paginated_plandata?page_num=" + curr_page + "&filter=" + filter;
		if(set){
			list_url += "&set=" + set;
		}
    	/** need page_length, curr_page and filter */
    	$.ajax({
            type: "GET",
            contentType: 'application/json; charset=utf-8',
            dataType: 'json',
            url : list_url
        }).done(function(data){
			/** set the set number filter, if found */
			let set_filter_elem = document.getElementById('set_num_filter');
			set_filter_elem.value = "";
			if(data.pagination_data.set_filter){
				set_filter_elem.value = data.pagination_data.set_filter;
			}
        	engine.planData = data;
        	// build as DOM properly
        	var _out = "<table><thead><tr><th>Set number</th><th>Description</th><th>Notes</th><th class='actions_col' colspan='2'>Actions</th></tr></thead>";
        	_out += "<tfoot><th>Set number</th><th>Description</th><th>Notes</th><th class='actions_col' colspan='2'>Actions</th></tfoot><tbody>";
        	
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
	            	let _notes = " - ";
	            	if(engine.planData.entries[a].Notes){
						_notes = engine.planData.entries[a].Notes;
					}
	            	
	            	var _downloadFlagIsChecked = '';
	            	if(_isFlaggedForDownload){
	            		_downloadFlagIsChecked = 'checked="checked"';
	            	}
	            	if(_isDownloaded){
	            		_downloadFlagIsChecked = 'disabled="disabled"';
	            	}
	            	
	            	let _isDownloadedMsg = '';
	            	if(_isDownloaded){
	            		_isDownloadedMsg = '<a href="/api/getstoredplan?getlocal=' + engine.planData.entries[a].key + '.pdf" target="_blank"><img src="/static/images/open.png" title="Open plan in browser"></a>'; 
	            		_isDownloadedMsg += ' <a href="/api/getstoredplan?action=download&getlocal=' + engine.planData.entries[a].key + '.pdf"><img src="/static/images/download.png" title="Save plan to file"></a>'
	            		_isDownloadedMsg += ' <span class="link" data-action="reset"><img src="/static/images/reset.png" title="Remove downloaded file"></span>'  ///api/resetdownload
	            	}
	            	/* Do as DOM elements - faster. Also - do some timing tests... */
	            	let isDownloadedMsg = engine.getDOMElement('span',[]);
	            	if(_isDownloaded){
						let a1 = engine.getDOMElement('a',[{'attr':'href', 'val' : '/api/getstoredplan?getlocal=' + engine.planData.entries[a].key + '.pdf'},{'attr':'target','val':'_blank'}]);
						let img1 = engine.getDOMElement('img',[{'attr':'src','val':'/static/images/open.png'}, {'attr':'title','val':'Open plan in browser'}]);
						a1.appendChild(img1);
						let a2 = engine.getDOMElement('a',[{'attr':'href', 'val' : '/api/getstoredplan?action=download&getlocal=' + engine.planData.entries[a].key + '.pdf'},{'attr':'target','val':'_blank'}]);
						let img2 = engine.getDOMElement('img',[{'attr':'src','val':'/static/images/download.png'}, {'attr':'title','val':'Save plan to file'}]);
						let s3 = engine.getDOMElement('span',[{'attr':'class', 'val' : 'link'},{'attr':'data-action','val':'reset'}]);
						let img3 = engine.getDOMElement('img',[{'attr':'src','val':'/static/images/reset.png'}, {'attr':'title','val':'Remove downloaded file'}]);
						a1.appendChild(img1);
						a2.appendChild(img2);
						s3.appendChild(img3);
						isDownloadedMsg.appendChild(a1);
						isDownloadedMsg.appendChild(a2);
						isDownloadedMsg.appendChild(s3);
					}
	            	
	            	_out += '<tr data-plan-item="' + engine.planData.entries[a].key + '"><td>' 
	            		+ engine.planData.entries[a].SetNumber+'</td><td class="plan-handler" data-plan-field="Description"><span>' 
	            		+ _desc + '</span></td><td class="plan-handler" data-plan-field="Notes"><span>' + _notes
	            		+ '</span></td><td class="download_checkbox"><span class="plan_add"><input type="checkbox" value="' 
	            		+ engine.planData.entries[a].key + '" ' + _downloadFlagIsChecked + '></span></td>'
	            		+ '<td>'+_isDownloadedMsg +'</td>'
	            		//+ '<td>' + isDownloadedMsg.innerHTML +'</td>'	//NOT outerHTML - because I don't want the wrapper...
	            		+ '</tr>';
	            	//or...
	            	let output_row = engine.getDOMElement('tr',[{'attr':'data-plan-item','val':'engine.planData.entries[a].key'}]);
	            	let td_setnum = engine.getDOMElement('td',[]);
	            	td_setnum.appendChild(document.createTextNode(engine.planData.entries[a].SetNumber));
	            	span_desc = engine.getDOMElement('span',[]);
	            	span_desc.appendChild(document.createTextNode(_desc));
	            	
            	}
            }
            _out += '</table>';
            $('#plans_list').html(_out);
//            $('#plans_listing').dataTable({
//            	  "pageLength": 50
//            });
            
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
            		//engine.resetDownload($(this).parent().parent().attr('data-plan-item'));
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
		let _wrapper = this.getDOMElement('ul',[]);
		let _pagination_info = this.getDOMElement('li',[{'attr':'class','val':'paginator_info'}]).appendChild(document.createTextNode('p ' + data.curr_page + ' of ' + total_pages + ' (of '+ data.total +' records)'));
		
		//get prev or next page numbers
		let prevpagemany = data.curr_page > 0 ? data.curr_page - 15 : 0;
		let prevpageone = data.curr_page > 0 ? data.curr_page-1 : 0;
		let nextpageone = data.curr_page <= total_pages ? data.curr_page+1 :  total_pages; 
		let nextpagemany = data.curr_page <= total_pages ? data.curr_page + 15 :  total_pages;
		
		let _back_one = this.getPaginationLink(data,prevpageone,'<',this.paginationHandler);
		let _back_many = this.getPaginationLink(data,prevpagemany,'<<',this.paginationHandler);
		let _fwd_one = this.getPaginationLink(data,nextpageone,'>',this.paginationHandler);
		let _fwd_many = this.getPaginationLink(data, nextpagemany, '>>', this.paginationHandler);
		
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
		_li.setAttribute('data-page_length',this.page_length);	//TODO: Set this programmatically
		_li.setAttribute('data-filter',data.filter_key);
		_li.appendChild(document.createTextNode(link_text));
		if(target_page > 0 && target_page <= total_pages){
			_li.setAttribute('class','paginator');
			_li.addEventListener('click',handler);
		}
		return(_li);
	},
	
	paginationHandler : function(){
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
    },
    
    /** function to generate DOM elements */
    getDOMElement :function(elemTypeString,attrsArray){
		let elem = document.createElement(elemTypeString);
		for(let a=0;a<attrsArray.length;a++){
			elem.setAttribute(attrsArray[a].attr,attrsArray[a].val);
		}
		return(elem);
	}
};

engine.init(document.getElementsByTagName('body')[0].getAttribute('data-page'));

//ajax start/stop for progress icon
$(document).bind('ajaxStart', function(){
//    $("#ajax-loading").dialog({
//        'modal':true
//    });
}).bind('ajaxStop', function(){
//    $("#ajax-loading").dialog('close');
});
