#Table of contents
- [actions](#actions)
- [repositories](#repositories)
  * [statistic repository](#statistic-repository)
  * [slack repository](#slack-repository)
- [clients](#clients)
  * [statistic client](#statistic-client)
  * [slack client](#slack-client)

#Velocloud-notificator summary
Every 10 minutes we send a message to a slack channel with the amount of times an edge status other than 
`CONNECTED` occurs.
#Application folder
#####(the specifics of each class and functions within the classes)
## actions
Actions has two important functions
-  `store_stats` is the callback function everytime velocloud-notifcator subscribes to `edge.status.ko`. 
    It also takes a message as a parameter and passes it to and calls the statistic_repository's `send_to_stats_client` 
    function.
-  `send_to_slack` takes a message as a parameter, and then makes a call to its slack_repository's `send_to_slack` 
    function and passes the message to slack_repository's `send_to_slack` message parameter. This action is 
    called every 10 minutes.
## repositories
### statistic repository
   Statistic repository usually receives a message in a byte format. So first it must
   decode the message from a byte to a string. Then using this line, `from ast import literal_eval`, 
   we can convert the newly made string into a dictionary. Having this dictionary allows us to
   grab both values from keys `activation id` and `edge state` located in that dictionary. Then
   we pass both of those values down to the statistic clients' `store_edge` function.
   
### slack repository
   Converts the message passed from action's `send_to_slack` to a json format, inorder for the slack
   client can to it to a slack channel. After message has been formatted it calls slack client's
   `send_to_slack`and passes the newly formatted message as the parameter for this function.
## clients
### statistic client
  - `store_edge` stores the data(`activation id` and `edge state`) gained from the statistic repository in 
     `edge_dictionary` with the `activation id` acting as the key and the `edge state` as the associated value.
     Once that has been established it makes a call to `store_statistics_dictionary` and passes the edge state
     as a parameter.
  - `store_statistics_dictionary` is called to store the amount of occurrences of an edge state to the 
    `stats_dictionary`. It makes a check first to see if the edge state passed to it is already a key in 
    `stats_dictionary`. If it is a new occurrence then add it to the dictionary with a value of 1. Else if it
    already exists then increment that value of that edge_state by 1.
  - `get_statistics` is usually called after 10 minutes has passed and returns a message that will be passed down
    by actions in `app.py` to be formatted and sent to slack. The message format should look something like:
    ````
       Edge Status Counters (last 10 minutes)
       SOME_EDGE_STATUS: XXX
       ANOTHER_EDGE_STATUS: XXX
       Total: (sum of all edge statuses' values)
    ````
    *note: This is only how it looks like on slack however it is actually one long string with `\n` as the newline
           breaker *
  - `clear_dictionaries` is called once the message has been sent to slack, and it clears both the `edge_dictionary`
     and the `stats_dictionary`. Which allows us to record new data to be sent to slack again after another 10 minutes.
### slack client
   Slack Client receives the message passed down from the slack repository. And prepares to make a `POST` call to 
   to a webhook url, which is provided in the config file located in the config folder of this 
   microservice. Any `POST` calls made to that url will post to a slack channel. It however
   first must check that the webhook url is a valid url by checking to see if the string 
   `https://` is within the url.  Once that is cleared, it then makes the request call. A message will be 
   printed to the console and returned to determine if the message was successfully sent or not based on the status
   code of the request call. 200 is a success and anything else is a failure.

