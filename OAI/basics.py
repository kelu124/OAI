from OAI.oaisetbase import APIBase, svt, ldt, hashme
import datetime
import os, json


is_prod = os.environ.get('IS_HEROKU', None)


## Helper class
class Helper(APIBase):


    def ask_GPT(self,system_intel, prompt,MODEL="gpt-3.5-turbo-1106"): 
        # Alternative "gpt-4"
        now = datetime.datetime.now() # current date and time2
        chat_messages = [{"role": "system", "content": system_intel},
                                            {"role": "user", "content": prompt}]
        response = self.CLIENT.chat.completions.create(
            model=MODEL,
            messages=chat_messages
        )
        now2 = datetime.datetime.now() # current date and time
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S") + " --> " + now2.strftime("%m/%d/%Y, %H:%M:%S")
        print("Processing with",MODEL,":\t",date_time)	

        answer = json.loads(response.json())["choices"][0]["message"]["content"]
        return answer


    def ask(self,CONTEXT,Q,v="gpt-3.5-turbo-16k-0613",ow=False,src="none"):
        STR = "Context: "+CONTEXT + "\n\n=========\n\nQuestion: "+ Q + "\n\n=========\n\nVersion: " + v
        ID = hashme(STR.encode('utf-8'))
        PATH = self.GOTOCACHE + ID
        #print(PATH)
        if ow:
            # Si on réécrit
            summary = self.ask_GPT(CONTEXT, Q, v)

            NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #print("saving after overwrite")
            self.DB.delete_many({"ID":ID})
            LOG = {"app":self.NAME,"query":STR, "ID":ID, "answer":summary, "when":NOW,"from":src}
            self.DB.insert_one(LOG)
            svt(PATH,summary) 
        else:
            CHECK_ONLINE = self.DB.find_one({"ID": ID})
            if CHECK_ONLINE: 
                summary = CHECK_ONLINE["answer"]
                # Si pas en local on sauve quand même
                if not os.path.exists(PATH):
                    svt(PATH,summary)
            else:
                # Rien en ligne
                # On check en local
                if not os.path.exists(PATH):
                    log = "loading from local file"
                    summary = self.ask_GPT(CONTEXT, Q, v)
                    svt(PATH,summary)
                else:
                    log = "Found cached locally"
                    summary = ldt(PATH)
                # On ajoute le résumé
                NOW = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.DB.delete_many({"ID":ID})
                LOG = {"app":self.NAME,"query":STR, "ID":ID, "answer":summary, "when":NOW,"from":src}
                self.DB.insert_one(LOG)
        
        return summary
