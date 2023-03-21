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
