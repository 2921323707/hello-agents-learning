# -*- coding: utf-8 -*-
#2025/12/3 Hello-Agent 2.2.3 ELIZA
import re 
import random 

# 定义ELIZA规则库 ：模式(正则表达式) -> 响应模板列表
rules = {
    r'I need (.*)':[
        "Why do you need {0} ?",
        "Would it really help you to get {0} ?",
        "Are you sure you need {0} ?"
    ],
    r'Why don\'t you (.*) \?':[
        "Do you really think I don't {0} ?",
        "Perhaps eventually I will {0} .",
        "Do you really want me to {0} ?"
    ],
    r'Why can\'t I (.*) \?':[
        "Do you think you should be able to {0} ?",
        "If you could {0} , what would you do ?",
        "I don't know -- why can't you {0} ?",
        "Have you really tried ?"
    ],
    r'Are you (.*) \?':[
        "Why does it matter whether I am {0} ?",
        "Would you prefer it if I were not {0} ?",
        "Perhaps you believe I am {0} .",
        "I may be {0} -- what do you think ?"
    ],
    r'I am (.*)':[
        "Did you come to me because you are {0} ?",
        "How long have you been {0} ?",
        "How do you feel about being {0} ?"
    ],
    r'.*':[
        "Please tell me more.",
        "Let's change focus a bit... Tell me about your family.",
        "Can you elaborate on that?"
    ]
}

#定义代词转换规则
pronoun_swap = {
    "i": "you", "you": "I", "me": "you", "my": "your",
    "your": "my", "yours": "mine", "mine": "yours"
}

def swap_pronouns(phrase):
    """
    对输入短语中的代词进行第一/第二人称转换
    """
    words = phrase.lower().split()
    swapped_words = [pronoun_swap.get(word, word) for word in words]
    return " ".join(swapped_words)

def respond(user_input):
    """
    根据用户输入生成ELIZA的响应
    """
    for pattern, responses in rules.items():
        match = re.match(pattern, user_input, re.IGNORECASE)
        if match:
            response_template = random.choice(responses)
            captured_groups = match.groups()
            swapped_groups = [swap_pronouns(group) for group in captured_groups]
            return response_template.format(*swapped_groups)
    return random.choice(rules[r'.*'])

def main():
    """
    主函数，用于与用户交互
    """
    print("Hello! I am ELIZA. How can I help you today?")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        response = respond(user_input)
        print("ELIZA:", response)

if __name__ == "__main__":
    main()