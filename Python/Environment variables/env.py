#Install the python-dotenv library with -- pip intstall python-dotenv

#Import necessary libraries
import os
from dotenv import load_dotenv, dotenv_values

#Load environment variables from .env file into the environment
load_dotenv("sample.env")

#Fetch values from the environent variables
database_host=os.getenv("DATABSE_HOST")
database_user=os.getenv("DATABSE_USER")
mail=os.getenv("MAIL")
api_key=os.getenv("API_KEY")

#Print the retrieved values
print(f"Database Host: {database_host}")
print(f"Database User: {database_user}")
print(f"Mail: {mail}")
print(f"API Key: {api_key}")

"""When the environment variable has the same name with a regular variable,
if the override parameter in the load_dotenv() is set to True,
the values specified in the .env file will overwrite any existing environent variables with the same name.
"""
load_dotenv(override=True)

#USING DOTENV VALUES
#Since we have imported the dotenv_values() function at the top of the program, we can proceed to use the function here
config=dotenv_values("sample.env") # loads the environment variables and converts them into a dictionary
print(config["API_KEY"])

#USING .env.shared and .env.secret
#Load environment varables from .env.secretand .env.shared
config={
    **dotenv_values(".env.secret"),
    **dotenv_values(".env.shared")
}

#Print the retrieved values
print(config["API_KEY"])
print(config["DATABASE_HOST"])
print(config["DATABASE_USER"])
print(config["MAIL"])