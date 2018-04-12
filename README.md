# lego-downloader
Python web application for Lego plans downloading. Comprised of a user inteface running under cherrypy and a fetcher running from a looping shell file driving a command-line python script.

The UI provides the option to build a local cache of all plans listed at https://brickset.com/exportscripts/instructions.

The UI also allows browsing of this cached view. The cached view offers options for flagging of selected plans for download. The flagged plans are downloaded and stored in MongoDB GridFS by the separate fetcher process (legoFileStore.py and fetch.sh).

The UI further allows display and local download of the plans already stored in MongoDB. I didn't want to link directly to the plans on lego.com, again for HTTP traffic reduction purposes (and my broadband is pretty poor).

## Planned updates:
 - Make it a bit prettier...
 - Ability to add unlisted/self scanned plans
 - Ability to update the notes/descriptions against each plan
 - Ability to delete a previously downloadwed plan

## WTF did I do this?
Because I wanted to digitize all the Lego plans I have (a lot...) and finding them on lego.com is a right pain in the bum...
