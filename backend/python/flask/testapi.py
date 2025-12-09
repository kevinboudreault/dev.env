from flask import Flask, render_template, jsonify
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/hi')
def hello():
    return 'Hi you.'

@app.route('/items')
def items():
    sub_lorem = [{ 'a': 'ipsum', 'b': 'dolor'},
                { 'a': 'ut', 'b': 'prespiciatis'}]

    a_list = ['Prehistory','Antiquity', 'Middle Ages', 'Modern', 'Contemporary']
    b_list = ['fr', 'en', sub_lorem]
    return jsonify(Categories=list_of_fruits, Translations=b_list)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')