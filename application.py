from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import pymongo
import scrapetube
from pytube import YouTube

application = Flask(__name__, static_folder='static') # initializing a flask app
app=application
CORS(app)


@app.route('/',methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET']) # route to show the review comments in a web UI
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            video_link = request.form['content'].replace(" ","")
            x = YouTube(video_link)
            channelid = x.channel_id
            #channelid = request.form['content'].replace(" ","")
            videos = scrapetube.get_channel(channelid)
            list =[]
            for video in videos:
                try:
                    url = "https://www.youtube.com/watch?v="
                    url1=url+str(video['videoId'])
                    list.append(url1)
                except Exception as e:
                    print(f"handling error as {e}")
            url_list = list[0:5]
            Review = []
            for url in url_list:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
                urlclient = requests.get(url, headers = headers)
                page = urlclient.content
                soup = BeautifulSoup(page , 'html.parser')
                try:
                    url_thumbnail = soup.find('meta',property='og:image')['content']
                except:
                    url_thumbnail = 'No Thumbnail'
                try:
                    title = soup.find('meta',property='og:title')['content']
                except:
                    title = 'No Title'
                try:
                    views = soup.find('meta',itemprop="interactionCount")['content']
                except:
                    views = 'no views'
                try:
                    Upload_Date = soup.find('meta',itemprop="uploadDate")['content'] 
                except:
                    Upload_Date = 'Not able to Find'
                mydict = {"Video_url":url ,"Thumbnail_url":url_thumbnail,"Title":title,"Views":views,"Upload_date":Upload_Date}
                Review.append(mydict)
            client = pymongo.MongoClient("mongodb+srv://anmolgupta01:Anmolgupta@cluster0.6d80uqa.mongodb.net/?retryWrites=true&w=majority")
            db = client['youtube_review_scrap']
            Result_col = db['review_scrap_data']
            Result_col.insert_many(Review)
            return render_template('results.html', Review=Review)
        except Exception as e:
            print('The Exception message is: ',e)
            return 'something is wrong'
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)