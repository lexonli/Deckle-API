# Deckle API 

##### Documentation on incorporating Google authentication process (OAuth 2.0)


* Using an API key to access personal calendars is not possible, access tokens must be used along with the OAuth 2.0 process
        reference: https://stackoverflow.com/questions/42015397/still-possible-to-use-google-calendar-api-with-api-key
* A brief description on OAuth 2.0
        reference: https://developers.google.com/api-client-library/python/guide/aaa_oauth
* Flow: OAuth 2.0 for TVs and device apps
        the whole setup process is documented here: https://developers.google.com/identity/protocols/OAuth2ForDevices
        make sure to visit again when getting the refresh token to work

* More comprehensive documentation on OAuth 2.0
        https://tools.ietf.org/html/rfc6749#page-4



* In python, I used requests to make calls to the authentication server at google for the access token and polling
        https://realpython.com/python-requests/

* The token is used to create credentials using the oauth2 client
        https://oauth2client.readthedocs.io/en/latest/source/oauth2client.client.html#oauth2client.client.AccessTokenCredentials
        source code: https://oauth2client.readthedocs.io/en/latest/_modules/oauth2client/client.html#AccessTokenCredentials

* The credentials object can then be put into the `build` function to create a client for the google calendar api calls
        Here: https://github.com/googleapis/google-api-python-client/blob/master/googleapiclient/discovery.py
        
        
* I was confused with the user_agent argument required for creating the credentials object, but I got it working anyway using an arbitrary one for mozilla firefox
  here is some info on user_agents
        https://forums.aws.amazon.com/thread.jspa?threadID=204244
        https://www.scrapehero.com/how-to-fake-and-rotate-user-agents-using-python-3/
        http://docs.developer.amazonservices.com/en_UK/dev_guide/DG_UserAgentHeader.html
        https://docs.aws.amazon.com/silk/latest/developerguide/user-agent.html
        
        
* The credentials object can then be put into the `build` function to create a client for the google calendar api calls
        Here: https://github.com/googleapis/google-api-python-client/blob/master/googleapiclient/discovery.py
        
        
 ##### Documentation on using datetime and handling timezone issues (running in US-east Virginia AWS is a pain in the ass)
 
 * Google calendar API is quite considerate, since it receives the datetime isoformat with timezone information
 
 * I had to spend a bit of time to look up how timezone-aware and timezone-naive datetimes work
        https://stackoverflow.com/questions/4530069/python-how-to-get-a-value-of-datetime-today-that-is-timezone-aware
 * Now, it's working great, since the API reads the time by looking at the timezone specified
        https://stackoverflow.com/questions/2331592/why-does-datetime-datetime-utcnow-not-contain-timezone-information
        
 ##### Amazon IAM policies
 * received this error when trying to run decklelist
 ```
 botocore.exceptions.ClientError: An error occurred (AccessDenied) when calling the GetObject operation: Access Denied
 ```
 Find ARN naming in https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html#genref-arns
 The problem was I specified the bucket itself in the policy only, not the object itself
 Solution: 
 ```
 add "/*" to the end of the bucket name in the policy
 ```
