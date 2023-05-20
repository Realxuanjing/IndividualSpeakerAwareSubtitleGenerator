# -*- coding: utf-8 -*-
from pydub import AudioSegment
from pydub.silence import detect_silence
import os
import uuid


# 生成guid
def GUID():
    return str(uuid.uuid1()).replace("-", "")


# 分割文件
def SplitSound(filename, save_path, save_file_name, start_time, end_time, audio_type='wav'):
    if not os.path.exists(save_path):
        try:
            os.mkdir(save_path)
        except Exception as e:
            print(e)

    sound = AudioSegment.from_file(filename, format=audio_type)
    result = sound[start_time:end_time]
    final_name = savePath
    if not savePath.endswith("/"):
        final_name = final_name + "/"
    final_name = final_name + save_file_name

    result.export(final_name, format=audio_type)
    # AudioSegment.export(result, format=audioType)


def SplitSilence(file_name, save_path, audio_type='wav'):
    sound = AudioSegment.from_file(file_name, format=audio_type)
    # print(len(sound))
    # print(sound.max_possible_amplitude)
    # start_end = detect_silence(sound,800,-57,1)
    start_end = detect_silence(sound, 300, -35, 1)

    # print(start_end)
    start_point = 0
    index = 1

    for item in start_end:
        if item[0] != 0:
            # 取空白部分的中位数
            end_point = (item[0] + item[1]) / 2
            print("%d-%d" % (start_point, end_point))
            SplitSound(file_name, save_path, str(index) + ".wav", start_point, end_point)
            index = index + 1
        start_point = item[1]

    # 处理最后一段音频
    # sound.len
    SplitSound(file_name, save_path, str(index) + ".wav", start_point, len(sound))
    # len(sound)


audioPath = r"D:\games\py_music\VoiceprintRecognition-Pytorch-legacy\audio_db\ceshi.wav"
savePath = r"D:\games\py_music\VoiceprintRecognition-Pytorch-legacy\audio\divide_music\data"
SplitSilence(audioPath, savePath)
