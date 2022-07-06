#!/usr/bin/env python3

"""Regularly pulls data from one API and inserts it into a DB. 
"""

from http import HTTPStatus as httpstatus
import os
import requests
import schedule
import snowflake.connector
import time



def connect_to_snowflake():
    """Create a connection to the snowflake end point instance.

    Using the environment variables defined in the docker-compose yaml
    file, attempt to establish a connection with the desired snowflake
    database instance and return the context of the connection.

    Parameters:
    - None

    Returns:
    - a snowflake database connection context
    """
    user = os.getenv('SNOWSQL_USER')
    passwd = os.getenv('SNOWSQL_PASSWORD')
    acct = os.getenv('SNOWSQL_ACCOUNT')
    session_name = os.getenv('SNOWSQL_CUSTOMER')
    #warehouse = os.getenv('SNOWSQL_WAREHOUSE')
    #database = os.getenv('SNOWSQL_DATABASE')
    #schema = os.getenv('SNOWSQL_SCHEMA')
    #[...]
    context = snowflake.connector.connect(
                  user=user, 
                  password=passwd, 
                  account=acct, 
                  session_parameters={
                      'QUERY_TAG' = session_name;
                      }                    
                  #, warehouse=warehouse
                  #, database=database
                  #, schema=schema
                  #[...]
                  )
    return context



def connect_to_tradedesk():
    """Authenticate against tradedesk. 

    Using the environment variables defined in the docker-compose yaml
    file, attempt to authenticate against tradedesk's API and return 
    the found authentication token. 

    Parameters:
    - None

    Returns: 
    - Tradedesk's Authentication Token
    - May return something else depending on how you handle errors
    """
    url = os.getenv('TRADEDESK_AUTH_URL')
    user = os.getenv('TRADEDESK_USERNAME')
    passwd = os.getenv('TRADEDESK_PASSWORD')

    headers = {
        'content-type': 'application/json'
    }
    post_data = {
        'Login': user, 
        'Password': passwd
    }

    login_attempt = requests.post(url, headers=headers, json=post_data)

    if login_attempt.ok:
        return login_attempt.json()['Token']
     
    # Handle login failure
    login_attempt.raise_for_status()

        

def pull(auth_token=''):
    """Query Tradedesk to gather some data to insert into snowflake. 

    Using the API endpoint environment variable from the docker-compose
    yaml file and the authentication token generated elsewhere, attempt
    to query Tradedesk for some information. On success, returns the 
    queried data. If we hit a rate limit, use the retry-after value
    provided from the Tradedesk API to wait and try again. Do not try
    more than 10 times. 

    Parameters: 
    - auth_token: string representation of the API authentication token
                  grabbed from connect_to_tradedesk(). 

    Returns:
    - json-ified data set queried for on success. 
    - May return something else if configured to do so.
    """
    url = os.getenv('TRADEDESK_API_ENDPOINT')

    headers = {
        'content-type': 'application/json', 
        'TTD-Auth': auth_token
    }

    post_data = {
        # Put some stuff here
    }

    attempts = 10
    while attempts > 0:
        query_results = requests.post(url, headers=headers, json=post_data)
    
        if query_results.ok:
            return query_results.json()

        elif query_results.status_code == httpstatus.TOO_MANY_REQUESTS:
            retry_after = int(query_results.headers['retry-after'])
            time.sleep(retry_after)
            retries -= 1

        #elif query_results.status_code == some other http error code:
        #    handle it



def push(data=None, con=None):
    """Push some data to a snowflake database instance. 

    With data retrieved from Tradedesk via pull() and a connection to a
    snowflake database instance via connect_to_snowflake(), insert the 
    data into the database instance. If it fails, rollback any changes
    close the connection, and raise an exception (or something else). 

    Parameters:
    - data: the data retrieved from Tradedesk and to be inserted into a
            snowflake database.
    - con: an established snowflake database instance created from 
           connect_to_snowflake(). 

    Returns
    - None
    """
    try:
        con.cursor.execute(
                #'''insert into table values data'''
                )
    except Exception as exception:
        con.rollback()
        con.close()
        raise exception

    con.close()


def job():
    """Pulls data from Tradedesk and pushes it to snowflake. 

    Authenticates against tradedesk and queries Tradedesk for some data
    to populate into snowflake. Connects to snowflake and then pushes
    the data to snowflake. 

    Parameters:
    - None

    Returns: 
    - None
    """
    auth_token = connect_to_tradedesk()
    data = pull(auth_token)
    con = connect_to_snowflake()
    push(data, con)



def sched_job():
    """Schedules a pull and push at 4:00 AM every day. 

    Reference: https://www.delftstack.com/howto/python/python-schedule/

    Parameters:
    - None

    Returns: 
    - None
    """
    schedule.every().day.at("04:00").do(job)



if __name__ == '__main__':
    sched_job()

