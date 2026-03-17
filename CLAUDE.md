# CLAUDE.md - PyNCM 项目指南

## 项目简介

PyNCM (`pyncm`) 是第三方网易云音乐 Python API 封装及 CLI 下载工具。版本 1.8.1，长期支持状态。

仓库：`mos9527/pyncm`

## 项目结构

```
pyncm/
  __init__.py          # Session 类、Session 序列化、WriteLoginInfo
  __main__.py          # CLI 下载工具（argparse、ThreadPoolExecutor 多线程下载）
  apis/
    __init__.py        # 加密修饰器：@WeapiCryptoRequest、@EapiCryptoRequest
    track.py           # 歌曲音频、详情、歌词、评论、收藏、听歌识曲
    login.py           # 所有登录方式（手机、邮箱、Cookie、二维码、匿名）
    playlist.py        # 歌单增删改查、评论、歌曲操作
    album.py           # 专辑信息及评论
    artist.py          # 艺术家专辑、歌曲、详情
    cloud.py           # 个人云盘上传流程
    cloudsearch.py     # 搜索 API 及类型常量
    user.py            # 用户资料、歌单、收藏、签到、足迹
    video.py           # MV 详情、资源 URL、评论
    exception.py       # LoginRequiredException、LoginFailedException
  utils/
    __init__.py        # RandomString、HexDigest、HexCompose、HashDigest、HashHexDigest、
                       #   GenerateSDeviceId、GenerateChainId、GenerateWNMCID
    crypto.py          # WeapiEncrypt、EapiEncrypt/Decrypt、LinuxApiEncrypt、AbroadDecrypt
                       #   AES-CBC/ECB、RSA（教科书式，无填充）、PKCS7 填充
    aes.py             # 纯 Python AES 实现（MODE_CBC、MODE_ECB）
    security.py        # Abroad 消息解密（SBOX）、cloudmusic_dll_encode_id
    helper.py          # TrackHelper、AlbumHelper、ArtistHelper、UserHelper、FuzzyPathHelper、
                       #   IDCahceHelper（线程安全的缓存基类）
    lrcparser.py       # LrcParser - 解析/创建/导出 LRC 歌词，二分查找 Find()
    yrcparser.py       # YrcParser - 逐词歌词解析，ASSWriter 导出 .ass 字幕
    constant.py        # 256 个已知可用的 deviceId（用于匿名登录）
demos/                 # 示例脚本（二维码登录、手机登录、云盘上传、歌单同步等）
tools/                 # 开发工具（b64deobfuscate.py、eapidumper.py）
```

## 架构与核心概念

### Session 模型

所有 API 调用均需显式传入 `session: Session` 关键字参数。`Session` 继承自 `requests.Session`：

```python
from pyncm import Session
session = Session()
# 配置示例：
session.force_http = True                      # 优先使用 HTTP
session.headers['X-Real-IP'] = '118.88.88.88'    # 海外用户修复 460 "Cheating" 问题
session.deviceId = 'custom_id'                 # 更改 EAPI 设备 ID
```

登录后可用属性：`session.logged_in`、`session.is_anonymous`、`session.uid`、`session.nickname`、`session.vipType`、`session.lastIP`。

Session 序列化：
```python
from pyncm import DumpSessionAsString, LoadSessionFromString
dump = DumpSessionAsString(session)   # -> "PYNCM..."（zlib + base64）
session = LoadSessionFromString(dump)
```

内部保存的状态：`eapi_config`、`weapi_config`、`login_info`、`csrf_token`、`cookies`。

### API 加密修饰器

`apis/__init__.py` 中定义了两种加密修饰器，所有 API 函数均由其包装：

- **`@WeapiCryptoRequest`** — 网页端/小程序 API。使用 AES-CBC（两轮加密）+ RSA 生成 `encSecKey`。路由：`/weapi/...`
- **`@EapiCryptoRequest`** — 新版客户端 API。使用 AES-ECB + MD5 摘要盐值。路由：`/eapi/...`

被修饰的 API 函数返回 `(url, payload_dict)` 或 `(url, payload_dict, method)`。修饰器负责加密、发送请求、解密响应、JSON 解析。同时自动处理 `abroad: true` 的海外响应。

