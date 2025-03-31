import os
import json
import ast
import traceback

async def Save(data, name): # must be list of dicts
    sortKeys = False
    try: 
        if(botlog is not None and botlog > 10): botlog = 0
    except: pass
    try:
        cwd = os.getcwd()
        path = f"{cwd}/{name}.json"

        if not os.path.exists(path):
            with open(path, 'w') as f:
                json.dump(data, f, sort_keys=sortKeys, indent=4)
                print(f"saved. {botlog} 1st try")
                f.close()

        else:
            
            try:
                with open(path) as f:
                    loaddata = json.load(f)
                    f.close()
                loaddata.update(data)
                with open(path, 'w') as f:
                    f.seek(0)
                    json.dump(loaddata, f, sort_keys=sortKeys, indent=4)
                    print(f"saved. {botlog} 2nd try")
                    f.close()
            except:
                traceback.print_exc()

                try:
                    with open(path, 'w') as f:
                        json.dump(data, f, sort_keys=sortKeys, indent=4)
                        print(f"saved. {botlog} 3rd try")
                        f.close()
                except: 
                    traceback.print_exc()

    except: traceback.print_exc()
    return

async def Load(name):# returns list of dicts
    try:
        cwd = os.getcwd()
        path = f"{cwd}/{name}.json"
        print(path)
        if not os.path.exists(path): print(path)
        
        else:
            with open(path, "r", encoding='utf-8-sig') as h:
                output = h.read()
                output = output.encode(encoding='utf-8',errors='strict')
                output = output.decode('UTF-8')

                try: data = ast.literal_eval(output)
                except: data = json.loads(output)
                h.close()
            return data
        
    except: traceback.print_exc()
    return
