import urllib3
import json
import logging
import random
import time

url_root = "https://abc.mustspace.net:8082"
http_pool_manager = urllib3.PoolManager()

headers = {
    "User-Agent" : "Mozilla/5.0 (iPhone; CPU iPhone OS 11_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E217 MicroMessenger/6.8.0(0x16080000) NetType/WIFI Language/en Branch/Br_trunk MiniProgramEnv/Mac"
}

config = {
    "pause_time_min_milisec" : 1000,
    "pause_time_max_milisec" : 3000
}

class NetworkError(Exception):
    
    pass

def get_post_list(page_number: int):
    if page_number >= 1:
        url = url_root + f"/getPostList?category_id=0&userId=0&page={page_number}&size=20"
        response = http_pool_manager.request('GET', url, headers = headers)
        
        if response.status == 200:
            result_raw = response.data.decode('UTF-8')
            result = json.loads(result_raw)
            return {
                "result" : result, 
                "raw" : result_raw
            }
        else:
            raise NetworkError("Connection to server failed")
    else:
        raise ValueError("Page number should > 0.")
    
def get_post_detail(post_id: int):
    if post_id >= 1:
        url = url_root + f"/getNews?id={post_id}&userId=0"
        response = http_pool_manager.request('GET', url, headers = headers)
        flag_success = False
        
        if response.status == 200:
            result_raw = response.data.decode('UTF-8')
            result = json.loads(result_raw)
            
            if "code" in result.keys():
                if result["code"] == 2002:
                    flag_success = False
            else:
                flag_success = True
                
            return {
                "flag" : flag_success,
                "result" : result,
                "raw" : result_raw
            }
        else:
            raise NetworkError("Connection to server failed")
    else:
        raise ValueError("Post ID should > 0.")
    

def crawl_by_range(starting_page = 1, exiting_page = None, ):
    
    page = starting_page - 1
    
    while True:
        page += 1
        
        
        logging.info(f"Requesting for post listing, page #{page}")
        post_list = get_post_list(page)["result"]
        
        if post_list == []:
            logging.info("No new post data found. Exiting.")
            return
        elif page == exiting_page:
            logging.info("Crawl page target reached. Exiting.")
            return
        
        logging.info(f"{len(post_list)} entries found!")
        
        for idx, p in enumerate(post_list, start = 1):
            logging.info(f"Requesting for post #{idx}/{len(post_list)}, post_id = {p['id']}")
            
            post_detail = get_post_detail(p["id"])
            if post_detail["flag"]:
                with open(f"./data/posts/{p['id']}.json", 'w') as f:
                    f.write(post_detail["raw"])
                    
                logging.info(f"Saved post #{p['id']} raw content to ./data/posts/{p['id']}.json.")
            else:
                with open(f"./data/failed.txt", "a+") as f:
                    f.write(f"{p['id']}\n")
                    
                logging.warning(f"Failed to request post #{p['id']}. ID saved to failed list.")
            
            sleep_time = random.randint(config["pause_time_min_milisec"], config["pause_time_max_milisec"])/1000
            logging.info(f"Paused execution for {sleep_time: .3f}s to limit request rate")
            time.sleep(sleep_time)


def save_post_list_raw(post_id_list):
    for idx, p in enumerate(post_id_list, start = 1):
            logging.info(f"Requesting for post #{idx}/{len(post_id_list)}, post_id = {p}")
            
            post_detail = get_post_detail(p)
            if post_detail["flag"]:
                with open(f"./data/posts/{p}.json", 'w') as f:
                    f.write(post_detail["raw"])
                    
                logging.info(f"Saved post #{p} raw content to ./data/posts/{p}.json.")
            else:
                with open(f"./data/failed.txt", "a") as f:
                    f.write(f"{p}\n")
                    
                logging.warning(f"Failed to request post #{p}. ID saved to failed list.")
            
            sleep_time = random.randint(config["pause_time_min_milisec"], config["pause_time_max_milisec"])/1000
            logging.info(f"Paused execution for {sleep_time: .3f}s to limit request rate")
            time.sleep(sleep_time)