import pyaudio
import wave


def detect_speech(filename):
    # 打开音频文件
    wf = wave.open(filename, 'rb')
    # 创建 PyAudio 对象
    p = pyaudio.PyAudio()
    # 打开音频流
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    print("channels is", wf.getnchannels())
    print("rate is", wf.getframerate())
    # 读取音频数据的块大小
    chunk = 1024
    # 获取采样率
    sample_rate = wf.getframerate()
    # 初始化变量
    is_speaking = False  # 是否正在说话
    start_time = 0  # 开始说话的时间
    end_time = 0  # 结束说话的时间
    num_silence_frames = 0  # 静音帧计数器
    start_time_list = []  # 每段说话的开始时间列表
    end_time_list = []  # 每段说话的结束时间列表
    # 读取音频流数据
    while True:
        data = wf.readframes(chunk)
        if not data:
            break
            # 向音频流写入数据
        stream.write(data)
        # 将 data 转换成整数列表
        data_int = [int.from_bytes(data[i:i + 2], byteorder='little', signed=True) for i in range(0, len(data), 2)]
        # 检测是否开始说话
        if not is_speaking and max(data_int) > 100:
            is_speaking = True
            start_time = wf.tell() / sample_rate
            num_silence_frames = 0
            # 检测是否结束说话
        elif is_speaking and max(data_int) <= 100:
            num_silence_frames += 1
            if num_silence_frames > 10:
                is_speaking = False
                end_time = wf.tell() / sample_rate
                start_time_list.append(start_time)
                end_time_list.append(end_time)
                # 如果在结束时还在说话，则添加这段说话的时间
    if is_speaking:
        end_time = wf.getnframes() / sample_rate
        start_time_list.append(start_time)
        end_time_list.append(end_time)
        # 关闭流
    stream.stop_stream()
    stream.close()
    # 终止 PyAudio 对象
    p.terminate()
    # 输出每段说话的起始和结束时间
    for i in range(len(start_time_list)):
        print("第 %d 段说话的起始时间: %.2f，结束时间: %.2f" % (i + 1, start_time_list[i], end_time_list[i]))
        # 返回每段说话的开始时间列表和结束时间列表
    return start_time_list, end_time_list


from pydub import AudioSegment
from pydub.playback import play

import wave
import audioop


def extract_audio(in_file, out_file, start_time, end_time):
    with wave.open(in_file, 'rb') as wav_in, wave.open(out_file, 'wb') as wav_out:
        # 获取原始音频的参数
        num_channels = wav_in.getnchannels()
        sample_width = wav_in.getsampwidth()
        frame_rate = wav_in.getframerate()
        num_frames = wav_in.getnframes()
        # 计算需要截取的帧数
        start_frame = int(start_time * frame_rate)
        end_frame = int(end_time * frame_rate)
        # 截取音频数据并写入文件
        data = wav_in.readframes(num_frames)
        # data = audioop.tomono(data, sample_width, 1, 0)  # 转为单声道
        # data = audioop.bias(data, sample_width, -128)  # 压缩动态范围
        # data = audioop.mul(data, sample_width, 2 ** 15 // 2)  # 调整音量
        data = data[start_frame * 2:end_frame * 2]
        wav_out.setnchannels(1)
        wav_out.setsampwidth(sample_width)
        wav_out.setframerate(frame_rate)
        wav_out.writeframes(data)


def split_audio_by_speech(filename):
    # 检测音频文件中的每段说话时间
    start_time_list, end_time_list = detect_speech(filename)
    # 使用 PyDub 打开音频文件
    audio = AudioSegment.from_file(filename)
    # 遍历每段说话时间，截取对应的音频并保存
    for i in range(len(start_time_list)):
        start_time = start_time_list[i]
        end_time = end_time_list[i]
        out_file = r'results\{}_{}_{}.wav'.format(i,start_time, end_time)
        extract_audio(filename, out_file, start_time, end_time)
        print('已保存分割后的音频文件：{}'.format(out_file))

    # 测试代码


filename = 'ceshi_30s_3peo.wav'
split_audio_by_speech(filename)
