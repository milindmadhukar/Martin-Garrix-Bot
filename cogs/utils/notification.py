def latestYtVid(latest_vid, new_vid):
    current = new_vid.execute()
    if latest_vid == None:
        return current
    else:
        if latest_vid['items'][0]['snippet']['resourceId']['videoId'] == current['items'][0]['snippet']['resourceId']['videoId']:
            return latest_vid
        else:
            return current