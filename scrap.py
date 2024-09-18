import csv
import json
from bs4 import BeautifulSoup

def write_csv_batch(filename, data):
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([
            'Questions', 'Type', 'Time Limit', 'Required', 'Page Break', 'Randomize', 'Columns',
            'Minimum Answers', 'Maximum Answers', 'Answer 1', 'Score', 'Answer 2', 'Score',
            'Answer 3', 'Score', 'Answer 4', 'Score', 'Answer 5', 'Score', 'Answer 6', 'Score'
        ])
        writer.writerows(data)

with open('Certified Platform App Builder.html', 'r', encoding='utf-8') as file:
    content = file.read()

soup = BeautifulSoup(content, 'html.parser')
questions = soup.find_all('div', class_='question-body')

batch_size = 60
batch_data = []
file_index = 1

for idx, question in enumerate(questions):
    question_text = question.find('p', class_='card-text').text.strip()
    choices = question.find_all('li', class_='multi-choice-item')
    cleaned_choices = [' '.join(choice.text.split()[1:]).strip() for choice in choices]

    while len(cleaned_choices) < 6:
        cleaned_choices.append('')

    correct_answer_tag = question.find('span', class_='correct-answer')
    correct_answer = correct_answer_tag.text.strip() if correct_answer_tag else None

    most_popular_answer = None
    script_tag = question.find('script', type='application/json')

    if script_tag:
        vote_data = json.loads(script_tag.string)
        if vote_data and 'voted_answers' in vote_data[0]:
            most_popular_answer = vote_data[0]['voted_answers']

    final_answer = most_popular_answer if most_popular_answer else correct_answer
    if correct_answer and most_popular_answer and correct_answer != most_popular_answer:
        question_text += ' (Community and Correct Answer Mismatch)'

    answer_scores = []
    for i, choice in enumerate(cleaned_choices):
        if final_answer and chr(65 + i) in final_answer:  # A=65, B=66, etc.
            answer_scores.append(1)  # Correct
        else:
            answer_scores.append(0)  # Incorrect

    min_answers = len(final_answer) if final_answer else 1
    max_answers = min_answers

    batch_data.append([
        question_text, 'Multiple Choice', 'No', 'Yes', 'No', 'Yes', '2',
        min_answers, max_answers,
        cleaned_choices[0], answer_scores[0],
        cleaned_choices[1], answer_scores[1],
        cleaned_choices[2], answer_scores[2],
        cleaned_choices[3], answer_scores[3],
        cleaned_choices[4], answer_scores[4],
        cleaned_choices[5], answer_scores[5]
    ])

    if (idx + 1) % batch_size == 0 or (idx + 1) == len(questions):
        write_csv_batch(f'questions_output_{file_index}.csv', batch_data)
        file_index += 1
        batch_data = []

print("Data has been exported to multiple CSV files.")
