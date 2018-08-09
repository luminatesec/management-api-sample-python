# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

This implementation of Luminate Security client is used to automate the process of creating applications (based on Luminate public API https://luminatepublicapi.docs.apiary.io/#).
Authentication to Luminate Security Service is Oauth based.


### How do I get set up? ###

#### 1. Steps

* Create a new API Client through Luminate Administration Portal

* Set luminate.properties configuration file (see section #2 - Configuration)

* Set luminate.application configuration file (see section #2 - Configuration)

* Run the container to create a new application as specified in the luminate.application configuration file 

```
#!bash

$ docker build -t luminate-client .

$ docker run -v <host dir for debug log files>:/opt/luminate-client/logs -v <host dir for conf files>:/opt/luminate-client/conf luminate-client
```

#### 2. Configuration

  luminate.properties configuration file that should be located under the conf directory (path is provided as a parameter to the 'docker run' command). It should include a single section named 'Luminate Properties' which contains keys with values as specified below. Explore Python ConfigParser to learn more about the structure of the file. 

  |Name                | Required  | Default Value   | Description                                                                                             | 
  |--------------------|-----------|---------------- |---------------------------------------------------------------------------------------------------------|
  |client_id           | Mandatory | N/A             | The client id of your API client that was configured through Luminate Administration Portal             |
  |client_secret       | Mandatory | N/A             | The client secret of the API client that was configured through Luminate Security Administration Portal |
  |tenant_name         | Mandatory | N/A             | Your Luminate Security tenant name                                                                      |
  |luminate_domain     | Mandatory | N/A             | Your Luminate Security Domain. For example luminatesec.com                                              |


  luminate.applications configuration file that should be located under the conf directory (path is provided as a parameter to the 'docker run' command). It can include multiple applications in different sections, each of which contains keys with values as specified below. Explore Python ConfigParser to learn more about the structure of the file. 

  |Name                | Required  | Default Value | Description                                                                              |
  |--------------------|-----------|---------------|------------------------------------------------------------------------------------------|
  |app_name            | Mandatory | N/A           | Application Name                                                                         |
  |description         | Optional  | Empty String  | Application Description                                                                  |
  |app_type            | Mandatory | N/A           | Application Type: HTTP or SSH                                                            |
  |internal_address    | Mandatory | N/A           | The Application internal address. For HTTP applications the format should be http://[DNS / IP address]:[port]. For SSH applications the format should be tcp://[DNS / IP address]:[port] |
  |site_name           | Mandatory | N/A           | The name of the site on which this application resides                                   |
  |email               | Optional  | None          | The e-mail address of the user to whom you would like to grant access to the application. Either email or group can be provided. |    
  |group_name          | Optional  | None          | The name of the group whose members should be granted with access to the application. Either email or group can be provided.     |                       
  |idp                 | Optional  | None          | Identity Provider of the user/group. The value should be an empy string for local users/groups                                                    |
  |ssh_users           | Optional  | N/A           | Specifies a list of user names that are available for SSH log-in on the remote machine. For example: ubuntu,unix1. This field is mandatory for SSH applications, not relevnat for web applications).    |
  |assigned_ssh_users  | Optional  | N/A           | A list of valid user-names on the remote SSH machine which this user will be allowed to log-in with on the remote-machine. For example: ubuntu,unix1. This filed should not be supplied for non-SSH applications). |
  
