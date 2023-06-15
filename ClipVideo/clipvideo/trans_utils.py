PUNC_LIST = ['，', '。', '！', '？', '、']


def pre_proc(text):
    res = ''
    for i in range(len(text)):
        if text[i] in PUNC_LIST:
            continue
        if '\u4e00' <= text[i] <= '\u9fff':
            if len(res) and res[-1] != " ":
                res += ' ' + text[i]+' '
            else:
                res += text[i]+' '
        else:
            res += text[i]
    if res[-1] == ' ':
        res = res[:-1]
    return res

def proc(raw_text, timestamp, dest_text):
    # simple matching
    ld = len(dest_text.split())
    mi, ts = [], []
    offset = 0
    while True:
        fi = raw_text.find(dest_text, offset, len(raw_text))
        # import pdb; pdb.set_trace()
        ti = raw_text[:fi].count(' ')
        if fi == -1:
            break
        offset = fi + ld
        mi.append(fi)
        ts.append([timestamp[ti][0]*16, timestamp[ti+ld-1][1]*16])
        # import pdb; pdb.set_trace()
    return ts


def write_state(output_dir, state):
    for key in ['/recog_res_raw', '/timestamp', '/sentences']:
        with open(output_dir+key, 'w') as fout:
            fout.write(str(state[key[1:]]))


def load_state(output_dir):
    state = {}
    with open(output_dir+'/recog_res_raw') as fin:
        line = fin.read()
        state['recog_res_raw'] = line
    with open(output_dir+'/timestamp') as fin:
        line = fin.read()
        state['timestamp'] = eval(line)
    with open(output_dir+'/sentences') as fin:
        line = fin.read()
        state['sentences'] = eval(line)
    return state
        
    