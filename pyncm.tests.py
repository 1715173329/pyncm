import unittest, logging, json
import pyncm
from pyncm.apis import *


logging.basicConfig(level="INFO")

session_str = "PYNCM..."

session = pyncm.LoadSessionFromString(session_str)

album_id = 28516
artist_id = 9272
song_id = 286970
playlist_id = 2804505435
user_id = 14179251276
mv_id = 38020


def res_logging(res, api_name):
    logging.info((api_name, res.get("code", None), type(res), len(res), res.keys(), len(json.dumps(res))))


class APITest(unittest.TestCase):
    def setup():
        print("setup")

    def test_album_GetAlbumInfo(self):
        res = album.GetAlbumInfo(album_id, session=session)
        res_logging(res, "GetAlbumInfo")
    
    def test_album_GetAlbumComments(self):
        res = album.GetAlbumComments(album_id, session=session)
        res_logging(res, "GetAlbumComments")

    def test_artist_GetArtistAlbums(self):
        res = artist.GetArtistAlbums(artist_id, session=session)
        res_logging(res, "GetArtistAlbums")

    def test_artist_GetArtistTracks(self):
        res = artist.GetArtistTracks(artist_id, session=session)
        res_logging(res, "GetArtistTracks")

    def test_artist_GetArtistTracks(self):
        res = artist.GetArtistTracks(artist_id, session=session)
        res_logging(res, "GetArtistTracks")

    def test_artist_GetArtistDetails(self):
        res = artist.GetArtistDetails(artist_id, session=session)
        res_logging(res, "GetArtistDetails")

    def test_cloud_GetCloudDriveInfo(self):
        res = cloud.GetCloudDriveInfo(50, 0, session=session)
        res_logging(res, "GetCloudDriveInfo")

    def test_cloud_GetCloudDriveItemInfo(self):
        res = cloud.GetCloudDriveItemInfo([293931], session=session)
        res_logging(res, "GetCloudDriveItemInfo")

    def test_cloud_upload(self):
        # TODO
        pass

    def test_cloud_SetRectifySongId(self):
        # TODO
        # 此 API 已测试通过。
        pass

    def test_cloudsearch(self):
        res = cloudsearch.GetSearchResult("愚人的国度", cloudsearch.SONG, session=session)
        res_logging(res, "GetSearchResult")

    def test_login(self):
        # TODO
        # 除 Cookies 登录外，其它登录方式已测试通过。
        # login 模块登录外功能未测试。
        pass

    def test_playlist_GetPlaylistInfo(self):
        res = playlist.GetPlaylistInfo(playlist_id, session=session)
        res_logging(res, "GetPlaylistInfo")

    def test_playlist_GetPlaylistAllTracks(self):
        res = playlist.GetPlaylistAllTracks(playlist_id, session=session)
        res_logging(res, "GetPlaylistAllTracks")

    def test_playlist_GetPlaylistComments(self):
        res = playlist.GetPlaylistComments(playlist_id, session=session)
        res_logging(res, "GetPlaylistComments")

    def test_playlist_SetManipulatePlaylistTracks(self):
        res = playlist.SetManipulatePlaylistTracks([2120125578], 406884341, "add", session=session)
        res_logging(res, "SetManipulatePlaylistTracks.add")
        res = playlist.SetManipulatePlaylistTracks([2120125578], 406884341, "del", session=session)
        res_logging(res, "SetManipulatePlaylistTracks.del")

    def test_playlist_create_and_remove(self):
        res = playlist.SetCreatePlaylist("PYNCM", session=session)
        res_logging(res, "SetPlaylist.create")
        id = res["id"]
        res = playlist.SetRemovePlaylist([id], session=session)
        res_logging(res, "SetPlaylist.remove")

    def test_track_GetTrackDetail(self):
        res = track.GetTrackDetail(song_id, session=session)
        res_logging(res, "GetTrackDetail")

    def test_track_GetTrackAudio(self):
        res = track.GetTrackAudio(song_id, session=session)
        res_logging(res, "GetTrackAudio")

    def test_track_GetTrackAudioV1(self):
        res = track.GetTrackAudioV1(song_id, session=session)
        res_logging(res, "GetTrackAudioV1")

    def test_track_GetTrackDownloadURL(self):
        # 已弃用
        pass

    def test_track_GetTrackDownloadURLV1(self):
        res = track.GetTrackDownloadURLV1(song_id, session=session)
        res_logging(res, "GetTrackDownloadURLV1")

    def test_track_GetTrackLyrics(self):
        res = track.GetTrackLyrics(song_id, session=session)
        res_logging(res, "GetTrackLyrics")

    def test_track_GetTrackLyricsV1(self):
        res = track.GetTrackLyricsV1(song_id, session=session)
        res_logging(res, "GetTrackLyricsNew")

    def test_track_GetTrackComments(self):
        res = track.GetTrackComments(song_id, session=session)
        res_logging(res, "GetTrackComments")

    def test_track_SetLikeTrack(self):
        res = track.SetLikeTrack(2706275303, True, session=session)
        res_logging(res, "SetLikeTrack.add")
        res = track.SetLikeTrack(2706275303, False, session=session)
        res_logging(res, "SetLikeTrack.del")

    def test_track_GetMatchTrackByFP(self):
        # TODO
        pass

    def test_user_GetUserDetail(self):
        res = user.GetUserDetail(user_id, session=session)
        res_logging(res, "GetUserDetail")

    def test_user_GetUserPlaylists(self):
        res = user.GetUserPlaylists(user_id, session=session)
        res_logging(res, "GetUserPlaylists")

    def test_user_GetUserAlbumSubs(self):
        res = user.GetUserAlbumSubs(session=session)
        res_logging(res, "GetUserAlbumSubs")

    def test_user_GetUserArtistSubs(self):
        res = user.GetUserArtistSubs(session=session)
        res_logging(res, "GetUserArtistSubs")

    def test_user_SetSignin(self):
        res = user.SetSignin(session=session)
        res_logging(res, "SetSignin")

    def test_user_SetWeblog(self):
        logs = [
            {
                "action": "play",
                "json": {
                    "download": 0,
                    "end": "interrupt",
                    "id": song_id,
                    "sourceId": album_id,
                    "time": 60,
                    "type": "song",
                    "wifi": 0,
                    "source": "list",
                },
            }
        ]
        res = user.SetWeblog(logs, session=session)
        res_logging(res, "SetWeblog")

    def test_video_GetMVDetail(self):
        res = video.GetMVDetail(mv_id, session=session)
        res_logging(res, "GetMVDetail")

    def test_video_GetMVResource(self):
        res = video.GetMVResource(mv_id, session=session)
        res_logging(res, "GetMVResource")

    def test_video_GetMVComments(self):
        res = video.GetMVComments(mv_id, session=session)
        res_logging(res, "GetMVComments")


if __name__ == "__main__":
    unittest.main()
