1. Record a Task
2. Transcribe the recording
3. verify if the transcription is a valid task, that can be done using pyautogui,
4. find out the steps involved using openai,
5. start endless loop, for completeing the task,
   1. take screenshot of the screen,
   2. pass it on to visual_chatgpt, and ask where to (click)/(type)/(hotkey) next related to task-step,
   3. do that using pyautogui,
   4. send screenshot to visual_chatgpt to verify if task done successfully,
   5. if yes, proceed to next task step,
   6. if no, check if we need user details to input,

How to access visual_chatgpt,

What can be done,

1. generate an image (took 30 mins)
2. reply to question/statement (takes ~8 seconds)
3. description about an uploaded image (takes ~8 seconds)
   a. upload an image,
   b. register image with visual_chatgpt,
   c. reply to questions related to image,

/run/predict -> 1, 2, 3b, 3c
/upload -> 3a

all of them require a session_hash,

payload format for, /run/predict

```js
    {
        "fn_index": 0,
        "data": ["how many ears does the cat have in this picture", null],
        "session_hash": "241c1opq266"
    }

    // data[0] is where the human question/statment goes in,
    // data[1] is null
```

how to get info related about an image,

1. upload the image, using 3a,
   a. upload should be done as a formdata,
2. register the image with visual_chatgpt,
   a. image meta data should be sent,

```js
{
    "name": "C:\\Users\\adtjh\\AppData\\Local\\Temp\\tmpwdztc6rg\\20230109_164316_j93fmfzz.jpg",
    "size": 752520,
    "data": "",
    "blob": {},
    "orig_name": "20230109_164316.jpg",
    "is_file": true
}
```

3. reply to questions related to image,

# Prompt:

### Check if valid task

'''Is this task a valid task which can be achieved using pyautogui functions, in a step by step manner?\ntask : {taskMessage}\njust reply with 0 for true or 1 for false'''.format(taskMessage=task)

### generate pyautogui function name (location if mouse move, text to write if typewrite, etc.) for a step of the task

'''
task: {taskMessage}
generate ,
'''.format(taskMessage=task)

```python
[
    {
        "task_finished": False,
        "purpose": "Open Run",
        "eval_func": "pyautogui.hotKey('win', 'r')"
    },
    # Find Run Input Box,
    {
        "task_finished": False,
        "purpose": "Type Chrome",
        "eval_func": "pyautogui.typewrite('chrome')"
    },
    # Find Ok Button,
    {
        "task_finished": False,
        "purpose": "Click Ok",
        "eval_func": "pyautogui.click(20, 900, clicks=1, interval=0.2, button='left')"
    },
    # wait for chrome to open,
    # find the url search bar,
    {
        "task_finished": False,
        "purpose": "Select URL Search Bar",
        "eval_func": "pyautogui.click(50, 400, clicks=1, interval=0.2, button='left')"
    },
    {
        "task_finished": False,
        "purpose": "Type in twitter.com",
        "eval_func": "pyautogui.typewrite('twitter.com')"
    },
    {
        "task_finished": False,
        "purpose": "Press Enter",
        "eval_func": "pyautogui.press('enter')"
    },
    # wait for website to open,
    # Find What's happening? in webpage
    {
        "task_finished": False,
        "purpose": "Click on What's happening?",
        "eval_func": "pyautogui.click(80, 300, clicks=1, interval=0.2, button='left')"
    },
    {
        "task_finished": False,
        "purpose": "Type in the tweet",
        "eval_func": "pyautogui.typewrite('Hello, world')"
    },
    {
        "task_finished": False,
        "purpose": "Press Tweet Button",
        "eval_func": "pyautogui.typewrite('Hello, world')"
    },
    # wait for tweet to be published
    {
        "task_finished": True,
    }
]
```

Reply with a object with three keys for the next step using the screenshot named {img_name}. The keys are: 'task_finished': a boolean indicating completion of the task, 'purpose': a brief description of the purpose of the next step in simple English, 'eval_func': a string with a valid pyautogui function to perform the next step, Ensure that the 'eval_func' key contains a valid pyautogui function and that all three keys are included in the reply. Set the 'task_finished' key to True once the task:{task} is completed and False otherwise, example output: {{'task_finished': False, 'purpose': 'Open Run', 'eval_func': 'pyautogui.hotkey('win', 'r')'}}