### 登录方式（login.py）

大部分 API（尤其 `GetTrackAudio`）**必须先登录**才能使用。可用方式：

| 函数 | 说明 |
|---|---|
| `LoginViaAnonymousAccount(deviceId=None)` | 最简单。内部使用 WeapiCryptoRequest。deviceId 从 `constant.py` 随机选取 |
| `LoginViaCellphone(phone, password/passwordHash/captcha, ctcode=86)` | 手机号登录。优先级：captcha > password > passwordHash |
| `LoginViaEmail(email, password/passwordHash)` | 邮箱登录 |
| `LoginViaCookie(MUSIC_U="...")` | 直接注入 Cookie |
| `LoginQrcodeUnikey()` + `LoginQrcodeCheck(unikey)` | 二维码登录流程。用 `GetLoginQRCodeUrl(unikey)` 获取可扫描链接 |

辅助函数：`LoginLogout()`、`LoginRefreshToken()`、`GetCurrentLoginStatus()`、`SetSendRegisterVerifcationCodeViaCellphone()`、`CheckIsCellphoneRegistered()`、`SetRegisterAccountViaCellphone()`。

## API 参考

### track.py — 歌曲

| 函数 | 加密 | 说明 |
|---|---|---|
| `GetTrackDetail(song_ids)` | Weapi | 获取歌曲详情。ids <= 1000。接受 list/str/int |
| `GetTrackAudio(song_ids, bitrate=320000, encodeType="aac")` | Eapi | 获取音频 URL。**需要登录** |
| `GetTrackAudioV1(song_ids, level="standard", encodeType="flac")` | Eapi | V1 音频接口。level: standard/exhigh/lossless/hires/jyeffect/sky/jymaster |
| `GetTrackDownloadURL(song_ids, ...)` | Eapi | **已弃用** — 抛出 NotImplementedError |
| `GetTrackDownloadURLV1(song_ids, level="standard")` | Eapi | 下载 API（有额度限制） |
| `GetTrackLyrics(song_id, lv=-1, tv=-1, rv=-1)` | Weapi | 获取歌词（原文/翻译/罗马音）。-1 = 最新版本 |
| `GetTrackLyricsV1(song_id)` | Eapi | V1 歌词接口，支持 yrc（逐词滚动歌词） |
| `GetTrackComments(song_id, offset=0, limit=20, beforeTime=0)` | Weapi | 获取歌曲评论。beforeTime 单位为秒 |
| `SetLikeTrack(song_id, like=True, userid=0)` | Eapi | 收藏/取消收藏歌曲到「我喜欢的音乐」 |
| `GetMatchTrackByFP(audioFP, duration, sessionId)` | Weapi | 听歌识曲（Shazam v2 算法） |

### playlist.py — 歌单

| 函数 | 加密 | 说明 |
|---|---|---|
| `GetPlaylistInfo(playlist_id, offset=0, limit=1000)` | Weapi | 获取歌单内容。注意：`tracks` 可能不完整，`trackIds` 始终完整 |
| `GetPlaylistAllTracks(playlist_id, offset=0, limit=1000)` | — | 便捷函数：先取 trackIds 再调用 GetTrackDetail |
| `GetPlaylistComments(playlist_id, pageNo=1, pageSize=20, cursor=-1)` | Weapi | 获取歌单评论 |
| `SetManipulatePlaylistTracks(playlist_ids, playlistId, op="add")` | Weapi | 添加/删除歌曲。op: "add"/"del" |
| `SetCreatePlaylist(name, privacy=False)` | Eapi | 新建歌单 |
| `SetRemovePlaylist(playlist_ids)` | Eapi | 删除歌单 |

### album.py — 专辑

| 函数 | 加密 | 说明 |
|---|---|---|
| `GetAlbumInfo(album_id)` | Weapi | 获取专辑信息及歌曲列表 |
| `GetAlbumComments(album_id, offset=0, limit=20, beforeTime=0)` | Weapi | 获取专辑评论 |

### artist.py — 艺术家

