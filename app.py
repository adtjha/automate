from flask import Flask, render_template, request, jsonify, json
import requests
import os
import openai
import pyautogui
import uuid
import re
import time

openai.api_key = os.getenv("OPENAI_API_KEY")
session_hash = os.getenv("SESSION_HASH")

# taskDetails = {
#     "id": "0",
#     "task": "",
#     "is_finished": "",
#     "started_at": "",
#     "steps": [],
# }

def predict(input):
    # if not (isinstance(input, str)):
    #     return False

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

app = Flask(__name__)

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
    resp = predict('''Is this task a valid task which can be achieved using pyautogui functions, in a step by step manner?\ntask : {taskMessage}\njust reply with 0 for true or 1 for false'''.format(taskMessage=task))
    if '0' in resp['data'][0][-1][1]:
        # doTask(task_finished=False, task=task)
        print(f"response for {task} is {resp['data'][0][-1][1]}")
        return jsonify({"result": str(resp['data'][0][-1][1])}), 200
    else:
        why = predict(f"state the reason why the task:{task}, can't be done ?")
        why = why.json()
        return jsonify({"result": str(resp['data'][0][-1][1]), "why": why['data'][0][-1][1]}), 200

@app.route('/do/')
def doTask():
    task=request.args.get('task')
    task_finished = False
    step_counter = 0
    steps_performed = []
    started_at = time.time()
    timeout = started_at + 300

    steps_response = predict(f"you are going to play a game I invented,\nIn this game, I don't know how to operate a computer, and you have to generate instructions to complete the task:'{task}',\nremember answer by AI is always an array of strings or else I lose the game,\nHuman:what are the steps involved in doing this task : 'Open chrome and tweet something',\nAI: ['opening chrome', 'opening twitter in a chrometab', 'generate a tweet', 'type in the tweet', 'click the tweet button']\nHuman:what are the steps involved in doing this task : 'Calculate 2+2 in calculator',\nAI: ['opening calculator', 'clicking on number 2', 'clicking on the + button', 'clicking on number 2', 'clicking on the = button', 'reading the result as 4']\nreply with an array of strings, containing the steps to undertake to complete the task.")

    # purify_steps_response = predict(f"remove everything including conjunctions and interjections from '{steps_response['data'][0][-1][1]}' and leaving only steps separated by a comma.")
    purify_steps_response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"string = \"{steps_response['data'][0][-1][1]}\"\nlist steps as an array",
        temperature=0.05,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    if eval(purify_steps_response['choices'][0]['text']):
        purify_steps_response = eval(purify_steps_response['choices'][0]['text'])

    # steps = purify_steps_response['data'][0][-1][1].split(',')

    # each_step_response = openai.Completion.create(
    #     model="text-davinci-003",
    #     prompt=f"now for each instructional step, generate an array of three strings, \n'task_finished': True if the task: {task} has been completed otherwise False, 'purpose': description of the purpose of the next step, 'eval_func':a string with a valid pyautogui function to perform the next step, reply should start with 'The steps to complete the task: '",
    #     temperature=0.05,
    #     max_tokens=256,
    #     top_p=1,
    #     frequency_penalty=0,
    #     presence_penalty=0
    # )

    # each_step_response = predict(f"now for each instructional step, generate an array of three strings, \n'task_finished': True if the task: {task} has been completed otherwise False, 'purpose': description of the purpose of the next step, 'eval_func':a string with a valid pyautogui function to perform the next step, reply should start with 'The steps to complete the task: '")

    # purify_each_step_response = predict(f"'{each_step_response['data'][0][-1][1]}'\nconvert this string to array of objects, where each object is an instructional step.")
    for step in purify_steps_response:
        # set name of screenshot.
        before_screenshot_name = f"step_{step_counter}".replace(' ','_').lower()

        # take screenshot
        before_screen = pyautogui.screenshot()

        # save the screenshot.
        before_screen.save(f"assets/{before_screenshot_name}.png")

        # upload the image to the server
        location = upload(location=f"assets/{before_screenshot_name}.png", name=f"{before_screenshot_name}", type='image/png')

        steps_performed.append(["upload", f"screenshot uploaded, name={before_screenshot_name}.png, location=assets/{before_screenshot_name}.png"])

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

        print(resp)
        # image has been uploaded and registered.
        img_name = resp

        steps_performed.append(["registered with visual_chatgpt", f"{resp}"])

        # ask for instruction providing image name, and task, step
        # resp = predict(f"image/{img_name} what is the next step ?")
        resp = predict(f"image/{img_name} screenshot where automation is being performed,  now for each instructional step: {step}, generate an 'eval_func':a string with a valid pyautogui function to perform the next step, reply should start with 'eval_func: '")

        eval_func = resp['data'][0][-1][1].split('eval_func:')[1]

        steps_performed.append(["eval_func", f"{eval_func}"])
        # evaluate the recieved function
        # eval(eval_func)
        print(eval_func)

    return jsonify({
            "task_finished": True,
            "steps_response": steps_response['data'][0][-1][1],
            "purify_steps_response": purify_steps_response,
            # "steps": steps,
            # "each_step": each_step_response['choices'][0]['text'],
            # "purify_each_step": purify_each_step_response['data'][0][-1][1],
            # "most_purified": array,
            "steps_performed": steps_performed,
            "started_at": started_at,
            "timeout": timeout,
            "now": time.time()
        }), 200




    # while not task_finished:


        # resp_string = predict(f"remove everything including conjunctions and interjections from '{resp['data'][0][-1][1]}' and leaving only steps separated by a comma.")

        # resp_obj = json.loads(re.search(r"\{.*\}", resp_string))

        # steps_performed.append([f"step_{step_counter}", resp_string])
        # print(resp_string)

        # # if time.time() > timeout:
        # if step_counter > len(steps) - 2:
        #     break
        # else:
        #     step_counter += 1

        # evaluate the recieved function
        # eval(eval_func)

    # return jsonify({"task_finished": True, "steps": steps, "performed": steps_performed, "started_at": started_at, "timeout": timeout, "now": time.time()}), 200

if __name__ == '__main__':
    app.run(debug=True)


# list stages(in terms of pyautogui functions) in order to do the task in the shortest possible way,
# for each step, generate a (pyautogui function call) as a string, which can be compiled using eval,
# compile that eval using eval, and generate a screenshot,
# upload screenshot and ask if the step was done, say '0', else '1',
# if its '0', ask for next step,
