import argparse
import pyaudio
import numpy as np
import wave
import sys
import time

def generate_sine_wave(frequency, duration, fs, volume):
    """生成指定频率和持续时间的正弦波。"""
    return (np.sin(2 * np.pi * np.arange(fs * duration) * frequency / fs) * volume).astype(np.float32)

def play_audio(stream, high_tone, low_tone, loop, duration):
    """播放高低音交替的声音序列。"""
    try:
        # 无限循环或者指定次数的循环
        while True if loop == -1 else loop > 0:
            stream.write(high_tone.tobytes())
            time.sleep(duration)
            stream.write(low_tone.tobytes())
            time.sleep(duration)
            if loop != -1:
                loop -= 1
                print("剩余循环次数: ", loop)
    except KeyboardInterrupt:
        # 捕捉到 Ctrl+C 的中断信号，停止播放
        print("\n播放停止。")

def list_audio_devices(p):
    """列出所有可用的音频输出设备。"""
    print("可用的音频输出设备:")
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        # 只列出具有输出通道的设备
        if dev['maxOutputChannels'] > 0:
            print(f"{i}: {dev['name']}")

def main(args):
    """主函数。"""
    p = pyaudio.PyAudio()

    # 设置声音的持续时间和间隔
    duration = 0.4  # 每个音符的持续时间，单位秒

    if args.choose:
        list_audio_devices(p)
        device_index = int(input("请输入输出设备的索引: "))
    else:
        device_index = args.device

    # 获取并检查设备信息
    device_info = p.get_device_info_by_index(device_index)
    max_channels = device_info.get('maxOutputChannels', 2)

    # 打开音频流
    stream = p.open(format=pyaudio.paFloat32,
                    channels=min(1, max_channels),
                    rate=44100,
                    output=True,
                    output_device_index=device_index)

    # 根据命令行参数生成音频源
    if args.source == 'sine':
        # 生成高频和低频正弦波音频数据
        high_tone = generate_sine_wave(880, duration, 44100, 1)
        low_tone = generate_sine_wave(440, duration, 44100, 1)
        # 播放音频
        play_audio(stream, high_tone, low_tone, args.loop, duration)
    elif args.source.endswith('.wav'):
        # 从文件加载WAV音频数据
        wf = wave.open(args.source, 'rb')
        # 播放音频
        play_audio(stream, wf.readframes(wf.getnframes()), args.loop, duration)

    # 关闭流和PyAudio
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == '__main__':
    # 设置命令行参数
    parser = argparse.ArgumentParser(description='音频播放器 CLI')
    parser.add_argument('--source', type=str, default='sine', help='音频源：“sine”或.wav文件路径')
    parser.add_argument('--loop', type=int, default=1, help='循环播放音频的次数。-1 为无限循环')
    parser.add_argument('--device', type=int, default=0, help='输出设备的索引')
    parser.add_argument('--choose', action='store_true', help='列出并选择输出设备')
    args = parser.parse_args()

    main(args)
