from answer_generation import *


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
            print("Okay, got it!")
            print(answer)
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
