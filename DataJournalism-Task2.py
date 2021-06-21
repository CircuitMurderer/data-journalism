"""
DATA JOURNALISM: Discourse analysis project - Task II
@Python 3.8.2, via LTP 4.1.4
Author: Zhao Yuqi
Date: 2021/6/19
"""
import ltp


def print_tree(mode, tree, word, parent=0, spaces=''):
    for sid, pid, con in tree:
        if pid == parent:
            if mode == 'sdp':
                print(spaces, word[sid - 1], ' - ', con, sep='')
            elif mode == 'dep':
                print(spaces, '-- ', con, ' -- ', word[sid - 1], sep='')
            else:
                print('Format error!')
                return
            print_tree(mode, tree, word, sid, spaces + '   ')


def find_sim(words, po, p_list, sd, forbid):
    dic = {}
    for i in range(len(words)):
        if sd[i][2] in forbid:
            continue
        if words[i] in dic.keys() or po[i] not in p_list:
            continue

        dic[words[i]] = []
        for j in range(len(words)):
            if words[i] == words[j]:
                dic[words[i]].append(j)

    return dic


def check_range(arr: list, cache):
    arr = list(set(arr).difference(set(cache)))
    arr = sorted(arr)

    for i in range(0, len(arr) - 1):
        if arr[i + 1] - arr[i] not in [0, 1]:
            arr[i] = arr[i + 1]

    return arr


def fix_phrase(words, rg, display=False):
    start = rg[0]
    end = rg[1]
    word = ''
    for k in range(start - 1, end):
        word += words[k]
    if display:
        print(word, ':', start, '~', end, end='')

    return word


def find_phrase(sd, cir, po, tpo, parent_id, owner_id, tar=-1):
    par = parent_id
    own = owner_id

    for sid, pid, con in sd:
        if sid - max(own) == 1 or min(own) - sid == 1:
            if pid in own or pid in par:
                if con in cir and po[sid - 1] in tpo or con == 'ATT':
                    if sid == tar:
                        continue
                    own.append(sid)
                    find_phrase(sd, cir, po, tpo, par, own, tar)

                elif con == 'ADV' and po[sid - 1] != 'nt':
                    if po[pid - 1] in ['a', 'd'] or sd[pid - 1][2] in ['ATT', 'ADV']:
                        own.append(sid)
                        find_phrase(sd, cir, po, tpo, par, own, tar)

            elif sid in par:
                if con in cir and po[sid - 1] in tpo or con == 'ATT':
                    if sid == tar:
                        continue
                    own.append(sid)
                    par.append(pid)
                    find_phrase(sd, cir, po, tpo, par, own, tar)

    return own


def find_event(sd, po, tpo, no):
    _, pid, _ = sd[no]
    sid, _, con = sd[pid - 1]
    if po[sid - 1] in tpo and con != 'CMP':
        return sid - 1
    else:
        return find_event(sd, po, tpo, sid - 1)


