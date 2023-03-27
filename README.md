# automate

### Brief
I created a flask server that displays a homepage with a chatbox. Users can record their tasks through the chatbox, and the server sends the task audio to the Whisper API, which generates a transcript. The task is then validated using the OpenAI GPT-3.5 API. If the task can be performed on a computer, it is broken down into smaller steps using the GPT-3.5 API. The server loops through each step, providing a screenshot to Visual_ChatGPT and asking for PyAutoGUI functions to complete that step. Once all the steps are completed, the server sends the response back to the frontend.

If I use a better fine-tuned model, It's possible to do much lengthy tasks. Also Visual chatgpt uses text-davinci-002, GPT-4 will have much better performance.

Here's a chat with ChatGPT summarising this project.
![chat with chatGPT](https://github.com/adtjha/automate/blob/master/assets/FireShot%20Capture%20027%20-%20Assistance%20Offered.%20-%20chat.openai.com.png?raw=true)

## Steps to Run.

### Setup Visual_ChatGPT
1. Clone the visual_chatgpt, into local environment,
2. Install and run visual_chatgpt (set your openai_key as environment variable),
3. Once running, goto page: http://127.0.0.1:7868,
4. type in 'hi', should get a reply,
5. Open console, click on networking tab,
6. click on any one of the '/predict' api requests, find out the payload content,
7. Get the session_hash, we will require that to send api requests directly from the flask server.

### Setup Flask Server
1. If in windows, run this to setup the virtual environment,
```bash
> cd Scripts
> activate.bat
```
2. Once inside the virtual environment, run
```bash
flask run 
```
3. Once the backend is running, goto localhost:5000,
