# propfinder-stm

heroku logs --tail
mongo "mongodb+srv://propfinder-stm-0uhxi.mongodb.net/test" --username rodrisouto
heroku git:remote -a propfinder-stm
git push heroku secret:master 
git push heroku master 



Get the public id from the logs at startup
	My public IP address is: xxx.xxx.xxx.xxx
Go to Network Access in MongoDB Atlas and whitelist that ip