def generate_sen(dp, words, po, verb_id, tar=-1):
    subs = ['SBV']
    objs = ['VOB', 'IOB', 'FOB', 'POB', 'DBL']
    all_cond_n = subs + objs + ['ATT']
    all_cond_v = subs + objs + ['ADV', 'CMP', 'ATT', 'COO']

    n = ['n', 'nh', 'ni', 'nl', 'ns', 'nz', 'nd']
    np_pos = n + ['a', 'd', 'm', 'p', 'c', 'i']
    vp_pos = ['v', 'd', 'a']

    stat = [False for _ in range(6)]
    has_print = dict(zip(subs + objs, stat))

    tm_set = []
    display = []
    dis_cache = []
    sub_sign = True
    obj_sign = True
    has_dis = False

    time_line = ''
    cplx_trigger = ''
    np_chain_item = ''

    for sid, pid, con in dp:
        np = []
        vp = []
        now_dis = ''
        if sid == tar + 1 and not has_dis:
            np = find_phrase(dp, all_cond_n, po, np_pos, [pid], [sid], verb_id + 1)
            np = check_range(np, dis_cache)
            np_t = [min(np), max(np)] if np else []

            if not np_t:
                continue

            np_word = fix_phrase(words, np_t)
            print(np_word, end=' ')
            now_dis = np_word

            has_dis = True
            display = np

            np_chain_item = np_word

        elif pid == verb_id + 1:
            n_word = []
            if ((con in subs and sub_sign) or (con in objs and obj_sign)) and po[sid - 1] != 'nt':
                if has_print[con]:
                    continue

                np = find_phrase(dp, all_cond_n, po, np_pos, [pid], [sid], pid)
                if (tar + 1 in np or sid in display) and has_dis:
                    has_print[con] = True
                    continue

                np = check_range(np, dis_cache)
                np_t = [min(np), max(np)] if np else []

                if not np_t:
                    continue

                n_word = fix_phrase(words, np_t)
                print(n_word, end=' ')
                now_dis = n_word

                if con in subs:
                    sub_sign = False
                else:
                    obj_sign = False

                has_print[con] = True

            if tar + 1 in np:
                has_dis = True
                display = np
                np_chain_item = n_word

        elif sid == verb_id + 1:
            vp = find_phrase(dp, all_cond_v, po, vp_pos, [pid], [sid])
            vp = check_range(vp, dis_cache)
            vp_t = [min(vp), max(vp)] if vp else []

            if not vp_t:
                continue

            vp_word = fix_phrase(words, vp_t)
            print(vp_word, end=' ')
            now_dis = vp_word
            cplx_trigger = vp_word

        if po[sid - 1] == 'nt' and (pid in [verb_id + 1, dp[verb_id][1]]):
            if po[sid] == 'nt':
                tm_set = [sid, sid + 1]
            elif po[sid - 2] == 'nt':
                tm_set = [sid - 1, sid]
            else:
                tm_set = [sid, sid]

        if np or vp:
            if not dis_cache:
                time_line += now_dis
            else:
                time_line += ' ' + now_dis
            dis_cache = np if np else vp

    if tm_set:
        time = fix_phrase(words, tm_set)
        print(time, end=' ')
        time_line += ' ' + time

    return np_chain_item, cplx_trigger, time_line


