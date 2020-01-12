import time
import mido
from typing import Dict, List


class Sequencer(object):

    def __init__(self):

        ports = mido.get_output_names()
        self.midiOUT = mido.open_output(ports[1])

        self.reader: mido.MidiFile = None
        self.isLoaded: bool = False
        self.isPlaying: bool = False

        self.timeline: Dict[float, list] = {}

    def load(self, *, smf: str) -> bool:
        try:
            self.reader = mido.MidiFile(smf, debug=False)
        except Exception as e:
            self.isLoaded = False
            print(e)
        else:
            self.isLoaded = True
            # print(self.reader)

            self.timeline.clear()
            timing: float = 0
            block: List[dict] = []
            for msg in self.reader:
                t = float(msg.time)
                if t:
                    self.timeline[timing] = block.copy()
                    block.clear()
                    block.append(msg)
                    timing += t
                else:
                    block.append(msg)
            # print(timeline)

        return self.isLoaded

    def play(self):
        if self.isLoaded:
            if self.isPlaying is False:
                self.isPlaying = True
                # self.reader.ticks_per_beat = 960
                for msg in self.reader.play(meta_messages=True):
                # for msg in self.reader:
                    try:
                        if msg.is_meta is False:
                            # if msg.time:
                            #     time.sleep(msg.time)
                            # time.sleep(msg.time)
                            self.midiOUT.send(msg)
                        else:
                            print(msg)
                    except KeyboardInterrupt as e:
                        break
                    else:
                        pass
                self.midiOUT.reset()
                self.isPlaying = False
                self.isLoaded = False
            else:
                print('already playing')
        else:
            print('not loaded')


if __name__ == '__main__':

    player = Sequencer()
    if player.load(smf='./SMFs/carnival.mid'):
        player.play()
