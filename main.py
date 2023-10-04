from answer_generation import *
import jsonlines
import json


def get_data_from_json():
    # test_datapoints will contain tuples of each question and answer pair from the test dataset
    test_datapoints = []
    with jsonlines.open('sanitized_data.jsonl') as f:
        for line in f.iter():
            problem = line["problem"]
            answer = line["boxed_solution"]
            test_datapoints.append((problem, answer))
    return test_datapoints


def generate_answer(problem):
    temp = 0  # adjust temperature to have produce different results if the results are failing
    still_going = True  # will keep going
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
        still_going = repeats < 5
        if repeats < 5:
            answer = result[1]
            temp += 0.4
            clear()
            return answer
        else:
            still_going = False
            return "FAILED TO PRODUCE ANSWER"


def generate_results(test_datapoints):
    results = []
    # for every problem and answer in the testing dataset, generate 5 answers in a list, which will then be the results
    for test_datapoint in test_datapoints:
        answers = []
        for i in range(5):
            answer = generate_answer(test_datapoint[0])
            answers.append(answer)
        results.append({test_datapoint[0] : answers})
    return results


def main():
    test_datapoints = get_data_from_json()
    results = generate_results(test_datapoints)
    with open("results.jsonl", 'w') as f:
        for item in results:
            f.write(json.dumps(item) + "\n")


main()
