from flask import Flask, render_template, request, jsonify, json, send_from_directory
from flask_socketio import SocketIO, emit
import requests
import os
import openai
import pyautogui
import uuid
import re
import time

pyautogui.PAUSE=1
pyautogui.FAILSAFE = False

openai.api_key = os.getenv("OPENAI_API_KEY")
session_hash = os.getenv("SESSION_HASH")

sid = ''

def predict(input):
    url = "http://127.0.0.1:7868/run/predict/"

    payload = json.dumps({
    "fn_index": 0,
    "data": [
        f"DO NOT GENERATE AN IMAGE. {input}",
        None
    ],
    "session_hash": session_hash
    })
    headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Host': '127.0.0.1:7868',
    'Origin': 'http://127.0.0.1:7868',
    'Referer': 'http://127.0.0.1:7868/?',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    payload_1 = json.dumps({
    "fn_index": 1,
    "data": [],
    "session_hash": session_hash
    })

    response_1 = requests.request("POST", url, headers=headers, data=payload_1)

    print(response_1.status_code)

    return response.json()

def upload(location, name, type):
    url = "http://127.0.0.1:7868/upload"

    boundary = uuid.uuid4().hex
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'multipart/form-data; boundary=' + boundary,
        'Host': '127.0.0.1:7868',
        'Origin': 'http://127.0.0.1:7868',
        'Referer': 'http://127.0.0.1:7868/?'
    }

    with open(location, 'rb') as f:
        files = {
            'files': (name, f, type),
        }
        data = b''
        for name, (filename, file, content_type) in files.items():
            data += b'--' + boundary.encode('ascii') + b'\r\n'
            data += f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode('utf-8')
            data += f'Content-Type: {content_type}\r\n\r\n'.encode('utf-8')
            data += file.read() + b'\r\n'

        data += b'--' + boundary.encode('ascii') + b'--\r\n'

    response = requests.post(url, headers=headers, data=data)

    return response.json()

def register(input):
    url = "http://127.0.0.1:7868/run/predict/"

    payload = json.dumps({
    "fn_index": 2,
    "data": [
        input,
        None,
        ""
    ],
    "session_hash": session_hash
    })
    headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Host': '127.0.0.1:7868',
    'Origin': 'http://127.0.0.1:7868',
    'Referer': 'http://127.0.0.1:7868/?',
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    response = response.json()

    response = response['data'][0][-1][0]

    print(response)

    pattern = r'image\\([\w\d]+\.(?:png|jpg|jpeg|gif))'

    match = re.search(pattern, response)
    if match:
        return match.group(1)
    else:
        return False

app = Flask(__name__, static_url_path='/assets/', static_folder="assets/", template_folder="templates")
# app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/audio', methods=['POST'])
def audio():
    audio_data = request.files.get('audio').read()
    print('Received audio data')

    # Create a temporary file to write the audio data to
    with open('audio.mp3', 'wb') as f:
        f.write(audio_data)

    # Transcribe the audio using the OpenAI API client
    with open('audio.mp3', 'rb') as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

    # Clean up the temporary file
    os.remove('audio.mp3')

    return transcript

@app.route('/validate/')
def validateTask():
    task = request.args.get('task')
    print(task)

    resp =  openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Is this task a valid task which can be automated using pyautogui functions, in a step by step manner?\ntask : '{task}'\nreply with 0 for true or 1 for false on the first line and the reason on the second line.",
        temperature=0.05
    )

    resp = resp['choices'][0]['text']

    if '0' in resp:
        doTask(task)
        print(f"response for {task} is {resp}")
        emit('steps', "Generating steps to complete task.", broadcast=True, namespace="/")
        return jsonify({"result": str(resp)}), 200
    else:
        # why = predict(f"state the reason why the task:{task}, can't be done ?")
        why = why.json()
        emit('steps', "Generating steps to complete task.", broadcast=True, namespace="/")
        return jsonify({"result": str(resp)}), 200

def screenshot(step_counter, when, retry):
    # set name of screenshot.
    before_screenshot_name = f"step_{step_counter}_{when}_{retry}".replace(' ','_').lower()

    # take screenshot
    before_screen = pyautogui.screenshot()

    # save the screenshot.
    before_screen.save(f"assets/{before_screenshot_name}.png")

    # upload the image to the server
    location = upload(location=f"assets/{before_screenshot_name}.png", name=f"{before_screenshot_name}", type='image/png')

    # image meta data along with location and size, for registering the image.
    img = {
            "name": location[0],
            "size": int(before_screen.size[0]*before_screen.size[1]),
            "data": "",
            "blob": {},
            "orig_name": f"{before_screenshot_name}.png",
            "is_file": True
        }
    resp =  register(img)

    return resp, before_screenshot_name

