# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

This implemntation of Luminate Security client is used to automate the process of creating applications. 
Autehtication to Luminate Security Service is Oauth based.


### How do I get set up? ###

#### 1. Steps

* Create a new API Client through Luminate Administration Portal

* Set luminate.properties configuration file (see section #2 - Configuration)

* Set luminate.application configuration file (see section #2 - Configuration)

* Run the container to create a new application as specified in the luminate.application configuration file 

```
#!bash

$ docker run -v <host dir for debug log files>:/opt/luminate-client/logs -v <host dir for conf files>:/opt/luminate-client/conf luminate-client
```

#### 2. Configuration
  luminate.properties configuration file is located at $APP_CONFIGURATION_PATH includes the following parameters:

  |Name                | Required  | Default Value   | Description                                                                                             | 
  |--------------------|-----------|---------------- |---------------------------------------------------------------------------------------------------------|
  |client_id           | Mandatory | N/A             | The client id of your API client that was configured through Luminate Administration Portal             |
  |client_secret       | Mandatory | N/A             | The client secret of the API client that was configured through Luminate Security Administration Portal |
  |tenant_name         | Mandatory | N/A             | Your Luminate Security tenant name                                                                      |
  |luminate_domain     | Mandatory | N/A             | Your Luminate Security Domain                                                                           |


  luminate.application configuration file is located at $APP_CONFIGURATION_PATH includes the following parameters:

  |Name                | Required  | Default Value | Description                                                                              |
  |--------------------|-----------|---------------|------------------------------------------------------------------------------------------|
  |app_name            | Mandatory | N/A           | Application Name                                                                         |
  |description         | Optional  | Empty String  | Application Description                                                                  |
  |app_type            | Mandatory | N/A           | Application Type: HTTP or SSH                                                            |
  |internal_address    | Mandatory | N/A           | The Application internal address                                                         |
  |site_name           | Mandatory | N/A           | The name of the site on which this application resides                                   |
  |email               | Optional  | None          | The e-mail address of the user to whom you would like to grant access to the application |                       
  |idp                 | Optional  | None          | Identity Provider of the user. This field should be empty in case of a local user        |