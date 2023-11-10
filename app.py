from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

# Questions and possible diagnoses (replace with actual data)

df = pd.read_csv("sca_database.csv")
# df['OR']= (df['yes']/df['acs']) / (df['no']/df['no_acs']) #FIXME Wrong

df['ODD_ACS_Exposed'] = (df['exposed_acs'])/(df['exposed_no_acs'])
df['ODD_NOACS_Unexposed'] = (df['total_acs'] - df['exposed_acs']) / (df['total_no_acs'] - df['exposed_no_acs'])
df['OR'] = df['ODD_ACS_Exposed']/df['ODD_NOACS_Unexposed']


df['significant'] = df['p_value']<0.05

order = np.argsort(df['OR'])[::-1]

questions = [df['question'].iloc[i] for i in order if df['p_value'].iloc[i]<0.05]

possible_diagnoses = {
    'YESYESYESYES': 'Angina',
    'YESYESNONO': 'Respiratory Issue',
    'NONONOYES': 'Possible Cardiac Issue',
    'NONONONONO': 'Non-specific Chest Pain'
}

list_symptomns = ""

current_question_index = 0
user_responses = []
current_or = 1
@app.route('/')
def index():
    return render_template('index.html', question=questions[current_question_index])

@app.route('/answer', methods=['POST'])
def answer():
    global current_question_index
    global user_responses
    global current_or
    global list_symptomns


    answer = request.form['answer']
    user_responses.append(answer)
    if answer == 'YES':
        current_or = current_or * df['OR'][df['question'] == questions[current_question_index]].values[0]
        symptomns = questions[current_question_index]
        list_symptomns = list_symptomns+"\n"+symptomns
    print(list_symptomns)
    print(answer,current_or)

    current_question_index += 1
    if current_question_index < len(questions):
        return jsonify({'question': questions[current_question_index],
                        'diagnosis':current_or,
                        'list_symptoms':list_symptomns})
    else:
        print('Finished asking questions')
        diagnosis_key = ''.join(user_responses)
        diagnosis = possible_diagnoses.get(diagnosis_key, 'Unknown Diagnosis')
        return jsonify({'diagnosis': diagnosis})

if __name__ == '__main__':
    app.run(debug=True)
