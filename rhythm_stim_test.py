import time

import mido
import numpy as np
from mido.midifiles import MetaMessage
from pygame import mixer


def wait_until(target_time):
    # target_timeになるまでbusy waitする
    while time.time() < target_time:
        time.sleep(0.000001)
    return


def main():
    # https://doi.org/10.1016/j.neuroimage.2020.116768　Fig1のパターンをDAWで作成→MIDIにエクスポート
    midi_file = "./rhythm.mid"
    # SuperDirtサンプラーから
    stime_sound_file = "./SD0050.WAV"

    nb_loop = 4  # パターンの繰り返し数
    stim_start_delay = 0  # 刺激提示開始までの待ち時間

    # init sound player
    freq = 44100  # audio CD quality
    bitsize = -16  # unsigned 16 bit
    channels = 1  # 1 is mono, 2 is stereo
    buffer = 1024  # number of samples
    mixer.init(freq, bitsize, channels, buffer)
    mixer.music.set_volume(0.8)
    mixer.music.load(stime_sound_file)

    # MIDI fileの読み込み
    mid = mido.MidiFile(midi_file)
    filtered_midi_msgs = list(
        msg for msg in mid if not (isinstance(msg, MetaMessage) and msg.time == 0)
    )

    start_time = time.time() + stim_start_delay
    planned_elapsed_time = 0
    input_time = 0.0
    error_list = []

    for i in range(nb_loop):
        print("loop", i)
        for msg in filtered_midi_msgs:
            input_time += msg.time
            t = input_time + start_time
            wait_until(target_time=t)
            now_time = time.time()
            if msg.type == "note_on":
                # ノンブロッキングで再生
                mixer.music.play()
                print("sound ")

            # 誤差の計算
            planned_elapsed_time += msg.time
            real_elapsed_time = abs(now_time - start_time)
            error_list.append(abs(planned_elapsed_time - real_elapsed_time))

    # エラーの平均と分散
    # 120BPMの場合、四分音符=0.5秒、 三十二分音符が50ms、2048分音符が1ms
    diff_array = np.array(error_list)
    mean = diff_array.mean()
    std = diff_array.std()
    print(f"error is {mean} ± {std} sec")


if __name__ == "__main__":
    import os
    from pathlib import Path

    os.chdir(Path(__file__).parent)
    main()
