# main flask app
from flask import Flask
from flask import request
from yabasic.sum import sum_list
from yabasic.sum import sum_list_test

app = Flask(__name__)

# health-check endpoint
@app.route("/", methods=['GET'])
def home():
    return "Hello, World!\n"

# post endpoint to retrieve yabasic function
@app.route("/sum_list", methods=['POST'])
def sum_function():
    data = request.get_data()
    data_list=eval(data)
    return str(sum_list(data_list))+'\n'

# test endpoint
@app.route("/sum_list_test", methods=['POST'])
def sum_function_test():
    data = request.get_data()
    data_list=eval(data)
    return str(sum_list_test(data_list))+'\n'

if __name__ == "__main__":
    # make Flask server publicly available
    app.run(host="0.0.0.0")
