import numpy as np
import scipy.signal as signal


def remove_noise(signal, win_size=512, step_size=256, rate=0.15, filt_len=15):
    # 分帧
    frames = frame(signal, win_size, step_size)
    # 计算能量
    energies = np.sum(np.square(frames), axis=1)
    # 计算阈值
    threshold = np.mean(energies) * rate
    # 将低于阈值的帧设置为0
    frames[np.where(energies <= threshold)] = 0
    # 重建信号
    signal = overlap(frames, win_size, step_size)
    # 中值滤波降噪
    signal = signal.medfilt(signal, filt_len)
    return signal


def frame(signal, win_size, step_size):
    # 零填充
    padded = np.pad(signal, (0, win_size - (len(signal) % win_size)), 'constant')
    # 分帧
    frames = np.lib.stride_tricks.as_strided(padded, shape=((len(padded) - win_size) // step_size + 1, win_size),
                                             strides=(padded.strides[0] * step_size, padded.strides[0]))
    return frames


def overlap(frames, win_size, step_size):
    # 计算重叠部分
    overlap = win_size - step_size
    # 重建信号
    signal = np.zeros((len(frames) - 1) * step_size + win_size)
    for i, frame in enumerate(frames):
        start = i * step_size
        end = start + win_size
        signal[start:end] += frame
        signal[start + overlap:end - overlap] *= 0.5
    return signal



import librosa
import soundfile as sf
 # 加载音频文件
path = 'chunk5.wav'
signal, sr = librosa.load(path, sr=16000)
 # 调用去噪函数
denoise_signal = remove_noise(signal)
 # 保存结果
sf.write('denoised_signal.wav', denoise_signal, sr)
 # 比较原始信号和去噪信号的声谱图
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 4))
plt.subplot(2, 1, 1)
plt.specgram(signal, NFFT=512, Fs=sr, cmap='Greys')
plt.title('Original Signal')
plt.xlabel('Time')
plt.ylabel('Frequency')
plt.subplot(2, 1, 2)
plt.specgram(denoise_signal, NFFT=512, Fs=sr, cmap='Greys')
plt.title('Denoised Signal')
plt.xlabel('Time')
plt.ylabel('Frequency')
plt.tight_layout()
plt.show()