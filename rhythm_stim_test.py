import time

import mido
import numpy as np
from mido.midifiles import MetaMessage
from pygame import mixer
from psychopy import core


def wait_until(target_time):
    sleep_time = target_time - time.time()
    core.wait(sleep_time)
    return
    # target_timeになるまでbusy waitする
    while time.time() < target_time:
        time.sleep(0.00001)
    return


class StimGenerator:
    def __init__(self, stim_sound_file: str, midi_file: str) -> None:
        # SuperDirtサンプラーから
        # 刺激提示開始までの待ち時間
        self._init_sound_player(stim_sound_file)
        self._init_midi_player(midi_file)

    def _init_sound_player(self, stim_sound_file):
        # init sound player
        freq = 44100  # audio CD quality
        bitsize = -16  # unsigned 16 bit
        channels = 1  # 1 is mono, 2 is stereo
        buffer = 1024  # number of samples
        mixer.init(freq, bitsize, channels, buffer)
        mixer.music.set_volume(0.8)
        mixer.music.load(stim_sound_file)

    def _init_midi_player(self, midi_file):
        # MIDI fileの読み込み
        midi_msgs = mido.MidiFile(midi_file)
        # MetaMessaegeで時間が0のものを取り除く
        self.filtered_midi_msgs = list(
            msg
            for msg in midi_msgs
            if not (isinstance(msg, MetaMessage) and msg.time == 0)
        )

    def _play_midi_stim(self):
        for msg in self.filtered_midi_msgs:
            self.midi_event_time += msg.time
            t = self.midi_event_time + self.start_time
            wait_until(target_time=t)
            now_time = time.time()
            if msg.type == "note_on":
                # ノンブロッキングで再生
                mixer.music.play()
                # トリガー

            # 誤差の計算
            real_elapsed_time = abs(now_time - self.start_time)
            self.error_list.append(abs(self.midi_event_time - real_elapsed_time))

    def run(self, nb_loop: int, stim_start_delay: float = 0):
        self.midi_event_time = 0  # MIDIイベントの発火時間の累積
        self.start_time = time.time() + stim_start_delay  # 刺激の提示開始時間
        self.error_list = []  # 音声イベントの発生タイミングの誤差
        for i in range(nb_loop):
            print(i)
            self._play_midi_stim()

        # エラーの平均と分散
        # 120BPMの場合、四分音符=0.5秒、 三十二分音符が50ms、2048分音符が1ms
        diff_array = np.array(self.error_list)
        mean = diff_array.mean()
        std = diff_array.std()
        print(f"error is {mean} ± {std} sec")
        return mean, std


def main():
    # https://doi.org/10.1016/j.neuroimage.2020.116768　Fig1のパターンをDAWで作成→MIDIにエクスポート
    midi_file = "./rhythm.mid"
    # SuperDirtサンプラーから
    stim_sound_file = "./SD0050.WAV"

    stim = StimGenerator(stim_sound_file, midi_file)
    stim.run(4, stim_start_delay=0.5)


if __name__ == "__main__":
    import os
    from pathlib import Path

    os.chdir(Path(__file__).parent)
    main()
