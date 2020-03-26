# propfinder-stm

heroku logs
heroku logs --tail
heroku logs --ps worker.1 --tail

mongo "mongodb+srv://propfinder-stm-0uhxi.mongodb.net/test" --username rodrisouto
heroku git:remote -a propfinder-stm
git push heroku master 

after clock
heroku ps:scale clock=1


To handle sensitive information I created a new branch called `secret` and didn't push it to my origin repository.
In that branch I did replace the values of `sensitive.conf.template` and changed the name to 'sensitive.conf'. 
	git push heroku secret:master 
	
However, I recommend to use Heroku's environment VARs!


Get the public id from the logs at startup
	My public IP address is: xxx.xxx.xxx.xxx
Go to Network Access in MongoDB Atlas and whitelist that ip

Monitoring (see Free dyno hours remaining)
	heroku ps
	heroku ps:scale
	heroku run bash


Config vars
	heroku config:set ENCRYPTION_KEY=my_secret_launch_codes

heroku releases