| 函数 | 加密 | 说明 |
|---|---|---|
| `GetArtistAlbums(artist_id, offset=0, limit=1000)` | Weapi | 获取艺术家所有专辑 |
| `GetArtistTracks(artist_id, offset=0, limit=1000, order="hot")` | Weapi | 获取艺术家歌曲。order: "hot"/"time" |
| `GetArtistDetails(artist_id)` | Weapi | 获取艺术家详情 |

### cloud.py — 个人云盘

上传流程（按顺序）：
1. `GetCheckCloudUpload(md5, ext, length, bitrate)` — 检查云盘资源是否已存在
2. `GetNosToken(filename, md5, fileSize, ext)` — 云盘占位，获取上传令牌
3. `SetUploadObject(stream, md5, fileSize, objectKey, token)` — 上传文件内容（目标 `45.127.129.8`）
4. `SetUploadCloudInfo(resourceId, songid, md5, filename, song, artist, album)` — 提交元信息
5. `SetPublishCloudResource(songid)` — 发布到云盘

其他：`GetCloudDriveInfo(limit, offset)`、`GetCloudDriveItemInfo(song_ids)`、`SetRectifySongId(oldSongId, newSongId)`（歌曲纠偏）。

### cloudsearch.py — 搜索

```python
GetSearchResult(keyword, stype=SONG, limit=30, offset=0)
```

类型常量：`SONG=1`、`ALBUM=10`、`ARTIST=100`、`PLAYLIST=1000`、`USER=1002`、`MV=1004`、`LYRICS=1006`、`DJ=1009`、`VIDEO=1014`。

### user.py — 用户

| 函数 | 加密 | 说明 |
|---|---|---|
| `GetUserDetail(user_id)` | Weapi | 获取用户资料详情 |
| `GetUserPlaylists(user_id, offset=0, limit=1001)` | Weapi | 获取用户创建的歌单 |
| `GetUserAlbumSubs(limit=30)` | Weapi | 获取收藏专辑（当前用户） |
| `GetUserArtistSubs(limit=30)` | Weapi | 获取收藏歌手（当前用户） |
| `SetSignin(dtype=0)` | Weapi | 每日签到。0=移动端(+4 EXP)，1=网页端(+1 EXP) |
| `SetWeblog(logs)` | Weapi | 用户足迹/行为记录 |

### video.py — MV

| 函数 | 加密 | 说明 |
|---|---|---|
| `GetMVDetail(mv_id)` | Weapi | 获取 MV 详情 |
| `GetMVResource(mv_id, res=1080)` | Weapi | 获取 MV 资源 URL。res: 240/480/720/1080 |
| `GetMVComments(mv_id, offset=0, limit=20)` | Weapi | 获取 MV 评论 |

## Helper 类（utils/helper.py）

- **`TrackHelper(track_dict)`** — 包装 API 返回的歌曲字典。属性：`ID`、`TrackName`、`TrackAliases`、`AlbumName`、`AlbumCover`、`Artists`、`Duration`（毫秒）、`TrackPublishTime`、`TrackNumber`、`CD`、`Title`、`Album`（返回 `AlbumHelper`）、`template`（文件名模板参数字典）。
- **`AlbumHelper(album_id)`** — 自动获取并缓存专辑信息。属性：`AlbumName`、`AlbumAliases`、`AlbumCompany`、`AlbumDescription`、`AlbumPublishTime`、`AlbumSongCount`、`AlbumArtists`。
- **`ArtistHelper(artist_id)`** — 自动获取并缓存。属性：`ID`、`ArtistName`、`ArtistTranslatedName`、`ArtistBrief`。
- **`UserHelper(user_id)`** — 自动获取并缓存。属性：`ID`、`UserName`、`Avatar`、`AvatarBackground`。
- **`FuzzyPathHelper(basepath)`** — O(1) 文件存在性检查，支持忽略扩展名匹配。方法：`exists(name)`、`fullpath(name)`、`get_extension(name)`。
- **`IDCahceHelper`** — 线程安全的单例缓存基类（通过 `__new__` + Lock 实现）。

