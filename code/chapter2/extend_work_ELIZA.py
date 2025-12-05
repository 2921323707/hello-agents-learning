import re
import random

# 定义规则库：模式(正则表达式) -> 响应模板列表
rules = {
    r'I need (.*)': [
        "Why do you need {0}?",
        "Would it really help you to get {0}?",
        "Are you sure you need {0}?"
    ],
    r'Why don\'t you (.*)\?': [
        "Do you really think I don't {0}?",
        "Perhaps eventually I will {0}.",
        "Do you really want me to {0}?"
    ],
    r'Why can\'t I (.*)\?': [
        "Do you think you should be able to {0}?",
        "If you could {0}, what would you do?",
        "I don't know -- why can't you {0}?"
    ],
    r'I am (.*)': [
        "Did you come to me because you are {0}?",
        "How long have you been {0}?",
        "How do you feel about being {0}?"
    ],
    r'.* mother .*': [
        "Tell me more about your mother.",
        "What was your relationship with your mother like?",
        "How do you feel about your mother?"
    ],
    r'.* father .*': [
        "Tell me more about your father.",
        "How did your father make you feel?",
        "What has your father taught you?"
    ],
    # 工作相关规则
    r'.* work .*': [
        "What do you do for a living?",
        "Why do you work?",
        "What do you do for fun?"
    ],
    # 爱好相关规则
    r'.* hobby .*': [
        "What are your hobbies?",
        "Do you have any hobbies?",
        "What do you enjoy doing in your free time?"
    ],
    r'.*': [
        "Please tell me more.",
        "Let's change focus a bit... Tell me about your family.",
        "Can you elaborate on that?"
    ]
}

# 会话内简单记忆，用于记住姓名、年龄、职业等关键信息（仅内存，会话结束即忘）
memory = {
    "name": None,
    "age": None,
    "job": None
}

# 定义代词转换规则
pronoun_swap = {
    "i": "you", "you": "i", "me": "you", "my": "your",
    "am": "are", "are": "am", "was": "were", "i'd": "you would",
    "i've": "you have", "i'll": "you will", "yours": "mine",
    "mine": "yours"
}

def swap_pronouns(phrase):
    """
    对输入短语中的代词进行第一/第二人称转换
    """
    words = phrase.lower().split()
    swapped_words = [pronoun_swap.get(word, word) for word in words]
    return " ".join(swapped_words)


def extract_info(user_input):
    """
    从用户输入中提取简单信息并保存到内存：name/age/job
    支持常见的英文表达，例如："my name is Alice", "I'm 30 years old", "I work as a teacher"
    """
    ui = user_input.strip()
    # 提取姓名
    name_patterns = [r"\bmy name is ([A-Za-z][A-Za-z '\\-]+)", r"\bcall me ([A-Za-z][A-Za-z '\\-]+)", r"\bi am called ([A-Za-z][A-Za-z '\\-]+)"]
    for p in name_patterns:
        m = re.search(p, ui, re.IGNORECASE)
        if m:
            name = m.group(1).strip()
            # 保持首字母大写
            memory['name'] = name.title()
            break

    # 提取年龄（数字）
    age_match = re.search(r"\b(?:i am|i'm)\s+(\d{1,3})(?:\s*years? old)?\b", ui, re.IGNORECASE)
    if age_match:
        memory['age'] = age_match.group(1)

    # 提取职业
    job_patterns = [r"\b(?:i am a|i'm a|i am an|i'm an|i work as a|i work as an)\s+([A-Za-z0-9_ '\\-]+)", r"\bi do work as a\s+([A-Za-z0-9_ '\\-]+)"]
    for p in job_patterns:
        m = re.search(p, ui, re.IGNORECASE)
        if m:
            memory['job'] = m.group(1).strip().lower()
            break


