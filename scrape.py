#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import requests,bs4,time


ID      = ""
PASS    = ""

URL     = "http://127.0.0.1:8000/"
LOGIN   = URL + "admin/login/"
TARGET  = URL + "admin/surveillance/information/"
TIMEOUT = 10
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:63.0) Gecko/20100101 Firefox/63.0'}


#TIPS:Djangoに対してrequestsライブラリからPOST文を送信する方法
# https://www.it-swarm-ja.com/ja/python/python-requests%e3%81%a7csrftoken%e3%82%92%e6%b8%a1%e3%81%99/1070253083/



#セッションを維持する(セッションメソッドからオブジェクトを作る)
client = requests.session()
client.get(LOGIN,timeout=TIMEOUT,headers=HEADERS)

#CSRFトークンを手に入れる
if 'csrftoken' in client.cookies:
    csrftoken = client.cookies['csrftoken']

login_data   = { "csrfmiddlewaretoken":csrftoken,
                 "username":ID,
                 "password":PASS
                 }

#ログインする
r   = client.post(LOGIN,data=login_data,headers={"Referer":LOGIN})
print(r)



#一覧ページ(TARGET)へアクセス、URLとメールアドレスのリストを手に入れる。
result  = client.get(TARGET,timeout=TIMEOUT,headers=HEADERS)
soup    = bs4.BeautifulSoup(result.content,"html.parser")

ids     = soup.select(".field-id")
urls    = soup.select(".field-url")
emails  = soup.select(".field-email")


#URLとメールを全て表示
for url in urls:
    print(url.text)

for email in emails:
    print(email.text)


#urlとemailを辞書型のリスト型にする。
length  = len(urls)
data    = []

for i in range(length):
    dic = { "id":ids[i].text,
            "url":urls[i].text, 
            "email":emails[i].text,
            "before":"",
            "after":"" }
    data.append(dic)
    
print(data)


while True:

    #指定したサイトへここでスクレイピングをする。(※注意、管理サイトにログインしたセッションでスクレイピングをすると、管理サイトの情報を一般ユーザーに知られてしまう可能性があるため、別セッションでスクレイピング)
    for d in data:
        
        try:
            if d["url"] != "": 
                result  = requests.get(d["url"],timeout=TIMEOUT,headers=HEADERS)
            else:
                print("削除済みデータ")
                continue
        except:
            print("スクレイピングエラー")
            continue
        else:
            print("スクレイピング開始")

            #現在のスクレイピング対象のHTMLもしくは文字列等をafterに代入。
            #print(result.content)
            
            soup    = bs4.BeautifulSoup(result.content,"html.parser")
            body    = soup.select("body")

            d["after"]  = body[0].text
            #d["after"]  = result.content

            #ここで前回のループで代入したbeforeと今回のループで代入したafterを比較。
            #比較に必要なbeforeとafterのいずれかが空欄になっている(比較できない状態)の場合は何もしない。
            if d["before"] == "" or d["after"] == "":
                pass
            else:
                #beforeとafterが不一致の場合、メール送信。
                if d["before"] != d["after"]:
                    #ここでメールを送信する
                    print("メール送信")

            #比較を終えたら新しい情報をbeforeへ入れる。
            d["before"] = d["after"]
            


    #管理サイトへアクセス。(dataとスクレイピング結果を比較する。不一致(更新されている)場合は内容を書き換える。)
    """
    管理画面で新しくスクレイピングしたものをN、これまでのデータをOとする。

    NにIDが無くて、Oにある場合、これは削除
    NにIDがあって、Oにない場合、これは新規作成
    NにIDがあって、Oにある場合、これは据え置きか編集のいずれかだろう。
    """

    result  = client.get(TARGET,timeout=TIMEOUT,headers=HEADERS)
    soup    = bs4.BeautifulSoup(result.content,"html.parser")

    ids         = soup.select(".field-id")
    urls        = soup.select(".field-url")
    emails      = soup.select(".field-email")
    length      = len(urls)


    #前のwhileループのIDとスクレイピングの結果手に入ったIDを比較するため、リスト型変数を生成
    #リストの内包表記
    new_id_list     = [ id.text for id in ids ] #←["1","32","4"]
    old_id_list     = [ d["id"] for d in data ] #←["1","32","4","5"]

    """
    #↑の内包表記は↓と等価
    new_id_list = []
    for id in ids:
        new_id_list.append(id.text)
    """



    print("==============")
    print(new_id_list)
    print(old_id_list)
    print("==============")


    """
    [{},{},{}]
    """


    #削除されたデータを消す。
    for o in old_id_list:

        #消したデータは無視
        if o == "":
            continue

        if o not in new_id_list:
            print("ない")
            len_data    = len(data)
            for i in range(len_data):
                if o == data[i]["id"]:
                    target  = i
                    break

            #TIPS:辞書型のデータは削除できない。故に空欄で塗りつぶす。
            data[target]["id"]      = ""
            data[target]["url"]     = ""
            data[target]["email"]   = ""
            data[target]["before"]  = ""
            data[target]["after"]   = ""

    
    #ここから新規作成処理
    #new_id_listとold_id_listを比較。new_id_listにあり、old_id_listにない場合、新規作成する。
    add_id_list = []
    for n in new_id_list:
        if n not in old_id_list:
            add_id_list.append(n)

    length  = len(ids)
    for i in range(length):

        if ids[i].text in add_id_list:

            dic     = {}
            dic["id"]      = ids[i].text
            dic["url"]     = urls[i].text
            dic["email"]   = emails[i].text
            dic["before"]  = ""
            dic["after"]   = ""

            data.append(dic)

            print("新規作成")

    print(data)

    #ここの待ち時間を30分以上に指定してしまうとHerokuがスリープしてしまう。
    time.sleep(10)