# @app.route('/do/')
def doTask(task):
    # task=request.args.get('task')
    task_finished = False
    step_counter = 0
    steps_performed = []
    started_at = time.time()
    timeout = started_at + 300

    steps_response = predict(f"Generate instructions to complete the task '{task}' without generating an image. Your reply should be an array of strings and include shortcut key combos. Avoid providing alternatives and remember that I don't know how to operate a computer.")
    steps_response = steps_response['data'][0][-1][1].replace("‘", "\"").replace("’", "\"").replace("\n", "")

    emit("steps", str(steps_response), broadcast=True, namespace="/")

    purify_steps_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system", "content": "You are a helpful assistant. You are going to assit me to operate a computer. Remember to either escape the double quotes inside the string using a backslash (\"), or use single quotes to delimit the inner strings."},
            {"role":"user", "content": "The steps to complete the task: Open Chrome and search about gandhi. are as follows:<br>\n<br>\n1. task_finished: False, purpose: open Chrome, eval_func: pyautogui.hotkey(‘win’,‘r’)<br>\n2. task_finished: False, purpose: type in ‘chrome’ in the search bar, eval_func: pyautogui.typewrite(‘chrome’)<br>\n3. task_finished: False, purpose: press enter to open Chrome, eval_func: pyautogui.press(‘enter’)<br>\n4. task_finished: False, purpose: type in ‘gandhi’ in the search bar, eval_func: pyautogui.typewrite(‘gandhi’)<br>\n5. task_finished: True, purpose: press enter to search for ‘gandhi’, eval_func: pyautogui.press(‘enter’)<br>\n<br>\nThese steps can be accessed in the format steps[0][‘task_finished’], steps[0][‘purpose’], steps[0][‘eval_func’]."},
            {"role":"assistant", "content": "[\"open Chrome\", \"type in 'chrome' in the search bar\", \"press enter to open Chrome\", \"type in 'gandhi' in the search bar\", \"press enter to search for 'gandhi'\"]"},
            {"role":"user", "content": f"string = \"{steps_response}\"\nlist steps in the form of a single array, where each value is an instructional step to do a single operation, remove any alternatives."},
        ]
    )

    purify_steps_response = purify_steps_response['choices'][0]['message']['content']
    print(purify_steps_response)

    start_index = purify_steps_response.find('[')
    end_index = purify_steps_response.find(']')
    if start_index != -1 and end_index != -1:
        purify_steps_response = purify_steps_response[start_index:end_index+1]

    purify_steps_response = json.loads(purify_steps_response)

    # pyautogui.hotkey('win', 'd')


    retry = 0
    while not task_finished:
        step = purify_steps_response[step_counter]
        # image has been uploaded and registered.
        img_name, before = screenshot(step_counter, 'before', retry)

        emit("images", f'{before}|screenshot taken before step:{step}', broadcast=True, namespace="/")

        resp = predict(f"image/{img_name} screenshot of screen. Is this step required ? to complete the game task:{task}. if required say 'required'")
        resp = resp['data'][0][-1][1]

        if not ('required' in resp):
            print(resp)
            emit('steps', f"Skipping this step because {resp}", broadcast=True, namespace="/")
            step_counter += 1
            # time.sleep(1)
            continue

        resp = ''
        if retry > 0:
            # ask for instruction providing image name, and task, step
            resp = predict(f"Retrying this step for the {retry} time, image/{img_name} screenshot of current screen, now for this instructional step: {step}, generate a valid pyautogui function with inputs (like this but not this \"eval_func: pyautogui.press('enter')\"). your reply will be used executed using an eval() function. your reply should start with 'eval_func: '.")
        else:
            resp = predict(f"image/{img_name} screenshot of current screen, now for this instructional step: {step}, generate all possible valid pyautogui function with inputs (like this but not this \"eval_func: \"pyautogui.typewrite('chrome', interval=0.25);\npyautogui.press('enter')\")\". your reply will be used executed using an eval() function. your reply should start with 'eval_func: '.")

        resp = resp['data'][0][-1][1]

        emit("steps", resp, json=True, broadcast=True, namespace="/")

        # regular expression pattern to match pyautogui function calls
        pattern = r'pyautogui\.\w+\(.*\)'

        # find all matches of the pattern in the string
        eval_func = re.search(pattern, resp).group()

        # remove unwanted characters.
        eval_func = eval_func.replace("“", "\"").replace("‘", "\'").replace("”", "\"").replace("’", "\'").replace("\n", "")

        steps_performed.append(["eval_func", f"{resp}"])
        # evaluate the recieved function
        eval(eval_func)

        print(resp)

        # time.sleep(0.3)

        img_name, before = screenshot(step_counter, 'after', retry)

        emit("images", f'{before}|screenshot taken after step:{step}', broadcast=True, namespace="/")

        task_done = predict(f"Has the step \"{step}\" been successfully automated using the pyautogui function {eval_func}, resulting in the expected screen shown in the image: images/{img_name}? say '0' for yes, '1' for no" )

        task_done = task_done['data'][0][-1][1]

        if '1' in task_done:
            if retry < 3 :
                retry += 1
            else:
                emit("steps", f"this task step has exceeded the retry limit.", broadcast=True, namespace="/")
                emit("task finished", broadcast=True, namespace="/")
                task_finished = True
            continue
        elif step_counter < len(purify_steps_response) - 1:
        # if step_counter < len(purify_steps_response) - 1:
            step_counter += 1
            retry = 0
        else:
          task_finished = True

    emit("task finished", broadcast=True, namespace="/")
    return 0

@socketio.on('msg_event')
def handle_message(message):
    print(f'received message: {message}')
    sid = request.sid
    emit("res_event", "Ok, from flask server.", broadcast=True, namespace="/")
    emit("steps", "Hello, there.\nRecord your task, and let me do the rest.", broadcast=True, namespace='/')

@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print(request.event["message"])
    return 0

@socketio.on_error('/chat') # handles the '/chat' namespace
def error_handler_chat(e):
    print(request.event["message"])
    return 0

@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    print(request.event["message"])
    return 0

if __name__ == '__main__':
    socketio.run(app)
    # app.run(debug=True)
