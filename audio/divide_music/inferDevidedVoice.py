import argparse
import functools
import os
import shutil

import numpy as np
import torch

from utils.reader import load_audio
from utils.record import RecordAudio
from utils.utility import add_arguments, print_arguments

parser = argparse.ArgumentParser(description=__doc__)
add_arg = functools.partial(add_arguments, argparser=parser)
add_arg('input_shape', str, '(1, 257, 257)', '数据输入的形状')
add_arg('threshold', float, 0.6, '判断是否为同一个人的阈值')
# add_arg('audio_db', str, '../../test_fenge/results', '音频库的路径')
add_arg('audio_db', str, 'audio/divide_music/voice_initial', '音频库的路径')
add_arg('model_path', str, 'models/resnet34.pth', '预测模型的路径')
args = parser.parse_args()

print_arguments(args)

device = torch.device("cuda")

model = torch.jit.load(args.model_path)
model.to(device)
model.eval()

person_feature = []
person_name = []


# 这里做了修改
def infer(audio_path, pan=False):
    input_shape = eval(args.input_shape)
    # print("args.input_shape is",args.input_shape)
    # data = load_audio(audio_path, mode='infer', spec_len=80)#spec_len=input_shape[2]
    data = load_audio(audio_path, mode='infer', spec_len=input_shape[2], pan=pan)  # spec_len=input_shape[2]
    data = data[np.newaxis, :]
    data = torch.tensor(data, dtype=torch.float32, device=device)
    # 执行预测
    feature = model(data)
    return feature.data.cpu().numpy()


# 加载要识别的音频库
def load_audio_db(audio_db_path):
    audios = os.listdir(audio_db_path)
    for audio in audios:
        # print('audio_db_path is', audio_db_path)
        # print('audio is', audio)
        path = os.path.join(audio_db_path, audio)
        name = audio[:-4]
        feature = infer(path)[0]
        person_name.append(name)
        person_feature.append(feature)
        print("Loaded %s audio." % name)


# 加载要识别的音频
def load_audio_people(audio_db_path, audio_people_wav):
    audio = audio_people_wav
    path = os.path.join(audio_db_path, audio)
    name = audio[:-4]
    feature = infer(path)[0]
    person_name.append(name)
    person_feature.append(feature)
    print("Loaded %s audio." % name)


# 音频识别
def recognition(path, pan=False):
    name = ''
    pro = 0
    feature = infer(path, pan)[0]
    #print("结果是", infer(path))
    for i, person_f in enumerate(person_feature):
        dist = np.dot(feature, person_f) / (np.linalg.norm(feature) * np.linalg.norm(person_f))
        if dist > pro:
            pro = dist
            name = person_name[i]
    return name, pro


# 声纹注册
def register(path, user_name):
    save_path = os.path.join(args.audio_db, user_name + os.path.basename(path)[-4:])
    shutil.move(path, save_path)
    feature = infer(save_path)[0]
    person_name.append(user_name)
    person_feature.append(feature)


from os import listdir

#if __name__ == '__main__':
def infer_main():
    load_audio_db(args.audio_db)

    record_audio = RecordAudio()

    # 获取子文件夹中的文件列表
    files = listdir('test_fenge/results')
    # 对每个文件进行计数
    num_files = sum(1 for file in files if file.endswith('.wav'))
    wav_files_name = []
    for file in files:
        if file.endswith('.wav'):
            wav_files_name.append(file)
    print(wav_files_name)
    num_files_diff = 1
    print("子文件夹 `data` 下有 {} 个文件。".format(num_files))

    P_res = open('people_result.txt', 'w', encoding='GBK')

    while num_files >= num_files_diff:
        # select_fun = int(input("请选择功能，0为注册音频到声纹库，1为执行声纹识别："))
        select_fun = 1
        if select_fun == 0:
            audio_path = record_audio.record()
            name = input("请输入该音频用户的名称：")
            if name == '': continue
            register(audio_path, name)
        elif select_fun == 1:
            for file in wav_files_name:
                if (file.startswith('{}'.format(num_files_diff - 1))):
                    wav_num_name = file
            audio_path = 'test_fenge/results/{}'.format(wav_num_name)
            name, p = recognition(audio_path)
            if (name == "空白"):
                name, p = recognition(audio_path, pan=True)
            if p > args.threshold:
                print("第%d句话识别为：%s，相似度为：%f" % (num_files_diff, name, p))
            else:
                source_path = audio_path
                folder_path = "audio/divide_music/voice_initial/"
                people_num_initial = 1
                people_num_bool = True
                while people_num_bool:
                    target_file_path = os.path.join(folder_path, "{}号人物.wav".format(people_num_initial))
                    if os.path.isfile(target_file_path):
                        print("目标文件夹中已经存在{}号人物.wav文件".format(people_num_initial))
                        people_num_initial += 1
                    else:
                        people_num_bool = False
                        print("目标文件夹中不存在{}号人物.wav文件,正在创建中".format(people_num_initial))
                        print("第%d句话识别为：%s号人物，相似度为：%f" % (num_files_diff, people_num_initial, 1.0))
                        name = "{}号人物".format(people_num_initial)

                destination_path = 'audio/divide_music/voice_initial/{}号人物.wav'.format(people_num_initial)
                shutil.copy(source_path, destination_path)
                print("音频库没有该用户的语音,正在注册")
                load_audio_people(args.audio_db, '{}号人物.wav'.format(people_num_initial))

        else:
            print('请正确选择功能')
        num_files_diff = num_files_diff + 1

        print(name, file=P_res, end='\n')

    P_res.close()