context:you will be providing pyautogui functions to automate, until the task:{task} is complete, {img_name} this is an image of current screen, generate an object that has three keys for the next step using the screenshot named {img_name}, task_finished: True if the task: {task} has been completed else False, purpose:description of the purpose of the next step, eval_func:a string with a valid pyautogui function to perform the next step'. Ensure that the 'eval_func' key contains a valid pyautogui function and that all three keys are included in the reply as an object. If you understand, reply with an object as explained. example output: {{'task_finished': False, 'purpose': 'Open Run', 'eval_func': 'pyautogui.hotkey('win', 'r')'}}

conditioning,

I,me:flask server,

```
you are going to guide the flask server to automate itself and complete the task:{task}. The completion of the task will be done using iteration. In each iteration, the server will provide you an screenshot image, and ask what is the next iteration. From the given image you have to gather information, about the current screen of the server. Your reply in each iteration, should be an object containing, three keys, task_finished: True if the task: {task} has been completed else False, purpose:description of the purpose of the next iteration, eval_func:a string with a valid pyautogui function to perform the next iteration. In each iteration reply with only an array, containing all three values. Once that is done, proceed to next iteration, this will go on till the task is complete. If you understand, reply with ok.
```

```
you are going to generate pyautogui functions to automate the computer and complete the task:{task}. The completion of the task will be done in loop. In each step, the server will provide you an screenshot, and ask 'what is the next step ?' . From that screenshot, you have to gather information, about the current screen of the server. Your reply in each time I ask, should be an object containing, three keys, task_finished: True if the task: {task} has been completed else False, purpose:description of the purpose of what you are trying to achieve, eval_func:a string with a valid pyautogui function to perform the next step. each time I ask reply with only an array, containing all three values. Once that is done, proceed to next step, this will go on till the task is complete. If you understand, say 'ok'
```

```
you are going to play a game I invented,
game starts with me stating the task to complete,
the object of the game is to complete the given task:{task},
the rules of the game are simple,
each round, I am going to provide an image, and ask 'what is the next step ?', you will reply with a generated json object, having three keys, 'task_finished': True if the task: {task} has been completed otherwise False, 'purpose': description of the purpose of the next step, eval_func:a string with a valid pyautogui function to perform the next step, till the task has been completed,
you will wait for my question before replying,
you should follow the rules rather than directly imagine from my game rules. If you understand, say 'ok'.
```

```
this is not a question about an image. you are going to play a game I invented,
the object of the game is to complete the given task:{task},
the rules of the game are simple,
each round, I am going to provide an image, and ask 'image/image_name.png what is the next step ? generate object',
your reply should only be a object having three keys 'task_finished': True if the task: {task} has been completed otherwise False, 'purpose': description of the purpose of the next step, 'eval_func':a string with a valid pyautogui function to perform the next step, till the task has been completed,
if task has completed, then reply 'task_finished:True'
exactly like this,

Human: image/3dcd6c88.png, what is the next step ? generate object.
AI:{{task_finished: False, purpose: 'Open Run', eval_func: pyautogui.hotKey('win', 'r') }},
Human: image/3dcd6c88.png, what is the next step ? generate object.
AI:{{task_finished: False, purpose: 'Type Chrome', eval_func: pyautogui.typewrite('chrome')}},
Human: image/3dcd6c88.png, what is the next step ? generate object.
AI:{{task_finished: False, purpose: 'Click Ok', eval_func: pyautogui.click(20, 900, clicks=1, interval=0.2, button='left')}},
Human: image/3dcd6c88.png, what is the next step ? generate object.
AI:{{task_finished: False, purpose: 'Select URL Search Bar', eval_func: pyautogui.click(50, 400, clicks=1, interval=0.2, button='left')}},
Human: image/3dcd6c88.png, what is the next step ? generate object.
AI:{{task_finished: False, purpose: 'Type in twitter.com', eval_func: pyautogui.typewrite('twitter.com')}},
Human: image/3dcd6c88.png, what is the next step ? generate object.
AI:{{task_finished: False,purpose: 'Press Enter',eval_func: pyautogui.press('enter')}},
Human: image/3dcd6c88.png, what is the next step ? generate object.
AI:{{task_finished: False,purpose: 'Click on What's happening?',eval_func: pyautogui.click(80, 300, clicks=1, interval=0.2, button='left')}},
Human: image/3dcd6c88.png, what is the next step ? generate object.
AI:{{task_finished: False,purpose: 'Type in the tweet',eval_func: pyautogui.typewrite('Hello, world')}},
Human: image/3dcd6c88.png, what is the next step ? generate object.
AI:{{task_finished: False,purpose: 'Press Tweet Button',eval_func: pyautogui.typewrite('Hello, world')}},
Human: image/3dcd6c88.png, what is the next step ? generate object.
AI:{{task_finished: True}}

stick to the rules rather than directly imagine from game rules, reply according to specified rules.
If you understand, say 'ok'.
```

