# lego-downloader
Python web application for Lego plans downloading. Comprised of a user inteface running under cherrypy and a fetcher running from a looping shell file driving a command-line python script.

The UI allows browsing of all plans listed at https://brickset.com/exportscripts/instructions and flagging of selected plans for download. The flagged plans are downloaded and stored in MongoDB GridFS.

The UI also allows display and local download of the plans already stored in MongoDB.

## Planned updates:
 - Ability to add unlisted/self scanned plans
 - Ability to update the notes/descriptions against each plan
 - Ability to delete a previously downloadwed plan

## WTF did I do this?
Because I wanted to digitize all the Lego plans I have (a lot...) and finding them on lego.com is a right pain in the bum...
