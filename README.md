# propfinder-stm

propfinder is a Telegram bot that runs on Heroku. It lets you set url queries for web apps to scrap them periodically and notify you via Telegram the publications you haven't seen yet.

Currently allowed web apps:
* https://www.zonaprop.com.ar
* https://www.argenprop.com
* https://inmuebles.mercadolibre.com.ar

## Usage
Available commands:
    
    /help - How it works
    /geturls - Get current urls
    /addurl <url> - Add new url
    /deleteurl <url> - Delete url (if does not exists, nothing happens)
    /updateunseen - Fetches all prop ads from your urls and returns those you haven't seen
    /vippify - Subscribe to receive updates each 20 minutes
    /unvippify - Unsubscribe


Adding URL example
```
    /addurl https://www.argenprop.com/departamento-alquiler-barrio-palermo-orden-masnuevos
```

---
## Monitoring
### Monitoring App
* `heroku logs`
* `heroku logs --tail`
* `heroku logs --ps worker.1 --tail`

### Monitoring Heroku
* See free dyno's hours remaining: `heroku ps`
* See processes: `heroku ps:scale`
* `heroku run bash`


Config vars
	heroku config:set ENCRYPTION_KEY=my_secret_launch_codes

---
## Database (Mongo Atlas)
* Create a database in Mongo Atlas
* Whitelist all ips in Mongo Atlas (`0.0.0.0/0`)
* From the cluster's UI click on `CONNECT` and copy the command that has this format: `mongo "mongodb+srv://<cluster-domain>/<database>" --username <user>`

---
## Deployment
* Follow these instructions to configure remote repository: https://devcenter.heroku.com/articles/git
* Activate clock scheduler: `heroku ps:scale clock=1`
* Upload and deploy code: `git push heroku master` 

---
## Handling Secrets
To handle sensitive information I created a new branch called `secret` and didn't push it to my origin repository.
In that branch I did replace the values of `sensitive.conf.template` and changed the name to 'sensitive.conf'. 
* `git push heroku secret:master`
	
However, I recommend to use Heroku's environment variables!

