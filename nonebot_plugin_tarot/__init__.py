from random import shuffle, randint
import random
import os
import nonebot
from typing import List
from pathlib import Path
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Event, PrivateMessageEvent, GroupMessageEvent, MessageSegment

CHAIN_REPLY = nonebot.get_driver().config.chain_reply
_TAROT_PATH = nonebot.get_driver().config.tarot_path
_NICKNAME = nonebot.get_driver().config.nickname
NICKNAME = "awesome_bot" if not _NICKNAME else list(_NICKNAME)[0]
DEFAULT_PATH = os.path.join(__file__, "resource")
TAROT_PATH = DEFAULT_PATH if not _TAROT_PATH else _TAROT_PATH

tarot = on_command("塔罗牌", aliases={"占卜"}, priority=5, block=True)

@tarot.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await tarot.send("请稍等，正在洗牌中")
    indices = random.sample(range(1, 78), 4)
    card_keys = list(cards.keys())
    shuffle(card_keys)
    chain = []
    for count in range(4):
        index = int(indices[count])
        card_key = card_keys[index - 1]
        meaning_key = list(meanings.keys())[count]
        meaning_value = meanings[meaning_key]
        image_file = Path(TAROT_PATH) / (card_key + ".jpg")

        # 特殊规则：愚者有两张
        if card_key == "愚者":
            rand = randint(1, 2)
            image_file = Path(TAROT_PATH) / (card_key + str(rand) + ".jpg")

        # 特殊规则：小阿卡纳分正位逆位
        if isinstance(cards[card_key], dict):
            rand = randint(1, 2)
            if rand == 1:
                card_value = cards[card_key]["正位"]
                card_key += "（正位）"
            else:
                card_value = cards[card_key]["逆位"]
                card_key += "（逆位）"
        else:
            card_value = cards[card_key]

        if isinstance(event, PrivateMessageEvent):
            text = meaning_key + "，" + meaning_value + "\n" + card_key + "，" + card_value + "\n"
            msg = MessageSegment.text(text)+ MessageSegment.image(image_file)
            if count < 3:
                await bot.send_private_msg(user_id=event.user_id, message=msg)
            else:
                await bot.send_private_msg(user_id=event.user_id, message=msg)

        if isinstance(event, GroupMessageEvent):
            if not CHAIN_REPLY:           
                text = meaning_key + "，" + meaning_value + "\n" + card_key + "，" + card_value + "\n"
                msg = MessageSegment.text(text) + MessageSegment.image(image_file)
                if count < 3:
                    await bot.send(event=event, message=msg, at_sender=True)
                else:
                    await tarot.finish(message=msg, at_sender=True)
            else:
                text = meaning_key + "，" + meaning_value + "\n" + card_key + "，" + card_value + "\n"
                msg = MessageSegment.text(text) + MessageSegment.image(image_file)
                if count < 4:
                    chain = await chain_reply(bot, chain, msg)
            if CHAIN_REPLY and count == 3:
                await bot.send_group_forward_msg(group_id=event.group_id, messages=chain)

async def chain_reply(bot: Bot, chain: List, msg: MessageSegment) -> List:
    data = {
        "type": "node",
        "data": {
            "name": f"{NICKNAME}",
            "uin": f"{bot.self_id}",
            "content": msg
        },
    }
    chain.append(data)
    return chain

