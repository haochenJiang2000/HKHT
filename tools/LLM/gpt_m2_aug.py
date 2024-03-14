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
                请你扮演一位语言知识丰富，尤其擅长造句的中文语言专家。
                """
            },
            # 指令prompt+输出控制prompt
            {
                "role": "user",
                "content": """
                    我会以<example>\t例句\t</example>的形式给出一个例句，
                    再以<mod_example>\t修改后的例句\t</mod_example>的方式给出修改后的例句，
                    以<special>\t造的句子需要包含的内容\t</special>
                    同时以<mod>\t修改提示\t</mod>的方式给出修改提示。

                    你需要模仿例句造句。造句方式如下： 
                    你需要一步步思考，分析例句结构，模仿例句，发挥想象力，用不同领域的知识填充，最终生成10句句子。
                    造句时你需要模仿该例句的整体组成结构；你需要分析例句开头的结构，使用尽可能相同的开头结构造句。
                    精确模仿该例句的整体组成结构，使用模板造句，以<tgt>\t造出的句子\t</tgt>的形式输出。

                    然后，你需要依据修改提示，仿照例句的修改方式，将造出的句子修改为病句，以<src>\t修改后的句子\t</src>的形式输出。
                    交换句子中特定成分的修改，需要先分析例句交换了什么成分，再模仿该方式在造出的句子上修改。

                    比如给定输入：
                    <example>\t中国高铁不仅运营规模大,而且还具有系统技术全面、造价低、建设速度快的特色,成为“中国速度”“中国制造”的新名片。\t</example>
                    <mod_example>\t不仅中国高铁运营规模大,而且还具有系统技术全面、造价低、建设速度快,成为“中国速度”“中国制造”的新名片。\t</mod_example>
                    <mod>\t原句将“中国高铁不仅”交换词序变为“不仅中国高铁”，模仿此修改方式交换句子中特定成分\t</mod>
                    <mod>\t模仿原句修改方式，将“的特色”表示的成分删除\t</mod>
                    <special>\t无\t</special>

                    你需要输出推理过程、十句造出的句子，并根据修改提示将造句修改为病句，应该输出的内容如下：
                    推理：
                        例句为“中国高铁不仅运营规模大,而且还具有系统技术全面、造价低、建设速度快的特色,成为“中国速度”“中国制造”的新名片。”
                        分析该例句结构：“...不仅...，而且具有...的特色，成为...”
                        分析该例句开头短句的结构：“...不仅...,”
                        使用上述结构，不同领域的知识填充，造十句句子，句子无特定内容要求。结果如下：
                        1. <tgt>\t这家公司不仅产品种类多，而且还具有质量可靠、价格实惠的特色，成为消费者心目中的首选品牌。\t</tgt>
                        ...  
                        10.<tgt>\t...\t</tgt>

                        例句将“中国高铁不仅”交换词序变为了“不仅中国高铁”,同时删除了“的特色”。修改提示为：
                        <mod>\t原句将“中国高铁不仅”交换词序变为“不仅中国高铁”，模仿此修改方式交换句子中特定成分\t</mod>
                        <mod>\t模仿原句修改方式：将“的特色”表示的成分删除\t</mod>
                        
                        分析例句修改方式：
                        原句将“中国高铁不仅”交换词序变为“不仅中国高铁”，是将”名词+不仅“交换词序变为”不仅+名词“
                        原句将“的特色”删除，即将”aaa的xx“结构中”的xx“成分删除
                        模仿该例句修改方式将造句改为病句，不用考虑语法是否正确,则造的十句句子应分别修改为：
                        1. <src>\t不仅这家公司产品种类多，而且还具有质量可靠、价格实惠，成为消费者心目中的首选品牌。\t</src>
                        ...  
                        10.<src>\t...\t</src>
                    
                    又比如给定输入：
                    <example>\t校庆活动期间，我校高度重视安全教育，采取多种措施做好安全工作，以防止出现校园踩踏事件。\t</example>
                    <mod_example>\t校庆活动期间，我校高度看重安全教育，采取多种措施做好安全工作，以防止出现校园踩踏事件的发生。\t</mod_example>
                    <mod>\t模仿原句修改方式，添加冗余成分“的发生”\t</mod>
                    <mod>\t模仿原句修改方式，将“重视”替换为“看重”\t</mod>
                    <special>\t重视\t</special>
                    
                    你需要输出推理过程、十句造出的句子，并根据修改提示将造句修改为病句，应该输出的内容如下：
                    推理：
                        例句为“校庆活动期间，我校高度重视安全教育，采取多种措施做好安全工作，以防止出现校园踩踏事件。”
                        分析该例句结构：“...期间，...重视...，...采取...，...出现...事件”
                        分析该例句开头短句的结构：“...期间”
                        使用上述结构，不同领域的知识填充，造十句句子，句子中要包含”重视“。结果如下：
                        1. <tgt>\t中秋国庆双节期间，地方政府应高度重视游客人流，采取多种措施做好引导工作，避免出现踩踏事件。\t</tgt>
                        ...  
                        10.<tgt>\t...\t</tgt>
                        
                        例句添加了冗余成分“的发生”,同时将“重视”替换为“看重”，修改提示为：
                        <mod>\t模仿原句修改方式，添加冗余成分“的发生”\t</mod>
                        <mod>\t模仿原句修改方式，将“重视”替换为“看重”\t</mod>
                        
                        分析例句修改方式：
                        原句添加冗余成分“的发生”，是将”防止xxx“结构添加成分变为”防止xxx的发生“
                        原句将将“重视”替换为“看重”，”重视安全教育“的动宾搭配变为”看重安全教育“，形成动宾搭配错误
                        模仿该例句修改方式将造句改为病句，不用考虑语法是否正确,则造的十句句子应分别修改为：
                        1. <src>\t中秋国庆双节期间，地方政府应高度看重游客人流，采取多种措施做好引导工作，避免出现踩踏事件的发生。\t</src>
                        ...  
                        10.<src>\t...\t</src>
                """
            },
        ]

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
                                                    messages=self.init_prompt + self.chat_list,
                                                    temperature=0,
                                                    n=1)
            answer = response.choices[0].message['content']
            # 添加历史对话，形成上下文关系
            self.chat_list.append({"role": "assistant", "content": answer})
            self.show_conversation(self.chat_list)
        else:
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                    messages=self.init_prompt + [temp],
                                                    temperature=0,
                                                    n=1)
            answers = [choice.message['content'].strip() for choice in response.choices]
            return answers


chatgpt = ChatGPT()

input_path = "data/gpt/hkht/4000_v2/hkht.4000.v2.train.gpt.input"
output_path = "data/gpt/hkht/4000_v2/hkht.4000.v2.train.gpt3.5.v2.output"

with open(input_path, "r", encoding="utf-8") as f:
    srcs = [[line for line in seq.split("\n")]for seq in f.read().split("\n\n") if seq]

    # 因长度限制，控制每组句子数为n
    n=1
    srcs_split = [srcs[i:i + n] for i in range(0, len(srcs), n)]

    # 容易中断，下次从断点开始
    idx = 0
    retry = 0
    last = datetime.now()
    while True:
        if idx >= len(srcs_split):
        # if idx >= 1:
            break
        try:
            print(f"正在处理{idx}/{len(srcs_split)}" + ("" if retry == 0 else f"，重试{retry}次"), end="\r")
            question = ""
            sentences = srcs_split[idx]
            for seq in sentences:
                noise = False
                specials = []
                error_seq, correct_seq, contents = seq[0], seq[1], seq[2:]

                question += f"<example>\t{correct_seq}\t</example>\n"
                question += f"<mod_example>\t{error_seq}\t</mod_example>\n"

                for content in contents:
                    error_type, src_content, tgt_content = content.split("\t")
                    if error_type == "noop":
                        noise = True
                    elif error_type == "R":
                        question += f"<mod>\t模仿原句修改方式，添加冗余成分“{src_content}”\t</mod>\n"
                    elif error_type == "W":
                        question += f"<mod>\t原句将“{tgt_content}”交换词序变为“{src_content}”，模仿此修改方式交换句子中特定成分\t</mod>\n"
                    elif error_type == "M":
                        question += f"<mod>\t模仿原句修改方式，将“{tgt_content}”表示的成分删除\t</mod>\n"
                    elif error_type == "S":
                        if (abs(len(src_content)-len(tgt_content)) > min(len(src_content), len(tgt_content))) or len(src_content) > 5 or len(tgt_content) > 5:
                            noise = True
                        else:
                            specials.append(tgt_content)
                            question += f"<mod>\t模仿原句修改方式：将“{tgt_content}”替换为“{src_content}”\t</mod>\n"

                if specials:
                    question += f"<special>\t{'、'.join(specials)}\t</special>"

            if not noise:
                # print(question)
                answers = chatgpt.ask(question)[0]
                with open(output_path, "a", encoding="utf-8") as f1:
                    f1.write(answers.strip()+"\n")
                    f1.write("==="+"\n")
        except Exception as e:
            print(e)
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
#     <example>\t在刚刚落幕的伦敦奥运会上，尽管中国的金牌总数跟北京奥运会相比有明显差距，中国体育代表团仍然赢得了全国人民的肯定和赞扬。\t</example>
#     <mod_example>\t在刚刚落幕的伦敦奥运会上，中国的金牌总数尽管跟北京奥运会相比有明显差距，中国体育代表团仍然赢得了全国人民的肯定和赞扬。\t</mod_example>
#     <mod>\t原句将“尽管中国的金牌总数”交换词序变为“中国的金牌总数尽管”，模仿此修改方式交换句子中特定成分。\t</mod>
#     <special>\t无\t</special>
#     """
# )[0])