from datetime import datetime
import os
import random
from time import sleep
import openai
from tqdm import tqdm

# Load your API key from an environment variable or secret management service
openai.api_key = "xxx"

class ChatGPT:
    def __init__(self, chat_list=[]) -> None:
        # 初始化对话列表
        self.chat_list = [
        ]
        self.init_prompt = [
            # 角色prompt， 指令prompt
            {
                "role": "system",
                "content": """
                请你以航空航天领域语言专家的身份，纠正句子中的各种语法错误。
            """
            },
            # 指令prompt+输出控制prompt
            {
                "role": "user",
                "content": """
                        我会以 ’<input>\t错误句子\t</input>’ 的形式给出需要修改的句子；
                        对每个需要修改的句子，在修改错误时，你需要先理解句子想表达的意思，分析后再纠正，最后以’<output>\t正确句子\t</output>’的形式输出纠错后的句子。
                """
            },
            # 输出控制
            {
                "role": "user",
                "content": "对于给出的句子，你必须严格按照<input>标签分开处理，最终返回的纠正答案必须和给出的句子一一对应，数量一致。"
            },

            #example
            {
               "role": "user",
               "content":
               """
                    <input>\t矢网的对应按键功能实现的线程在另外一个循环中来实现。\t</input>
                    
                    <input>\t该框架模型除了充分利用自动化响应提高对抗黑客的能力和减轻管理员负担义务以外，还将管理员置于非常重要的地位。\t</input>
                    
                    <input>\t不但他自己认真学习，而且还尽力在帮助其他同学。\t</input>
                    
                    <input>\t系统开机后可设置处于在启动模式下，在仅在此模式下，可以向DSP传送程序。\t</input>
                    
                    <input>\t通常滤波使用的线性误差方程的前提是姿态失准角为小量。\t</input>
               """
            },
            {
               "role": "assistant",
               "content":
                """
                    <input>\t矢网的对应按键功能实现的线程在另外一个循环中来实现。\t</input>
                    句中的“实现”重复，可以删除“在另外一个循环中来实现“中的“来实现”
                    <output>\t矢网的对应按键功能实现的线程在另外一个循环中。\t</output>
                    
                    <input>\t该框架模型除了充分利用自动化响应提高对抗黑客的能力和减轻管理员负担义务以外，还将管理员置于非常重要的地位。\t</input>
                    句中存在搭配错误，“减轻管理员负担义务”义务不能搭配负担，同时义务也不能被减轻，可以把义务删去。
                    <output>\t该框架模型除了充分利用自动化响应提高对抗黑客的能力和减轻管理员负担以外，还将管理员置于非常重要的地位。\t</output>
                    
                    <input>\t不但他自己认真学习，而且还尽力在帮助其他同学。\t</input>
                    该句子存在语序错误，“不但他”应改为“他不但”。
                    <output>\t他不但自己认真学习，而且还尽力在帮助其他同学。\t</output>
                    
                    <input>\t系统开机后可设置处于在启动模式下，在仅在此模式下，可以向DSP传送程序。\t</input>
                    句中"可设置处于在启动模式下"表达不准确，应改为"可以设置为启动模式"；同时"在仅在此模式下"表达不准确，应改为"仅在此模式下"。
                    <output>\t系统开机后可以设置为启动模式，仅在此模式下，可以向DSP传送程序。\t</output>
                    
                    <input>\t通常滤波使用的线性误差方程的前提是姿态失准角为小量。\t</input>
                    句子“滤波使用的线性误差方程的前提”应改为“滤波使用线性误差方程的前提”。
                    <output>\t通常滤波使用线性误差方程的前提是姿态失准角为小量。\t</output>
                """
            },
        ]

        # 随机采样十条作为example
        # hsk_train = open("data/yaclc/para/yaclc-fluency_dev_single.para", "r", encoding="utf-8").readlines()
        # # random sample 10 sent from hsk
        # samples = [sample.split("\t") for sample in random.sample(hsk_train, 5)]
        # self.init_prompt.append({"role": "user", "content": "\n".join([f"<{i}>\t{sample[0]}" for i, sample in enumerate(samples)])})
        # self.init_prompt.append({"role": "assistant", "content": "\n".join([f"<{i}>\t{sample[1]}" for i, sample in enumerate(samples)])})

    # 显示接口返回
    def show_conversation(self, msg_list):
        for msg in msg_list:
            if msg['role'] == 'user':
                print(f"Me: {msg['content']}\n")
            else:
                print(f"ChatGPT: {msg['content']}\n")

    # 提示chatgpt
    def ask(self, prompt, need_record=False):
        temp = {"role": "user", "content": prompt}
        if need_record:
            self.chat_list.append(temp)
            # gpt-4, gpt-4-0314, gpt-3.5-turbo
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                    messages=self.init_prompt+self.chat_list,
                                                    temperature=0,
                                                    n=1)
            answer = response.choices[0].message['content']
            # 添加历史对话，形成上下文关系
            self.chat_list.append({"role": "assistant", "content": answer})
            self.show_conversation(self.chat_list)
        else:
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                    messages=self.init_prompt+[temp],
                                                    temperature=0,
                                                    n=1)
            answers = [choice.message['content'].strip() for choice in response.choices]
            return answers


chatgpt = ChatGPT()
with open("data/hkht/hkht-data/hkht.test.src", "r", encoding="utf-8") as f:
    srcs = [line for line in f.read().split("\n") if line]

    # 因长度限制，二十句一组
    n = 5
    srcs_split = [srcs[i:i + n] for i in range(0, len(srcs), n)]

    # 容易中断，下次从断点开始
    idx = 0
    retry = 0
    last = datetime.now()
    while True:
        if idx >= len(srcs_split):
        # if idx >= 10:
            break
        try:
            print(f"正在处理{idx}/{len(srcs_split)}" + ("" if retry == 0 else f"，重试{retry}次"), end="\r")
            question = ""
            sentences = srcs_split[idx]
            for sen_idx, sen in enumerate(sentences):
                question += f"<input>\t{sen}\t</input>\n"
            answers = chatgpt.ask(question)

            output = ""
            for ans_idx, ans in enumerate(answers):
                ans = [line.strip() for line in ans.split("\n") if line]
                output += "\n\n".join(ans) + "\n"

            with open("data/hkht/hkht-data/hkht.test.gpt3.5.cot.out", "a", encoding="utf-8") as f1:
                f1.write(output)
        except Exception as e:
            # print(e)
            sleep(5)
            retry += 1
            print("调用失败，重新请求...重试次数:", retry)
            continue
        else:
            print(f"已完成{idx}/{len(srcs_split)}, time: {datetime.now() - last}")
            last = datetime.now()
            retry = 0
            idx += 1


# 测试
# print(chatgpt.ask(
#     """
#     <input>\t我认为空气污染是跟我们的生活密切的问题，所以一定要最优先解决，优其是像北京那样的大城市。\t</input>
#
#     <input>\t最后，要关主一些关于天气预报的新闻。\t</input>
#
#     <input>\t累得连设计未来的力量都没有\t</input>
#     """
#                   )[0])
