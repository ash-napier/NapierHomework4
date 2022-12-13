# python-character-generator
## Summary
This tool can create random fantasy characters for use in fantasy stories or games. Characters can be randomly generated, or custom created based on the following characteristics:
- Name
- Profession from available options: Alchemist, Librarian, Cartographer, Cook, Herbalist, Leatherworker, Sailor, Smith, Woodcarver, Brewer, Carpenter, Cobbler, Glassblower, Jeweler, Mason, Painter, Potter, Weaver, Politician, Mercenary
- Class from available options: Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, Ranger, Rogue, Sorcerer, Warlock, Wizard, Artificer
- Race from available options: Dragonborn, Dwarf, Elf, Gnome, Half-Elf, Halfling, Half-Orc, Human, Tiefling
- Gender from available options: Male, Female, Nonbinary
- Personality Traits from over 1000 possible traits from Abrasive to Zealous
- Quirk from over 100 possible quirks that help make your character memorable
## Dev Notes
- This app was built in Cloud9 with boto3 and fpdf. 
- The app connects to AWS DynamoDB and S3 and may require aadditional work for you to run the app yourself to ensure you are connected to an AWS environment.
- Running this app will build resources in your AWS environment which may affect your monthly bill. Be sure to delete resources when done using the app.
- The BUCKET_NAME is a hard coded value for an S3 bucket, be sure to change the name to something that makes sense for you.
## User Manual
When running the application, the user will be prompted with the following main menu:
```
************************** MAIN MENU **************************
*  NPC BUILDER                                                *
***************************************************************
*  [1] Generate A Random Character                            *
*  [2] Build A Custom Character                               *
*  [3] View Saved Characters                                  *
*  [4] Download A Saved Character                             *
*  [5] Delete A Saved Character                               *
*  [6] Delete All Saved Characters                            *
*  [0] Exit the program                                       *
***************************************************************
```
### Option 1. Generate a random character
When this option is selected, the tool will randomly generate a character by pulling data from the database of available options. The tool displays the generated data for the character to the user with the following prompt:
-	User prompt: Would you like to save this character? Enter yes or no:
  -	If the user enters “yes” or “y”: The tool will create a PDF file of the character data and save it to both local storage and an S3 bucket.
  -	If the user enters “no” or “n” then the tool will return to the main menu without saving the character.
### Options 2. Generate a Custom Character
When this option is selected, the tool will walk the user through making a character with any combination of user selected attributes or randomly generated attributes. For each attribute, the user will receive with the following prompt:
-	User prompt: Would you like to use a random (attribute name)? Enter yes or no:
  -	If the user enters “yes” or “y” the tool will select a random value from the database of available values for the attribute. 
  -	If the user enters “no” or “n”, the tool will either prompt the user to select from the available options or enter their own text for the option depending on the attribute.
Once the user has selected or randomly generated all of the attributes for the character, the tool will display the character to the user with the following prompt:
-	User prompt: Would you like to save this character (yes or no)?
  -	If the user enters “yes” or “y”, The tool will create a PDF file of the character data and save it to both local storage and an S3 bucket.
  -	If the user enters “no” or “n”, then the tool will return to the main menu.
  -	If the user enters invalid input, they will see a Yes or No Error.
### Option 3:  View Saved Characters
When this option is selected, the tool will list all files currently in the S3 bucket.
### Option 4: Download A Saved Character
When this option is selected, the tool will show the available character files in the S3 bucket and prompt the following:
- User prompt: Which object would you like to select?
  - If the user enters a valid number that corresponds to an object, the file will be downloaded from the S3 bucket to local storage.
  - If the user enters an invalid selection, they will see the Number Selection Error
### Option 5. Delete A Saved Character
When this option is selected, the tool will show the available character files in the S3 bucket and prompt the following:
- User prompt: Deleted characters are permanently erased and cannot be restored. Would you like to continue? Enter yes or no:
  - If the user enters “yes” or “y”, the tool will display the available characters to be deleted and display the following prompt:
    - User prompt: Which object would you like to select?
      - If the user enters a valid number that corresponds to an object, the file will be deleted from the S3 bucket.
      -	If the user enters an invalid selection, they will see the Number Selection Error
  -	If the user enters “no” or “n”, then the tool will return to the main menu.
  -	If the user enters invalid input, they will see a Yes or No Error.
Option 6. Delete All Saved Characters
When this option is selected, the tool will show the available character files in the S3 bucket and prompt the following:
-	User prompt: Deleted characters are permanently erased and cannot be restored. Are you sure you want to do this? Enter yes or no:
  -	If the user enters “yes” or “y”, the tool will delete all files from the S3 bucket.
  -	If the user enters “no” or “n”, then the tool will return to the main menu.
  -	If the user enters invalid input, they will see a Yes or No Error.
## Troubleshooting Errors
### Yes or No Error 
If you see an error when answering a yes or no question, then the user entry contained characters that were not “yes”, “y”, “no”, or “n”. To resolve this error, attempt your entry again using only those characters.
### Number Selection Error
If you see an error on a number selection question, then you may have entered a character that wasn’t the number (digits) that corresponds to a menu option. To resolve this error, attempt your entry again using only the digit that corresponds to a valid menu option.