```
this is not a question about an image. you are going to play a game I invented,
the object of the game is to complete the given task:{task},
the rules of the game are simple,
each round, I am going to provide an image, and ask 'image/image_name.png what is the next step ? generate object',
your reply should only be an array having three values 'task_finished': True if the task: {task} has been completed otherwise False, 'purpose': description of the purpose of the next step, 'eval_func':a string with a valid pyautogui function to perform the next step, till the task has been completed,
if task has completed, then reply 'task_finished:True'
exactly like this,

Human: image/3dcd6c88.png, what is the next step ?
AI: [False, 'Open Run', 'pyautogui.hotKey('win', 'r')']
Human: image/3dcd6c88.png, what is the next step ?
AI: [False, 'Type Chrome', 'pyautogui.typewrite('chrome')']
Human: image/3dcd6c88.png, what is the next step ?
AI: [False, 'Click Ok', 'pyautogui.click(20, 900, clicks=1, interval=0.2, button='left')']
Human: image/3dcd6c88.png, what is the next step ?
AI: [False, 'Select URL Search Bar', 'pyautogui.click(50, 400, clicks=1, interval=0.2, button='left')']
Human: image/3dcd6c88.png, what is the next step ?
AI: [False, 'Type in twitter.com', 'pyautogui.typewrite('twitter.com')']
Human: image/3dcd6c88.png, what is the next step ?
AI: [False, 'Press Enter', 'pyautogui.press('enter')']
Human: image/3dcd6c88.png, what is the next step ?
AI: [False, 'Click on What's happening?', 'pyautogui.click(80, 300, clicks=1, interval=0.2, button='left')']
Human: image/3dcd6c88.png, what is the next step ?
AI: [False, 'Type in the tweet', 'pyautogui.typewrite('Hello, world')']
Human: image/3dcd6c88.png, what is the next step ?
AI: [False, 'Press Tweet Button', 'pyautogui.typewrite('Hello, world')']
Human: image/3dcd6c88.png, what is the next step ?
AI: [True]

stick to the rules rather than directly imagine from game rules, reply according to specified rules.
If you understand, say 'ok'.
```

first find out the steps, to perform in order to complete the task, in an array

you are going to play a game I invented,
In this game, I don't know how to operate a computer, and you have to generate instructions to complete the task:'{task}',
remember answer by AI is always an array of strings or else I lose the game,
Human:what are the steps involved in doing this task : 'Open chrome and tweet something',
AI: ['opening chrome', 'opening twitter in a chrometab', 'generate a tweet', 'type in the tweet', 'click the tweet button']
Human:what are the steps involved in doing this task : 'Calculate 2+2 in calculator',
AI: ['opening calculator', 'clicking on number 2', 'clicking on the + button', 'clicking on number 2', 'clicking on the = button', 'reading the result as 4']
reply with an array of strings, containing the steps to undertake to complete the task.

now go through that array, step by step, and increment the step_counter only when a step is finished successfuly,

- screenshot, description: screenshot of the screen which the Human is in, Human needs to complete this step:{step}. If you understand say 'ok'.

- what is the next step ? generate an array of three strings, 'task_finished': True if the task: {task} has been completed otherwise False, 'purpose': description of the purpose of the next step, 'eval_func':a string with a valid pyautogui function to perform the next step

  if task_finished == True:
  escape
  else
  continue

now for each instructional step, generate an array of three strings, \n'task_finished': True if the task: {task} has been completed otherwise False, 'purpose': description of the purpose of the next step, 'eval_func':a string with a valid pyautogui function to perform the next step,

now for each instructional step, generate an array of three strings, \n'task_finished': True if the task: {task} has been completed otherwise False, 'purpose': description of the purpose of the next step, 'eval_func':a string with a valid pyautogui function to perform the next step,

Convert given string to an array of steps which can be read using a python code.\n\n\n{response}\n\n\nreply only an array, treat this as if this message will be read by a computer,
