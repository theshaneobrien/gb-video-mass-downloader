# Giant Bomb Video Mass Downloader

## What it does:

Starts from the earliest videos and goes through and downloads them one by one.

## How to run:

Requires "Requests" to be installed with: **pip3 install requests**

Fill in "apiKey" with your Giant Bomb Developer API Key: https://www.giantbomb.com/api/

You can add more filters to the "filters" var, default set to only grab premium videos

See documentation here for filters: https://www.giantbomb.com/api/documentation/#toc-0-48

In command line:

**python3 getVideos.py**


Happy to take pull requests =D


## Known issue:

Some videos on Giant Bomb return a "403 Forbidden" error, I haven't added any error checking to catch this.

The app will close when this is encountered.

To fix it you can download the offending video off the website (it seems the API has the wrong video url stored?)

You must then open archiveProgress.json in your favorite text editor and add 1 to the value of "currentOffset" and start the program again... easy, right?
