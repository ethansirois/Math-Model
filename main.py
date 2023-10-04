import os
import openai
from HIDDEN import API_KEY
openai.api_key = API_KEY


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
        os.system('python py.py > out.txt')
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


def provide_answer(problem, code, answer):
    messages = [
        {"role": "system", "content": "You are an elegant mathematician and Python programming expert. You will provide"
                                      " context to the calculated answer by providing a complete sentence containing"
                                      " the calculated answer. YOU WILL NEVER DO ANY CALCULATIONS. You will only use "
                                      "the calculated answer that is provided. If the problem asks to select from a "
                                      "list of choices, state which choice"
                                      " is correct. If the answer does not align with any of the options, respond with"
                                      " what's wrong with the solution and follow this with 'REPEAT'. "},
        {"role": "user", "content": "Here is the problem: " + problem + ". Here is the generated response and code: "
                                    + code + ". Here is the calculated answer: " + answer + "." + '\n'}
    ]
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0
    )
    return completion.choices[0].message["content"]


def clear():
    os.remove('py.py')
    os.remove('out.txt')


def main():
    temp = 0
    still_going = True
    problem = str(input("Please input your question\n"))
    print("\nHappy to help! One moment please.")
    while still_going and temp <= 2:
        sol = solve_with_script(problem, temp)
        code = generate_pure_code(sol)
        result = compute(code)
        repeats = 0
        while result[0] == "ERROR" and repeats <= 4:
            error_msg_w_code = result[1]
            sol = solve_with_script(error_msg_w_code, temp)
            code = generate_pure_code(sol)
            result = compute(code)
            repeats += 1
        if repeats < 5:
            answer = result[1]
            response = provide_answer(problem, sol, answer)
            print("Okay, got it!")
            print(response)
            u2 = str(input("Is this answer sufficient? If not, we'll turn up the temp and hope for the best "
                           "(answer with 'y' or 'n')\n"))
            still_going = u2 == 'n'
            temp += 0.4
            u3 = str(input("want to see the code produced? (answer with 'y' or 'n')\n"))
            if u3 == 'y':
                print(sol)
            clear()
        else:
            still_going = False
            print("sorry, but it just couldn't generate the right code.")


main()
