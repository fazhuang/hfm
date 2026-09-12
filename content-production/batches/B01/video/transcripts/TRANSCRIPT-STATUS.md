# HFM CONTENT-B01 — Video Transcript Status (诚实记录)

```text
ASR_ENGINE_AVAILABLE = NO
(本地未安装 openai-whisper / vosk / 其他中文 ASR；未联网调用外部 STT)
```

## 结论

```text
VIDEO_TRANSCRIPTS_COMPLETE = NO
TRANSCRIPTION_METHOD = PENDING (Batch 02 需授权安装/接入中文 ASR 或人工转写)
SPEECH_SIGNAL = VAD 检查完成（ffmpeg silencedetect -38dB / 1.2s）
CONTENT_DESCRIPTION = NOT_VIEWED_BY_MODEL（本会话模型不支持读图；不得以文件名臆测画面内容）
```

因此 `video-segments.csv` 中所有 `CONTENT_DESCRIPTION / PEOPLE / PLACE / EVENT /
HFM_RELEVANCE / RECOMMENDED_USAGE` 均标记为未检视（NEEDS_REVIEW），仅保留可验证的技术分帧与 VAD
信号。任何画面内容描述都不得伪造。

## 技术可验证事实（已记录于 probes/*.json）

| 资产 | 时长 | 容器 | 视频 | 音频 | 备注 |
| --- | --- | --- | --- | --- | --- |
| HFM-A000007 《针灸鼻祖皇甫谧》第1集 大器晚成.mpg | 915.5 s | mpeg | mpeg2video 720×576 yuv420p | mp2 48kHz 2ch | 全片解码干净；场景切点 26 处 |
| HFM-A000008 皇甫谧一.mpg | ~109.8 s（解码验证 2746 帧 @25fps） | mpeg | mpeg2video 720×576 yuv420p | ac3 48kHz 2ch | 容器时长 N/A；解码报 ac-tex damaged / MVs not available，部分段落存在损伤 |

## 转写建议（Batch 02）

1. 授权安装本地中文 ASR（whisper small/medium 或 vosk-zh）或提供人工转写；
2. 转写输出保留 `RAW_TRANSCRIPT`（含时间戳），与任何规范化/纠错分离；
3. 转写后结合抽帧画面审看，再回填 `video-segments.csv` 内容字段并升级 `REVIEW_STATUS`；
4. HFM-A000008 需先做损伤段定位（损坏段建议标记 UNUSABLE 或作技术修复评估）。
