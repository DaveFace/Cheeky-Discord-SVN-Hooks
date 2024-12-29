# Cheeky Discord SVN Hooks

These hook scripts can be used to send a Webhook to Discord when someone makes a change to a Subversion repository. With a few modifications you could make it work for other SVN hooks, too.

There are two versions: one is a simple bash script, another is a Python script. Both do the job, but the Python script grabs a few extra details. It looks a little something like this:

<p align="center">
  <img src="https://github.com/DaveFace/Cheeky-Discord-SVN-Hooks/blob/main/Preview.png"/>
</p>

*FYI: The webhook username / icon is set in your Discord server, not the script.*

## Installing

- This has only been tested on a Linux server (Ubuntu, specifically) running vanilla Apache Subversion
- The Python script has been tested on Python 3.8 and 3.10

### 1 - Set up the Discord Bot

1. On the Discord channel you want to post updates to, go to **Edit Channel > Integrations > Webhooks**, and then click **New Webhook**
2. Set the Icon and Name to whatever you want - the script doesn't interfere with these
3. Click **Copy Webhook URL**

### 2 - Configure the Script

Open the `post-commit` file in an editor (Notepad will do if you have no shame) - this is the file without a `.py` extension. It's a Bash script that Subversion will call on certain events, called hooks, when placed inside your repository's hooks directory.

1. Change `WEBHOOK=` to your Discord Webhook URL
2. Change `REPO=` to your server's repository path, e.g. `/mnt/svn/your-repo-name`, do not use the `/home/svn/your-repo-name` path

### 3 - Install it

1. Copy the scripts from either the `Bash` or `Python` directory into `/mnt/svn/your-repo-name/hooks`
2. Use the terminal to navigate to `/mnt/svn/your-repo-name/hooks` and run the following commands:
   1. `sudo chmod a+x post-commit`
   2. `sudo chmod a+x post-commit.py` (if using the python script)
3. If you're using the Python script, make sure the requests package is installed (`pip install requests`)
4. Test the script with the command `./post-commit "blah" 69`, or some other revision number you know exists

## Troubleshooting

If either script doesn't run, it's probably one of these issues:

- Insufficent permissions on the script, try the following commands:
  - `chown www-data:www-data post-commit`
  - `chown www-data:www-data post-commit.py`
- A path is set incorrectly
  - The PYTHON and SVNLOOK paths should be broadly applicable, but double check that these are correct
  - The repository path should be the server location, not the user location (i.e. it should not be /home/svn/your-repo) - [otherwise you'll encounter this issue](https://github.com/svn-all-fast-export/svn2git/issues/133)
  - Double check the Webhook URL, then check it again
