"""
-*- coding: utf-8 -*-
========================
Python YouTube API
========================
Forked from: Chirag Rathod (Srce Cde)
Email: chiragr83@gmail.com
========================
Updated by: Fergus Boyd
Email: fergus.p.boyd@gmail.com

Returns a pandas DataFrame of youtube comments and replies, used for my data science pipelines.
"""

import json
import pandas as pd
from urllib.parse import urlparse, urlencode, parse_qs
from urllib.request import urlopen

class YouTubeApi():

    def __init__(self, api_key):
        self.key = api_key
        self.comment_url = 'https://www.googleapis.com/youtube/v3/commentThreads'
        self.replies_url = 'https://www.googleapis.com/youtube/v3/comments'

    def load_comments(self, mat):
        colNames = ['commentID', 'parentID', 'author', 'time', 'comment', 'likes', 'noReplies']
        df = pd.DataFrame(columns=colNames)
        for item in mat["items"]:
            comment = item["snippet"]["topLevelComment"]
            cmID = comment['id']
            paID = None
            autr = comment["snippet"]["authorDisplayName"]
            text = comment["snippet"]["textDisplay"]
            time = comment["snippet"]["publishedAt"]
            like = comment["snippet"]["likeCount"]
            rply = item["snippet"]["totalReplyCount"]

            comment_df = pd.DataFrame([[cmID, paID, autr, time, text, like, rply], ], columns=colNames)
            df = df.append(comment_df, ignore_index=True)

            if rply > 0:
                reply_df = self.get_comment_replies(parent_id=cmID)
                df = df.append(reply_df, ignore_index=True)

        return df

    def get_video_comment(self, vid, max_return=100):
        parms = {
                    'part': 'snippet,replies',
                    'maxResults': max_return,
                    'videoId': vid,
                    'textFormat': 'plainText',
                    'key': self.key
                }

        try:
            matches = self.openURL(self.comment_url, parms)
            i = 2
            mat = json.loads(matches)
            nextPageToken = mat.get("nextPageToken")
            all_comments = self.load_comments(mat)

            while nextPageToken:
                parms.update({'pageToken': nextPageToken})
                matches = self.openURL(self.comment_url, parms)
                mat = json.loads(matches)
                nextPageToken = mat.get("nextPageToken")

                new_comments = self.load_comments(mat)
                all_comments = all_comments.append(new_comments, ignore_index=True)

            return all_comments
        except KeyboardInterrupt:
            print("User Aborted the Operation")

        except:
            print("Cannot open URL or fetch comments at the moment")

    def get_comment_replies(self, parent_id, max_return=100):
        parms = {
                    'part': 'snippet',
                    'maxResults': max_return,
                    'parentId': parent_id,
                    'textFormat': 'plainText',
                    'key': self.key
                }

        try:
            matches = self.openURL(self.replies_url, parms)
            i = 2
            mat = json.loads(matches)
            nextPageToken = mat.get("nextPageToken")
            all_replies = self.load_replies(mat)

            while nextPageToken:
                parms.update({'pageToken': nextPageToken})
                matches = self.openURL(self.replies_url, parms)
                mat = json.loads(matches)
                nextPageToken = mat.get("nextPageToken")

                new_replies = self.load_replies(mat)
                all_replies = all_replies.append(new_replies, ignore_index=True)

            return all_replies
        except KeyboardInterrupt:
            print("User Aborted the Operation")

        except:
            print("Cannot fetch replies at the moment")

    def load_replies(self, mat):
        colNames = ['commentID', 'parentID', 'author', 'time', 'comment', 'likes', 'noReplies']
        df = pd.DataFrame(columns=colNames)
        for item in mat["items"]:
            cmID = item['id']
            paID = item["snippet"]["parentId"]
            autr = item["snippet"]["authorDisplayName"]
            text = item["snippet"]["textDisplay"]
            time = item["snippet"]["publishedAt"]
            like = item["snippet"]["likeCount"]
            rply = None

            reply_df = pd.DataFrame([[cmID, paID, autr, time, text, like, rply], ], columns=colNames)
            df = df.append(reply_df, ignore_index=True)

        return df


    def openURL(self, url, parms):
            f = urlopen(url + '?' + urlencode(parms))
            data = f.read()
            f.close()
            matches = data.decode("utf-8")
            return matches
