# -*- utf-8 -*- 
#2025/12/7 菜小包
# 模仿N-gram模型计算句子概率的过程
import collections

#给定一个实例语料库
corpus = "datawhale agent learns datawhale agent works"
tokens = corpus.split()
n = len(tokens)
# print(tokens)
# print(f"语料库总词数: {n}")

# 1.首秀计算datawhale的概率P(datawhale)
count_datawhale = tokens.count('datawhale')
p_datawhale = count_datawhale/n 
print(f"第一步: P(datawhale) = {count_datawhale}/{n} = {p_datawhale:.3f}")

#2.计算P(agent|datawhale)
bigrams = zip(tokens,tokens[1:])
bigram_counts = collections.Counter(bigrams)
count_datawhale_agent = bigram_counts[('datawhale','agent')]
# print(count_datawhale_agent)
p_agent_given_datawhale = count_datawhale_agent/count_datawhale
print(f"第二步: P(agent|datawhale) = {count_datawhale_agent}/{count_datawhale} = {p_agent_given_datawhale:.3f}")

#3.计算P(learns|agent)
count_agent_learns = bigram_counts[('agent','learns')]
count_agent = tokens.count('agent')
p_learns_given_agent = count_agent_learns/count_agent
print(f"第三步: P(learns|agent) = {count_agent_learns}/{count_agent} = {p_learns_given_agent:.3f}")

#最后，三者相乘
p_sentence = p_datawhale * p_agent_given_datawhale * p_learns_given_agent
print(f"最后: P('datawhale agent learns') ≈ {p_datawhale:.3f} * {p_agent_given_datawhale:.3f} * {p_learns_given_agent:.3f} = {p_sentence:.3f}")