def recall_response(user_input):
    """
    如果用户在询问已记忆的信息，返回相应的回复字符串；否则返回 None
    支持：What's my name? How old am I? What's my job?
    """
    ui = user_input.lower()
    # 询问姓名
    if re.search(r"\bwhat(?:'s| is) my name\b|do you know my name\b|who am i\b", ui):
        if memory.get('name'):
            return f"You told me your name is {memory['name']}."
        else:
            return "I don't think you've told me your name yet. What should I call you?"

    # 询问年龄
    if re.search(r"how old am i\b|what(?:'s| is) my age\b", ui):
        if memory.get('age'):
            return f"You said you are {memory['age']} years old."
        else:
            return "I don't know your age yet. How old are you?"

    # 询问职业
    if re.search(r"what(?:'s| is) my job\b|what do i do for a living\b|what do i do\b", ui):
        if memory.get('job'):
            return f"You mentioned you work as {memory['job']}."
        else:
            return "I don't know your job yet. What do you do for work?"


def respond(user_input):
    """
    根据规则库生成响应
    """
    # 先从输入中提取并记忆可能的信息
    extract_info(user_input)

    # 检查用户是否在询问已记忆的信息
    recall = recall_response(user_input)
    if recall:
        return recall
    for pattern, responses in rules.items():
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            # 捕获匹配到的部分
            captured_group = match.group(1) if match.groups() else ''

            # 进行代词转换
            swapped_group = swap_pronouns(captured_group)
            # 从模板中随机选择一个并格式化
            response = random.choice(responses).format(swapped_group)
            return response
    # 如果没有匹配任何特定规则，使用最后的通配符规则
    return random.choice(rules[r'.*'])

# 主聊天循环
if __name__ == '__main__':
    print("Therapist: Hello! How can I help you today?")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Therapist: Goodbye. It was nice talking to you.")
            break
        response = respond(user_input)
        print(f"Therapist: {response}")





#####
#与GPT的差异
# ELIZA是检测到用户输入的模式进行匹配，然后基于预定义的规则生成响应。
# 与GPT不同，ELIZA的响应是基于规则库的，而不是基于训练数据的。

#####
#为什么基于规则的方法在处理开放域对话时会遇到"组合爆炸"问题并且难以扩展维护？能否使用数学的方法来说明？
 
# 说明：组合爆炸（简明注释）
# - 核心原因：规则系统需要为不同的“意图 / 话题 / 修饰 / 上下文”组合编写规则，
#   随着这些维度数量增加，规则数按乘积或指数级增长，难以维护。
#
# - 简单数学模型：设有 k 个独立特性（feature），第 i 个特性有 a_i 个可能取值，
#   则需要的规则数约为 R = Π_{i=1..k} a_i。
#   若每个特性取值相同为 a，则 R = a^k（指数增长）。
#
# - 特殊情形：若有 n 个二值修饰（有/无），则组合因子为 2^n；若需要考虑长度为 h 的
#   历史上下文、每步有 s 个状态，则历史组合数量约为 s^h，随 h 指数增长。
#
# - 与语言空间的关系：词汇量 V、句长 L 时，可能的句子数量近似为 V^L，说明用规则
#   覆盖所有表达是不现实的。
#
# - 匹配成本：若有 R 条规则、每条匹配平均代价为 O(L)，则一次匹配的时间复杂度约为
#   O(R * L)，规则越多，响应匹配越慢，且需要处理规则冲突与优先级。
#
# - 工程缓解建议：
#   - 槽位填充(slot-filling) + NLU：把理解问题拆成意图识别与槽位抽取，避免枚举组合。
#   - 层次化/模板化规则：先粗匹配后精细化，使用通用模板替代大量近似规则。
#   - 混合方法：规则用于关键控制点，使用统计/神经模型做理解与泛化。
#   - 自动化发现：用对话日志自动发现未覆盖模式，生成样本或待添加规则，减轻人工维护。
#
# 小结：规则系统在维度或上下文长度增加时会出现指数级或乘积级的规则增长（例如 a^k、2^n、s^h），
# 因此在开放域场景下可扩展性差。采用槽位化、模板化或引入 ML 模型的混合方案通常能有效缓解该问题。
