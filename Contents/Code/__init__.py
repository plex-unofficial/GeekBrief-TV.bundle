# -*- coding: utf-8 -*-
#
# Author: Witto
#
# [2009-06-24] Version 0.2 - Adding episode thumbs
# [2009-06-23] Version 0.1 - Initial release
#
# This Plug-In for the GeekBrief.TV: Shiny, Happy Tech News
# All rights stay with GeekBrief.TV
# This plug-in just lists the latest briefs from their site: http://www.geekbrief.tv/
#
# Code base in the COMPIZmediacenter Plugin, using the following tutorial:
# http://forums.plexapp.com/index.php?showtopic=5547
#
# We use FRAMEWORK #1 because I think it must be better than #0 :)
#

from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

import re

PLUGIN_PREFIX   = "/video/GeekBrief.TV"
ROOT_URL        = "http://www.geekbrief.tv/"
FEED_URL        = 'http://www.podshow.com/feeds/hd.xml'
GB_HOST		= "www.geekbrief.tv"

CACHE_INTERVAL  = 3600

MainArt         = "%s/:/resources/%s" % (PLUGIN_PREFIX, "background-art.jpg")
MainThumb       = "%s/:/resources/%s" % (PLUGIN_PREFIX, "thumb-art.jpg")

Log('(PLUG-IN) Finished importing libraries & setting global variables')

####################################################################################################
def Start():

        # Add the MainMenu prefix handler
        Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, L('GeekBrief.TV'), 'thumb-art.jpg', 'background-art.jpg')

        # Set up view groups
        Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
        Plugin.AddViewGroup("Info", viewMode="InfoList", mediaType="items")

        # Set the default cache time
        HTTP.SetCacheTime(14400)

        # Set the default MediaContainer attributes
        MediaContainer.title1 = 'GeekBrief.TV'
        MediaContainer.content = 'InfoList'
        MediaContainer.art = MainArt
	MediaContainer.thumb = MainThumb
	VideoItem.thumb = MainThumb

        Log('(PLUG-IN) Finished initiallizing the plug-in')

####################################################################################################


def MainMenu(sender = None, Hallo = None):

        global MainArt
        global MainThumb

        Log('(PLUG-IN) **==> ENTER Main Menu')
        if MainThumb == None:
                MainArt         = "%s/:/resources/%s" % (PLUGIN_PREFIX, "background-art.jpg")
                MainThumb       = "%s/:/resources/%s" % (PLUGIN_PREFIX, "thumb-art.jpg")

        dir = MediaContainer(art = MainArt, title1="GeekBrief.TV", viewGroup="InfoList")

	page = XML.ElementFromURL(FEED_URL, False)
    	episodes = page.xpath("//channel/item")

	for episode in episodes:

		episodeFullTitle = episode.xpath("./title/text()")[0]
		search = re.search(r'^([^|]+)\|?(.*)$', episodeFullTitle)
		episodeTitle = search.group(1).replace('(medium)', '')
                Log(episodeTitle)
		episodeDescription = search.group(2).replace(",", "\n- ")
		try:
	                episodeNumber = (int)(re.search(r'#\s*(\d+)', episodeTitle).group(1))
			episodeThumbPath = "/wp-content/images/thumbnails/gbtv.%04d.png" % episodeNumber
			episodeThumb = "http://%s%s" % (GB_HOST, episodeThumbPath)
		except:
			episodeThumb = None

		if(episodeDescription):
			episodeDescription = '- ' + episodeDescription
		else:
			# Get the long description
			episodeDescription = tidyString(episode.xpath("./description/text()")[0])

		# Strip out just the tags
		episodeDescription = strip_tags(episodeDescription)

		episodeFlv = episode.xpath("./enclosure")[0].get('url')
		episodeLength = (int)((int)(episode.xpath("./enclosure")[0].get('length')) / 181.37)

		dir.Append(VideoItem(episodeFlv, episodeTitle, summary=episodeDescription,  duration=episodeLength, thumb=episodeThumb))

	Log('(PLUG-IN) <==** EXIT Main Menu')
	return dir

####################################################################################################

# FRAMEWORK ADDITIONS:

def tidyString(stringToTidy):
  # Function to tidy up strings works ok with unicode, 'strip' seems to have issues in some cases so we use a regex
  if stringToTidy:
    # Strip new lines
    #stringToTidy = re.sub(r'\n', r' ', stringToTidy)
    # Strip leading / trailing spaces
    stringSearch = re.search(r'^\s*(\S.*?\S?)\s*$', stringToTidy)
    if stringSearch == None:
      return ''
    else:
      return stringSearch.group(1)
  else:
    return ''


def strip_tags(value):
    "Return the given HTML with all tags stripped."
    return re.sub(r'<[^>]*?>', '', value).replace("&quot;", '"').replace("&amp;", "&")

