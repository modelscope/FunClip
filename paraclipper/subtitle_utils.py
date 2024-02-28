def time_convert(ms):
    ms = int(ms)
    tail = ms % 1000
    s = ms // 1000
    mi = s // 60
    s = s % 60
    h = mi // 60
    mi = mi % 60
    h = "00" if h == 0 else str(h)
    mi = "00" if mi == 0 else str(mi)
    s = "00" if s == 0 else str(s)
    tail = str(tail)
    if len(h) == 1: h = '0' + h
    if len(mi) == 1: mi = '0' + mi
    if len(s) == 1: s = '0' + s
    return "{}:{}:{},{}".format(h, mi, s, tail)


class Text2SRT():
    def __init__(self, text, timestamp, offset=0):
        self.token_list = [i for i in text.split() if len(i)]
        self.timestamp = timestamp
        start, end = timestamp[0][0] - offset, timestamp[-1][1] - offset
        self.start_sec, self.end_sec = start, end
        self.start_time = time_convert(start)
        self.end_time = time_convert(end)
    def text(self):
        res = ""
        for word in self.token_list:
            if '\u4e00' <= word <= '\u9fff':
                res += word
            else:
                res += " " + word
        return res
    def len(self):
        return len(self.token_list)
    def srt(self, acc_ost=0.0):
        return "{} --> {}\n{}\n".format(
            time_convert(self.start_sec+acc_ost*1000),
            time_convert(self.end_sec+acc_ost*1000), 
            self.text())
    def time(self, acc_ost=0.0):
        return (self.start_sec/1000+acc_ost, self.end_sec/1000+acc_ost)


def generate_srt(sentence_list):
    srt_total = ''
    for i, d in enumerate(sentence_list):
        t2s = Text2SRT(d['text'], d['timestamp'])
        if 'spk' in d:
            srt_total += "{}  spk{}\n{}".format(i, d['spk'], t2s.srt())
        else:
            srt_total += "{}\n{}".format(i, t2s.srt())
    return srt_total

def generate_srt_clip(sentence_list, start, end, begin_index=0, time_acc_ost=0.0):
    start, end = int(start * 1000), int(end * 1000)
    srt_total = ''
    cc = 1 + begin_index
    subs = []
    for i, d in enumerate(sentence_list):
        if d['timestamp'][-1][1] <= start:
            continue
        if d['timestamp'][0][0] >= end:
            break
        # parts in between
        if (d['timestamp'][-1][1] <= end and d['timestamp'][0][0] > start) or (d['timestamp'][-1][1] == end and d['timestamp'][0][0] == start):
            t2s = Text2SRT(d['text'], d['timestamp'], offset=start)
            srt_total += "{}\n{}".format(cc, t2s.srt(time_acc_ost))
            subs.append((t2s.time(time_acc_ost), t2s.text()))
            cc += 1
            continue
        if d['timestamp'][0][0] <= start:
            if not d['timestamp'][-1][1] > end:
                for j, ts in enumerate(d['timestamp']):
                    if ts[1] > start:
                        break
                _text = " ".join(d['text'].split()[j:])
                _ts = d['timestamp'][j:]
            else:
                for j, ts in enumerate(d['timestamp']):
                    if ts[1] > start:
                        _start = j
                        break
                for j, ts in enumerate(d['timestamp']):
                    if ts[1] > end:
                        _end = j
                        break
                _text = " ".join(d['text'].split()[_start:_end])
                _ts = d['timestamp'][_start:_end]
            if len(ts):
                t2s = Text2SRT(_text, _ts, offset=start)
                srt_total += "{}\n{}".format(cc, t2s.srt(time_acc_ost))
                subs.append((t2s.time(time_acc_ost), t2s.text()))
                cc += 1
            continue
        if d['timestamp'][-1][1] > end:
            for j, ts in enumerate(d['timestamp']):
                if ts[1] > end:
                    break
            _text = " ".join(d['text'].split()[:j])
            _ts = d['timestamp'][:j]
            if len(_ts):
                t2s = Text2SRT(_text, _ts, offset=start)
                srt_total += "{}\n{}".format(cc, t2s.srt(time_acc_ost))
                subs.append(
                    (t2s.time(time_acc_ost), t2s.text())
                    )
                cc += 1
            continue
    return srt_total, subs, cc
