from flask import Flask, render_template, request, jsonify, json, send_from_directory
from flask_socketio import SocketIO, emit
import eventlet
import requests
import os
import openai
import pyautogui
import uuid
import re
import time

eventlet.monkey_patch()

pyautogui.PAUSE=1
pyautogui.FAILSAFE = False

openai.api_key = os.getenv("OPENAI_API_KEY")
session_hash = os.getenv("SESSION_HASH")



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

app = Flask(__name__, static_url_path='/assets')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/audio', methods=['POST'])
# @socketio.on("transcribe")
def audio():
    audio_data = request.files.get('audio').read()
    # audio_data = file['audio']
    print('Received audio data')

    # Create a temporary file to write the audio data to
    with open('audio.mp3', 'wb') as f:
        f.write(audio_data)

    # Transcribe the audio using the OpenAI API client
    with open('audio.mp3', 'rb') as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

    # Clean up the temporary file
    os.remove('audio.mp3')

    # emit('transcript_result', f"\"{transcript}\"")

    return transcript

# @app.route('/validate/')
@socketio.on('validate')
def validateTask(task):
    # task = request.args.get('task')
    print(task)
    resp = predict()

    resp =  openai.Completion.create(
        model="text-davinci-003",
        prompt='''Is this task a valid task which can be automated using pyautogui functions, in a step by step manner?\ntask : {taskMessage}\nreply with 0 for true or 1 for false on the first line and the reason on the second line.'''.format(taskMessage=task),
        temperature=0.7
    )

    if '0' in resp['data'][0][-1][1]:
        emit("validation result", {"result": str(resp['data'][0][-1][1]), "response": resp})
        doTask(task)
        print(f"response for {task} is {resp['data'][0][-1][1]}")
        # return jsonify({"result": str(resp['data'][0][-1][1]), "response": resp}), 200
    else:
        # why = predict(f"state the reason why the task:{task}, can't be done ?")
        why = why.json()
        # return jsonify({"result": str(resp['data'][0][-1][1]), "why": why['data'][0][-1][1]}), 200
        emit("validation result", {"result": str(resp['data'][0][-1][1]), "why": why['data'][0][-1][1]})

def screenshot(step_counter, when, retry):
    # set name of screenshot.
    before_screenshot_name = f"step_{step_counter}_{when}_{retry}".replace(' ','_').lower()

    # take screenshot
    before_screen = pyautogui.screenshot()

    # save the screenshot.
    before_screen.save(f"assets/{before_screenshot_name}.png")

    # upload the image to the server
    location = upload(location=f"assets/{before_screenshot_name}.png", name=f"{before_screenshot_name}", type='image/png')

    # steps_performed.append(["upload", f"screenshot uploaded, name={before_screenshot_name}.png, location=assets/{before_screenshot_name}.png"])

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

    # steps_performed.append(["registered with visual_chatgpt", f"{resp}"])

    return resp

# @app.route('/do/')
def doTask(task):
    # task=request.args.get('task')
    task_finished = False
    step_counter = 0
    steps_performed = []
    started_at = time.time()
    timeout = started_at + 300

    steps_response = predict(f"you are going to play a game I invented,\nIn this game, I don't know how to operate a computer, and you have to generate instructions to complete the task:'{task}',\nremember your reply is always an array of strings or else I lose the game,\nreply with an array of strings, containing the steps to undertake to complete the task:{task}. try to use shortcut key combos.")

    emit("steps", steps_response['data'][0][-1][1])

    purify_steps_response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"string = \"{steps_response['data'][0][-1][1]}\"\nlist steps as an array",
        temperature=0.05
    )

    if eval(purify_steps_response['choices'][0]['text']):
        purify_steps_response = eval(purify_steps_response['choices'][0]['text'])


    while not task_finished and timeout > time.time():
        step = purify_steps_response[step_counter]
        # image has been uploaded and registered.
        img_name = screenshot(step_counter, 'before', retry)

        emit("images", img_name)

        resp = predict(f"image/{img_name} screenshot of screen. Is this step necessary ? to achieve game task:{task}. if necessary say 'necessary'")
        resp = resp['data'][0][-1][1]

        if not ('necessary' in resp):
            print(resp)
            emit('steps', f"Skipping this step because {resp}")
            step_counter += 1
            time.sleep(1)
            continue

        resp = ''
        if retry > 0:
            # ask for instruction providing image name, and task, step
            resp = predict(f"Retrying this step for the {retry} time, image/{img_name} screenshot of current screen, now for this instructional step: {step}, generate a valid pyautogui function with inputs (like this but not this \"eval_func: pyautogui.press('enter')\"). your reply will be used executed using an eval() function. your reply should start with 'eval_func: '.")
        else:
            resp = predict(f"image/{img_name} screenshot of current screen, now for this instructional step: {step}, generate a valid pyautogui function with inputs (like this but not this \"eval_func: pyautogui.press('enter')\"). your reply will be used executed using an eval() function. your reply should start with 'eval_func: '.")

        resp = resp['data'][0][-1][1]

        emit("steps", resp)

        # regular expression pattern to match pyautogui function calls
        pattern = r'pyautogui\.\w+\(.*\)'

        # find all matches of the pattern in the string
        eval_func = re.search(pattern, resp).group()

        # remove unwanted characters.
        eval_func = eval_func.replace("‘", "\"").replace("’", "\"").replace("\n", "")

        steps_performed.append(["eval_func", f"{resp}"])
        # evaluate the recieved function
        eval(eval_func)

        print(resp)

        time.sleep(0.3)

        img_name = screenshot(step_counter, 'after', retry)

        task_done = predict(f"image/{img_name} screenshot, has the automation been successfully performed, for this instructional step: {step} ? If yes say '0', otherwise '1'" )

        task_done = task_done['data'][0][-1][1]

        if '1' in task_done:
            if retry < 3 :
                retry += 1
            else:
                emit("steps", f"this task step has exceeded the retry limit.")
                emit("task finished")
                task_finished = True
            continue
        elif step_counter < len(purify_steps_response) - 1:
            step_counter += 1
            retry = 0
        else:
          task_finished = True

    emit("task finished")
    return 0

@socketio.on('msg_event')
def handle_message(message):
    print(f'received message: {message}')
    emit("res_event", "Ok, from flask server.")

if __name__ == '__main__':
    socketio.run(app)
    # app.run(debug=True)
