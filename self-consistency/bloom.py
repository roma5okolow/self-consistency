"""Call Bloom-176B model to get predictions"""

import dataclasses
import json
import random
import re


RATIONALE_BATCH = 40
TEMPERATURE = 0.7
INPUT_TRAIN = 'grade-school-math/grade_school_math/data/train.jsonl'
INPUT_TEST = 'grade-school-math/grade_school_math/data/test.jsonl'
OUTPUT_PATH = 'self-consistency/BLOOM-answers/gsm_sc_001.jsonl'

@dataclasses.dataclass
class Example:
	question: str
	answer: str
	thought: str


def train_prompt(lines, size, calculations=False):
	"""
	choose random sample of exaxt size from train dataset to create train_prompt
	"""
	prompt = ''
	inds = random.sample(range(len(lines)), size)
	for ind in inds:
		data = json.loads(lines[ind])
		question = data['question']
		thought = data['answer']
		answer = extract_answer(thought)
		thought = thought.split('###')[0]
		
		if not calculations:
			thought = re.sub(r'<<.+>>', '', thought)
		
		prompt += 'Q: ' + question + '\nA: ' + thought + ' The answer is ' + answer  + '.\n\n'

	return prompt

ANS_RE = re.compile(r"#### (\-?[0-9\.\,]+)")
INVALID_ANS = "[invalid]"

def extract_answer(completion):
    match = ANS_RE.search(completion)
    if match:
        match_str = match.group(1).strip()
        match_str = match_str.replace(",", "")
        return match_str
    else:
        return INVALID_ANS

def main():

	with open(INPUT_TRAIN, 'r') as train:
		lines_train = train.readlines()

	with open(INPUT_TEST, 'r') as test:
		lines_test = test.readlines()

	input_list = []

	for line in lines_test:
		data = json.loads(line)
		question = data['question']

		prompt = train_prompt(lines=lines_train, size=8)
		input_list.append(prompt + 'Q: ' + question.replace('\\n', '\n') + '\nA:')
	
	

if __name__ == '__main__':
	main()