cards = {
    "圣杯1": "家庭生活之幸福，别的牌可给予其更多内涵，如宾客来访、宴席、吵架",
    "圣杯10": "家庭幸福，预料之外的好消息",
    "圣杯2": "成功和好运，但细心、专心会是获取它们的必要条件",
    "圣杯3": "切忌轻率、鲁莽，它们会给事业带来厄运",
    "圣杯4": "不易说服的人，未婚的男子或女子，婚姻推迟",
    "圣杯5": "无根据的嫉妒，缺乏果断误了大事，且逃避责任",
    "圣杯6": "轻信，你容易被欺骗，特别是被不值得信任的同伴欺骗",
    "圣杯7": "善变或食言，提防过分乐观的朋友和无主见的熟人",
    "圣杯8": "令人愉快的公司或友谊，聚合或有计划的庆祝活动",
    "圣杯9": "梦里与愿望实现，好运与财富",
    "圣杯侍者": "一个永远的亲密朋友，或许是分别很久的童年朋友或初恋情人",
    "圣杯国王": "诚实、善良的男子，但容易草率地做出决定，并不可依赖",
    "圣杯王后": "忠诚、钟情的女人，温柔大方，惹人怜爱",
    "圣杯骑士": "假朋友，来自远方陌生的人，勾引者，应当把握当前命运",
    "宝剑1": "不幸，坏消息，充满嫉妒的情感",
    "宝剑10": "悲伤，否定好兆头",
    "宝剑2": "变化，分离",
    "宝剑3": "一次旅行，爱情或婚姻的不幸",
    "宝剑4": "疾病，经济困难，嫉妒，各种小灾难拖延工作的进度",
    "宝剑5": "克服困难，获得生意成功或者和谐的伙伴",
    "宝剑6": "只要有坚韧不拔的毅力，就能完成计划",
    "宝剑7": "与朋友争吵，招来许多麻烦",
    "宝剑8": "谨慎，看似朋友的人可能成为敌人",
    "宝剑9": "疾病、灾难、或各种不幸",
    "宝剑侍者": "嫉妒或者懒惰的人，事业上的障碍，或许是骗子",
    "宝剑国王": "野心勃勃、妄想驾驭一切",
    "宝剑王后": "奸诈，不忠，一个寡妇或被抛弃的人",
    "宝剑骑士": "传奇中的豪爽人物，喜好奢侈放纵，但勇敢、有创业精神",
    "权杖1": "财富与事业的成功，终生的朋友和宁静的心境",
    "权杖10": "意想不到的好运，长途旅行，但可能会失去一个亲密的朋友",
    "权杖2": "失望，来自朋友或生意伙伴的反对",
    "权杖3": "不止一次的婚姻",
    "权杖4": "谨防一个项目的失败，虚假或不可靠的朋友起到了破坏作用",
    "权杖5": "娶一个富婆",
    "权杖6": "有利可图的合伙",
    "权杖7": "好运与幸福，但应提防某个异性",
    "权杖8": "贪婪，可能花掉不属于自己的钱",
    "权杖9": "和朋友争辩，固执的争吵",
    "权杖侍者": "一个诚挚但缺乏耐心的朋友，善意的奉承",
    "权杖国王": "一个诚挚的男人，慷慨忠实",
    "权杖王后": "一个亲切善良的人，但爱发脾气",
    "权杖骑士": "幸运地得到亲人或陌生人的帮助",
    "钱币1": "重要的消息，或珍贵的礼物",
    "钱币10": "把钱作为目标，但并不一定会如愿以偿",
    "钱币2": "热恋，但会遭到朋友反对",
    "钱币3": "争吵，官司，或家庭纠纷",
    "钱币4": "不幸或秘密的背叛，来自不忠的朋友，或家庭纠纷",
    "钱币5": "意外的消息，生意成功、愿望实现、或美满的婚姻",
    "钱币6": "早婚，但也会早早结束，第二次婚姻也无好兆头",
    "钱币7": "谎言，谣言，恶意的批评，运气糟透的赌徒",
    "钱币8": "晚年婚姻，或一次旅行，可能带来结合",
    "钱币9": "强烈的旅行愿望，嗜好冒险，渴望生命得到改变",
    "钱币侍者": "一个自私、嫉妒的亲戚，或一个带来坏消息的使者",
    "钱币国王": "一个脾气粗暴的男人，固执而充满复仇心，与他对抗会招来危险",
    "钱币王后": "卖弄风情的女人，乐于干涉别人的事情，诽谤和谣言",
    "钱币骑士": "一个有耐心、有恒心的男人，发明家或科学家",
    "愚者": {
        "正位": "活在当下，或随遇而安，如果每天都很重试，便能回味无穷",
        "逆位": "时机的关键所在，表示还不是时机，也代表没能把握住时机，或太固执于过去的计划，过分依赖他人的建议",
    },
    "魔术师": {
        "正位": "富有外交手腕，但需要坚定的意志和正当的目的才能把它发挥出来。成功可以获得巨大收获；但失败的话...",
        "逆位": "毫无意义的投机心态。漫无目的、缺乏自律，也暗示精神上的困扰。极端下意味着丧失良知和反社会",
    },
    "女教皇": {"正位": "宁静、直觉、含蓄、谨慎，被动接受以得到发展", "逆位": "诡异、猜疑、冷漠、迟缓，内心发展后，回到了现实生活"},
    "女皇": {"正位": "具有魅力、优雅和毫无保留的爱，有创造力和聪明才智", "逆位": "自负、矫情，无法容忍缺陷。不应过于理想化"},
    "皇帝": {"正位": "坚强的意志和稳固的力量，通过努力和自律达到成功", "逆位": "任性、暴虐和残忍，意味着由于缺乏自律而失败，高处不胜寒"},
    "教皇": {
        "正位": "信心十足，不疑惑，对事情有正确的理解力，寻找新的方法，可能感到阻力，但事实会证明一切",
        "逆位": "爱说教，唱高调以及独断，也代表新的观念形成、或拒绝流俗。为自己的人生写剧本，按自己对生命的理解而活",
    },
    "恋人": {
        "正位": "道德、美学、更深层次的精神和肉体上的渴望，暗示一段新的关系，或已有关系的新形态，也暗示沉醉于爱河",
        "逆位": "欲求不满、多愁善感、迟疑不决。意味着任何追求新阶段的努力都只建立于期待和梦想，也可以意味一段关系的结束",
    },
    "战车": {
        "正位": "成功、有才能、有效率，抛开过去的束缚。如果牌阵总体结果不好，应该考虑有哪方面过于激烈",
        "逆位": "暗示专治的态度和拙劣的方向感，可能被情绪懵逼了视线。太过多愁善感",
    },
    "力量": {
        "正位": "代表个人魅力与追求成功的决心，象征爱与坚强的意志力，可驾驭不易控制的能量，拥有优势力量",
        "逆位": "自满、滥权，对人生无望，害怕被热情和欲望冲昏头脑。去做自己想做的",
    },
    "隐士": {"正位": "代表有所坚持，有目标、深沉且专注", "逆位": "代表不易原谅他人，可能感到寂寞。如果害怕放弃某些东西，会失去成长的机会"},
    "命运之轮": {"正位": "代表无论喜欢与否，改变终将会到来", "逆位": "意味着要对抗改变可能很困难，但是成败输赢不是固定的，请迎接未来"},
    "正义": {
        "正位": "正直、公平、诚实、纪律，只要对自己诚实，未来能得到改善；或代表成功解决某个争议",
        "逆位": "暗示消极、不满的心态，代表无休止的争议或不协调。必须要找到原因，否则不和将一再出现",
    },
    "吊人": {
        "正位": "代表有偿的牺牲，代表任性极限、解决问题、有人文特质，代表一段反省的时光、内在的平和宁静，也代表在不同角度，会有不同的感受",
        "逆位": "代表无偿的牺牲，代表精神有所局限且缺乏远见，代表听从他人期望而不顺从自己的想法。顺从自有好处",
    },
    "死神": {
        "正位": "代表顺从变化，放下曾经紧抓不放的事物，会得到新生；同时意味接受死亡，便会活得更充实",
        "逆位": "意味并不相信改变会带来好结果，因此拒绝改变；代表掩饰绝望",
    },
    "节制": {"正位": "代表节制，调试热情，不致过分越轨，还代表运用知识和理解力来条件行为的能力", "逆位": "代表轻浮和过度追求时髦，也可代表学习和旅行"},
    "恶魔": {
        "正位": "代表感官的魅力和热情的表达，接受了糟糕的状态而不愿改变",
        "逆位": "即使肢体上受到束缚，精神仍可以翱翔，积极寻找改变的方法，放下控制欲，才能发现真正的自由",
    },
    "塔": {
        "正位": "表示能接受挫折，勇敢克服困难，或许感到深深的痛苦与失望，但都是为了自己能有所成长",
        "逆位": "代表得意忘形、自作自受、沉溺于虚幻的想象。无法抗拒改变，其终究会发生",
    },
    "星星": {
        "正位": "代表着乐观与无限的希望，对自己充满信心，将迎来一段心平气和的时光",
        "逆位": "需要心灵上的自由。适当舍弃没有价值的事物，会让你看的更清楚",
    },
    "月亮": {
        "正位": "意味着敏感、体谅、感同身受，代表对圆满的不安，越幸福的时候，越担心不幸会到来",
        "逆位": "代表感情上的顺从、被动和缺乏自我，面对心中的想法，才能解决问题",
    },
    "太阳": {
        "正位": "代表着具有激情、人际和谐以及美好名声等正面的特质，意味着有创造性的事物，可以在生活中感到快乐、爱与价值",
        "逆位": "代表骄傲、自负、虚伪等反面特征，然而，生命与世界任然支持你，它也可能暗示竞争，也许是自己与自己的竞争",
    },
    "审判": {
        "正位": "代表具有超越自我、发觉无限潜力的特质，了解生命的相连，才能了解自己的精神意志、知道如何表达他",
        "逆位": "代表着缺少应对忧郁的能力，而越是逃避，空虚感更加加深；试图弥补，解决之道来自内心",
    },
    "世界": {
        "正位": "意味着报酬优厚，收获巨大",
        "逆位": "预示巨大的障碍、涣散的精神及自怜的性格，同时也代表旅行；有人以为是成功带来了快乐，实是快乐带来了成功",
    },
}

meanings = {
    "第一张牌": "代表过去，即已经发生的事",
    "第二张牌": "代表问题导致的局面",
    "第三张牌": "表示困难可能有的解决方法",
    "切牌": "表示问卜者的主观想法",
}
