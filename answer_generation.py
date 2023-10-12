import openai
import os
openai.api_key = os.getenv("OPENAI_API_KEY")


def solve_with_script(problem, temp):
    messages = [
        {"role": "system", "content": "You are an elegant mathematician who is incredible at Python. The user can only "
                                      "read Python code blocks, so you must answer their problem by creating a Python"
                                      "code block by encasing it in triple backticks, e.g., ```\ncode goes here\n```. "
                                      "You comment each line of code to explain your work using '#'. You first import "
                                      "'os' and "
                                      "'importlib.util'. Before importing a package, use "
                                      "'importlib.util.find_spec({insert package name here})' to see if the package"
                                      " is installed already. If the package needs to be installed, use "
                                      "'os.system('pip install {insert package name}')'. You will store the answer "
                                      "in a variable"
                                      " named 'answer', and your last line of the code block will be 'print(answer)'."},
        {"role": "user", "content": "What's a Python script that can correctly solve the following problem: " +
                                    problem + '\n'}
    ]
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=temp
    )
    return completion.choices[0].message["content"]


def generate_pure_code(code):
    split_up = code.splitlines()
    in_block = False
    code_blocks = []
    start_block = -1
    for i in range(len(split_up)):
        if "```" in split_up[i]:
            if in_block:
                code_blocks.append((start_block, i))
            else:
                start_block = i
            in_block = not in_block
    pure_code = ""
    if len(code_blocks) == 0:
        pure_code = code
    elif start_block == -1:
        return 'FAILURE'
    for block in code_blocks:
        for i in range(block[0] + 1, block[1]):
            pure_code += split_up[i] + '\n'
    return pure_code


def compute(code):
    pure_code = generate_pure_code(code)
    if pure_code == 'FAILURE':
        return "FAILURE", "something went wrong when getting the code block"
    with open('py.py', 'w') as fp:
        fp.write(pure_code)
    try:
        os.system('py py.py > out.txt')
        f = open('out.txt', 'r')
        content = f.read()
        if len(content) == 0:
            print("failure bc out.txt is empty")
            return "EMPTY", "the code failed"
        else:
            lines = content.splitlines()
            answer = content
            return "SUCCESS", answer
    except Exception as error:
        wrong = "An error has occurred when executing the following code. Here is the error: " + str(error) + ". Here is" \
                    " the code: \n" + pure_code
        return "ERROR", wrong


def clear():
    os.remove('py.py')
    os.remove('out.txt')