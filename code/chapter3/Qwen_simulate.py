import torch 
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "Qwen/Qwen1.5-0.5B-Chat"

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

#加载分词器
tokenizer = AutoTokenizer.from_pretrained(
    model_id,
    trust_remote_code=True
    )

#加载模型，并将其移动到指定设备
model = AutoModelForCausalLM.from_pretrained(model_id).to(device)

print("模型和分词器加载完成！")

messages = [
    {"role":"system","content":"You are a helpful assistant."},
    {"role":"user","content":"你好，请介绍你自己。"}
]

#使用分词器的模板格式化输入
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

#编码输入文本
model_inputs = tokenizer([text], return_tensors="pt").to(device)

print("编码后的输入文本:")
print(model_inputs)

#使用模型生成回答
# max_new_tokens 控制了模型最多能生成多少个新的Token
generated_ids = model.generate(
    model_inputs.input_ids, #identifiers
    max_new_tokens=512
)

generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids) #同时处理多个输入
]

response = tokenizer.batch_decode(generated_ids,skip_special_tokens=True)[0]

print("\n模型的回答:")
print(response)