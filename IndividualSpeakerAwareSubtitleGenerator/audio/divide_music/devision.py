from pydub import AudioSegment
import librosa
import numpy
# 导入音频文件
with open(r'D:\games\py_music\VoiceprintRecognition-PyTorch-legacy\audio_db\ceshi.wav', 'rb') as source_audio:
 audio = librosa.load(source_audio)
print(type(audio))
# 将音频预处理
audio = audio.astype('float32')

# 对音频进行平均
audio = audio / 2

# 对音频进行熵化
audio = audio.map(librosa.log_softmax)

# 将音频分割成多个子片段
splits = audio.split()

# 对每个子片段进行预处理
splits_per_epoch = int(splits[0] * len(splits[1]))
audio_per_epoch = audio.split(splits_per_epoch)

# 提取每个人单独说话的音频
说话_audios = []
for epoch in AudioSegment.epochs(audio_per_epoch):
 for part in audio_per_epoch:
     if part.start == 0:
         if part.end > epoch.start:
             break
         说话_audios.append(audio[epoch.start: part.end+1])

# 提取每个人单独说话的音频
for epoch, audio in enumerate(audio_per_epoch):
 for part in audio:
     if part.start > 0:
         print(part.data.text)
         break

# 保存音频文件为音频
audio_text = audio.data.text
audio_path = f'{audio_text}.wav'
librosa.write_aiff(audio_path, audio)