def main():
    noun_relation = ['ATT']
    verb_relation = ['ADV']

    n = ['n', 'nh', 'ni', 'nl', 'ns', 'nz']

    tg0 = '江苏大风天气已致11死，省委书记作批示。' \
          '受东北冷涡影响，4月30日，江苏沿江及以北地区遭受突发大风、冰雹等强对流天气袭击。灾情发生后，省委、省政府连夜部署。' \
          '省委书记娄勤俭作出批示，要求全力搜救失联人员，加强节日期间安全防范工作，组织好抗灾救灾，妥善安置受灾群众，确保人心稳定、社会安定。'

    tg1 = '千千万万普通人最伟大，习近平这样赞美劳动者！' \
          '今天是国际劳动节。习近平总书记视察调研期间，总要看望慰问一线劳动者，鼓励大家勇敢追梦。' \
          '他曾说，“人世间的一切幸福，都是要靠辛勤的劳动来创造。我们都在努力奔跑，我们都是追梦人。”'

    tg2 = '拜登上台100天后，这个变化让人吃惊！' \
          '新冠肺炎疫情下，美国国内贫富差距加速拉大。 据今日俄罗斯网站援引彭博社的数据报道说，' \
          '美国总统拜登执政的头100天里，美国最富裕人群的财富增加了1950亿美元。'

    tg3 = '国防部告诫日本：非常危险！' \
          '日本政府近日发表外交蓝皮书，渲染所谓“中国军事威胁”，恶意攻击抹黑中方，粗暴干涉中国内政，' \
          '是极其错误和不负责任的，中方对此表示强烈不满和坚决反对，已向日方提出严正交涉。'

    tg4 = '俄媒：拜登的战略难以拯救美国。' \
          '自由主义全球化的不平衡、2008年至2009年经济衰退后果的延续，以及美国国内政治发展的深层次矛盾，' \
          '这一切导致美国社会危机明显加剧。一些专家甚至认为，美国和更广泛的整个西方文明目前所面临的危机在深度和结构上都是前所未有的。'

    tg5 = '记者专访中国驻印度大使，信息量大！' \
          '目前，印度正受到第二波新冠疫情侵袭，多地疫情蔓延势头迅猛，单日新增病例连续9天超过30万起。' \
          '4月30日，中国国家主席习近平就印度新冠肺炎疫情向印度总理莫迪致慰问电，并表示中方愿同印方加强抗疫合作，向印方提供支持和帮助。'

    tg6 = '中国这时候派出舰船是何意？' \
          '印尼海军“南伽拉”号潜艇失事的惨剧令人扼腕。中国国防部4月30日透露，应印尼政府请求，' \
          '中国军队已派出舰船，赴龙目海峡相关海域，协助印尼救援“南伽拉”号失事潜艇。'

    tg7 = '福奇建议印度：快学中国！' \
          '印度新冠疫情失控，美国首席传染病专家安东尼·福奇在接受《印度快报》专访时建议，' \
          '印度应立即封锁国家数周，并像中国那样建造临时医院。'

    tg8 = '关键时刻，中国力挺俄罗斯！' \
          '4月26日，中国外交部发言人华春莹在社交媒体推特上发文称，“我们强烈反对美国及一些欧洲国家单方面强加给俄罗斯的制裁，沟通总是有必要的。”' \
          '随后，俄外交部官方账号转发了华春莹的推文，并用三个表情作为评论：俄罗斯国旗+中国国旗+加油，意思显而易见。'

    tg9 = '日本自卫队错误处理放射性废弃物，防卫省道歉。' \
          '据日本广播协会（NHK）当地时间4月30日消息，' \
          '位于日本茨城县的陆上自卫队于2019年错误地委托没有得到日本政府许可的企业处理超过标准的放射性废弃物。' \
          '目前，该废弃物被送回，保管在自卫队设施内。日本防卫省对此表示“深刻检讨，深表歉意”。'

    lt = ltp.LTP('base')

    target = tg0
    seg, hid = lt.seg([target])  # 分词

    pos = lt.pos(hid)  # 词性标注
    dep = lt.dep(hid)  # 句法分析

    '''
    print('\n*** Word segment:')
    print('/'.join(seg[0]))
    print('***')

    print('\nSyntax tree:')
    print_tree('dep', dep[0], seg[0])
    '''

    # 打印原始新闻
    print('\n原始新闻:')
    print(target)

    # 找到词汇链
    word_chain = find_sim(seg[0], pos[0], n, dep[0], noun_relation + verb_relation)
    word_chain = sorted(word_chain.items(), key=lambda each_word: len(each_word[1]), reverse=True)
    word_chain_spl = word_chain[:2]

    # 进行文本分析
    print('\n\n文本分析:')
    count = 1
    for wd, wd_list in word_chain_spl:
        print('Base NP', count, '--', wd, ':')
        count += 1

        events = []
        is_head = True

        np_chain = []
        complex_trig = []
        time_lines = []
        for i in wd_list:
            x = find_event(dep[0], pos[0], 'v', i)
            if x in events:
                continue

            if is_head:
                print('\t事件要素:', end=' ')
                is_head = False
            else:
                print(' -> ', end=' ')

            nps, trig, line = generate_sen(dep[0], seg[0], pos[0], x, i)
            np_chain.append(nps)
            complex_trig.append(trig)
            time_lines.append(line)
            events.append(x)

        print()
        verbs = [seg[0][i] for i in events]
        print('\t事件链:', ' -> '.join(verbs))
        print('\t复杂触发词:', ' -> '.join(complex_trig))
        print('\tNP链:', ' -> '.join([np_chain[i] + ' ' + verb for i, verb in enumerate(verbs)]))
        print('\t生成文本:\n', '\n'.join(['\t- ' + sen for sen in time_lines]))
        print()

    '''
    for i in range(len(seg[0])):
        print(i, seg[0][i], pos[0][i])
    '''


if __name__ == '__main__':
    main()
