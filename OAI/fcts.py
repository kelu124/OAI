from OAI.oaisetbase import APIBase, svt, ldt, hashme

import os, openai, datetime
import requests, json

from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored


GPT_MODEL = "gpt-3.5-turbo-1106"

class askFCT(APIBase):

    @retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
    def chat_completion_request(self,messages, functions=None, function_call=None, model=GPT_MODEL):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + openai.api_key,
        }
        json_data = {"model": model, "messages": messages}
        if functions is not None:
            json_data.update({"functions": functions})
        if function_call is not None:
            json_data.update({"function_call": function_call})
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=json_data,
            )
            return response
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e
        
    def pretty_print_conversation(self,messages):
        role_to_color = {
            "system": "red",
            "user": "green",
            "assistant": "blue",
            "function": "magenta",
        }
        
        for message in messages:
            if message["role"] == "system":
                print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
            elif message["role"] == "user":
                print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
            elif message["role"] == "assistant" and message.get("function_call"):
                print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
            elif message["role"] == "assistant" and not message.get("function_call"):
                print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
            elif message["role"] == "function":
                print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))


    def askFct(self,CONTEXT,Q,functions,modelGPT=GPT_MODEL,ow=False,src="none",seed=""):

        messages = []
        messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.\n"+CONTEXT})
        messages.append({"role": "user", "content": Q})
        
        messages, summary = self.askFtcEngine(messages,functions,modelGPT=modelGPT,ow=ow,src=src,seed=seed)
        if "content" in summary.keys():
            ANSWER = summary["content"]
            if (not ANSWER) and ("message" in summary.keys()): 
                ANSWER = summary["message"]
        elif "choices" in summary.keys():
            ANSWER = summary["choices"]
        else:
            print(summary)
        return messages, ANSWER


    def askFtcEngine(self,messages,functions,modelGPT=GPT_MODEL,ow=False,src="none",seed=""):
        #print(messages)

        MSG = json.dumps(messages)+"\n\n=========\n\n"
        MSG += "\n\n=========\nFUNCTION\n=========\n\n"+ str(functions)
        if len(seed): 
            MSG += "\n\n=========\n\nSeed: " + seed
        ID =hashme(MSG)

        PATH = self.GOTOCACHE + ID
        if ow:
            # Si on réécrit
            

            chat_response = self.chat_completion_request(
                messages, functions, model=modelGPT
            )
            summary = chat_response.json()#["choices"][0]["message"]
            svt(PATH,json.dumps(summary))
            NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.DB.delete_many({"ID":ID})
            LOG = {"app":self.NAME,"query":MSG, "ID":ID, "answer":summary, "when":NOW,"from":src}
            self.DB.insert_one(LOG)
        else:
            CHECK_ONLINE = self.DB.find_one({"ID": ID})
            if CHECK_ONLINE:
                summary = CHECK_ONLINE["answer"]
                # Si pas en local on sauve quand même
                if not os.path.exists(PATH):
                    svt(PATH,json.dumps(summary))
            else:
                # Rien en ligne
                # On check en local
                if not os.path.exists(PATH):
                    chat_response = self.chat_completion_request(
                        messages, functions, model=modelGPT
                    )
                    summary = chat_response.json()#["choices"][0]["message"]

                    svt(PATH,json.dumps(summary))
                else:
                    summary = json.loads(ldt(PATH))
                # On ajoute le résumé
                NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                LOG = {"app":self.NAME,"query":MSG, "ID":ID, "answer":summary, "when":NOW,"from":src}
                self.DB.delete_many({"ID":ID})
                LOG = {"app":self.NAME,"query":MSG, "ID":ID, "answer":summary, "when":NOW,"from":src}
                self.DB.insert_one(LOG)

        if "content" in summary.keys():
            messages.append(summary)
        if "choices" in summary.keys():
            summary = summary["choices"][0]["message"]
            messages.append(summary)


        return messages,summary