<div align="center">
<img src="http://photos.prnewswire.com/prnfull/20141022/153661LOGO?p=publish"  width="300" height="120">
</div>

# 1. How to run

In this section we explain all the useful information that we can use when working in our local environment.

In order to raise our system we will have to go to the root folder of our system and launch the following command

```html
docker-compose up
```

This will launch our system by creating a local docker image and deploying our fetcher.

It is important to keep in mind that this process launches a multitude of requests against the production environment
and it is important to limit them all so as not to overload the system.

To facilitate the work in local we also have several local configurations that allow us to test step by step our
application avoiding possible problems of launching too many requests.

To launch this configuration in Intellij you will need to verify that the following steps were done:
```html
- Go to Settings >> Build, Execution, Deployment >> Docker
- Select "TCP socket"
- Enter 'unix:///var/run/docker.sock' under "Engine API URL"
```