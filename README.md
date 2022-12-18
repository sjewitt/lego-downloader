# LEGO Plans Downloader:
Python web application for Lego plans downloading. Comprised of a user inteface running under cherrypy and a fetcher running from a looping shell file driving a command-line python script.

The UI provides the option to build a local cache of all plan links listed at https://brickset.com/exportscripts/instructions. This is the 'Load plans from source' link.

![Start screen](https://github.com/sjewitt/lego-downloader/blob/master/static/lego-1.png)

*LEGO Plans downloader - Start screen*


The UI also allows browsing of this cached view via the 'List plans' link. 

The following screen allows you to list plans already stored locally, list plans not stored locally, those you have flagged to download the PDF but have not yet completed, or all download links, regardless of PDF download status.

![List download links options](https://github.com/sjewitt/lego-downloader/blob/master/static/lego-2.png)

*LEGO Plans downloader - Plan link listing options*


The cached view of the 'Not stored' plans offers options for flagging of selected plans for download. The flagged plans are downloaded and stored in MongoDB GridFS by the separate fetcher process (legoFileStore.py and fetch.sh).

![Flag for download](https://github.com/sjewitt/lego-downloader/blob/master/static/lego-4.png)

*LEGO Plans downloader - Flag for download*


The cached view of the 'Stored' plans offers options for downloading, opening or resetting (to re-download) the plans retrieved and  already stored in MongoDB. 

![See or download locally stored plans](https://github.com/sjewitt/lego-downloader/blob/master/static/lego-3.png)

*LEGO Plans downloader - Open or download locally stored plans*


I didn't want to link directly to the plans on lego.com for HTTP traffic reduction purposes (and my broadband is pretty poor).

## Planned updates:
 - Make it a bit prettier...
 - Ability to add unlisted/self scanned plans
 - Ability to update the notes/descriptions against each plan			DONE
 - Ability to delete a previously downloaded plan						DONE (defacto - it's the reset button)
 - add UI alert if mongo is unavailable!
 - pass params/rewrite the URL to allow an f5 reload (otherwise it reverts to the default not storedf list)
 - in-place field editor needs to compare existing with incoming for non-equality, only save and set edited=True if not matching	DONE
 - dupe: 71286_X_K 2 - OK			DONE - a bug, no URL against this record
 - change words to icons on fetched display			DONE
 - on re-fetch, indicate NEW entries, and maybe discontinued entries - I want to KEEP older entries...
 - implement the page jump-to
 - implement a search on Notes and Description fields
 - indicate that these fields are in fact editable on hover
 - add config option for mongo location, data source etc.

 
 
## WTF did I do this?
Because I wanted to digitize all the Lego plans I have (a lot...) and finding them on lego.com is a right pain in the bum...