所有 `*Helper(id)` 类基于 `IDCahceHelper`，使用前需调用 `helper.setSession(session)`。

## 歌词解析（utils/lrcparser.py、utils/yrcparser.py）

**LrcParser**：解析、创建、合并、导出 LRC 格式歌词。
- `LrcParser(lrc_string)` — 初始化时解析
- `.lyrics` — `defaultdict`，以时间戳（秒）为键
- `.AddLyrics(timestamp, value)` — 添加歌词行
- `.DumpLyrics()` — 导出为 LRC 字符串
- `.Find(lyrics, timestamp)` — 二分查找最近匹配

**YrcParser**：逐词滚动歌词解析（网易云私有格式）。
- `YrcParser(version, yrc_string).parse()` → `YrcLine` 列表（每行包含 `YrcBlock`，含 `t_begin`、`t_duration`、`text`）
- **ASSWriter**：将解析后的 YRC 转换为 ASS 字幕格式（使用 `\K` 卡拉 OK 标签）。

## CLI 工具（__main__.py）

```bash
python -m pyncm <分享链接或ID> [选项]
```

核心功能：
- 自动解析网易云分享链接/URL/纯 ID（`parse_sharelink()`）
- 子任务类型：`Song`、`Playlist`、`Album`、`Artist`、`User`（均继承 `Playlist` 基类）
- `TaskPoolExecutorThread` + `ThreadPoolExecutor` 多线程下载
- 通过 `mutagen` 自动打标签（MP3/FLAC/M4A/OGG）
- 下载歌词（LRC + 可选 YRC→ASS）
- Session 保存/加载实现持久化登录
- 输出模板支持：`{id}`、`{year}`、`{no}`、`{album}`、`{track}`、`{title}`、`{artists}`

## 加密内部实现（utils/crypto.py、utils/security.py）

- **Weapi**：AES-128-CBC（随机 16 字符密钥双重加密）+ 教科书式 RSA（无填充）密钥交换
- **Eapi**：AES-128-ECB + MD5 摘要盐值。数据格式：`url-36cd479b6b5-text-36cd479b6b5-digest`
- **LinuxApi**：AES-128-ECB（遗留接口，未在用）
- **Abroad 解密**：双重 SBOX 替换 + IV 异或（密钥：`fuck~#$%^&*(458`）
- **匿名登录 ID 生成**：与 `3go8&$8*3*3h0k(2)2` 异或后 MD5 → base64

## 常见使用模式

### 最简 API 调用

```python
from pyncm import Session
from pyncm.apis import login, track

session = Session()
login.LoginViaAnonymousAccount(session=session)
result = track.GetTrackAudio(29732235, session=session)
# result['data'][0]['url'] -> 音频 URL
```

### 海外用户修复

```python
session.headers['X-Real-IP'] = '118.88.88.88'
```

### 批量操作

`song_ids` 参数接受 `list | str | int`。批量操作时传入列表（每次最多 1000 项）。

## 构建与安装

```bash
pip install pyncm
# 或从源码安装：
pip install -e .
```

可选依赖：`mutagen`（音频标签）、`tqdm`（进度条）、`coloredlogs`（彩色日志）。

## 测试

```bash
python pyncm.tests.py
```

## 重要注意事项

- 项目处于**长期支持**状态 — 仅处理关键 BUG 和上游 API 变更。
- `GetTrackDownloadURL`（v0）已弃用，会抛出 `NotImplementedError`。请使用 `GetTrackDownloadURLV1`。
- 下载 API（`GetTrackDownloadURLV1`）有额度限制，一般优先使用 `GetTrackAudioV1` 获取播放 URL。
- `GetPlaylistInfo` 未登录时返回的 `tracks` 不完整，但 `trackIds` 始终完整。建议使用 `GetPlaylistAllTracks` 获取完整数据。
- 所有评论的 `beforeTime` 参数单位为**秒**（内部会乘以 1000 传给 API）。
- Helper 类（`AlbumHelper` 等）通过 `IDCahceHelper.__new__` 按 ID 实现单例缓存。
- Helper 属性上的 `@Default(default=...)` 修饰器会在发生任何异常时静默返回默认值。
