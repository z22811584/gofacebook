import requests
import re
import json
from bs4 import BeautifulSoup
import time
import pandas as pd
# 參數設定
bac=""
rs = requests.Session()
content_df = [] # post
feedback_df = [] # reactions
bac = bac #nextpage
headers = {'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
            'x-fb-lsd': 'GoogleBot'}
data = {'lsd': 'GoogleBot',
        '__a': 'GoogleBot'}
params = {
    'bac': bac,
    'multi_permalinks': '',
    'refid': '18'
    }


#留言抓取FC
def comment_cat(comment_content,comment_count):
    comment_count=int(comment_count)
    comment_lib=[]
    comment_url="https://m.facebook.com/groups/1260448967306807/permalink/"+str(comment_content)
    resp = rs.get(comment_url, params=params)
    data = re.sub(r'for \(;;\);','',resp.text)
    soup = BeautifulSoup(data, 'lxml')
    print("目前有",comment_count,"則留言")

    #定位留言資料位置
    data_loc=resp.text
    data_loc2=resp.text.find("</h3><div class=")+len("</h3><div class=")+1
    data_loc=data_loc[data_loc2:data_loc2+2]   

    #小於10則留言 全輸出結束
    if comment_count<=10:
        for i in soup.find_all("div",f"{data_loc}"):
            comment_one=i.text

            comment_lib.append(comment_one)     


    #大於10則留言
    elif comment_count >10:
        #找出個位數
        ten=(comment_count//10)*10
        one=comment_count%10

        #抓出小於10的全部留言
        for i in soup.find_all("div",f"{data_loc}"):
            comment_one=i.text

            comment_lib.append(comment_one)   

        #抓出大於10的留言
        for ii in range(10,ten,10):
            comment_url_2=comment_url+"?p="+str(ii)
            resp = rs.get(comment_url_2, params=params)
            data = re.sub(r'for \(;;\);','',resp.text)
            soup = BeautifulSoup(data, 'lxml')
            print("已經抓取",ii,"/",comment_count,"則留言")

            #定位留言資料位置
            data_loc=resp.text
            data_loc2=resp.text.find("</h3><div class=")+len("</h3><div class=")+1
            data_loc=data_loc[data_loc2:data_loc2+2]           

            for i in soup.find_all("div",f"{data_loc}"):
                comment_one=i.text

                comment_lib.append(comment_one)
            time.sleep(4)

    return comment_lib
##\3a = :
##\3d = =
##\26 = &

#主程式FC
def gofacebook(bac=''):

    groupurl="https://www.facebook.com/groups/1260448967306807"


    # 導向 m.facebook
    groupurl = re.sub('www','m', groupurl)

    # Post方法參數
    params = {
        'bac': bac,
        'multi_permalinks': '',
        'refid': '18'
        }
    resp = rs.post(groupurl, headers=headers, params=params, data=data)
    resp = re.sub(r'for \(;;\);', '', resp.text)
    resp = json.loads(resp)
    soup = BeautifulSoup(resp['payload']['actions'][0]['html'], "lxml")   


    #--資料處理
    temp={}
    for article in soup.select('section > article'):
        articles=[]
        pre_articles=temp.copy() #記憶體位置處理

        #內容處理
        pre_articles.update({"content":article.find("div","_5rgt _5nk5 _5msi").text})

        #圖片處理
        img=article.find("div",{'data-ft':'{"tn":"H"}'})

        #圖片網址擷取
        imglib=[]
        for test2 in str(img).split('(')[1:]: #定位網址
            test3=str(test2).split(")")[0][1:-1]
            img=test3

            #編碼處理
            img=img.replace("\\3a ",":")
            img=img.replace("\\3d ","=")
            img=img.replace("\\26 ","&")

            imglib.append(img)

        #輸出給字典
        pre_articles.update({"img":imglib})

        #留言處理
        comment_content=re.findall('"tl_objid":"(.*?)"', str(article))[0]
        try:
            comment_count=article.find("span","cmt_def _28wy").text[:-4]
        except:
            comment_count=0

        comment_lib=comment_cat(comment_content,comment_count)
        pre_articles.update({"comment":comment_lib})

        #postID
        pre_articles.update({"postid":comment_content})

        print(pre_articles)
        #輸出List
        articles.append(pre_articles)

        ##輸出資料
        try:
            df=pd.read_excel("output.xlsx")
        except:
            df = pd.DataFrame(columns =["PostID", "文章內容", "文章圖片", "文章留言"])
            df.to_excel('output.xlsx',
                        header=True,
                        sheet_name= "FB文章抓取",
                        index=False,  #不保留index
                        na_rep="none")   #如果有缺失值,可以通過na_rep的方式把缺失值替換成自定義的名字


        for i in range(len(articles)):
            df.loc[len(df)+1]=[ str(articles[i]["postid"]),
                                 articles[i]["content"], articles[i]["img"],
                                 ",".join(articles[i]["comment"])]

        df.to_excel('output.xlsx',
                    header=True,
                    sheet_name= "FB文章抓取",
                    index=False,  #不保留index
                    na_rep="none")   #如果有缺失值,可以通過na_rep的方式把缺失值替換成自定義的名字
        
        print("EXCEL資料已更新")


    #下一頁的token
    bac = re.findall('bac=(.*?)%3D', soup.select('div > a.primary')[0]['href'])[0]



    #延遲後繼續
    time.sleep(4)

#跑程式
def main():
    bac=""
    for i in range(2):
        gofacebook(bac)

if __name__=='__main__':

    main()
