# eduCool

a backend server for an e-learning application that allows communication via posts or video conference

## Name Origin:

educ~~ation~~ + ~~sch~~ool = educool

that's it, honestly it's inspired by educative, I liked how the name is just the adjective of 'educate' and I started to think of other cool derivatives and combinations

## Project Status

currently archived, untill further notice, the core APIs work fine, the users can create/enroll in courses, post, comment, or join video conference rooms

## Project Screen Shot(s)
later

## Demo video:
later

## Installation and Setup Instructions

Clone down this repository. You will need `docker` installed on your machine.

### Installation:

- change directory to the cloned repo dir

- add env file:
  
  ```touch edu_cool/.env sfu/.env```

  for local development, all the environment variables have a default value, so it'll work fine if you're trying the system locally, the env files are added since they're specified in the docker compose file
  
- run the services

  ```docker compose up```
  
**Note for firefox users(or any ff based browser) :**

  for the video conference feature to work locally you either need to:
  
  - hit ```about:config``` in the address bar
    
  - then search for ```media.peerconnection.ice.loopback``` and make sure this is set to true
    
    **OR**
    
  - make sure you're connected to the router
    
  - in `sfu/.env` file add:
    
    ```ANNOUNCEDIP='your local private ip here(the one assigned from the router not a loopback)'```

  since firefox doesn't allow ice loopback to local address by default

## Behind the scenes:

- after my graduation, I was grinding leetcode consistently and 
applying for jobs, but I thought another personal project or open 
source contribution might help my resume stand out, I also needed a 
refresher for the BE foundations I've learnded and to learn other 
skills listed on jobs' descriptions, I found the roadmap here 
useful: https://roadmap.sh/backend ,

  then I started to pick up some technologies like drf, django channels, webrtc and mediasoup through project based documentation, or tutorials, after locking in for a while I decided to go in public, start building and share my progress on linkedin from time to time
  (umm, pretty much that's it, not gonna share my autobiography here on gh or smth)

- Challenges: one of the major challenges was authenticating websocket with jwt cookies, might start blogging about it

- Technologies: Python, Django, DRF, Django-channels, Javascript, NodeJs, Mediasoup, Docker

- How it works?:

	* Django http server, serving the rest api
	
	* Mediasoup running over a NodeJs server, as an sfu to scale the webrtc connections
	
	* Django-channels handling the websocket connection between the client and the mediasoup server

- PSA: 

  no ai agent was used for building this, this project was built from scratch using H.I(human intelligence), as I wanted to sharpen my problem solving and critical thinking skills, and keep my brain away from rotting even a little bit without depending on ai completely, I beleive learning to use ai is like the evolution of google dorks and I can adapt and anticipate it easily, so I'm not completely anti-ai either, I just didn't want to follow the repititive waves of hype