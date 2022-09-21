import sys
import requests
import subprocess
import textwrap
from datetime import datetime

# Runs svnlook as a process and returns the output
def svnlook(request: str):
	process = subprocess.Popen(
		[svnlook_path, request, repo_path, "-r", revision_id], stdout=subprocess.PIPE)
	result = process.communicate()[0]
	result = result.strip().decode()
	return result

# Takes the raw output of "svnlook changed" and filters it into a dictionary containing
# an array of added, modified, and deleted files
def make_changelist_dict(raw: bytes):
	# Tidy up the text
	text = raw.strip().decode()

	# Make our temp data structure
	changes = {
		"added": [],
		"modified": [],
		"deleted": []
	}

	# Iterate over each line
	lines = text.splitlines()
	for line in lines:
		# Each line will have a prefix indicating the type of change, then some spaces, then the filepath
		# E.g. U trunk/Content/somefile.uasset
		# We only want to split at this first gap, not any spaces in the filepath
		change_type, change = line.split(maxsplit=1)

		# Catch directories being included in the changelist - we (probably) don't care about these
		if change.endswith(["/", "\\"]):
			break

		# Python 3.10 has a proper match / case statement (better late than never, eh) which is the better way to do this
		if change_type == "A":  # Added
			changes["added"].append(change)
		elif change_type == "U":  # Updated
			changes["modified"].append(change)
		elif change_type == "D":  # Deleted
			changes["deleted"].append(change)

	return changes

# Using the output of make_changelist_dict, returns a summary of changes.
# Not used in the script at the moment
def make_changelist_output(changelist: dict, limit: int = 6):
	# Create the output text
	output = ""

	for key, value in changelist.items():
		# Why can't Python act like a fucking normal language and have something like list.count return an integer?
		change_count = len(value)

		if change_count == 0:
			break
		else:
			output = output + CHANGELIST_DISPLAY[key]

			iter_count = min(limit, change_count)
			for i in range(iter_count):
				output = output + "\n" + value[i]

			if change_count > limit:
				output = output + "\n" + \
					f"*(Showing {limit} of {change_count} changes)*"

			output = output + "\n\n"

	return output

# Sends the payload to Discord
def yeet(payload: dict):
	message = requests.post(webhook_url, json=payload)
	try:
		message.raise_for_status()
	except requests.exceptions.HTTPError as whoops:
		print(f"💩 - {whoops}")
	else:
		print(f"💦 - Webhook delivered successfully! Code {message.status_code}")


# Specify character limits
MAX_USER = 30
MAX_LOG = 256

# Add a bit of flair ✨
COLOUR_SUMMARY = 15277667  # Discord LUMINOUS_VIVID_PINK
CHANGELIST_DISPLAY = {
	"added": "**Added**",
	"modified": "**Modified**",
	"deleted": "**Deleted**"
}

# Read the command line arguments from SVN
svnlook_path = sys.argv[1]
webhook_url = sys.argv[2]
repo_path = sys.argv[3]
revision_id = sys.argv[4]

# Get the author data
user = svnlook("author")
user = textwrap.shorten(user, width=MAX_USER, placeholder="...")

# Get the log (commit message)
log = svnlook("log")
if log.isspace():
	log = "No commit message provided 😢"
else:
	log = textwrap.shorten(log, width=MAX_LOG, placeholder="...")

# Get the changelist as a dict
# Protip: for full text output, pass this dict into make_changelist_output, it can be a bit much for the Discord embed width though
changelist_raw = svnlook("changed")
changelist_dict = make_changelist_dict(changelist_raw)

# Format the revision text. Nice.
revision_text = f"#{revision_id} (nice)" if revision_id.endswith("69") else f"#{revision_id}"

# Put it all together
payload = {
	"embeds": [
		{
			"title": f"🎉 Hooray! A new commit from {user} - Revision {revision_text}",
			"color": COLOUR_SUMMARY,
			"description": log,
			"fields": [
				{
					"name": "Added",
					"value": str(len(changelist_dict["added"])) + " file(s)",
					"inline": True
				},
				{
					"name": "Modified",
					"value": str(len(changelist_dict["modified"])) + " file(s)",
					"inline": True
				},
				{
					"name": "Deleted",
					"value": str(len(changelist_dict["deleted"])) + " file(s)",
					"inline": True
				}
			],
			"timestamp": datetime.now().isoformat()
		}
	]
}

# Yeet that shit to Discord
yeet(payload)
