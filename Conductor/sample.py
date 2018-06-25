import mido


def main():
    reader = mido.MidiFile('./SMFs/ConcertinoOp107.mid')

    info = reader.__dict__

    print(info)

    division = info['ticks_per_beat']
    tracks = info['tracks']

    print("Division = %d" % (division))

    for a, track in enumerate(tracks):
        print("Track[%d] %s" % (a, track.name))

        for index, msg in enumerate(track):
            # print("-- msg[%d] %s" % (index, msg))
            if msg.is_meta:
                print("-- msg[%d] META(%s)" % (index, msg.type))

    return


if __name__ == '__main__':
    main()
